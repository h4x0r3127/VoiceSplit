from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass
class AudioData:
    waveform: np.ndarray  # shape: (samples,) mono or (channels, samples)
    sample_rate: int
    duration: float
    file_path: str


@dataclass
class VADSegment:
    start: float
    end: float
    confidence: float


@dataclass
class DiarizationSegment:
    start: float
    end: float
    speaker_label: str


@dataclass
class SpeakerEmbedding:
    speaker_label: str
    embedding: np.ndarray  # 192-dim ECAPA-TDNN vector
    segments: List[DiarizationSegment]


@dataclass
class SpeakerCluster:
    cluster_id: str
    color: str
    embedding: np.ndarray
    segments: List[DiarizationSegment]


@dataclass
class SeparatedAudio:
    speaker_id: str
    waveform: np.ndarray
    sample_rate: int


@dataclass
class TranscriptSegment:
    start: float
    end: float
    speaker_id: str
    text: str
    confidence: float


@dataclass
class AudioMetadata:
    tempo: float
    pitch_mean: float
    energy_mean: float
    speaking_rate: float
    pause_duration_total: float
    dominant_emotion: str


@dataclass
class PipelineResult:
    speakers: List[SpeakerCluster]
    separated_audio: List[SeparatedAudio]
    transcript: List[TranscriptSegment]
    metadata: AudioMetadata


class AudioLoaderInterface(ABC):
    @abstractmethod
    async def load(self, file_path: str) -> AudioData:
        ...


class NoiseReductionInterface(ABC):
    @abstractmethod
    async def reduce(self, audio: AudioData) -> AudioData:
        ...


class VADInterface(ABC):
    @abstractmethod
    async def detect(self, audio: AudioData) -> List[VADSegment]:
        ...


class DiarizationInterface(ABC):
    @abstractmethod
    async def diarize(
        self, audio: AudioData, vad_segments: List[VADSegment]
    ) -> List[DiarizationSegment]:
        ...


class EmbeddingInterface(ABC):
    @abstractmethod
    async def extract(
        self, audio: AudioData, segments: List[DiarizationSegment]
    ) -> List[SpeakerEmbedding]:
        ...


class ClusteringInterface(ABC):
    @abstractmethod
    def cluster(self, embeddings: List[SpeakerEmbedding]) -> List[SpeakerCluster]:
        ...


class SeparationInterface(ABC):
    @abstractmethod
    async def separate(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[SeparatedAudio]:
        ...


class TranscriptionInterface(ABC):
    @abstractmethod
    async def transcribe(
        self, audio: AudioData, clusters: List[SpeakerCluster]
    ) -> List[TranscriptSegment]:
        ...


class MetadataInterface(ABC):
    @abstractmethod
    async def analyze(
        self, audio: AudioData, separated: List[SeparatedAudio]
    ) -> AudioMetadata:
        ...


class ReconstructionInterface(ABC):
    @abstractmethod
    async def reconstruct(
        self,
        separated: List[SeparatedAudio],
        selected_ids: List[str],
        original: AudioData,
    ) -> AudioData:
        ...
