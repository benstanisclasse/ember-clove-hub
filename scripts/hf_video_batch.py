"""Run a list of short AI video jobs through the Higgsfield API (Seedance 2.5 reference-to-video), one after another.

Job file: {"style": text added to every prompt, "refs": {name: local image path}, "duration": s, "resolution": "720p",
"jobs": [{key, refs: [names], prompt}]}. Local reference images are uploaded once per run (hf_api.upload).
Saves <outdir>/<key>.mp4 and <outdir>/results.json (key -> result URL). Skips keys that already have an MP4, so a
rerun only does what's missing. Every job is recorded in studio.db (generation_jobs) like hf_image_batch.py; Higgsfield
reports no cost per request, so cost stays "not reported".
Run: python -I scripts/hf_video_batch.py <jobs.json> <outdir>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
from studio import content  # noqa: E402

MODEL = "bytedance/seedance-2.5/reference-to-video"


def first_mp4(node):
    """The first .mp4 URL anywhere in a status response (its shape differs between models)."""
    if isinstance(node, str):
        return node if node.startswith("http") and ".mp4" in node else None
    items = node.values() if isinstance(node, dict) else node if isinstance(node, list) else []
    for item in items:
        found = first_mp4(item)
        if found:
            return found
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    res_file = out / "results.json"
    results = json.loads(res_file.read_text(encoding="utf-8")) if res_file.exists() else {}
    todo = [j for j in spec["jobs"] if not (out / f"{j['key']}.mp4").exists()]
    urls = {name: hf_api.upload(path) for name, path in spec["refs"].items()
            if any(name in j["refs"] for j in todo)}
    con = content.connect()
    for job in todo:
        refs = [urls[r] for r in job["refs"]]
        prompt = f"{job['prompt']} {spec.get('style', '')}".strip()
        payload = {"prompt": prompt, "image_urls": refs, "duration": spec.get("duration", 10),
                   "resolution": spec.get("resolution", "720p"), "aspect_ratio": "9:16", "output_format": "mp4",
                   "generate_audio": False}
        jid = content.start_job(con, f"VID-{out.name}/{job['key']}", "video", "higgsfield", MODEL,
                                {k: v for k, v in payload.items() if k not in ("prompt", "image_urls")},
                                prompt_hash=content.sha256_text(prompt)[:16], prompt_text=prompt, refs=refs)
        try:
            sub = hf_api.submit(MODEL, payload)
            status = hf_api.wait(sub["status_url"], every=10, timeout_s=1500)
        except Exception as e:  # keep going; report at the end
            content.finish_job(con, jid, "failed", error=f"{type(e).__name__}: {e}")
            print(f"{job['key']}: ERROR {e}")
            continue
        if status.get("status") != "completed":
            content.finish_job(con, jid, status.get("status") or "failed", sub.get("request_id"),
                               cost_basis="not reported", error=str(status)[:300])
            print(f"{job['key']}: {status.get('status')}")
            continue
        url = first_mp4(status)
        if not url:
            content.finish_job(con, jid, "failed", sub.get("request_id"), error=f"no video URL in {str(status)[:300]}")
            print(f"{job['key']}: completed but no video URL")
            continue
        dest = out / f"{job['key']}.mp4"
        hf_api.download(url, dest)
        content.finish_job(con, jid, "completed", sub.get("request_id"), None, "not reported", output_path=dest,
                           output_url=url)
        results[job["key"]] = {"url": url, "request_id": sub.get("request_id"), "prompt": prompt}
        content.atomic_write(res_file, json.dumps(results, indent=1))
        print(f"{job['key']}: saved")
    con.close()


if __name__ == "__main__":
    main()
