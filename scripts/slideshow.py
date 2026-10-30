"""Turn ad pictures (and optionally a short clip) into a vertical TikTok slideshow video.

Same format as TikTok test 01: 1080x1920, 30 fps, H.264, a silent AAC track, still slides with a short crossfade.

  python scripts/slideshow.py <out.mp4> <seconds_per_slide> <item> [<item> ...]

An item is a picture (.png/.jpg), shown for seconds_per_slide, or a clip (.mp4), shown for its own length without
sound. Pictures are cropped to 9:16 from the centre if needed.
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

W, H, FPS, FADE = 1080, 1920, 30, 0.4


def clip_seconds(ff: str, path: str) -> float:
    out = subprocess.run([ff, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit(f"no duration for {path}")


def main(out: str, per_slide: float, items: list[str]) -> None:
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p"
    args, lengths = [ff, "-y", "-hide_banner", "-loglevel", "error"], []
    for item in items:
        if Path(item).suffix.lower() == ".mp4":
            args += ["-i", item]
            lengths.append(clip_seconds(ff, item))
        else:
            args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{per_slide + FADE}", "-i", item]
            lengths.append(per_slide + FADE)
    parts = [f"[{i}:v]{fit},trim=duration={lengths[i]:.3f},setpts=PTS-STARTPTS,fps={FPS},settb=AVTB[v{i}]" for i in range(len(items))]
    last, offset = "v0", lengths[0] - FADE
    for i in range(1, len(items)):
        parts.append(f"[{last}][v{i}]xfade=transition=fade:duration={FADE}:offset={offset:.3f}[x{i}]")
        last, offset = f"x{i}", offset + lengths[i] - FADE
    total = sum(lengths) - FADE * (len(items) - 1)
    parts.append(f"[{last}]trim=duration={total:.3f},format=yuv420p[vout]")
    args += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
             "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", f"{len(items)}:a",
             "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "20", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "32k", "-shortest", "-movflags", "+faststart", out]
    subprocess.run(args, check=True)
    print(f"{out}: {total:.2f} s")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3:])
