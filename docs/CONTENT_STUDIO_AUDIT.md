# Ember Studio — Content Studio 2.0 Technical Audit (Phase A)

Date: 2026-10-27. Scope: everything that plans, makes, checks, approves, publishes and measures content: the TikTok
pipeline (`scripts/studio/`, `studio/studio.db`, `studio/bible/`), the Facebook photo poster
(`scripts/facebook_photos.py`, `data/facebook/`), AI image tooling (`scripts/hf_*.py`), the PostZen client, the older
"Hub 1.0" creative records, and how all of it reaches the dashboard. Method: line-by-line reading of the code (file:line
references below are relative to the Hub), read-only database queries, and the operations log. **Nothing was changed.**

---

## 1. Summary

Ember Studio's TikTok pipeline is solid where it was designed to be: a strict stage machine, rule gates that refuse
bad scripts and calendars, prompts built only from an approved template and bible, owner-only approvals with quoted
words, and 35+ tests. Around it, the system has grown by hand:

- **Facebook runs on JSON files that no longer match practice.** All 12 posts now in PostZen were edited by hand to use
  AI pictures, links in the caption and `#aigenerated`; the planner code still says "real supplier photos only, link in
  the first comment, no AI label" (`facebook_photos.py:3-8, 244`). Re-planning the same week overwrites the file and
  loses PostZen ids and approvals (`:328-330`).
- **There is no shared content record.** A TikTok video is an `episodes` row; a Facebook post is an entry in a plan JSON;
  an AI picture is a PNG plus a CDN URL in `results.json`; Hub 1.0 creatives are CSV rows and recipe files. They use four
  different id schemes and nothing links a post to its product, asset, cost and results in one place.
- **"Delivered to TikTok drafts" can be mistaken for "live".** PostZen returned a post URL and status "published" two
  seconds after a draft upload (EW-20261102-3, transitions 18:07:06 → 18:07:08); the dashboard label I added on 10/27
  treats draft-mode + URL as live (`publishing.py:46-57`). Nothing proves public publication except the owner's manual
  `posted` command.
- **Approvals are not bound to the media.** An approved TikTok episode stores the owner's quote and time, but no hash
  of the video; `publish` uploads whatever file is at `video_path` then (`cli.py:204`, `publishing.py:87,104`).
  Facebook has one free-text approval per publish run, not per post (`facebook_photos.py:251`).
- **Generation and image metadata are thin.** Per attempt, only the latest prompt, hash, model and cumulative cost
  survive on the episode row; template version, references used, provider job id, timings and earlier attempts are not
  stored (`production.py:153-157`). AI images record no model, cost, request id, QA or approval at all.
- **Measurement for learning has not started.** The `metrics` table and the MEASURED stage are unused (0 rows, no code
  path). Performance history exists only since 2026-10-27 in `analytics.db post_snapshots` (Dashboard Phase B).
- **No retries anywhere** in PostZen or Higgsfield calls; timeouts can leave billed jobs unrecorded
  (`postzen.py:30-45`, `production.py:139-143`, `hf_api.py:56-57`).

## 2. Where the new prompt's assumptions differ from the code

The master prompt was written from my earlier summary. Checked against the implementation:

