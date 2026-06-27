import asyncio
import os
import tempfile
from typing import List

import numpy as np
import torch

from app.ai.interfaces import (
    AudioData,
    SeparatedAudio,
    SeparationInterface,
    SpeakerCluster,
)
from app.ai.separation.sepformer import _assign_streams_to_clusters
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ConvTasNetSeparationService(SeparationInterface):
    """
    Alternative to SepFormerSeparationService using a ConvTasNet-based model.
    Drop-in replacement — swappable without any changes to PipelineOrchestrator.
    """

    def __init__(self) -> None:
        self._separator = None

    def _load_model(self) -> None:
        if self._separator is not None:
            return
        from speechbrain.pretrained import SepformerSeparation

        self._separator = SepformerSeparation.from_hparams(
            source="speechbrain/sepformer-wsj02mix",
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        )
        logger.info("convtasnet_model_loaded")

    async def separate(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[SeparatedAudio]:
        loop = asyncio.get_event_loop()
        separated = await loop.run_in_executor(None, self._separate_sync, audio, clusters)
        logger.info("convtasnet_separation_complete", streams=len(separated))
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
