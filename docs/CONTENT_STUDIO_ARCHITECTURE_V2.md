# Content Studio 2.0 — Proposed Architecture

Status: **proposal for owner review** (Phase A). Companion documents: `CONTENT_STUDIO_AUDIT.md`,
`CONTENT_STUDIO_ROADMAP.md`. Coordinated with Dashboard 2.0 (`DASHBOARD_ARCHITECTURE_V2.md`): one dashboard, one
Shopify connector, one history store, one backup job.

Guiding rule: **extend Ember Studio, don't replace it.** Python + SQLite + the existing CLI, gates and bible. New
capability is added as tables, modules and dashboard pages next to what exists; the TikTok stage machine and its tests
keep working unchanged at every step.

---

## 1. The six subsystems mapped onto what exists

| Subsystem (prompt) | Built on | New pieces |
|---|---|---|
| **A Content Intelligence** | Dashboard Intelligence page, `ui.alerts`, `decide.py` rules | daily/weekly reports, findings and knowledge tables (Roadmap F) |
| **B Creative Planning** | `cli.py plan` + `gates.check_calendar/check_outfits`; Facebook `plan()` | one planner front-end for both channels, shared rotation/season rules, outfit compatibility rules for Facebook, product signals from Shopify |
| **C Production Engine** | `production.generate/trial`, templates, `hf_image_batch.py` | generation-job and asset records for video **and** images; template versioning |
| **D Quality Assurance** | `production.qa` (transcript, duration, speech, frame sheet), Facebook AI-marker scan | severity levels, product-fidelity review, availability check, caption rule check, media-hash-bound approvals |
| **E Publishing Orchestrator** | `publishing.publish`, `facebook_photos.publish`, `postzen.py` | one publish-job table with receipts and honest states, retries, the "Ready for TikTok publication" queue |
| **F Performance & Learning** | analytics.db `post_snapshots`, `account_daily`, Shopify sessions/UTM | 24 h / 48 h / 7 d marks, content features, experiments, knowledge base |

Deterministic Python does planning, gates, scheduling, syncing and bookkeeping. AI models are used only where they add
something: scripts and captions (as today, through approved templates), images and video, and optional assistive
visual checks whose output is advisory and validated against the owner's decisions.

## 2. Data layer

Two SQLite files, as today, with clear roles:

- **`studio/studio.db` — what we make and decide** (conveyor, content, approvals, experiments, knowledge).
- **`studio/analytics.db` — what platforms reported** (snapshots, store, ads; Dashboard 2.0). Content performance is
  joined by platform post id; no third database.

### 2.1 Canonical content record (studio.db)

```
content_items        one row per piece of content, any channel
  content_id   TEXT PK       e.g. TT-EW-20261103-1, FB-20261028-0900, FB-AI-…
  channel      TEXT          tiktok | facebook (instagram later)
  kind         TEXT          tiktok_video | fb_product_photo | fb_outfit_photo | fb_ai_picture
  workflow     TEXT          name of the step list it follows (§3)
  state        TEXT          current step
  series, concept, hook_type, hook_text, cta_type, caption, caption_style
  scheduled_at TEXT (UTC)    + slot label in Eastern
  episode_id   TEXT NULL     → episodes.id for TikTok (episodes keeps all video-specific fields)
  created_at, updated_at, archived INTEGER
content_products     content_id, product_gid, variant_gid NULL, role (featured|outfit_piece|store_shoes)
content_assets       content_id, asset_id, position
content_events       generalised transitions: content_id, from, to, actor, reason, at, files JSON, error
```

- TikTok keeps `episodes` and `transitions` exactly as they are; a thin adapter creates/updates the matching
  `content_items` row and mirrors every transition into `content_events`, so nothing in the gates or tests changes.
- Facebook plan JSON files become `content_items` rows (with a one-time import that keeps hand edits, `planned_for`,
  `posted_early`, approvals and PostZen ids). Plan files stay as read-only exports for review sheets.
- Products are referenced by **Shopify GID** everywhere (wardrobe store pieces already carry the Shopify product; the
  Facebook handle maps to a GID through analytics.db `products`).

### 2.2 Assets and generation jobs