| Prompt says | Actually |
|---|---|
| "Seedance provides AI video generation" | No direct Seedance/BytePlus call. Seedance 2.5 runs through **OpenRouter** (5 real episodes) or **Higgsfield** (7 real episodes, via `trial` + `promote`); Kling v3 is wired as a trial model (`production.py:31-40, 118-145`). `rules.generation.provider` is never read. |
| "Consistent character appearance" enforced by references | The face reference is **off** (`rules.yaml:88 face_reference: false`); references sent are room, product and store-piece photos only (`gates.py:306-316`). The README still says a face image is sent. |
| Production can generate approved content | `wardrobe.yaml` is currently **draft** (edited after approval), so real `generate` and `trial` are blocked until the owner re-approves it (`studio/bible/wardrobe.yaml:6`, `bible.py:260-261`). |
| Facebook: "supplier product images", "first-comment links", "manual approval" | The live/queued posts use **AI pictures, links in the caption, `#aigenerated`**, all hand-edited outside the planner. Approval is one quote per publish run. |
| PostZen provides "watch time / completion rate" | PostZen's analytics fields are views, impressions, reach, likes, comments, shares, saves, clicks (`publishing.py:116`). Watch time, completion, profile visits and followers-per-post are **not available**. |
| Workflow ends in MEASURED | No code moves an episode to MEASURED; `metrics` table never written (`db.py:48-50`). |
| Unified calendar to be built | Already built in Dashboard 2.0 Phase D (week/month/day/list, filters, detail drawer with production history). |
| Shopify integration to be connected | Already built in Dashboard 2.0 Phase C (`scripts/shopify_api.py`, `shopify_sync.py`, analytics.db `products/variants/orders/store_*`). Reuse, don't duplicate. |
| Experiment registry | Hub 1.0 has a schema (`hubdata.py`, 18 columns) but **0 rows**; creatives reference experiment ids that don't exist. |

## 3. How the TikTok pipeline works (as implemented)

**Stages and transitions** (`db.py:14-27`):
`PLANNED→SCRIPTED→GENERATED→QA_PASSED|QA_FAILED→APPROVED|REJECTED→SCHEDULED→POSTED→MEASURED`, with
`QA_FAILED→SCRIPTED|GENERATED|QA_PASSED(owner accept)`, `REJECTED→SCRIPTED`, `SCHEDULED→SCHEDULED` (caption change).
Each target state requires fields (`db.py:73-82`): script_json; prompt_text+hash+video_path+model and an existing file;
qa_json; approval_json; caption; post_url + `ai_label_on` (checked, not stored, `:94,112`). Owner-only moves need
`actor=="owner"` and a quote (`db.py:103-107`) — "owner" is a self-declared CLI flag, not an identity.

**Bible approvals** (`bible.py:19-39, 260-261`): sha256 of each YAML's settings (16 hex chars); any non-comment edit
returns the file to draft. Not covered: reference image bytes, the Jinja templates, `prompt_style.py`, trial model prices.

**Planner** (`cli.py:39-98`, `gates.py:132-257`): fills slots 08:30/12:30/19:30 Eastern; series by pinned weekday/slot,
then a round-robin cycle that restarts each run; rooms rotated by series count (count includes test copies, `:49`);
outfits by seeded random draws (featured piece 0.5, dress 0.25, outerwear by season, store shoes 0.5, bag 0.4…) with
up to 200 attempts against hard outfit rules (season, occasion, outdoor coat, 21-day outfit and 4-post base-piece
no-repeat, exactly one store piece, shoe rotation ≤ 3/week). The whole calendar is checked before saving
(all-or-nothing). Product share > 0 is never enforced as a maximum (`gates.py:242-244`); value share is checked only in
full 7-post windows.

**Script gate** (`gates.py:28-65`): 4 lines + 4 actions; banned phrases (substring), banned regex (prices, N days),
`tts_avoid`, 41–53 words, product CTA wording, soft-line rules, ≥ 2 product facts for product posts, outfit unchanged.
The **caption is never checked** against these rules (`cli.py:210-213`).

**Generation** (`production.py`): prompt from `video_prompt.j2` / `video_prompt_frame.j2` / `first_frame.j2` filled from
the bible with StrictUndefined; prompt hash stored, template name not. Up to 4 reference images. Cost: OpenRouter
`usage.cost` (else estimate); Higgsfield always the estimate ($4.20/14 s). Caps all null (owner choice). No retries;
jobs are polled, not cancelled, on timeout.

**QA** (`production.py:163-225`): faster-whisper `medium.en` transcript must match the script word for word; duration
within ±0.6 s of 14 s; speech coverage ≥ 70 %; a 2 fps frame sheet for the owner. **No automated visual check.** Owner
`accept` overrides set `passed=True` and keep the original checks; 7 of 12 generated real episodes were owner-accepted.

