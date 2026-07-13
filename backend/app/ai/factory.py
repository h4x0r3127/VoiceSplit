from app.ai.pipeline import PipelineOrchestrator

from app.ai.preprocessing.audio_loader import AudioLoaderService
from app.ai.preprocessing.noise_reduction import NoiseReductionService

from app.ai.vad.silero import SileroVADService
from app.ai.diarization.pyannote import PyannoteDiarizationService
from app.ai.embeddings.speechbrain import SpeechBrainEmbeddingService

from app.ai.clustering.agglomerative import AgglomerativeClusteringService
from app.ai.separation.sepformer import SepFormerSeparationService
from app.ai.transcription.whisper import WhisperTranscriptionService
from app.ai.metadata.librosa_analyzer import LibrosaMetadataService
from app.ai.reconstruction.reconstructor import AudioReconstructionService


def get_pipeline() -> PipelineOrchestrator:
    return PipelineOrchestrator(
        loader=AudioLoaderService(),
        noise_reducer=NoiseReductionService(),
        vad=SileroVADService(),
        diarizer=PyannoteDiarizationService(),
        embedder=SpeechBrainEmbeddingService(),
        clusterer=AgglomerativeClusteringService(),
        separator=SepFormerSeparationService(),
        transcriber=WhisperTranscriptionService(),
        metadata_analyzer=LibrosaMetadataService(),
        reconstructor=AudioReconstructionService(),
    )