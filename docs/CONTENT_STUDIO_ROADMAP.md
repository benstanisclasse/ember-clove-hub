# Content Studio 2.0 — Roadmap

Status: **for owner approval** (Phase A checkpoint). Order follows the prompt's phases, re-ranked by what the audit
found. Each phase ends with a report (features, files, database changes, tests, results, open issues) and a checkpoint.

## 1. Ranked improvements

Scores 1–5 (5 = best): Impact on reliable, learnable content; Effort (5 = small); Disruption risk (5 = safe).

| Rank | Improvement | Impact | Effort | Risk | Why now |
|---|---|---|---|---|---|
| 1 | **Honest publish states** (`publish_jobs`, never count a TikTok draft as live; "Ready for TikTok publication" queue) | 5 | 4 | 5 | Today the dashboard can call a draft "live"; 7 drafts are queued for the next days |
| 2 | **Facebook into the database** (`content_items` import of both plan files incl. hand edits; plan-overwrite guard; per-post publish records) | 5 | 3 | 4 | Code and practice have diverged; re-planning would lose PostZen ids |
| 3 | **Facebook planner matches current practice** (AI-picture posts as a workflow, `#aigenerated`, link placement as a setting) | 5 | 3 | 4 | Removes hand assembly of every post |
| 4 | **Media-bound approvals** (asset/caption hashes checked at publish) | 4 | 4 | 5 | Prevents an approval silently applying to a different file or caption |
| 5 | **PostZen reliability** (retries + backoff, upload once, per-post records, failures recorded, one bad GET not fatal) | 4 | 4 | 5 | No retries today; failures leave no trace |
| 6 | **Generation/asset records** (`generation_jobs`, `assets`, `asset_refs`; image cost + request id; no overwritten attempts) | 4 | 3 | 5 | Needed for cost-per-asset and model comparisons |
| 7 | **SQLite and file safety** (WAL + busy timeout, atomic writes) | 3 | 5 | 5 | Dashboard thread and CLI write concurrently |
| 8 | **Shared rule module** (banned phrases/regex for scripts *and* captions *and* Facebook; one season rule source) | 4 | 3 | 4 | Facebook checks far weaker; captions never checked |
| 9 | **Product availability check at publish** (Shopify active + in stock + link works) | 4 | 4 | 5 | Prevents promoting a removed product |
| 10 | **Content features + 24 h/48 h/7 d marks** (hook, series, product, CTA, slot, day; from existing snapshots) | 5 | 3 | 5 | Foundation for all learning; data collection must start early |
| 11 | **UTM `utm_content=<content_id>`** (with Dashboard Phase E) | 4 | 4 | 4 | Links posts to store sessions/orders |
| 12 | **Template versioning + reference hashing** | 3 | 4 | 4 | Which configuration made which video |
| 13 | **Facebook outfit compatibility rules** (category, colour family, season, style) | 3 | 3 | 5 | Random outfits are skipped by hand today |
| 14 | **Product-fidelity review sheet + recorded verdicts** | 4 | 3 | 5 | AI pictures must not misrepresent products |
| 15 | **Experiment registry + comparisons** | 4 | 3 | 5 | Useful after ~2 weeks of tagged content |
| 16 | **Daily/weekly reports, knowledge base, recommendations** | 4 | 3 | 5 | After features and experiments exist |
| 17 | **Script similarity, extra ffprobe checks** | 2 | 4 | 5 | Nice to have |
| 18 | Character consistency automation (face-match scores), model comparison framework | 3 | 2 | 4 | Needs labelled examples first; face reference is currently off |

## 2. Phases

### Phase B — Unified content infrastructure (≈ 2–3 sessions)
1. Migrations (with a backup first): `content_items`, `content_products`, `content_assets`, `content_events`,
   `publish_jobs` in studio.db; WAL + busy timeout.
2. TikTok adapter: every episode mirrored into `content_items` and its transitions into `content_events`; existing CLI,
   gates and 35+ tests unchanged.
