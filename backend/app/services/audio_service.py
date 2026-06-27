import json
import subprocess
from dataclasses import dataclass
from typing import Optional

from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AudioInfo:
    duration: float
    format_name: str
    sample_rate: int
    channels: int
    bit_rate: int
    codec_name: str


class AudioService:
    def validate_audio_file(self, path: str) -> AudioInfo:
        from app.utils.ffmpeg import FFmpegWrapper

        wrapper = FFmpegWrapper()
        probe_data = wrapper.probe(path)

        format_info = probe_data.get("format", {})
        streams = probe_data.get("streams", [])

        audio_stream = next(
            (s for s in streams if s.get("codec_type") == "audio"), None
        )
        if audio_stream is None:
            raise ValueError(f"No audio stream found in file: {path}")

        return AudioInfo(
            duration=float(format_info.get("duration", 0)),
            format_name=format_info.get("format_name", "unknown"),
            sample_rate=int(audio_stream.get("sample_rate", 44100)),
            channels=int(audio_stream.get("channels", 1)),
            bit_rate=int(format_info.get("bit_rate", 0)),
            codec_name=audio_stream.get("codec_name", "unknown"),
        )

    def convert_to_wav(self, input_path: str, output_path: str) -> None:
        from app.utils.ffmpeg import FFmpegWrapper

        wrapper = FFmpegWrapper()
        wrapper.convert(
            input_path,
            output_path,
            extra_args=["-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le"],
        )
        logger.info("audio_converted_to_wav", input=input_path, output=output_path)

    def extract_segment(
        self,
        input_path: str,
        output_path: str,
        start: float,
        end: float,
    ) -> None:
        from app.utils.ffmpeg import FFmpegWrapper

        wrapper = FFmpegWrapper()
        duration = end - start
        wrapper.convert(
            input_path,
            output_path,
            extra_args=["-ss", str(start), "-t", str(duration)],
        )
        logger.info(
            "audio_segment_extracted",
            input=input_path,
            start=start,
            end=end,
            output=output_path,
        )

    def get_audio_duration(self, path: str) -> float:
        info = self.validate_audio_file(path)
        return info.duration