**Publishing** (`publishing.py:60-113`): `draft` = PostZen `uploadAsDraft` (lands in the TikTok app); `scheduled` =
public, owner-only, caption must contain `#aigenerated`. Idempotency via `x-request-id` (`<id>-<mode>`), but the video is
re-uploaded on every attempt. Failures are not caught or recorded. Status refresh fetches every post each sync; one
failed GET aborts the TikTok sync. POSTED is set only by the owner's `posted --url --ai-label-on`.

**Current state** (DB, 2026-10-27): 21 real episodes — 1 POSTED, 11 SCHEDULED, 9 SCRIPTED; 12 test episodes; 216
transitions; 17 spend rows = $38.45; 0 metrics rows. PostZen: 7 draft-mode posts queued for their slots, 2 draft
uploads delivered (one confirmed live by views), 1 public scheduled post.

## 4. How the Facebook poster works (as implemented)

- **Feed and eligibility** (`facebook_photos.py:34, 47-55, 113-121`): public `products.json`; vendor = Ember & Clove,
  product type set, not skipped, in season (string month-day window 10-15…03-15 with 21 warm-only title words), at least
  one "real" photo (32-hex filename), a usable first sentence. **Not checked: inventory, price, active status.**
- **Choice** (`:179-205`): seeded shuffle, prefer a different product type than the last single post, 14-day no-repeat
  (fallback can repeat). Every 4th post is an outfit of `rng.choice(tops), rng.choice(bottoms), rng.choice(finish)` —
  **purely random** (`:169-175`); boots/slippers typed "Sandals" land in the finish pool.
- **Photos** (`:64-98`): up to 4 real photos; each scanned once for AI markers by a case-sensitive byte search
  (`c2pa`, `jumb`, `trainedAlgorithmicMedia`, generator names), cached forever as true/false.
- **Captions** (`:124-166`): title, first description sentence (rejected if it contains $, ship, deliver, sale, hurry,
  limited, today only), colour line, random question from a small pool. Outfit caption fixed. Link + UTM
  (`utm_campaign=fb_photos&utm_content=<date>_<HHMM>`, no product or post id) in the first comment.
- **Publish** (`:228-253`): skips posts already sent; idempotency key `fb-<date>-<slot>`; appends one approval quote per
  run (even if nothing was sent); writes plan and history only after the loop — a mid-loop PostZen error loses the record
  of posts already scheduled.
- **Auto mode** exists but is off (`rules.json auto_publish false`); no scheduled task.
- **Reality vs code**: all 12 queued posts were hand-edited (AI picture from `data/media_generated/facebook_2026-10-28/`,
  `ai_picture` path, `first_comment: null`, link in caption, `#aigenerated`, one product swap with `products_planned`);
  the 10/27 live post's plan entry still holds the old caption and UTM. The approvals carry keys `publish()` never writes.

## 5. AI images, PostZen, Hub 1.0

- **Higgsfield images** (`hf_api.py`, `hf_image_edit.py`, `hf_image_batch.py`): models `flare`
  (marketing-studio/image/flare, ≤ 16 refs) and `qwen`; job file `{style, jobs[{key, aspect, refs, prompt}]}`; output PNG
  + `results.json {key: CDN URL}`. **Not recorded**: model parameters, request id, time, cost, prompt version, QA result,
  approval, rejection reason, link to the PostZen media URL or post. Review = contact sheets sent to the owner; approval =
  chat words copied into plan files and `log.md`.
- **PostZen client** (`postzen.py`): get/post/put/delete/upload/sync_external; 60 s timeouts; **no retries or 429
  handling**; idempotency only when a key is passed; `upload` defaults content type to video/mp4.
- **Hub 1.0 records** (`hubdata.py`, `decide.py`, `economics.py`, `metrics_sync.py`, `recipe.py`): creatives.csv 16 rows
  (one corrupt row, no ad ids), experiments.csv 0, metrics.csv 0, products.csv 13 (old catalogue). Nothing in
  `scripts/studio/` uses them. Worth keeping: the **creative tag vocabulary**, the **experiment schema**, the **decide.py
  status rules**, and the **one-field-at-a-time variant idea** in recipes.

## 6. Where each kind of data lives today

