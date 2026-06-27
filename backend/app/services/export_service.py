import os
import uuid
import json
import asyncio
from typing import List

from app.models.export import Export, ExportFormat, ExportStatus
from app.models.job import Job
from app.models.speaker import Speaker
from app.services.storage.base import StorageService
from app.utils.ffmpeg import FFmpegWrapper
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ExportService:
    def __init__(self, storage: StorageService) -> None:
        self._storage = storage
        self._ffmpeg = FFmpegWrapper()

    async def create_export(
        self,
        export: Export,
        job: Job,
        speakers: List[Speaker],
        work_dir: str,
    ) -> str:
        """
        Orchestrate export generation. Returns the S3 key of the exported file.
        Raises on failure — caller should update export status to FAILED.
        """
        os.makedirs(work_dir, exist_ok=True)

        selected_ids = {str(sid) for sid in export.selected_speaker_ids}
        selected_speakers = [s for s in speakers if str(s.id) in selected_ids]

        if not selected_speakers:
            raise ValueError("No matching speakers found for selected IDs")

        output_format = export.output_format
        export_key = f"exports/{export.id}/{export.id}.{output_format.value}"

        if output_format in (ExportFormat.TXT, ExportFormat.JSON, ExportFormat.CSV):
            output_path = os.path.join(work_dir, f"export.{output_format.value}")
            self._build_transcript_export(job, selected_speakers, output_path, output_format)
        else:
            audio_path = await self._build_audio_export(
                job, selected_speakers, work_dir, output_format
            )
            output_path = audio_path

        await self._storage.upload_from_path(
            export_key, output_path, _content_type(output_format)
        )
        logger.info(
            "export_uploaded",
            export_id=str(export.id),
            key=export_key,
            format=output_format.value,
        )
        return export_key

    def _build_transcript_export(
        self,
        job: Job,
        speakers: List[Speaker],
        output_path: str,
        fmt: ExportFormat,
    ) -> None:
        metadata = job.audio_metadata or {}
        transcript = metadata.get("transcript", [])
        selected_labels = {s.label for s in speakers}

        filtered = [seg for seg in transcript if seg.get("speaker_id") in selected_labels]

        if fmt == ExportFormat.TXT:
            with open(output_path, "w", encoding="utf-8") as fh:
                for seg in filtered:
                    fh.write(f"[{seg.get('start', 0):.2f}s] {seg.get('speaker_id', '')}: {seg.get('text', '')}\n")

        elif fmt == ExportFormat.JSON:
            with open(output_path, "w", encoding="utf-8") as fh:
                json.dump({"segments": filtered}, fh, indent=2)

        elif fmt == ExportFormat.CSV:
            import csv

            with open(output_path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=["start", "end", "speaker_id", "text", "confidence"])
                writer.writeheader()
                for seg in filtered:
                    writer.writerow(
                        {
                            "start": seg.get("start", 0),
                            "end": seg.get("end", 0),
                            "speaker_id": seg.get("speaker_id", ""),
                            "text": seg.get("text", ""),
                            "confidence": seg.get("confidence", 1.0),
                        }
                    )

    async def _build_audio_export(
        self,
        job: Job,
        speakers: List[Speaker],
        work_dir: str,
        fmt: ExportFormat,
    ) -> str:
        import numpy as np
        import soundfile as sf

        mixed: np.ndarray | None = None
        target_sr = 16000

        for speaker in speakers:
            if not speaker.preview_s3_key:
                continue
            raw = await self._storage.download_file(speaker.preview_s3_key)
            spk_path = os.path.join(work_dir, f"{speaker.id}.wav")
            with open(spk_path, "wb") as fh:
                fh.write(raw)

            data, sr = sf.read(spk_path, dtype="float32")
            if sr != target_sr:
                import resampy
                data = resampy.resample(data, sr, target_sr)

            if mixed is None:
                mixed = data
            else:
                if len(data) > len(mixed):
                    pad = np.zeros(len(data) - len(mixed), dtype=np.float32)
                    mixed = np.concatenate([mixed, pad])
                elif len(mixed) > len(data):
                    pad = np.zeros(len(mixed) - len(data), dtype=np.float32)
                    data = np.concatenate([data, pad])
                mixed = mixed + data

        if mixed is None:
            mixed = np.zeros(target_sr, dtype=np.float32)

        peak = np.abs(mixed).max()
        if peak > 0:
            mixed = mixed / peak * 0.95

        wav_path = os.path.join(work_dir, "mixed.wav")
        sf.write(wav_path, mixed, target_sr, subtype="PCM_16")

        if fmt == ExportFormat.WAV:
            return wav_path

        out_path = os.path.join(work_dir, f"export.{fmt.value}")
        bitrate = "320k" if fmt == ExportFormat.MP3 else "0"
        self._ffmpeg.convert_format(wav_path, out_path, fmt.value, bitrate=bitrate)
        return out_path


def _content_type(fmt: ExportFormat) -> str:
    mapping = {
        ExportFormat.MP3: "audio/mpeg",
        ExportFormat.WAV: "audio/wav",
        ExportFormat.FLAC: "audio/flac",
        ExportFormat.TXT: "text/plain",
        ExportFormat.JSON: "application/json",
        ExportFormat.CSV: "text/csv",
    }
    return mapping.get(fmt, "application/octet-stream")
