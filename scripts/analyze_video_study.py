"""Analyse the video study: what separates each product's best-selling video from a typical stalled video of the
same product and month (table video_features, filled by scripts/video_pilot.py --scope all).

Paired comparison, so product and month are held fixed. For each signal: how common it is among winners vs
comparisons, and in how many pairs the winner has it but the comparison doesn't (and the reverse), with an exact sign
test. Numbers (length, cuts, talking speed...) use the share of pairs where the winner's value is higher.
Run: python -I scripts/analyze_video_study.py
"""
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kalodata_db  # noqa: E402

APPAREL = {"Womenswear & Underwear", "Menswear & Underwear", "Shoes", "Fashion Accessories", "Kids' Fashion",
           "Muslim Fashion", "Luggage & Bags", "Jewelry Accessories & Derivatives"}
OUT = kalodata_db.ROOT / "VIDEO_STUDY_2026-10.md"


def load():
    con = sqlite3.connect(f"file:{kalodata_db.DB}?mode=ro", uri=True)
    d = pd.read_sql("SELECT * FROM video_features", con)
    con.close()
    tags = d["tags_json"].apply(json.loads).apply(pd.Series)
    d = pd.concat([d.drop(columns=["tags_json"]), tags], axis=1)
    for col in ("detail_closeups", "presenter_looks_ai_generated"):  # the tagger answers true/false as text or bool
        d[col] = d[col].map(lambda x: str(x).strip().lower() in ("true", "1", "yes"))
    d["has_text_hook"] = d["on_screen_text_first_3s"].fillna("").str.strip().str.len() > 0
    d["has_cta"] = d["cta"].fillna("none") != "none"
    d["spoken_hook"] = d["hook_text"].fillna("").str.split().str.len() >= 3
    d["person_at_0s"] = d["first_frame"].isin(["face", "person_with_product"])
    d["product_at_0s"] = pd.to_numeric(d["product_first_seen_s"], errors="coerce") <= 1
    d["apparel"] = d["category"].isin(APPAREL)
    d = add_elements(d)
    full = d.groupby("pair")["role"].nunique()
    return d[d["pair"].isin(full[full == 2].index)]


ELEMENT_ENUMS = ["room", "lighting", "presenter_presents_as", "age_group", "hair_color", "hair_length", "makeup",
                 "color_palette", "camera_style", "main_shot_distance", "camera_movement", "visual_quality"]
ELEMENT_LISTS = ["jewelry", "worn_with", "props", "actions"]
ELEMENT_FLAGS = ["nails_done", "glasses", "background_people"]


def add_elements(d):
    """Join the detailed elements (scripts/video_elements.py --study) when they exist: one column per value."""
    con = sqlite3.connect(f"file:{kalodata_db.DB}?mode=ro", uri=True)
    try:
        e = pd.read_sql("SELECT video_id, elements_json FROM video_elements", con)
    except Exception:
        return d
    finally:
        con.close()
    rows = []
    for vid, js in zip(e["video_id"], e["elements_json"]):
        el, row = json.loads(js), {"video_id": vid, "has_elements": True}
        for k in ELEMENT_ENUMS:
            row[f"el_{k}"] = str(el.get(k, "")).strip().lower()
        for k in ELEMENT_LISTS:
            items = el.get(k) or []
            items = items if isinstance(items, list) else [items]
            for it in items:
                row[f"el_{k}__{str(it).strip().lower()}"] = True
        for k in ELEMENT_FLAGS:
            row[f"el_{k}"] = str(el.get(k)).strip().lower() in ("true", "1", "yes")
        rows.append(row)
    e = pd.DataFrame(rows)
    d = d.merge(e, on="video_id", how="left")
    for c in [c for c in d.columns if "__" in c] + [f"el_{k}" for k in ELEMENT_FLAGS if f"el_{k}" in d]:
        d[c] = d[c].fillna(False).astype(bool)
    return d


def element_signals(d):
    sig = []
    for k in ELEMENT_ENUMS:
        col = f"el_{k}"
        if col in d:
            sig += [(col, v) for v in d[col].dropna().value_counts().index[:6] if v]
    sig += [(c, None) for c in sorted(c for c in d.columns if "__" in c) if d[c].mean() >= 0.05]
    sig += [(f"el_{k}", None) for k in ELEMENT_FLAGS if f"el_{k}" in d]
    return sig