```
assets               asset_id PK, type (video|image|frame_sheet), path, sha256, width, height, duration_s,
                     source (generated|supplier|upload), provider, model, model_version, template, template_hash,
                     prompt_hash, created_at, postzen_media_url, cdn_url
asset_refs           asset_id, ref_kind (face|room|product|store_piece|style), ref_path_or_url, ref_sha256
generation_jobs      job_id PK, asset_id NULL, content_id, provider, provider_job_id, model, settings JSON,
                     started_at, finished_at, status (submitted|completed|failed|timeout|cancelled), cost_usd,
                     cost_basis (billed|estimate), error
```

- The `spend` table stays (it feeds caps); each new job also writes `generation_jobs`, so attempts are never
  overwritten and Higgsfield image jobs finally have a cost (estimate, labelled) and a request id.
- `sha256` of the media is what approvals bind to (§4).

### 2.3 Publishing

```
publish_jobs   job_id PK, content_id, asset_sha256, channel, mode (tiktok_draft|tiktok_public|fb_scheduled|fb_now),
               idempotency_key UNIQUE, postzen_post_id, platform_post_id, submitted_at, scheduled_for,
               state, state_evidence, last_checked_at, attempts, error
```

States (never collapsed):

| State | Meaning | Evidence required |
|---|---|---|
| `submitted` | PostZen accepted the request | PostZen post id |
| `scheduled` | PostZen will send at the slot | PostZen status scheduled |
| `in_tiktok_drafts` | Delivered to the owner's TikTok drafts | draft mode + PostZen published |
| `awaiting_manual_post` | Draft delivered, slot time reached | time ≥ slot, no public evidence |
| `public` | Live and visible | **public evidence**: the post appears in PostZen analytics or `sync-external` with a platform id and views/impressions, or the owner's `posted` command |
| `failed` | PostZen or platform reported failure | error text |

A TikTok draft is **never** `public` because PostZen returned a URL or "published" (audit finding §1).

### 2.4 Experiments and learning (studio.db)

```
experiments        id, hypothesis, channel, product_gid NULL, variable, variants JSON, primary_metric,
                   secondary JSON, min_sample, design (randomised|observational), start, end, status, result JSON,
                   interpretation, decision, decided_by, decided_at
experiment_items   experiment_id, content_id, variant
findings           id, period, kind (daily|weekly|anomaly|pattern), text, evidence JSON, sample_size, created_at
knowledge          id, statement, type (observed_result|ai_interpretation|recommended_change|approved_policy),
                   evidence JSON, status (proposed|approved|rejected), owner_quote, created_at
```

Schema seeded from the Hub 1.0 experiments CSV (18 columns) and its creative tag vocabulary (`config/hub.json tags`).
Approved policy changes still go through the bible (`bible-approve`); `knowledge` never edits the bible by itself.

### 2.5 Performance (analytics.db, reused)

- `post_snapshots` (every 15 min since 2026-10-27) already gives true lifetime counters over time; 24 h / 48 h / 7 d
  values are read from the snapshot nearest each mark after `published_at`, only when such a snapshot exists.
- New view `content_performance` joins `publish_jobs.platform_post_id` → snapshots, plus Shopify UTM sessions by
  `utm_content = content_id` (from the new link convention).
- Unavailable metrics (watch time, completion, profile visits) are shown as "not provided by PostZen".

## 3. Workflow engine

A workflow is a declared list of steps with the checks each step requires, kept in code and validated by tests (no
free-form YAML that could weaken a gate):

```
tiktok_video   : planned → scripted → generated → qa → awaiting_approval → approved → scheduled
                 → submitted → in_tiktok_drafts → public → measuring      (+ failed, archived)
fb_photo       : planned → images_selected → captioned → qa → awaiting_approval → approved → scheduled
                 → submitted → public → measuring
fb_ai_picture  : planned → image_generated → product_fidelity_review → captioned → qa → awaiting_approval
                 → approved → scheduled → submitted → public → measuring
```

- The TikTok workflow is a **view over the existing stage machine** (`episodes.state` → workflow step), so the proven
  transitions table and gates remain the source of truth.
