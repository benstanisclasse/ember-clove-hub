"""Ember's references library (Content Studio 2.0, Phase D item 7): every face reference version and every approved or
rejected example, with its sha256, who decided and their words. Table `character_refs` in studio/studio.db.

It records; it never changes who Ember is. The face the videos use is still only studio/bible/character.yaml
`face_refs` (locked by sha256 in studio/bible/approved_assets.json), and changing it still needs the owner's
`cli.py bible-approve character`. A library entry can be marked approved or rejected only by the owner, with a quote.

  kind       face_ref (a face reference image: the one in use, earlier versions, candidates) | example (a frame sheet
             or still from a video, kept as a good or bad example of how Ember should look)
  verdict    approved | rejected | candidate
  in_use     1 for the face references character.yaml uses right now (set by sync, never by hand)

  python scripts/studio/cli.py refs sync | list | add PATH --kind example --note "..." | verdict REF_ID approved --quote "..."
"""
import json
import re
from pathlib import Path

import yaml

HUB = Path(__file__).resolve().parents[2]
ALLOWED_DIRS = ("studio/refs/", "studio/episodes/")
IMAGE_EXT = (".png", ".jpg", ".jpeg")


def _rel(path):
    p = Path(path)
    p = p if p.is_absolute() else HUB / p
    rel = str(p.resolve().relative_to(HUB.resolve())).replace("\\", "/")
    if not rel.startswith(ALLOWED_DIRS) or not rel.lower().endswith(IMAGE_EXT):
        raise ValueError(f"{rel}: references live under {' or '.join(ALLOWED_DIRS)} as .png/.jpg")
    return rel


def _sha(rel):
    from studio import content
    return content.sha256_file(HUB / rel)


def _insert(con, kind, rel, verdict, source, quote=None, actor=None, at=None, note=None, version=None):
    """Adds a row once per path; returns True if it was new."""
    from studio import content
    cur = con.execute("INSERT OR IGNORE INTO character_refs (kind, version, path, sha256, verdict, in_use, source, quote, "
                      "actor, at, note) VALUES (?,?,?,?,?,0,?,?,?,?,?)",
                      (kind, version, rel, _sha(rel), verdict, source, quote, actor, at or content.now_utc(), note))
    return bool(cur.rowcount)


def sync(con, bible_dir=None):
    """Bring the library up to date from what is on record (idempotent): character.yaml's face references (approved,
    in use), the face candidates the owner chose between, and the frame sheets of every video the owner approved."""
    bible_dir = Path(bible_dir or HUB / "studio" / "bible")
    char = yaml.safe_load((bible_dir / "character.yaml").read_text(encoding="utf-8"))
    log = (bible_dir / "approvals.log").read_text(encoding="utf-8") if (bible_dir / "approvals.log").exists() else ""
    char_quote = next((ln.split("\t", 2)[2].strip().removeprefix("owner: ") for ln in log.splitlines()
                       if "\tcharacter\t" in ln), None)
    raw = (bible_dir / "character.yaml").read_text(encoding="utf-8")
    choice = re.search(r"^face_refs:.*#\s*(.+)$", raw, flags=re.M)
    added = 0
    in_use = []
    for f in char.get("face_refs") or []:
        rel = _rel(f)
        in_use.append(rel)
        version = (con.execute("SELECT MAX(version) FROM character_refs WHERE kind = 'face_ref'").fetchone()[0] or 0) + 1
        added += _insert(con, "face_ref", rel, "approved", "character.yaml", char_quote, "owner", char.get("approved_at"),
                         choice.group(1).strip() if choice else None, version)
    con.execute("UPDATE character_refs SET in_use = CASE WHEN path IN (%s) THEN 1 ELSE 0 END WHERE kind = 'face_ref'"
                % ",".join("?" * len(in_use)), in_use)
    used_sha = {r[0] for r in con.execute("SELECT sha256 FROM character_refs WHERE in_use = 1")}
    cand = HUB / "studio" / "refs" / "candidates"
    for f in sorted(cand.glob("face_option_*.png")) if cand.exists() else []:
        rel = _rel(f)
        chosen = _sha(rel) in used_sha
        added += _insert(con, "face_ref", rel, "approved" if chosen else "rejected", "face candidates 2026-10-26",
                         choice.group(1).strip() if choice else None, "owner", char.get("approved_at"),
                         "the option chosen; same file as the face reference in use" if chosen else "not chosen")
    for ep in con.execute("SELECT id, state, video_path, approval_json FROM episodes WHERE test = 0 AND video_path IS NOT NULL "
                          "AND state IN ('APPROVED', 'SCHEDULED', 'POSTED', 'MEASURED', 'REJECTED')"):
        approval = json.loads(ep["approval_json"] or "{}")
        if not approval.get("owner_quote"):
            continue
        vp = Path(ep["video_path"].replace("\\", "/"))
        sheet = HUB / vp.with_name(vp.stem + "_frames.jpg")
        if sheet.exists():
            added += _insert(con, "example", _rel(sheet), "rejected" if ep["state"] == "REJECTED" else "approved",
                             ep["id"], approval["owner_quote"], "owner", approval.get("at"),
                             "frames of a video the owner " + ("rejected" if ep["state"] == "REJECTED" else "approved"))
    con.execute("UPDATE character_refs SET quote = substr(quote, 8) WHERE quote LIKE 'owner: %'")  # early rows
    con.commit()
    return added


