"""Publish a redacted copy of the Hub's git history to the public GitHub repo (owner asked 2026-10-29).

The local repo and the private remote (`origin`) keep everything. This script rebuilds `master` in a temporary
bare repo with private values replaced by XXX in every file version and commit message, checks the result, and
pushes it to the public repo. The rebuild is deterministic, so unchanged old commits keep their ids and a normal
push fast-forwards; after adding a new value to the redaction list, old commits change and --force is needed.

Replaced with XXX:
  - every ID in config/hub.json (keys ending _id, _ids, _code; not "secrets")
  - every value in config/public_redact.json "literals" (not in git: the list itself is private)
  - patterns: emails at gmail.com / bridgemarkservices.com, ###-###-#### numbers (Google Ads accounts, phones),
    TikTok ad ids (1880 + 12 digits), Meta ad ids (1202 + 14 digits), Google Ads AW- tags
Shopify product/theme ids, creator video ids and competitor pages stay: they are public on the web already.

Run: python -I scripts/publish_public.py [--dry-run] [--force]
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
PUBLIC_URL = "https://github.com/benstanisclasse/ember-clove-hub.git"
BRANCH = "refs/heads/master"
MASK = b"XXX"
PATTERNS = [
    (re.compile(rb"[A-Za-z0-9._%+-]+@(?:gmail\.com|bridgemarkservices\.com)\b", re.I), b"XXX@XXX.com"),
    (re.compile(rb"(?<![\d-])(?!123-456-7890|111-222-3333)\d{3}-\d{3}-\d{4}(?![\d-])"), b"XXX-XXX-XXXX"),
    (re.compile(rb"(?<!\d)1880\d{12}(?!\d)"), MASK),
    (re.compile(rb"(?<!\d)1202\d{14}(?!\d)"), MASK),
    (re.compile(rb"\bAW-\d{6,}"), b"AW-XXX"),
]


def config_ids(node, out):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "secrets":
                continue
            if key.endswith(("_id", "_ids", "_code")) and isinstance(value, (str, int)):
                out.add(str(value))
            elif key.endswith("_ids") and isinstance(value, list):
                out.update(str(v) for v in value)
            else:
                config_ids(value, out)
    elif isinstance(node, list):
        for v in node:
            config_ids(v, out)
    return out


def load_literals():
    ids = config_ids(json.loads((HUB / "config/hub.json").read_text(encoding="utf-8")), set())
    extra = json.loads((HUB / "config/public_redact.json").read_text(encoding="utf-8"))["literals"]
    values = {v for v in ids | set(extra) if len(v) >= 6}
    # Longest first so a value inside another is not half-replaced.
    return [re.compile(rb"(?<![A-Za-z0-9])" + re.escape(v.encode()) + rb"(?![A-Za-z0-9])")
            for v in sorted(values, key=len, reverse=True)]


def redact(data, literals):
    if b"\0" in data[:8000]:  # binary (images, PDFs): left as is
        return data
    for rx in literals:
        data = rx.sub(MASK, data)
    for rx, repl in PATTERNS:
        data = rx.sub(repl, data)
    return data


def rewrite(stream, literals):
    """Redact every `data` block (blobs and commit messages) of a git fast-export stream."""
    out, i = [], 0
    while i < len(stream):
        nl = stream.index(b"\n", i)
        line = stream[i:nl + 1]
        i = nl + 1
        if line.startswith(b"data "):
            n = int(line[5:])
            body = redact(stream[i:i + n], literals)
            i += n
            out += [b"data %d\n" % len(body), body]
        else:
            out.append(line)
    return b"".join(out)


def leaks(repo, literals):
    log = subprocess.run(["git", "-C", repo, "log", "-p", "--all", "--format=%B"],
                         capture_output=True, check=True).stdout
    found = [rx.pattern.decode(errors="replace") for rx in literals if rx.search(log)]
    found += [rx.pattern.decode() for rx, _ in PATTERNS if rx.search(log)]
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="build and check, do not push")
    ap.add_argument("--force", action="store_true", help="force-push (needed after the redaction list changes)")
    args = ap.parse_args()

    literals = load_literals()
    stream = subprocess.run(["git", "-C", str(HUB), "fast-export", "--signed-tags=strip", "--reencode=yes",
                             BRANCH], capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        repo = str(Path(tmp) / "public.git")
        subprocess.run(["git", "init", "-q", "--bare", repo], check=True)
        subprocess.run(["git", "-C", repo, "fast-import", "--quiet"], input=rewrite(stream, literals), check=True)
        found = leaks(repo, literals)
        if found:
            sys.exit(f"Not published: redacted copy still matches {len(found)} rule(s).")
        head = subprocess.run(["git", "-C", repo, "rev-parse", BRANCH], capture_output=True, text=True,
                              check=True).stdout.strip()
        print(f"Redacted copy built and checked: {head[:10]}, {len(literals)} values + {len(PATTERNS)} patterns.")
        if args.dry_run:
            return
        push = ["git", "-C", repo, "push", PUBLIC_URL, f"{BRANCH}:{BRANCH}"] + (["--force"] if args.force else [])
        subprocess.run(push, check=True)
        print(f"Pushed to {PUBLIC_URL}")


if __name__ == "__main__":
    main()