- Each step lists its required checks; a step cannot be skipped and a failed critical check blocks the next step.
- Overrides keep today's model: owner only, quoted, recorded, and **bound to the asset's sha256**. Legal/platform
  requirements (AI disclosure) cannot be overridden.

## 4. Approvals bound to media

- Approving content stores `{owner_quote, at, asset_sha256, caption_sha256}`.
- Publishing recomputes both hashes; any difference blocks the publish and asks for re-approval.
- The bible approval hash is extended to cover the prompt templates and `prompt_style.py` (template versioning),
  and reference images are hashed in `asset_refs`, so a changed reference shows up as a new configuration.

## 5. Quality assurance with severities

| Severity | Examples | Effect |
|---|---|---|
| Critical | wrong product, product inactive/out of stock at publish, missing AI disclosure, corrupt media, unapproved or changed asset | blocks |
| High | transcript mismatch, banned phrase in caption, product-fidelity doubt | needs owner accept with quote |
| Medium | duration or speech coverage slightly off, repeated script structure | shown for review |
| Low | style notes | informational |

New checks, all deterministic first: caption run through the same banned-phrase/regex rules as scripts (one shared rule
module for both channels); product availability from analytics.db `variants`; ffprobe checks (resolution, aspect,
audio present, duration, frame errors); script similarity against the last N scripts (word n-gram overlap). Product
fidelity starts as a side-by-side review sheet (generated asset next to the Shopify photos) with the owner's verdict
recorded; an optional vision-model comparison can be added later as advisory, measured against those verdicts.

## 6. Publishing reliability

- One shared PostZen helper with retries and exponential backoff for 429/5xx (safe because every send carries an
  idempotency key), media uploaded once per asset and reused (`assets.postzen_media_url`).
- Every send writes a `publish_jobs` row **before** calling PostZen and updates it after, so a crash mid-loop leaves a
  record; Facebook `publish()` writes per post, not after the loop.
- Caption changes after submission are pushed to PostZen (`PUT posts/{id}`) or block until re-sent.
- SQLite: WAL mode and a busy timeout for studio.db; atomic temp-file-and-rename for every JSON/CSV the dashboard reads.
- Sync: one failed status GET is recorded and skipped, not fatal for the whole job.

## 7. Dashboard integration (no second app)

New views inside the existing sidebar (Dashboard 2.0 Phase D shell and `ui.*` components):

| Prompt §19 | Where |
|---|---|
| Content operations (pipeline, approvals, failed jobs, generation and publishing queues) | **Content Studio** page: new "Queue" tab (from `content_items` + `publish_jobs`) and **"Ready for TikTok publication"** list (thumbnail/frame, caption, slot, draft status, AI-label reminder, approval) |
| Creative analytics | **Content Studio → Performance** (extended with 24 h/48 h/7 d, per-1,000 rates, by series/hook/product) |
| Experimentation | **Intelligence** page, Experiments tab |
| Production economics | **Operations → Costs** (spend by provider/model/kind, rejection rate, cost per approved and per published asset) |
| Intelligence | **Intelligence** page (daily/weekly findings, knowledge base with observed vs interpreted vs approved) |

## 8. Shared with Dashboard 2.0 (do not duplicate)

- Shopify: `scripts/shopify_api.py` + `shopify_sync.py` (products, variants with cost and stock, orders with UTM).
- History store and sync health: `studio/analytics.db`, `analytics.job`, `sync_runs`.
- Backups and git: nightly task + local repo.
- UTM convention: Dashboard Phase E defines it; Content Studio adds `utm_content=<content_id>` so a post ties to store
  sessions and orders.
- Ads drill-down (being added to `ads_snapshot.py` / `analytics.py` in Dashboard Phase E) links paid creatives to the
  same `assets` records later.

## 9. Safety and approvals (unchanged principles)

Autonomous: analysis, ideas, drafts, scripts, previews within spend settings, QA, comparisons, recommendations,
schedules-as-proposals, reports. Owner approval: publishing, bible/rule changes, posting frequency, starting selling,
Ember's identity, product representation, full auto-posting, new paid services, spend limits, ad budgets, deleting
history. Approvals stay immutable and hash-bound; test or failed assets can never reach production without a quoted
owner decision.
