import asyncio
from typing import Awaitable, Callable, List

from app.ai.interfaces import (
    AudioData,
    AudioLoaderInterface,
    ClusteringInterface,
    DiarizationInterface,
    EmbeddingInterface,
    MetadataInterface,
    NoiseReductionInterface,
    PipelineResult,
    ReconstructionInterface,
    SeparationInterface,
    SpeakerCluster,
    TranscriptionInterface,
    VADInterface,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

ProgressCallback = Callable[[str, int, str], Awaitable[None]]

_STAGE_WEIGHTS = {
    "LOADING": 5,
    "NOISE_REDUCTION": 10,
    "VAD": 15,
    "DIARIZING": 30,
    "EMBEDDING": 40,
    "CLUSTERING": 45,
    "SEPARATING": 70,
    "TRANSCRIBING": 85,
    "ANALYZING": 95,
    "COMPLETED": 100,
}


class PipelineOrchestrator:
    def __init__(
        self,
        loader: AudioLoaderInterface,
        noise_reducer: NoiseReductionInterface,
        vad: VADInterface,
        diarizer: DiarizationInterface,
        embedder: EmbeddingInterface,
        clusterer: ClusteringInterface,
        separator: SeparationInterface,
        transcriber: TranscriptionInterface,
        metadata_analyzer: MetadataInterface,
        reconstructor: ReconstructionInterface,
    ) -> None:
        self._loader = loader
        self._noise_reducer = noise_reducer
        self._vad = vad
        self._diarizer = diarizer
        self._embedder = embedder
        self._clusterer = clusterer
        self._separator = separator
        self._transcriber = transcriber
        self._metadata_analyzer = metadata_analyzer
        self._reconstructor = reconstructor

    async def run(
        self,
        job_id: str,
        audio_path: str,
        progress_callback: ProgressCallback,
    ) -> PipelineResult:
        logger.info("pipeline_start", job_id=job_id, audio_path=audio_path)

        await progress_callback("LOADING", _STAGE_WEIGHTS["LOADING"], "Loading audio file...")
        audio = await self._loader.load(audio_path)
        logger.info("pipeline_loaded", job_id=job_id, duration=audio.duration)

        await progress_callback(
            "NOISE_REDUCTION", _STAGE_WEIGHTS["NOISE_REDUCTION"], "Reducing background noise..."
        )
        clean_audio = await self._noise_reducer.reduce(audio)

        await progress_callback("VAD", _STAGE_WEIGHTS["VAD"], "Detecting speech segments...")
        vad_segments = await self._vad.detect(clean_audio)
        logger.info("pipeline_vad_done", job_id=job_id, segments=len(vad_segments))

        await progress_callback(
            "DIARIZING", _STAGE_WEIGHTS["DIARIZING"], "Detecting speaker boundaries..."
        )
        diarization_segments = await self._diarizer.diarize(clean_audio, vad_segments)
        logger.info(
            "pipeline_diarization_done",
            job_id=job_id,
            segments=len(diarization_segments),
        )

        await progress_callback(
            "EMBEDDING", _STAGE_WEIGHTS["EMBEDDING"], "Extracting speaker voice prints..."
        )
        embeddings = await self._embedder.extract(clean_audio, diarization_segments)
        logger.info("pipeline_embeddings_done", job_id=job_id, speakers=len(embeddings))

        await progress_callback(
            "CLUSTERING", _STAGE_WEIGHTS["CLUSTERING"], "Clustering speaker identities..."
        )
        clusters: List[SpeakerCluster] = self._clusterer.cluster(embeddings)
        logger.info("pipeline_clustering_done", job_id=job_id, clusters=len(clusters))

        await progress_callback(
            "SEPARATING", _STAGE_WEIGHTS["SEPARATING"], "Separating individual speaker audio..."
        )
        separated_audio = await self._separator.separate(clean_audio, clusters)
        logger.info("pipeline_separation_done", job_id=job_id, streams=len(separated_audio))

        await progress_callback(
            "TRANSCRIBING", _STAGE_WEIGHTS["TRANSCRIBING"], "Transcribing speech..."
        )
        transcript = await self._transcriber.transcribe(clean_audio, clusters)
        logger.info("pipeline_transcription_done", job_id=job_id, segments=len(transcript))

        await progress_callback(
            "ANALYZING", _STAGE_WEIGHTS["ANALYZING"], "Analyzing audio metadata..."
        )
        metadata = await self._metadata_analyzer.analyze(clean_audio, separated_audio)

        await progress_callback("COMPLETED", _STAGE_WEIGHTS["COMPLETED"], "Pipeline complete!")
        logger.info("pipeline_complete", job_id=job_id)

        return PipelineResult(
            speakers=clusters,
            separated_audio=separated_audio,
            transcript=transcript,
            metadata=metadata,
        )
