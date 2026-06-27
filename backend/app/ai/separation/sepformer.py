import asyncio
import tempfile
import os
from typing import List, Optional

import numpy as np
import torch

from app.ai.interfaces import (
    AudioData,
    SeparationInterface,
    SeparatedAudio,
    SpeakerCluster,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _assign_streams_to_clusters(
    streams: np.ndarray,
    clusters: List[SpeakerCluster],
    audio: AudioData,
) -> List[SeparatedAudio]:
    """
    Assign separated streams to speaker clusters using cross-correlation
    between each stream and the expected speech mask for each cluster.
    Falls back to sequential assignment when clusters > streams.
    """
    n_streams = streams.shape[0]
    n_clusters = len(clusters)
    sr = audio.sample_rate

    if n_streams >= n_clusters:
        scores = np.zeros((n_clusters, n_streams))
        for ci, cluster in enumerate(clusters):
            mask = np.zeros(len(audio.waveform), dtype=np.float32)
            for seg in cluster.segments:
                s = int(seg.start * sr)
                e = min(int(seg.end * sr), len(mask))
                mask[s:e] = 1.0

            for si in range(n_streams):
                stream = streams[si]
                n = min(len(mask), len(stream))
                scores[ci, si] = float(np.dot(mask[:n], np.abs(stream[:n])))

        assigned: List[SeparatedAudio] = []
        used_streams: set = set()
        for ci, cluster in enumerate(clusters):
            best_stream = int(np.argmax(scores[ci]))
            while best_stream in used_streams and len(used_streams) < n_streams:
                scores[ci, best_stream] = -1
                best_stream = int(np.argmax(scores[ci]))
            used_streams.add(best_stream)
            assigned.append(
                SeparatedAudio(
                    speaker_id=cluster.cluster_id,
                    waveform=streams[best_stream],
                    sample_rate=sr,
                )
            )
        return assigned
    else:
        return [
            SeparatedAudio(
                speaker_id=clusters[i].cluster_id if i < n_clusters else f"speaker_{i}",
                waveform=streams[i],
                sample_rate=sr,
            )
            for i in range(n_streams)
        ]


class SepFormerSeparationService(SeparationInterface):
    def __init__(self) -> None:
        self._separator = None

    def _load_model(self) -> None:
        if self._separator is not None:
            return
        from speechbrain.pretrained import SepformerSeparation

        self._separator = SepformerSeparation.from_hparams(
            source="speechbrain/sepformer-whamr",
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        )
        logger.info("sepformer_model_loaded")

    async def separate(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[SeparatedAudio]:
        loop = asyncio.get_event_loop()
        separated = await loop.run_in_executor(None, self._separate_sync, audio, clusters)
        logger.info("separation_complete", streams=len(separated))
        return separated

    def _separate_sync(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[SeparatedAudio]:
        import soundfile as sf

        self._load_model()

        waveform = audio.waveform
        if waveform.ndim > 1:
            waveform = waveform.mean(axis=0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            sf.write(tmp_path, waveform, audio.sample_rate, subtype="PCM_16")
            est_sources = self._separator.separate_file(path=tmp_path)
        finally:
            os.unlink(tmp_path)

        streams = est_sources.squeeze().cpu().numpy()
        if streams.ndim == 1:
            streams = streams[np.newaxis, :]
        elif streams.ndim == 2 and streams.shape[0] > streams.shape[1]:
            streams = streams.T

        return _assign_streams_to_clusters(streams, clusters, audio)