def binary_table(d, cols):
    rows = []
    w, c = d[d["role"] == "winner"].set_index("pair"), d[d["role"] == "comparison"].set_index("pair")
    for col, val in cols:
        a = (w[col] == val) if val is not None else w[col].astype(bool)
        b = (c[col] == val) if val is not None else c[col].astype(bool)
        a, b = a.align(b, join="inner")
        only_w, only_c = int((a & ~b).sum()), int((~a & b).sum())
        p = binomtest(only_w, only_w + only_c).pvalue if only_w + only_c else 1.0
        rows.append({"signal": f"{col}={val}" if val is not None else col, "winners": f"{a.mean():.0%}",
                     "comparisons": f"{b.mean():.0%}", "pairs winner-only": only_w, "pairs comparison-only": only_c,
                     "p": round(p, 3)})
    return pd.DataFrame(rows)


def numeric_table(d, cols):
    rows = []
    w, c = d[d["role"] == "winner"].set_index("pair"), d[d["role"] == "comparison"].set_index("pair")
    for col in cols:
        a, b = pd.to_numeric(w[col], errors="coerce").align(pd.to_numeric(c[col], errors="coerce"), join="inner")
        ok = a.notna() & b.notna()
        hi, lo = int((a[ok] > b[ok]).sum()), int((a[ok] < b[ok]).sum())
        p = binomtest(hi, hi + lo).pvalue if hi + lo else 1.0
        rows.append({"measure": col, "winners (median)": round(float(a.median()), 2),
                     "comparisons (median)": round(float(b.median()), 2), "winner higher": f"{hi}/{hi + lo}",
                     "p": round(p, 3)})
    return pd.DataFrame(rows)


def md(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(x) for x in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    d = load()
    n = d["pair"].nunique()
    nums = ["duration_s", "cuts_per_10s", "words_per_s", "speech_share", "product_first_seen_s"]
    bins = [("person_at_0s", None), ("product_at_0s", None), ("has_text_hook", None), ("spoken_hook", None),
            ("has_cta", None), ("detail_closeups", None), ("presenter_looks_ai_generated", None), ("ai_video", 1),
            ("ad", 1), ("production", "polished"), ("presenter", "on_camera_speaking"), ("presenter", "no_person")]
    cats = []
    for col in ("hook_type", "format", "first_frame", "product_shown_as_0s"):
        for val in d[col].dropna().value_counts().index[:8]:
            cats.append((col, val))
    parts = [f"# Video study: what separates winning videos (2026-10)\n",
             f"{n} pairs ({n * 2} videos), {d['category'].nunique()} categories. Each pair: a product's best-selling "
             "September video vs a typical video of the same product that got some views and stalled. Product and "
             "month are the same, so differences are about the video. Small p (under 0.05) = unlikely to be chance.\n",
             "## Measurements\n", md(numeric_table(d, nums)), "\n## Signals\n", md(binary_table(d, bins)),
             "\n## Hook type, format and opening (share of videos)\n", md(binary_table(d, cats))]
    if "has_elements" in d and d["has_elements"].fillna(False).any():
        el = d[d.groupby("pair")["has_elements"].transform(lambda s: s.fillna(False).all())]
        parts += [f"\n## Elements: room, look, jewelry, styling, props, lighting, camera ({el['pair'].nunique()} pairs)\n",
                  md(binary_table(el, element_signals(el)).sort_values("p"))]
    for label, sub in (("Apparel, shoes, bags and accessories", d[d["apparel"]]), ("Everything else", d[~d["apparel"]])):
        if sub["pair"].nunique() >= 5:
            parts += [f"\n## {label} ({sub['pair'].nunique()} pairs)\n", md(numeric_table(sub, nums)), "",
                      md(binary_table(sub, bins[:6]))]
    win = d[d["role"] == "winner"].sort_values("revenue", ascending=False)
    parts += ["\n## Winning hooks (first 3 s, spoken or on screen)\n"]
    for r in win.head(25).itertuples():
        hook = r.hook_text if r.spoken_hook else (r.on_screen_text_first_3s or "(visual only)")
        parts.append(f"- **{r.category}** · ${r.revenue:,.0f} · {r.hook_type} / {r.format}: \"{str(hook)[:120]}\"")
    parts += ["\n## Limits\n", "- Tags come from a vision model (Claude Haiku 5.5): objective measures are reliable, "
              "hook type and format are judgement calls (pilot showed some disagreement between models).",
              "- One month (September), one winner and one comparison per product; about 4 products per category.",
              "- Comparisons came from public TikTok links; winners from links with Kalodata as backup."]
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("\n".join(parts[:7]))
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
