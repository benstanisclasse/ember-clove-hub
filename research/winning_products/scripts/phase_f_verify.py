"""Phase F transcription check (PHASE_F_PLAN.md, data handling): compare the independent re-query files
_work/cj/verify/<cand>.json with the collector files _work/cj/<cand>.json.
Pass = every variant price and weight exact, the matching freight quote exact (same method names and fees), and CJ stock
within +-5% per variant x country (stock moves). Writes _work/phase_f_verify.json.
Run: python -I research/winning_products/scripts/phase_f_verify.py [F|H]
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).resolve().parents[1] / "_work"


def f(x):
    try:
        return round(float(x), 4)
    except (TypeError, ValueError):
        return None


out = {}
PFX = sys.argv[1] if len(sys.argv) > 1 else "F"   # "H" for the Phase H check (PHASE_H_PLAN.md H3)
for vf in sorted((W / "cj" / "verify").glob(f"{PFX}*.json")):
    c = vf.stem
    new = json.loads(vf.read_text(encoding="utf-8"))
    old = json.loads((W / "cj" / f"{c}.json").read_text(encoding="utf-8"))
    r = {"issues": []}
    ov = {str(v["vid"]): v for v in old.get("variants") or []}
    nv = {str(v["vid"]): v for v in new.get("variants") or []}
    r["variants_old_new"] = [len(ov), len(nv)]
    for vid, v in nv.items():
        o = ov.get(vid)
        if o is None:
            r["issues"].append(f"variant {vid} missing in collector file")
            continue
        for k in ("variantSellPrice", "variantWeight"):
            if f(o.get(k)) != f(v.get(k)):
                r["issues"].append(f"{vid} {k}: saved {o.get(k)} vs now {v.get(k)}")
    for vid in set(ov) - set(nv):
        r["issues"].append(f"variant {vid} in collector file but not returned now")
    oi = {(str(x["vid"]), x["countryCode"]): x for x in old.get("inventory") or []}
    ni = {(str(x["vid"]), x["countryCode"]): x for x in new.get("inventory") or []}
    stock_dev = []
    for key, x in ni.items():
        o = oi.get(key)
        a, b = f((o or {}).get("totalInventory")) or 0, f(x.get("totalInventory")) or 0
        dev = abs(a - b) / max(a, b, 1)
        stock_dev.append(dev)
        if o is None:
            r["issues"].append(f"inventory row {key} missing in collector file")
        elif dev > 0.05:
            r["issues"].append(f"stock {key}: saved {a} vs now {b} ({dev:.0%})")
    r["max_stock_dev"] = round(max(stock_dev), 4) if stock_dev else None
    nf = new.get("freight") or {}
    match = [q for q in old.get("freight") or [] if str(q.get("vid")) == str(nf.get("vid"))
             and q.get("origin") == nf.get("origin") and str(q.get("zip")) == str(nf.get("zip"))]
    if not match:
        r["issues"].append(f"no saved freight quote for {nf.get('vid')} {nf.get('origin')} {nf.get('zip')}")
    else:
        om = {m["logisticName"]: f(m.get("totalPostageFee")) for m in match[0]["methods"]}
        nm = {m["logisticName"]: f(m.get("totalPostageFee")) for m in nf.get("methods") or []}
        r["freight_methods_old_new"] = [len(om), len(nm)]
        for k in set(om) | set(nm):
            if om.get(k) != nm.get(k):
                r["issues"].append(f"freight {k}: saved {om.get(k)} vs now {nm.get(k)}")
    r["pass"] = not r["issues"]
    out[c] = r
summary = {"checked": len(out), "passed": sum(r["pass"] for r in out.values()), "items": out}
(W / ("phase_f_verify.json" if PFX == "F" else f"phase_{PFX.lower()}_verify.json")).write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps({k: {"pass": v["pass"], "n_issues": len(v["issues"]), "first": v["issues"][:4]} for k, v in out.items()}, indent=1))
print("passed", summary["passed"], "of", summary["checked"])