3. Facebook import: both plan files → `content_items` (keeping hand edits, `ai_picture`, `planned_for`, approvals,
   PostZen ids); plan files become exports; `plan` refuses to overwrite a plan that has sent posts.
4. `publish_jobs` for both channels; honest states (§2.3 of the architecture); TikTok "public" only on public evidence
   or `posted`; fix the dashboard label accordingly.
5. PostZen helper: retries/backoff, upload once per asset, write the job before and after each call.
6. Dashboard: Content Studio **Queue** tab and **Ready for TikTok publication** list; calendar reads `content_items`.
- **Acceptance:** every TikTok and Facebook item visible in one queue with correct state; the 7 queued TikTok drafts show
  "scheduled to drafts", none "live"; re-running Facebook `plan` cannot destroy sent posts; all old tests pass + new
  tests for adapter, import, states, idempotency.

### Phase C — Data collection and creative metadata (≈ 2 sessions)
1. `generation_jobs`, `assets`, `asset_refs`; Higgsfield image jobs recorded (cost estimate labelled, request id).
2. Content features on every item (series, hook type/text, CTA, caption style, product category, slot, weekday,
   duration, scene/room, outfit pieces) — filled automatically from the bible/plan, editable tags from the Hub
   vocabulary.
3. 24 h / 48 h / 7 d marks and per-1,000 rates from `post_snapshots`; "not provided" for missing metrics.
4. UTM `utm_content=<content_id>` on new Facebook links (and TikTok bio/link where possible), agreed with Dashboard Phase E.
5. Data-quality checks: duplicate post ids, missing product links, partial syncs.
- **Acceptance:** cost per generated, approved and published asset per provider/model; each published post shows its
  features and 24 h/48 h/7 d numbers once those marks pass.

### Phase D — Production quality (≈ 2–3 sessions)
1. Facebook AI-picture workflow (generate → fidelity review → caption → QA → approve → schedule) replacing hand assembly.
2. Shared rule module for scripts, captions and Facebook text; captions checked at `schedule`.
3. Product availability at publish; flag (not replace) scheduled content whose product went inactive or out of stock.
4. Media-bound approvals; severity levels; owner overrides recorded with the asset hash.
5. Template/prompt-style hashing in the bible approval; reference images hashed.
6. Facebook outfit compatibility rules; caption formats rotated (no same structure twice in a row).
7. Character references library (versions, approved and rejected examples) — no change to Ember's identity.
- **Acceptance:** no Facebook post needs manual JSON editing; a changed video or caption cannot publish under an old
  approval; an out-of-stock product blocks its post with a clear message.

### Phase E — Creative experimentation (when ~2 weeks of tagged content exist)
Experiment registry, assignment of content to variants, comparisons with sample size and uncertainty, Winner / Loser /
Inconclusive / Collecting; first candidates: link placement on Facebook (caption vs first comment), product shown in
the first 2 seconds vs later, posting-time windows (existing slots stay default).

### Phase F — Intelligence engine
Daily and weekly reports, anomaly checks against each metric's own history, recommendations with evidence, cost and
success metric, and the knowledge base separating observed result / interpretation / recommended change / approved policy.

### Phase G — Product and store intelligence (with Dashboard Phase F)
Product promotion ranking from margin, stock, season, audience response and store data (from the shared Shopify sync),
content → product → link → session → order chain.

### Phase H — Hardening
Regression, publishing reliability and integration-failure tests, performance, security, documentation.

## 3. Coordination with Dashboard 2.0

| Topic | Owner of the work | Note |
|---|---|---|
| UTM convention | Dashboard Phase E (being worked on in another session) | Content Studio adds `utm_content=<content_id>` |
| Ads drill-down / paid creatives | Dashboard Phase E | Later linked to `assets` |
| Calendar | Dashboard Phase D (built) | Switches its source to `content_items` in Content Studio Phase B |
| Shopify | Dashboard Phase C (built) | Reused for availability, products, store outcomes |
| Profitability | Dashboard Phase F | Feeds product ranking in Content Studio Phase G |
| Intelligence page | Dashboard Phase G / Content Studio F | One page, one findings table |

