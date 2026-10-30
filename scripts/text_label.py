"""Finish a vertical clip for TikTok: 1080x1920, 30 fps, silent AAC track, and optionally one short text label.

The label copies the look of the top barbed-wire videos (WINNER_STUDY.md): one line of plain white text with a soft
shadow, centred, near the top by default (clear of TikTok's caption and button areas). Adding a label is an edit, so label
versions need the owner's approval before use.

  python scripts/text_label.py <in.mp4> <out.mp4> ["label text" [height 0-1, default 0.12]]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "C:/Windows/Fonts/segoeuib.ttf"


def label_png(text: str, path: Path, y: float) -> None:
    font = ImageFont.truetype(FONT, 64)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    pos = ((W - (x1 - x0)) // 2, int(H * y))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((pos[0] + 2, pos[1] + 3), text, font=font, fill=(0, 0, 0, 170))
    layer = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)), layer)
    ImageDraw.Draw(layer).text(pos, text, font=font, fill=(255, 255, 255, 255))
    layer.save(path)


def main(src: str, out: str, text: str | None = None, y: float = 0.12) -> None:
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1,fps={FPS}"
    with tempfile.TemporaryDirectory() as tmp:
        args = [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src]
        if text:
            png = Path(tmp) / "label.png"
            label_png(text, png, y)
            args += ["-i", str(png), "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                     "-filter_complex", f"[0:v]{fit}[v];[v][1:v]overlay=0:0,format=yuv420p[vout]",
                     "-map", "[vout]", "-map", "2:a"]
        else:
            args += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                     "-filter_complex", f"[0:v]{fit},format=yuv420p[vout]", "-map", "[vout]", "-map", "1:a"]
        args += ["-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "19", "-c:a", "aac",
                 "-b:a", "32k", "-shortest", "-movflags", "+faststart", out]
        subprocess.run(args, check=True)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None,
         float(sys.argv[4]) if len(sys.argv) > 4 else 0.12)
