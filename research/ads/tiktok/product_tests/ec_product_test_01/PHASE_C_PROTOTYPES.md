# TikTok image-ad test 01 — Phase C: hero prototypes

Date: 2026-10-28. Status: **30 prototypes ready for owner review.** Nothing published to TikTok, no ad spend.

- **Review page (owner only):** https://claude.ai/artifact/Gy4ik4p3dPwRBWXCkr346b — Approve / Request revision /
  Regenerate / Reject / Save for later + comment per concept. Decisions are stored in the page's database (collection
  `reviews`, one document per ad) with the reviewer, time and the prototype's SHA-256; a remade picture gets a new hash,
  so its old decision shows as "needs re-review".
- **Files:** `prototypes_manifest.json` (ad, raw image + hash, prototype + hash, version, headline, caption);
  `creative_matrix.csv` (status prototype_v1_awaiting_review); tools in `tools/` (job builder, overlay + sheets script,
  review page template, final job file). Images (not in git): `data/media_generated/tiktok_test_01/` — `heroes/`
  (raw 752×1344), `prototypes/` (1080×1920 with headline), `review_sheets/` (10 product contact sheets + overview_30.jpg).

## Production
- Model: Higgsfield Marketing Studio Flare (`marketing-studio/image/flare`, quality high, 1k, 9:16) with each product's
  Shopify photos as references (watermarked and creator photos excluded). Run 5 jobs in parallel (~8 min for 26).
- Headline: Georgia Bold 58 px, one size for the whole set, ink on light / cream on dark, centred in the empty top band
  (y≈175 px of 1920, below TikTok's top tabs). **No disclosure text on pictures** (owner 2026-10-28); AI disclosure =
  TikTok AI label on the Spark post only (no caption hashtag, owner 2026-10-28).
- Framing fix: first pictures put heads where the headline goes; prompts now require the upper ~28% to be calm
  background. Close-up/macro slide-1 shots could not leave headline space without a visible seam, so C slide 1 for P001,
  P003, P009 became medium shots with the detail large (macros move to slide 2), and P012 A became a still life.

## QA (first filter; the owner's viewing decides realism)
| Item | Result |
|---|---|
| Product match (colour, cut, hardware, details) | 30/30 pass at review size |
| Anatomy (legs uncrossed, hands, stance) | 30/30 pass at review size; not checked at full zoom on every hand |
| Season / setting | November settings throughout; no summer styling |
| Headline space | 30/30 clear of faces and product |
| Failures fixed | P001 A/B/C, P003 A/B, P006 A (head in headline zone); P003 C (wrong framing, sandals/bare legs); P009 C (seam); P012 A (seam); P013 C (copied supplier sunglasses/bag/wall) |
| Known soft spots | P011 B and C show nearly the same outfit (C differs on slides 2–3); P012 B carries a shoulder bag (styling prop) |

## Cost (estimate — Higgsfield reports no per-request cost)
48 Flare requests today for this test (45 completed incl. the cost probe; 3 stopped mid-run, may still be charged):
30 kept, 18 superseded/test. At ≈ $0.20–0.30 each ≈ **$10–14**. Exact charge: Higgsfield console.

## Next (Phase D/E)
Owner reviews on the page. Approved concepts get slides 2–3, final copy check and export; rejected ones get nothing
more; "Request revision"/"Regenerate" get one remake each with the owner's comment.