Recommended order across both programs: **Content Studio B → Dashboard E (in progress elsewhere) → Content Studio C →
Content Studio D → then E/F of both as data accumulates.**

## 4. Decisions needed from the owner

1. Approve Content Studio Phase B as the next build (unified records, Facebook into the database, honest publish states,
   PostZen reliability, Ready-for-TikTok queue).
2. Facebook link placement default while untested: **in the caption** (what all queued posts now use) or first comment.
3. Facebook AI pictures become a standard post type (each still reviewed and approved by you) — yes/no.
4. Re-approve `wardrobe.yaml` (currently draft because it changed after approval), so production video generation is
   possible again — after reviewing the change.
5. Face reference for Ember's videos: keep off (current) or test on again in trials for consistency.

---

## Phase B report (2026-10-27, owner: "Approved: build Content Studio Phase B (unified content records, Facebook into the database, honest publish states, PostZen reliability, Ready-for-TikTok queue). Facebook link default: in the caption. AI pictures as a standard Facebook post type, each still approved by me.")

**Implemented**
- `scripts/studio/content.py`: tables in studio.db — `content_items`, `content_products`, `content_assets`,
  `content_events`, `publish_jobs`, `media_uploads`. Every real TikTok episode is mirrored as `TT-<id>` (its 216
  transitions copied once as events); every Facebook plan post as `FB-<plan start>-<nn>` (status changes between syncs
  become events). Dashboard job "content" runs after the TikTok/Facebook syncs (~1 s) and writes `content_queue.json` +
  `content_events.json`.
- **Honest publish states**: submitted / scheduled / in_tiktok_drafts / awaiting_manual_post / public / paused / failed.
  A TikTok draft is "public" only with public evidence (views or impressions in PostZen analytics) or the owner's
  `posted`. Today: dinner video public (33 views), drizzly-day video "post it now", 7 drafts scheduled for their slots.
- **Reliability**: studio.db in WAL with a 30 s busy timeout; PostZen client retries 429/5xx/dropped connections for
  reads, updates and keyed creates (never unkeyed creates); TikTok videos uploaded once and reused (`media_uploads`);
  every TikTok and Facebook send writes its publish job before and after the call and records failures; one failed
  status check no longer aborts a sync; atomic writes for plan, history and dashboard queue files; Shopify client
  retries dropped connections (a live sync had failed on one).
- **Facebook**: `rules.json link_placement: caption` (default) and `ai_pictures: true`; AI posts are refused unless the
  caption has #aigenerated; each sent post stores its own approval (owner's words, time, caption and photo hashes) and
  is saved immediately; `plan` refuses to overwrite a week that has posts in PostZen. The 10/27 slippers record was
  corrected to what was actually sent (planned caption kept as `caption_planned`).
- **Dashboard (Content Studio page)**: "Ready for TikTok publication" (filmstrip thumbnail from the QA frame sheet via
  `/media/frames/<episode>`, slot, caption, state, approval, AI-label reminder) and "Content queue" (all 33 items,
  filters Open / Needs you / Scheduled / Public / All and by channel, history drawer, CSV).

**Tests:** `scripts/studio/test_content.py` 27 tests (states incl. "a draft with a URL is not public", mirrors and
idempotency, record/upload-once, atomic writes, PostZen retry rules, Facebook caption link / AI refusal / plan guard,
frame route) — full suite 101/101 at the time of the run.

**Files:** new `scripts/studio/content.py`, `scripts/studio/test_content.py`; changed `scripts/postzen.py`,
`scripts/shopify_api.py`, `scripts/studio/db.py`, `scripts/studio/publishing.py`, `scripts/facebook_photos.py`,
`studio/dashboard/index.html`, `data/facebook/rules.json`, `data/facebook/plan_2026-10-28.json` (one record corrected).
`dashboard_server.py` content job + frame route were committed inside the parallel Dashboard Phase E commit 189074b.

**Database changes:** new tables in studio.db only (backup taken first); episodes/transitions untouched.

