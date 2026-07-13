from app.ai.pipeline import PipelineOrchestrator

from app.ai.preprocessing.loader import AudioLoaderService
from app.ai.preprocessing.noise_reduction import NoiseReductionService

from app.ai.vad.silero import SileroVADService
from app.ai.diarization.pyannote import PyannoteDiarizationService
from app.ai.embeddings.speechbrain import SpeechBrainEmbeddingService

from app.ai.clustering.hdbscan import HDBSCANClusteringService
from app.ai.separation.sepformer import SepFormerSeparationService
from app.ai.transcription.whisper import WhisperTranscriptionService
from app.ai.metadata.analyzer import MetadataAnalyzerService
from app.ai.reconstruction.reconstructor import ReconstructionService


def get_pipeline() -> PipelineOrchestrator:
    return PipelineOrchestrator(
        loader=AudioLoaderService(),
        noise_reducer=NoiseReductionService(),
        vad=SileroVADService(),
        diarizer=PyannoteDiarizationService(),
        embedder=SpeechBrainEmbeddingService(),
        clusterer=HDBSCANClusteringService(),
        separator=SepFormerSeparationService(),
        transcriber=WhisperTranscriptionService(),
        metadata_analyzer=MetadataAnalyzerService(),
        reconstructor=ReconstructionService(),
    )