"""Build an HTML page for the owner to review a week of planned and scripted episodes before anything is generated.

  python scripts/studio/review_page.py --start 2026-11-02 --days 7

Writes studio/episodes/review_<start>.html: one card per post with the day and time, series, location photo, the
outfit (the Ember & Clove piece highlighted with its listing photo), the four spoken lines with their shots, the planned
follow line and the caption. Read-only: it changes nothing in the conveyor.
"""
import argparse
import base64
import datetime as dt
import html
import io
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio import bible, db, gates  # noqa: E402

HUB = Path(__file__).resolve().parents[2]


def thumb(path, size):
    im = Image.open(HUB / path).convert("RGB")
    im.thumbnail(size)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    b = bible.load()
    con = db.connect()
    end = (dt.date.fromisoformat(a.start) + dt.timedelta(days=a.days - 1)).isoformat()
    eps = [dict(r) for r in con.execute("SELECT * FROM episodes WHERE post_date BETWEEN ? AND ? ORDER BY post_date, slot",
                                        (a.start, end))]
    items = {i.id: i for i in b["wardrobe"].items}
    rooms = {r.id: r for r in b["world"].rooms}
    series = {s.id: s for s in b["series"].items}
    room_img = {r: thumb(rooms[r].ref_images[0], (180, 320)) for r in {e["room_id"] for e in eps}}
    cards = []
    for e in eps:
        outfit = json.loads(e["outfit_json"] or "[]")
        store = next((items[o] for o in outfit if items[o].store_product), None)
        basics = [items[o].name for o in outfit if not items[o].store_product]
        script = json.loads(e["script_json"]) if e["script_json"] else None
        shots = "".join(
            f"<li><span class=line>&ldquo;{html.escape(ln)}&rdquo;</span><span class=shot>{html.escape(ac)}</span></li>"
            for ln, ac in zip(script["lines"], script["actions"])) if script else "<li><em>not scripted yet</em></li>"
        words = len(gates.words(" ".join(script["lines"]))) if script else 0
        day = dt.date.fromisoformat(e["post_date"]).strftime("%a %b %d").replace(" 0", " ")
        store_html = (f"<div class=store><img src='{thumb(store.reference_images[0], (120, 120))}' alt=''>"
                      f"<div><b>Ember &amp; Clove:</b> {html.escape(store.name)} ({html.escape(store.color)})</div></div>"
                      if store else "")
        cards.append(f"""
<article class=card>
  <img class=room src='{room_img[e['room_id']]}' alt='{html.escape(rooms[e['room_id']].name)}'>
  <div class=body>
    <div class=meta><b>{day} · {e['slot']}</b> · {html.escape(series[e['series_id']].name)} · {html.escape(rooms[e['room_id']].name)}
      {'<span class=out>outdoors</span>' if rooms[e['room_id']].outdoor else ''} <span class=id>{e['id']}</span></div>
    {store_html}
    <div class=wears>Also wears: {html.escape(', '.join(basics))}</div>
    <ol>{shots}</ol>
    <div class=foot>{words} words · follow line: <b>{html.escape(e['cta_line'] or 'none')}</b> ·
      caption: {html.escape(script.get('caption', '') if script else '')}</div>
  </div>
</article>""")
    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1"><title>Ember week review</title>
<style>
:root{{--bg:#faf7f2;--card:#fff;--ink:#2b2420;--muted:#7a6e66;--accent:#a4472a;--line:#e8e0d6}}
@media (prefers-color-scheme: dark){{:root{{--bg:#1c1917;--card:#26221f;--ink:#f1ebe4;--muted:#b3a79c;--accent:#e08a66;--line:#3a332e}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:22px;margin:0 0 4px}} .lede{{color:var(--muted);margin:0 0 20px}}
.card{{display:flex;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;margin:0 0 14px}}
.room{{width:110px;height:196px;object-fit:cover;border-radius:8px;flex:none}}
.body{{min-width:0;flex:1}} .meta{{font-size:13px;color:var(--muted)}} .meta b{{color:var(--ink)}}
.out{{background:var(--accent);color:#fff;border-radius:99px;padding:1px 8px;font-size:11px;margin-left:4px}}
.id{{float:right;font-family:ui-monospace,monospace;font-size:11px}}
.store{{display:flex;align-items:center;gap:10px;margin:8px 0 4px}} .store img{{width:56px;height:56px;object-fit:cover;border-radius:6px;background:#fff}}
.wears{{font-size:13px;color:var(--muted)}}
ol{{padding-left:20px;margin:8px 0}} li{{margin:0 0 6px}} .line{{display:block}} .shot{{display:block;font-size:12px;color:var(--muted)}}
.foot{{font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:6px}}
@media (max-width:560px){{.card{{flex-direction:column}} .room{{width:100%;height:160px}}}}
</style></head><body><main>
<h1>Ember, week of {dt.date.fromisoformat(a.start).strftime('%B %d').replace(' 0', ' ')}</h1>
<p class=lede>{len(eps)} posts, planned and scripted, nothing generated. Each card shows where she films, what she wears
(one Ember &amp; Clove piece), the four spoken lines with their shots, and the caption. Every script already passed the
conveyor's rules; this review is for how it sounds and looks.</p>
{''.join(cards)}
</main></body></html>"""
    out = HUB / "studio" / "episodes" / f"review_{a.start}.html"
    out.write_text(page, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
