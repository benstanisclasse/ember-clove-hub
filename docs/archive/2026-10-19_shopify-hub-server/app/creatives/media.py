"""ffmpeg / ffprobe helpers (both are in the Docker image). Failures return None: a missing
probe never blocks a creative, a missing thumbnail only blocks platforms that need one."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app.log import get_logger

log = get_logger(__name__)
EXT = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


def ext_for(mime: str) -> str:
    return EXT.get(mime, ".bin")


def probe(content: bytes, mime: str) -> dict[str, Any] | None:
    """``{width, height, duration}`` via ffprobe, or None."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"in{ext_for(mime)}"
        path.write_bytes(content)
        try:
            out = subprocess.run(  # noqa: S603
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-print_format",
                    "json",
                    "-show_streams",
                    "-show_format",
                    str(path),
                ],
                capture_output=True,
                timeout=60,
                check=True,
            ).stdout
        except (subprocess.SubprocessError, OSError) as exc:
            log.warning("ffprobe_failed", error=str(exc)[:200])
            return None
    info = json.loads(out or b"{}")
    stream = next(
        (s for s in info.get("streams", []) if s.get("codec_type") in ("video", "image")), {}
    ) or next(iter(info.get("streams", [])), {})
    duration = (info.get("format") or {}).get("duration")
    return {
        "width": stream.get("width"),
        "height": stream.get("height"),
        "duration": float(duration) if duration not in (None, "N/A") else None,
    }


def thumbnail(video: bytes, mime: str = "video/mp4", at_seconds: float = 1.0) -> bytes | None:
    """A JPEG frame from ``at_seconds`` in (falls back to the first frame)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    with tempfile.TemporaryDirectory() as d:
        src, dst = Path(d) / f"in{ext_for(mime)}", Path(d) / "thumb.jpg"
        src.write_bytes(video)
        for ts in (at_seconds, 0.0):
            try:
                subprocess.run(  # noqa: S603
                    [
                        ffmpeg,
                        "-y",
                        "-v",
                        "error",
                        "-ss",
                        str(ts),
                        "-i",
                        str(src),
                        "-frames:v",
                        "1",
                        "-q:v",
                        "2",
                        str(dst),
                    ],
                    capture_output=True,
                    timeout=120,
                    check=True,
                )
                if dst.exists() and dst.stat().st_size > 0:
                    return dst.read_bytes()
            except (subprocess.SubprocessError, OSError) as exc:
                log.warning("thumbnail_failed", at=ts, error=str(exc)[:200])
    return None