**Limits / next**
- Facebook plan files are still the working source; the database mirrors them. Making the database the source (and the
  AI-picture generate → fidelity review → caption → approve flow) is Phase D.
- Media-hash-bound approval is enforced for Facebook sends (hashes stored per post); TikTok approval binding to the
  video hash is Phase D (publish jobs already store the asset hash).
- Item series show ids (e.g. `minneapolis-weather`), not display names.

**Next: Phase C** (generation/asset records, content features, 24 h/48 h/7 d marks, `utm_content=<content_id>` with
the attribution convention now in `scripts/attribution.py`).

## Phase C report (2026-10-27, commit 97f7869)

Owner: "Yes, start Content Studio Phase C: generation and asset records, content features, 24h/48h/7-day performance
marks and utm_content with the content id."

**Built**
- **Generation records** (studio.db `generation_jobs`, `assets`, `asset_refs`): `production.py` opens a job before every
  video and first-frame call and closes it with status, provider request id, cost and cost basis (Higgsfield video =
  "estimate", OpenRouter = billed when reported); any exception marks the job failed. `hf_image_batch.py` records every
  image job (model, prompt, references, request id, output file and URL); Higgsfield reports no image cost, so it stays
  empty ("not reported"). Assets are hashed (sha256) and de-duplicated by path.
- **Backfill** (idempotent): 46 historical jobs from the spend table, episode videos and the image job files.
  Higgsfield video 7 jobs $29.40 (estimate), OpenRouter video 6 jobs $8.98, first frame $0.07, 3 failed/unknown,
  29 images with cost "not recorded". Recorded total $38.45.
- **Content features** (`content_features`, 489 values): slot, weekday, series, room, CTA, hook type and text, words,
  duration, outfit pieces, store piece and product category, model, attempts; for Facebook post kind, AI picture,
  caption asks a question, caption length, products. Owner-set values (`source='owner'`) are never overwritten.
- **Performance marks** (`content_marks`): 24 h / 48 h / 7 d / latest from real `post_snapshots` only, using the first
  snapshot within 6 h after the mark; otherwise the mark stays empty. Anchor = scheduled time for PostZen posts, or
  the first snapshot with views for TikTok drafts posted by hand (the exact posting time is unknown; the basis is shown).
- **utm_content = content id**: Facebook plans now give each post `content_id` `FB-<week start>-<nn>` and its link
  carries `utm_content=<content_id>` (older posts keep their date_slot value). `content_links` maps every link to its
  item; Shopify UTM sessions (cart/checkout/completed) are credited per item.
- **Quality checks** (`content_quality.json`): duplicate PostZen ids, public without a link, no product, AI picture
  without #aigenerated (critical), Facebook post without a tracked link, generation job stuck over 2 h. Currently 0.
- **Dashboard**: Content performance page gained "Post performance, compared fairly" (per live post: seen at
  24h/48h/7d/now, engagement and clicks per 1,000 impressions, store visits, generation cost), "Compare by feature"
  (10 features, groups under 5 posts marked "too few to compare") and "Production cost" (by kind/provider/model with
  cost basis; unknown costs show "not recorded", never $0). Content Studio page shows a data-quality notice when any
  check fails. Datasets `content_jobs` and `content_quality` are served (added by the Dashboard session).

**Tests:** 13 new in `scripts/studio/test_content.py` (job lifecycle and hashing, failed job keeps no cost, backfill
idempotency, owner features preserved, hook types, marks only inside the window, hand-posted anchor, links + store
sessions, AI-disclosure check, link content id). Full suite 121/121.

**Limits**
- Only 3 posts are live, so no 24 h mark has been captured yet (snapshots began 10/27) and every feature group is
  "too few to compare". The comparison becomes useful after ~2 weeks of posting.
- Image costs are unknown (Higgsfield does not report them); cost per live post covers videos only.
- TikTok captions carry no store link, so TikTok store visits can't be credited per video (bio link only).

**Next: Phase D** (production quality: Facebook AI-picture workflow in the database, shared rule module, product
availability at publish, media-bound approvals).
