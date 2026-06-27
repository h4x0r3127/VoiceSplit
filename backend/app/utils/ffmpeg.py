import json
import subprocess
from typing import List

from app.utils.logging import get_logger

logger = get_logger(__name__)


class FFmpegWrapper:
    def run_command(self, args: List[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            logger.error(
                "ffmpeg_command_failed",
                command=args,
                stderr=result.stderr,
                returncode=result.returncode,
            )
            raise RuntimeError(
                f"FFmpeg command failed (exit {result.returncode}): {result.stderr}"
            )
        return result

    def probe(self, file_path: str) -> dict:
        args = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path,
        ]
        result = self.run_command(args)
        return json.loads(result.stdout)

    def convert(self, input_path: str, output_path: str, extra_args: List[str] | None = None) -> None:
        args = ["ffmpeg", "-y", "-i", input_path]
        if extra_args:
            args.extend(extra_args)
        args.append(output_path)
        self.run_command(args)
        logger.info("ffmpeg_convert", input=input_path, output=output_path)

    def extract_audio(self, video_path: str, output_path: str) -> None:
        self.convert(
            video_path,
            output_path,
            extra_args=["-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2"],
        )
        logger.info("ffmpeg_extract_audio", video=video_path, output=output_path)

    def convert_format(
        self,
        input_path: str,
        output_path: str,
        format: str,
        bitrate: str = "192k",
    ) -> None:
        extra_args: List[str] = []
        if format == "mp3":
            extra_args = ["-acodec", "libmp3lame", "-ab", bitrate]
        elif format == "flac":
            extra_args = ["-acodec", "flac"]
        elif format == "wav":
            extra_args = ["-acodec", "pcm_s16le"]
        elif format == "aac":
            extra_args = ["-acodec", "aac", "-ab", bitrate]

        self.convert(input_path, output_path, extra_args=extra_args)
        logger.info("ffmpeg_convert_format", input=input_path, format=format, output=output_path)
