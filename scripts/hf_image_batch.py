"""Run a list of product-photo jobs through the Higgsfield API, one after another (see hf_image_edit.py).

Job file: {"B": base url for "@NAME" refs, "style": text added to every prompt, "jobs": [{key, aspect, refs, prompt}]}.
Saves <outdir>/<key>.png and <outdir>/results.json (key -> result URL, for uploading approved photos). Skips keys
that already have a PNG, so a rerun only does what's missing.
Every job is also recorded in studio.db (generation_jobs + assets + asset_refs, Content Studio Phase C): model,
prompt, references, request id, timings and status. Higgsfield reports no cost per image, so cost stays empty
("not reported") rather than guessed.
Run: python -I scripts/hf_image_batch.py <jobs.json> <outdir> [model]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
from hf_image_edit import MODELS  # noqa: E402
from studio import content  # noqa: E402


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    name = sys.argv[3] if len(sys.argv) > 3 else "flare"
    path, payload = MODELS[name]
    res_file = out / "results.json"
    results = json.loads(res_file.read_text(encoding="utf-8")) if res_file.exists() else {}
    con = content.connect()
    for job in spec["jobs"]:
        dest = out / f"{job['key']}.png"
        if dest.exists():
            continue
        refs = [spec["B"] + r[1:] + ".jpg" if r.startswith("@") else r for r in job["refs"]]
        prompt = f"{spec.get('style', '')} {job['prompt']}".strip()
        jid = content.start_job(con, f"IMG-{out.name}/{job['key']}", "image", "higgsfield", path,
                                {"aspect": job["aspect"], "model_key": name, "job_file": Path(sys.argv[1]).name},
                                prompt_hash=content.sha256_text(prompt)[:16], prompt_text=prompt, refs=refs)
        try:
            sub = hf_api.submit(path, payload(prompt, refs, job["aspect"]))
            status = hf_api.wait(sub["status_url"], every=5, timeout_s=600)
        except Exception as e:  # keep going; report at the end
            content.finish_job(con, jid, "failed", error=f"{type(e).__name__}: {e}")
            print(f"{job['key']}: ERROR {e}")
            continue
        if status.get("status") != "completed":
            content.finish_job(con, jid, status.get("status") or "failed", sub.get("request_id"),
                               cost_basis="not reported", error=str(status)[:300])
            print(f"{job['key']}: {status.get('status')}")
            continue
        url = (status.get("images") or [{}])[0].get("url")
        hf_api.download(url, dest)
        content.finish_job(con, jid, "completed", sub.get("request_id"), None, "not reported", output_path=dest, output_url=url)
        results[job["key"]] = url
        content.atomic_write(res_file, json.dumps(results, indent=1))
        print(f"{job['key']}: saved")
    con.close()


if __name__ == "__main__":
    main()
