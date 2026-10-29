"""Product photo regeneration through the Higgsfield developer API.

Sends public reference image URLs and a prompt to an image-edit model, waits, saves the image. Used for replacing
low-quality product photos; every output is compared against the saved originals and approved by the owner before it
goes on the store.
Run: python -I scripts/hf_image_edit.py <model> <out.png> <aspect> "<prompt>" <ref_url> [<ref_url> ...]
  model: qwen (alibaba/qwen-image-3/edit, 1-3 refs) | flare (marketing-studio/image/flare, up to 16 refs)
         | flare4k (same, 4K output)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402

NEGATIVE = "logo, brand name, text, watermark, extra straps, changed design, deformed feet, extra toes, blur"
MODELS = {
    "qwen": ("alibaba/qwen-image-3/edit",
             lambda p, refs, ar: {"prompt": p, "image_urls": refs[:3], "resolution": "1k", "aspect_ratio": ar,
                                  "negative_prompt": NEGATIVE}),
    "flare": ("marketing-studio/image/flare",
              lambda p, refs, ar: {"prompt": p, "image_urls": refs[:16], "resolution": "1k", "aspect_ratio": ar,
                                   "quality": "high", "enhance_prompt": False}),
    "flare4k": ("marketing-studio/image/flare",
                lambda p, refs, ar: {"prompt": p, "image_urls": refs[:16], "resolution": "4k", "aspect_ratio": ar,
                                     "quality": "high", "enhance_prompt": False}),
}


def main():
    name, out, aspect, prompt, refs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
    path, payload = MODELS[name]
    sub = hf_api.submit(path, payload(prompt, refs, aspect))
    status = hf_api.wait(sub["status_url"], every=5, timeout_s=600)
    if status.get("status") != "completed":
        raise SystemExit(f"{status.get('status')}: {str(status)[:300]}")
    url = (status.get("images") or [{}])[0].get("url")
    hf_api.download(url, out)
    print(f"saved {out} ({path}, request {sub.get('request_id')})")


if __name__ == "__main__":
    main()
