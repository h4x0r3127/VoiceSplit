import asyncio
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np
import torch

from app.ai.interfaces import (
    AudioData,
    DiarizationSegment,
    EmbeddingInterface,
    SpeakerEmbedding,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SpeechBrainEmbeddingService(EmbeddingInterface):
    def __init__(self, model_source: str = "speechbrain/spkrec-ecapa-voxceleb") -> None:
        self._model_source = model_source
        self._classifier = None

    def _load_model(self) -> None:
        if self._classifier is not None:
            return
        from speechbrain.pretrained import EncoderClassifier

        self._classifier = EncoderClassifier.from_hparams(
            source=self._model_source,
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        )
        logger.info("speechbrain_ecapa_loaded", source=self._model_source)

    async def extract(
        self,
        audio: AudioData,
        segments: List[DiarizationSegment],
    ) -> List[SpeakerEmbedding]:
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, self._extract_sync, audio, segments
        )
        logger.info("embeddings_extracted", speakers=len(embeddings))
        return embeddings

    def _extract_sync(
        self,
        audio: AudioData,
        segments: List[DiarizationSegment],
    ) -> List[SpeakerEmbedding]:
        self._load_model()

        waveform = audio.waveform
        sr = audio.sample_rate

        speaker_segments: Dict[str, List[DiarizationSegment]] = defaultdict(list)
        for seg in segments:
            speaker_segments[seg.speaker_label].append(seg)

        results: List[SpeakerEmbedding] = []
        for label, segs in speaker_segments.items():
            chunk_embeddings: List[np.ndarray] = []
            for seg in segs:
                start_sample = int(seg.start * sr)
                end_sample = int(seg.end * sr)
                chunk = waveform[start_sample:end_sample]

                if len(chunk) < sr * 0.5:
                    continue

                chunk_tensor = torch.FloatTensor(chunk).unsqueeze(0)
                with torch.no_grad():
                    emb = self._classifier.encode_batch(chunk_tensor)
                chunk_embeddings.append(emb.squeeze().cpu().numpy())

            if not chunk_embeddings:
                continue

            mean_embedding = np.mean(chunk_embeddings, axis=0)
            results.append(
                SpeakerEmbedding(
                    speaker_label=label,
                    embedding=mean_embedding,
                    segments=segs,
                )
            )

        return results
