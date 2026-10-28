"""Turn a raw base video into a finished 9:16 ad: hook text, timed captions, and a branded end card.

Text stays inside TikTok's safe zone (clear of the top bar, the right-side buttons and the bottom caption area).
Music is not added here; it is chosen from TikTok's commercial library when the ad is created.

  render_ad(src, dest, hook=None, captions=[(start, end, text)], end_card={...}, end_secs=2.5)
"""
import subprocess
import tempfile
from pathlib import Path

import cv2
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 720, 1280
FONTS = Path("C:/Windows/Fonts")
SERIF_BOLD = str(FONTS / "georgiab.ttf")
SERIF = str(FONTS / "georgia.ttf")
SANS_SEMI = str(FONTS / "seguisb.ttf")
SANS = str(FONTS / "segoeui.ttf")

CREAM = (251, 246, 239)
BROWN = (59, 36, 24)
RUST = (168, 74, 28)
PEACH = (232, 162, 122)

# Safe zone for in-feed ads: keep text between y=150 and y=1000 and within x=60..600 (right-side icons).
SAFE_LEFT, SAFE_RIGHT = 60, 600


def _wrap(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines


def _text_block(text, font_path, size, y_center, fg, bg, pad=22, radius=18, max_w=SAFE_RIGHT - SAFE_LEFT - 40):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, size)
    lines = _wrap(draw, text, font, max_w)
    line_h = int(size * 1.22)
    block_w = max(draw.textlength(l, font=font) for l in lines)
    block_h = line_h * len(lines)
    cx = (SAFE_LEFT + SAFE_RIGHT) / 2
    x0, y0 = cx - block_w / 2 - pad, y_center - block_h / 2 - pad
    draw.rounded_rectangle([x0, y0, cx + block_w / 2 + pad, y_center + block_h / 2 + pad], radius=radius, fill=bg)
    for i, l in enumerate(lines):
        lw = draw.textlength(l, font=font)
        draw.text((cx - lw / 2, y0 + pad + i * line_h), l, font=font, fill=fg)
    return img


def hook_overlay(text, y=300, size=50):
    """y is the block's vertical center; move it per ad so the hook never covers a face."""
    return _text_block(text, SERIF_BOLD, size, y, CREAM, BROWN + (225,), pad=24)


def caption_overlay(text):
    return _text_block(text, SANS_SEMI, 34, 880, (255, 255, 255), (20, 12, 8, 165), pad=16, radius=14)


def end_card(last_frame_bgr, card):
    """card: dict(product, price, line1, line2, cta)."""
    frame = Image.fromarray(cv2.cvtColor(cv2.resize(last_frame_bgr, (W, H)), cv2.COLOR_BGR2RGB))
    bg = frame.filter(ImageFilter.GaussianBlur(18))
    bg = Image.alpha_composite(bg.convert("RGBA"), Image.new("RGBA", (W, H), (42, 24, 16, 190)))
    d = ImageDraw.Draw(bg)
    cx = (SAFE_LEFT + SAFE_RIGHT) / 2

    def centered(y, text, font, fill):
        d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)

    brand = ImageFont.truetype(SANS_SEMI, 26)
    spaced = "  ".join("EMBER & CLOVE".split(" "))
    centered(300, " ".join(spaced), brand, PEACH)
    prod_font = ImageFont.truetype(SERIF, 44)
    y = 370
    for line in _wrap(d, card["product"], prod_font, SAFE_RIGHT - SAFE_LEFT - 20):
        centered(y, line, prod_font, CREAM)
        y += 56
    centered(y + 14, card["price"], ImageFont.truetype(SERIF_BOLD, 72), CREAM)
    small = ImageFont.truetype(SANS, 32)
    centered(y + 120, card["line1"], small, CREAM)
    centered(y + 168, card["line2"], small, CREAM)
    btn_font = ImageFont.truetype(SANS_SEMI, 36)
    bw = d.textlength(card["cta"], font=btn_font) + 90
    by = y + 250
    d.rounded_rectangle([cx - bw / 2, by, cx + bw / 2, by + 76], radius=38, fill=RUST)
    centered(by + 14, card["cta"], btn_font, CREAM)
    return bg.convert("RGB")


def _probe(src):
    cap = cv2.VideoCapture(str(src))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(n - 2, 0))
    ok, last = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read the last frame of {src}")
    return n / fps, fps, last


def _has_audio(ffmpeg, src):
    out = subprocess.run([ffmpeg, "-hide_banner", "-i", str(src)], capture_output=True, text=True).stderr
    return "Audio:" in out


def render_ad(src, dest, hook=None, captions=(), end_card_spec=None, end_secs=2.5):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    duration, fps, last = _probe(src)
    tmp = Path(tempfile.mkdtemp(prefix="ec_ad_"))
    layers = []  # (png_path, start, end)
    if hook:
        p = tmp / "hook.png"
        hook_overlay(hook["text"], y=hook.get("y", 300), size=hook.get("size", 50)).save(p)
        layers.append((p, hook["start"], hook["end"]))
    for i, (start, end, text) in enumerate(captions):
        p = tmp / f"cap{i}.png"
        caption_overlay(text).save(p)
        layers.append((p, start, end))
    card_path = tmp / "endcard.png"
    end_card(last, end_card_spec).save(card_path)

    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
    for p, _, _ in layers:
        cmd += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(p)]
    cmd += ["-loop", "1", "-framerate", f"{fps:g}", "-t", f"{end_secs}", "-i", str(card_path)]
    card_idx = len(layers) + 1
    audio_in = _has_audio(ffmpeg, src)
    if not audio_in:
        cmd += ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
    silence_idx = card_idx + (1 if audio_in else 2)
    cmd += ["-f", "lavfi", "-t", f"{end_secs}", "-i", "anullsrc=r=44100:cl=stereo"]

    f = [f"[0:v]fps={fps:g},scale={W}:{H},setsar=1[v0]"]
    cur = "v0"
    for i, (_, start, end) in enumerate(layers, start=1):
        f.append(f"[{cur}][{i}:v]overlay=0:0:enable='between(t,{start},{end})'[v{i}]")
        cur = f"v{i}"
    f.append(f"[{cur}]format=yuv420p[vm]")
    f.append(f"[{card_idx}:v]fps={fps:g},scale={W}:{H},setsar=1,fade=t=in:st=0:d=0.3,format=yuv420p[ve]")
    main_audio = "0:a" if audio_in else f"{card_idx + 1}:a"
    f.append(f"[{main_audio}]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{duration:.3f}[am]")
    f.append(f"[{silence_idx}:a]aresample=44100,aformat=channel_layouts=stereo[ae]")
    f.append("[vm][am][ve][ae]concat=n=2:v=1:a=1[v][a]")
    cmd += ["-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dest)]
    subprocess.run(cmd, check=True)
    return {"base_seconds": round(duration, 2), "end_card_seconds": end_secs,
            "total_seconds": round(duration + end_secs, 2), "layers": [(s, e) for _, s, e in layers]}