def add(con, path, kind, note, actor="claude"):
    """A new candidate (e.g. a possible new face reference, or a still worth keeping); verdict comes from the owner."""
    if kind not in ("face_ref", "example"):
        raise ValueError("kind is face_ref or example")
    rel = _rel(path)
    if not _insert(con, kind, rel, "candidate", "added", None, actor, None, note):
        raise ValueError(f"{rel} is already in the library")
    con.commit()
    return con.execute("SELECT ref_id FROM character_refs WHERE path = ?", (rel,)).fetchone()[0]


def verdict(con, ref_id, value, quote, actor):
    """Owner only, with their words. Never touches character.yaml: approving a face candidate does not make it Ember's
    face (that is a bible change: edit face_refs, then `bible-approve character`)."""
    from studio import content
    if actor != "owner" or not (quote or "").strip():
        raise ValueError("only the owner marks a reference approved or rejected, with their words (--quote)")
    if value not in ("approved", "rejected"):
        raise ValueError("verdict is approved or rejected")
    row = con.execute("SELECT * FROM character_refs WHERE ref_id = ?", (ref_id,)).fetchone()
    if row is None:
        raise ValueError(f"no reference {ref_id}")
    if row["in_use"] and value == "rejected":
        raise ValueError("this face reference is in use; replace it in character.yaml (bible approval) first")
    if _sha(row["path"]) != row["sha256"]:
        raise ValueError(f"{row['path']} changed since it was added; add the new file instead")
    version = row["version"]
    if row["kind"] == "face_ref" and value == "approved" and version is None:
        version = (con.execute("SELECT MAX(version) FROM character_refs WHERE kind = 'face_ref'").fetchone()[0] or 0) + 1
    con.execute("UPDATE character_refs SET verdict = ?, quote = ?, actor = ?, at = ?, version = ? WHERE ref_id = ?",
                (value, quote, actor, content.now_utc(), version, ref_id))
    con.commit()


def rows(con):
    from studio import content
    out = []
    for r in con.execute("SELECT * FROM character_refs ORDER BY kind DESC, in_use DESC, verdict, ref_id"):
        r = dict(r)
        f = HUB / r["path"]
        r["file_ok"] = f.exists() and content._cached_sha(f) == r["sha256"]  # cached by mtime+size
        out.append(r)
    return out


def check(con, bible_dir=None):
    """Problems: a face reference in character.yaml that the library doesn't hold as approved, or a library file that
    changed or disappeared."""
    bible_dir = Path(bible_dir or HUB / "studio" / "bible")
    char = yaml.safe_load((bible_dir / "character.yaml").read_text(encoding="utf-8"))
    issues = []
    for f in char.get("face_refs") or []:
        r = con.execute("SELECT verdict FROM character_refs WHERE path = ?", (_rel(f),)).fetchone()
        if not r or r["verdict"] != "approved":
            issues.append({"severity": "high", "check": "face reference not in the library as approved", "detail": f})
    for r in rows(con):
        if not r["file_ok"]:
            issues.append({"severity": "medium", "check": "reference file changed or missing", "detail": r["path"]})
    return issues
