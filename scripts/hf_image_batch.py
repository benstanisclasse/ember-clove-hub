"""Run a list of product-photo jobs through the Higgsfield API, one after another (see hf_image_edit.py).

Job file: {"B": base url for "@NAME" refs, "style": text added to every prompt, "jobs": [{key, aspect, refs, prompt}]}.
Saves <outdir>/<key>.png and <outdir>/results.json (key -> result URL, for uploading approved photos). Skips keys
that already have a PNG, so a rerun only does what's missing.
Run: python -I scripts/hf_image_batch.py <jobs.json> <outdir> [model]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
from hf_image_edit import MODELS  # noqa: E402


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    path, payload = MODELS[sys.argv[3] if len(sys.argv) > 3 else "flare"]
    res_file = out / "results.json"
    results = json.loads(res_file.read_text()) if res_file.exists() else {}
    for job in spec["jobs"]:
        dest = out / f"{job['key']}.png"
        if dest.exists():
            continue
        refs = [spec["B"] + r[1:] + ".jpg" if r.startswith("@") else r for r in job["refs"]]
        prompt = f"{spec.get('style', '')} {job['prompt']}".strip()
        try:
            sub = hf_api.submit(path, payload(prompt, refs, job["aspect"]))
            status = hf_api.wait(sub["status_url"], every=5, timeout_s=600)
        except Exception as e:  # keep going; report at the end
            print(f"{job['key']}: ERROR {e}")
            continue
        if status.get("status") != "completed":
            print(f"{job['key']}: {status.get('status')}")
            continue
        url = (status.get("images") or [{}])[0].get("url")
        hf_api.download(url, dest)
        results[job["key"]] = url
        res_file.write_text(json.dumps(results, indent=1))
        print(f"{job['key']}: saved")


if __name__ == "__main__":
    main()
