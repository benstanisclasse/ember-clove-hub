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