| Data | TikTok | Facebook | AI images | Other |
|---|---|---|---|---|
| Content item | studio.db `episodes` | plan JSON entries | — | Hub 1.0 recipes/creatives.csv (stale) |
| Media | `studio/episodes/<id>/*.mp4` | Shopify CDN / PostZen media URL | `data/media_generated/**` + Higgsfield CDN | backups `media_mirror` |
| Approval | `approval_json` (quote, time) | plan `approvals[]` (per run) | chat + log.md | bible `approvals.log` |
| Publishing state | `postzen_post_id`, `publish_mode`, `platform_status`, `post_url` | plan `postzen_post_id/status/post_url` + history.json | — | PostZen itself |
| Performance | analytics.db `post_snapshots` (since 10/27) + dashboard CSVs | same | — | |
| Cost | `spend` + `cost_usd` (promote double-counts) | none | none | creatives.csv (stale) |
| Products | `wardrobe.yaml` store pieces (text keys) | handles in plan | Shopify CDN ref URLs | analytics.db `products/variants` (Dashboard C) |
| Experiments | — | — | — | experiments.csv (empty) |
| History of changes | `transitions` (good) | log.md only | log.md only | |

## 7. Findings by the prompt's ten categories

1. **Duplicated functionality** — two planners with separate rotation/season logic (`gates.py` vs
   `facebook_photos.py:102-121`); no-price/no-urgency rules in three places, the Facebook version far weaker
   (`facebook_photos.py:36` vs `rules.yaml:45-71`); `METRICS`/`_num` defined twice; transition INSERT repeated in 6
   places; three economics formulas (economics.py, profitability_model, pricing_study).
2. **Fragmented content metadata** — four id schemes (`EW-YYYYMMDD-N`, Facebook date/slot, Hub 1.0
   `EC-P..-A..-H..-V..`, PostZen/platform ids); hook/format/CTA tags exist only in Hub 1.0's vocabulary.
3. **Repeated business rules** — seasons, banned phrases, link/UTM format, AI-disclosure rule each coded separately.
4. **Missing relationships** — product/room/series are text keys into YAML; outfit as JSON text; post → asset → cost →
   result not linked; UTMs carry no content id; Facebook dashboard rows have no product link.
5. **Fragile publishing** — no retries; failures unrecorded; plan overwrite; draft-vs-live ambiguity; caption changes
   after submission never reach PostZen; re-upload on retry.
6. **Unnecessary manual steps** — Facebook AI-picture posts assembled by hand; POSTED recorded by hand; approvals copied
   from chat into JSON. (Posting TikTok drafts by hand is required by the AI-label limitation and should stay.)
7. **Missing history** — per-attempt generation metadata overwritten; no snapshots before 10/27; Facebook edits only in
   log.md; replaced PostZen ids survive only in free text.
8. **Race conditions** — dashboard thread and CLI both write studio.db (default 5 s timeout, no WAL/busy_timeout, read-
   then-update in `move()`); dashboard sync rewrites Facebook plan files while `publish` or a hand edit may write them;
   no atomic writes for plan/history/results/dashboard files.
9. **Error handling** — uncaught `RuntimeError`/`TimeoutError` after billed provider calls; one failed status GET aborts
   a whole sync; frame-sheet ffmpeg return code unchecked; feed fetch aborts planning.
10. **Opportunities** — see `CONTENT_STUDIO_ROADMAP.md`. The highest-leverage ones are a canonical content record with
    Facebook moved into the database, honest publish states with receipts, media-bound approvals, and structured
    generation/asset metadata. All reuse what exists.

## 8. Security notes

- "Owner" is a CLI string; approvals are only as strong as the discipline of the person running commands. Acceptable
  for one operator on one PC; keep quotes and add media hashes so an approval cannot silently apply to a different file.
- Keys stay in user env vars (Higgsfield, Shopify) or Downloads\key.txt (PostZen, still to move). No secrets are
  written by the content code. `run_facebook_auto.cmd` reads key.txt with a regex.

## 9. What not to change

The bible-and-gates design, the template-only prompts, owner-only approvals, the TikTok drafts + manual AI-label
posting, the 3 slots and audience-first mix, the transitions log, and the no-caps decision (visibility, not limits).
