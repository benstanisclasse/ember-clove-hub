# Market Intelligence Engine — Engineering Audit (Phase A)

Date: 2026-10-28. Scope: the Kalodata research stack (collection, ingestion, storage, feature code, models as code,
weekly report, video study tooling, Meta/TikTok ad research scripts) and how it fits the rest of the Hub. Method: code
read-through, read-only SQLite inspection (`mode=ro`), raw-file reconciliation, `EXPLAIN QUERY PLAN`, scheduled-task
and git/backup checks. **No API calls were made and no file, model, database or report was changed.** Data quality,
model validity and creative research are covered by the other three Phase A audits; they are only touched here where
the code causes them.

Legend: **[V]** verified in this audit (file:line, query or command output); **[I]** inferred, not proven.

---

## 1. Summary

The engine is a set of hand-run, single-purpose scripts that grew in two days (10/25–10/26). The core pieces are sound
and worth keeping: one Kalodata client with a hard credit cap, a raw-file-first record of every paid call, a resumable
bulk downloader, a SQLite loader that keeps the full JSON of every record, and a training/scoring pipeline that reads the
database read-only. The problems are around it: nothing protects the data, nothing records what was spent, results
cannot be rebuilt on demand, and none of it is connected to the Hub that was built since.

Most important findings:

1. **None of the market data is backed up or versioned.** `.gitignore:22` excludes `research/`, and
   `scripts/backup_hub.py:21-24` backs up only `studio/*.db`, `data`, `config`, `studio/bible`, `studio/dashboard`,
   `docs`, `log.md`. `backups/2026-10-27/` holds no research file **[V]**. A disk failure loses `kalodata.db` (397 MB),
   `raw/` (304 MB, ~533 credits ≈ $53 of paid responses), the models, 15 reports and the paid video-tagging tables.
2. **The database silently drops data that was paid for.** `kalodata.py:53-60` writes each response to
   `raw/<folder>/<name>.json` (overwriting a same-named file), then loads it; `kalodata_db.py:72-73` skips any file
   already in `pulls`. A retry that succeeds after a failure under the same name therefore updates the raw file but not
   the DB. **6 of 18 weekly comment-insight files now hold successful responses that the DB still records as failed,
   with no rows in `comment_insights`** (e.g. `raw/weekly_2026-10-26/weekly_comments_1729495345537783705.json`) **[V]**.
3. **There is no credit ledger.** Each run keeps an in-memory `Budget` (`kalodata.py:33-41`) and prints a total; the
   cost of a call is not stored in the raw file or in `pulls`. Spend can only be reconstructed: successful saved
   responses imply ~532.7 credits; purchases (≈15 + 1,000) minus the last saved balance (474.5, 10/26 11:40) imply
   ~540.5 — an unexplained gap of ~8 credits **[V, by reconstruction]**. The core run itself printed 478.2 "charged"
   vs 472.5 real (log.md:165). Kalodata is absent from the Hub cost ledger (`analytics.db generation_costs` has only
   Higgsfield and OpenRouter video rows) **[V]**.
4. **Duplicate-request protection exists only in the bulk downloader, and only by file name.** `kalodata_core.get()`
   reuses a saved response from `raw/core/` (`kalodata_core.py:34-50`); `weekly_breakout_report.fetch()` reuses only
   *today's* file (`:166-172`); `--scan` (`:62-79`) and all of `kalodata.py` re-pay every time. The same request saved
   under two names was paid twice: 11 request duplicates, 12 extra files, e.g. `pilot_womenswear_2026-08_p1..p5` =
   `core_products_2026-08_601152_p1..p5` **[V]** (small money, but the pattern grows with weekly runs).
5. **Pull metadata is thin and the key facts live in file names.** `pulls` has no timestamp, cost, checksum, run id or
   provider message; `pulled_on` is the folder name (`kalodata_db.py:83`), so **4,986 of 5,153 pulls (97%) say
   `pulled_on = 'core'`** **[V]**. Month, category, list and page are parsed out of names like
   `core_risers_2026-09_601152_p3` in four places (`kalodata_core.py:99-100`, `train_product_model.py:53-55`,
   `video_pilot.py:72`, `pilot_model.py:29`) although the same values are in `filters`/`date_range`.
6. **Results are not reproducible from the current state.** `train_product_model.py:45-46` selects pulls by
   `name LIKE 'core_risers_%'`, which now also matches the deep riser pages p3–p10 added after model v1: the panel would
   be 251,654 product-months today vs 230,052 for model v1 **[V]**. Nothing records which pulls a model or report used.
   The weekly model cache is keyed only on month list and feature names (`weekly_breakout_report.py:96-101`), not on
   the data, so it would be reused after the data changed. About 10 of the 15 `research/kalodata/*.md` reports and
   several CSVs (`video_links_core.csv`, `seasonality_groups_monthly.csv`, `subcategories_*.csv`) have **no generating
   script in `scripts/`** — they came from inline session code **[V: grep finds no producer]**.
7. **Nothing runs unattended.** No Windows task or Claude scheduled task touches the market engine (only "Ember Hub
   Nightly Backup", "Ember Studio Dashboard", and the Claude task "ads-dashboard-refresh") **[V]**. The only weekly
   report (10/26) ran **without `--scan`** — there are no `weekly_products_*` pulls — so it scored September data, not
   fresh lists **[V]**. Logs are ad-hoc redirects (`core_download.log`, `video_*.log`).
8. **No integration with the Hub.** No dashboard page, `analytics.db` table, `sync_runs` job, cost-ledger row or
   Shopify product link refers to Kalodata or `research/` (grep of `scripts/studio/`, `studio/dashboard/`) **[V]**.
   `pricing_study.py:17-18` takes fees and refunds from hard-coded constants in `test_product_economics.py:18` instead
   of `config/hub.json → economics` used by `studio/profit.py:45-48` (values match today; they can drift) **[V]**.

Not a problem: SQLite performance. The heaviest query (training load, 257,600 rows) takes 0.9 s; the DB passes
`integrity_check` **[V]**.

---

## 2. Inventory

| Component | What it does | Status |
|---|---|---|
| `scripts/kalodata.py` (227 lines) | Kalodata client: `call()` (raw save + auto-load), `Budget` cap, `rank()`; first-day research, product-videos, comments, `balance` subcommands | **Keep `call`/`Budget`, fix** (ledger, unique raw names, timestamp, cache check); retire the one-off `research()` |
| `scripts/kalodata_core.py` (181) | Resumable bulk download of the core dataset (12 months × 29 categories, 6 phases) | **Keep**; move its cache check into the client; drop name parsing |
| `scripts/kalodata_db.py` (129) | Loads `raw/*/*.json` into `kalodata.db` (`pulls` + 5 typed tables, full JSON kept) | **Fix**: reload-on-change, richer `pulls`, natural keys, separate derived tables |
| `research/kalodata/kalodata.db` | 397 MB SQLite: 5,153 pulls, 259,418 product rows, 135,653 video rows, + `video_features`/`video_elements`/`video_audio` (184–185 rows) | **Keep, back up**; split raw-derived vs analysis tables |
| `research/kalodata/raw/` | 5,153 JSON responses (path, request, status, response) in 6 folders | **Keep as source of truth; back up** |
| `scripts/pilot_model.py` | First Aug→Sep Womenswear model (superseded) | **Archive** |
| `scripts/train_product_model.py` (268) | Builds the product-month panel, trains 4 models, forward test, scores latest month | **Keep logic, fix inputs** (data snapshot, months from data, read pulls by columns) |
| `scripts/score_breakouts.py`, `explain_breakouts.py` | Breakout model without riser position; per-product explanations (hard-coded `PICKS` names) | **Fold into one scoring module**; explanations generic |
| `scripts/weekly_breakout_report.py` (530) | Scores risers, filters, enriches (paid), checks links, writes PDF/CSV/history | **Fix** (cache, ledger, offline rebuild, schedule); keep PDF layout |
| `research/kalodata/model_v1_2026-10-25/` | `models.joblib`, `breakout_models.joblib`, 46 MB panel, scores, results | **Keep, version** with a manifest |
| `scripts/video_pilot.py`, `video_elements.py`, `video_audio.py`, `analyze_video_study.py` | Video study: download, whisper, cuts, frame sheets, OpenRouter tags, paired analysis | **Keep as study tools**; share one tagging/cut module; write costs to ledger |
| `scripts/analyze_topads.py`, `download_topads.py` | TikTok Top Ads transcripts/frames (434 MB under `research/tiktok/ads`) | **Keep**; dedupe with video_pilot helpers |
| `scripts/meta_ad_library_list.py` | Writes one CSV from 100 rows typed into the script as literals | **Replace** with a data file + loader (it is data, not code) |
| `scripts/pricing_study.py` | Owner-formula pricing check from a Shopify export | **Fix**: use `profit.py`/config economics |
| Reports `research/kalodata/*.md` (15) | Findings, plans, model write-ups | **Keep**; mark which are regenerable |

---

## 3. Collection and credit control

**Endpoints used [V, raw files]:** `tiktok/product/rank` (2,617 files), `tiktok/video/rank` (1,399),
`tiktok/product/detail` (1,022), `tiktok/category/rank` (14), `tiktok/product/comment/insight` (18), `tiktok/video/url`
(20), `tiktok/video/detail` (1), `tiktok/video/download` (1, 404), `credit/balance` (3); 58 early files have no stored
path and are classified by name prefix (`kalodata_db.py:38-41`).

**Request building.** One function, `kalodata.call()` (`kalodata.py:44-65`), POSTs JSON with the key header read from
`hub_env.get_secret("kalodata_api")` on every call. Common params (`region=US`, `en-US`, `USD`) at `:28`. Costs are
passed in by each caller as literals (0.1 per 100 rank rows, 0.1 detail, 1.0 comments, 0.5 video URL) — the billing
table exists only in the docstring (`:4-5`).

**Credit cap.** `Budget.charge()` stops *before* a call that would exceed `--max-credits` (`:37-41`). Good, and every
paid entry point requires the flag (weekly report defaults to 15, `weekly_breakout_report.py:408`). Caveats: the cap
counts failed calls (which Kalodata usually does not bill) and counts each retry; it is per-run only, so two runs can
each spend the full cap.

**Retries and errors.**
- `kalodata.py` itself has no retry and does not catch `requests` exceptions; a dropped connection ends a run.
- `kalodata_core.get()` retries up to 5 times (`:51`; its docstring says "twice", `:46`), backs off on connection
  errors, and stops on code 501. 39 core pulls failed permanently, all "product/video not found" (Virtual Products and
  similar empty category-months) **[V]**.
- `weekly.fetch()` retries only when the message contains "timeout" (`:177-179`). The 8 failed weekly comment calls had
  message `None` (6) or "No enough comments" (2), so they were not retried in-run; 6 later succeeded on a re-run **[V]**.
- Rate limit: 1.1 s sleep after successful calls only (`kalodata.py:64`).

**Caching / "check before paying".** As above (finding 4). Nothing checks `kalodata.db`; nothing matches on request
content; `kalodata.py` subcommands and `--scan` never check. The weekly comment lookup reuses any `*comments_<pid>.json`
from the last 28 days (`:153-163`) — the right idea, but done by folder-name date parsing.

**Raw file naming.** `RAW` is fixed at import time to `raw/<today>` (`kalodata.py:30`) and reassigned as a module
global by three callers (`kalodata_core.py:30`, `video_pilot.py:115`, `weekly_breakout_report.py:64,185`). Same-name
files are overwritten: `balance.json` exists in 3 folders and each folder keeps only its last balance **[V]**.

**Ledger and reconciliation [V].** No ledger. Saved balances: 505.7 (10/25 23:19), 486.1 (10/26 00:11, after the
weekly report; 19.6 credits, matching the weekly folder's successful calls), 474.5 (10/26 11:40). Reconstruction from
successful raw responses: core 494.7, weekly 19.6, pilot videos 10.1, first day 7.3, subcategories 1.0 = 532.7.
Refused-but-billed video downloads (log.md:173) and failed comment calls are invisible in this method.

---

## 4. Ingestion and storage

**Load path.** Every paid call is loaded immediately (`kalodata.py:57-60`, failures to load are printed and the raw
file kept — good). `kalodata_db.py load` loads anything missing. Raw vs DB today: 5,153 files, 5,153 pulls, 0 missing,
0 orphans; 6 stale (finding 2) **[V]**.

**Schema [V].** `pulls(pull_id, file UNIQUE, pulled_on, name, endpoint, region, date_range, filters, http_status,
success, n_records)`. Record tables `products`, `videos`, `product_details`, `categories`, `comment_insights` have
`pull_id, position`, untyped columns and `raw_json`; **no primary key and no natural key** (product × month × list).
Indexes: `pull_id` and the entity id on the three big tables. `CREATE TABLE IF NOT EXISTS` runs on every connect
(`:47-60`); there is no schema version or migration path.

**Idempotency.** File-level only. Re-running `load` is safe; a changed file is never reloaded; the same request under
a different name loads twice. Records repeat by design (259,418 product rows for 136,291 products; 135,653 video rows
for 98,484 videos), and de-duplication happens in pandas (`train_product_model.py:62-65`) **[V]**.

**What is kept per pull.** Kept: file, folder, name, endpoint, region, date range, other request params, HTTP status,
success, record count, full JSON per record. Missing: request time (only file mtimes — core 10/25 19:22–23:19), credit
cost, provider code/message, checksum, run id/script/version. The provider's `cached` flag is in the JSON but `None`
in all 5,153 files **[V]**.

**Storage.** `raw_json` is 232 MB of the 397 MB DB (products 142 MB, videos 79 MB) **[V]**, duplicating `raw/` (304 MB).
Disk: 82 GB free of 400 GB **[V]** — fine for now. Analysis tables written by the video tools (`video_features`,
`video_elements`, `video_audio`) live in the same DB but **cannot be rebuilt from `raw/`** (they cost OpenRouter money
and CPU), so "rebuild the DB from raw" would lose them **[V: created by `video_pilot.py:245-250`,
`video_elements.py:86`, `video_audio.py:90`]**.

---

## 5. Code quality

**Hard-coded values [V].**
- Month list duplicated: `kalodata_core.py:28`, `train_product_model.py:31` (ends 2026-09; the weekly report extends it
  in place, `weekly_breakout_report.py:86-93`).
- Dated paths: `model_v1_2026-10-25` (`train_product_model.py:30`), `pilot_model_2026-10-25`, `VIDEO_STUDY_2026-10.md`,
  `pricing_export_2026-10-26.jsonl` (`pricing_study.py:21`), `ad_library_100_2026-10-27.csv`.
- Category ids/sets: `FASHION`, `SKIP_CATS`, `APPAREL_CATS` (`weekly_breakout_report.py:53-58`), `APPAREL` names
  (`analyze_video_study.py:21`), `PILOT_PRODUCTS` (`video_pilot.py:40-42`), product-name `PICKS`
  (`explain_breakouts.py:21-22`).
- Season keyword regexes and risk thresholds (`weekly_breakout_report.py:56-57, 243-257`), `pilot_model.py:49`
  date literal, model name `TAG_MODEL` (`video_pilot.py:38`).
- `meta_ad_library_list.py` embeds 100 data rows as Python literals.

**Fragile parsing [V].** Pull names → month/category/page (finding 5); `pilot_model.py:29` reads the page as the last
character of the name (breaks at page 10). `recent_comments` parses folder names into dates (`:157`). Branded-product
check is "seller's first word appears in the product name" (`weekly_breakout_report.py:455-456`).

**Duplicated logic [V].** Three response caches (`kalodata_core.cached/get`, `weekly.fetch`, `weekly.recent_comments`);
two OpenRouter tag calls with their own retry loops (`video_pilot.py:~220-243`, `video_elements.py:59-80`); two scene-cut
detectors (`analyze_topads.py:26`, `video_pilot.py:163`); three Whisper loaders; per-product contribution code in both
`explain_breakouts.py:93-97` and `weekly_breakout_report.py:142-149`; economics constants in `test_product_economics.py`
vs `config/hub.json`.

**Other.**
- Path roots are mixed: `kalodata*.py` use `hub_env.HUB_ROOT` (honours `EMBERCLOVE_HUB_ROOT` for tests);
  `train_product_model.py:28`, `pilot_model.py:22`, `video_audio.py:23` use `__file__` and ignore it.
- Writers open `kalodata.db` read-write even for reads (`kalodata_core.py:85,93`, `pilot_model.py:35`,
  `video_pilot.py:263`); training/reporting correctly use `mode=ro`.
- `video_pilot.py` downloads (possibly paying 0.5 credit) before checking "already processed" (`:271-286`, only when the
  local MP4 is missing) and always records `TAG_MODEL` even if OpenRouter fell back to a backup model (`:305`).
- `seller_names()` builds one `IN (?,?,…)` with every candidate id (`weekly_breakout_report.py:115-121`); ~27k ids today,
  SQLite's limit is 32,766 — will fail as lists deepen **[I]**.
- No tests for any market script (`def test_` only in `scripts/studio/`) **[V]**.
- Cross-cut for the model auditor: `--scan` labels a rolling last-30-days pull as the current calendar month
  (`:82-83`) and fills gap months with no data (`:86-93`), so lag features go missing after a skipped month **[I]**.

---

## 6. Reporting

**Flow (`weekly_breakout_report.py`).** Load core panel (`tp.load/build`) → load or train breakout models (cache) →
optional `--scan` (paid) → score risers outside top 500 → filters → per pick: contributions, paid enrichment (detail
0.1, top videos 0.1, comments 1.0 unless ≤28 days old), live link check against tiktok.com (`:200-206`), sparkline PNG
→ PDF (reportlab, Arial from `C:/Windows/Fonts`), CSV, `weekly/history.csv` (same-day rerun replaces that day's rows,
`:466-468`) → final `credit/balance` call (`:490`).

**Dependencies [V].** Python 3.13.0; pandas 2.2.3, numpy 2.1.3, scikit-learn 1.7.0, joblib 1.5.1, scipy 1.15.1,
reportlab 4.2.5, PyMuPDF 1.24.14 (installed; not imported by the report), matplotlib 3.10.0, OpenCV 4.12.0,
faster-whisper 1.2.1, transformers 5.16.1, torch 2.14 CPU. `imageio_ffmpeg` and `yt_dlp` exist **only in the user
site-packages**, so `python -I` (the house style) cannot import them — `video_pilot.py`/`analyze_topads.py` must run
without `-I`. Python 3.10 and 3.12 are also installed and lack scikit-learn. No `requirements.txt`. Models were pickled
with scikit-learn 1.7.0; an upgrade can break `joblib.load` **[I]**.

**Reproducibility.** A report cannot be regenerated offline: even without `--scan` it re-pays enrichment on any later
day (detail/videos cached same-day only), makes live HTTP link checks, and calls `balance`. The intermediate scores and
enrichment are not saved, only the PDF/CSV. One report exists (`weekly_breakouts_2026-10-26.pdf`, Sep data).

---

## 7. Scheduling and operations

- **Scheduled:** nothing for the market engine (finding 7). Hub pattern available: Windows tasks running
  `python -I scripts\…` from the Hub folder (backup task, last result 0), and `analytics.sync_runs` for job health
  (jobs today: shopify, tiktok, facebook, snapshots, content, ads:*) **[V]**.
- **Unattended run today:** possible in principle (no Claude dependency in the Kalodata scripts; secrets read from the
  registry by `hub_env._read_user_env`), but no wrapper, no log file, no failure alert, no lock against two concurrent
  runs, and the weekly report has no `--scan` default. The video tools need OpenRouter and the user site-packages.
- **Operations docs:** `DASHBOARD_OPERATIONS.md:45` lists the Kalodata key only; no runbook for the engine.

## 8. Security

- Keys come only from user env vars via `hub_env.get_secret` (`kalodata_api`, `openrouter_api`); no market script reads
  `os.environ` directly **[V]**.
- Raw files store request body and response, **not headers**, so the key is not on disk (`kalodata.py:55`) **[V]**.
- Pattern scan of `scripts/`, `research/`, `docs/`, `config/`, `log.md` for OpenRouter/PostZen/Shopify token shapes and
  `secret-key`/`Bearer` literals: **no matches** (file names only were printed) **[V]**.
- `raw/pilot_videos/url_*.json` hold Kalodata signed video URLs (5-minute expiry) — harmless.
- The weekly report fetches tiktok.com pages with a browser user agent; low risk, but it is an external call in an
  otherwise offline "regenerate" path.

## 9. Integration with the rest of the Hub

| Hub piece | Today | Recommendation |
|---|---|---|
| Dashboard (6 sections) | Nothing from the engine; Intelligence page is rule-based findings | Show market outputs on the **existing Intelligence page** (a "Market" tab: latest breakout picks, credit balance/spend, data freshness). No second dashboard or PDF-only channel |
| `studio/analytics.db` + `sync_runs` | Not used | Record each engine run as a `sync_runs` job (`market:scan`, `market:weekly`) so Ops/Health shows freshness and failures. Keep the 400 MB Kalodata data in its own DB; put only small outputs (picks, scores summary, run records) in analytics.db or expose via `/data` |
| Cost ledger (`generation_costs`, `data/costs/generation_costs.csv`) | No Kalodata rows; video-study OpenRouter tagging ($0.24) absent | Write one ledger row per paid Kalodata call/run (credits and USD at $0.10) and per OpenRouter tagging call — the Phase F plan already names Kalodata (`DASHBOARD_IMPLEMENTATION_PLAN.md:63`) |
| `profit.py` / config economics | `pricing_study.py` uses separate constants | Any product-economics in the engine (store-candidate margin, allowable CPA) calls `profit.py`/`profitability_model.ship` and `config economics`. Do not write new economics |
| Shopify (`shopify_api.py`, analytics `products`) | No mapping between Kalodata product ids and store products | Add a small mapping table (Shopify product ↔ Kalodata look-alike ids) so market signals can feed Content Studio Phase G product ranking |
| Content Studio | Video-study findings reach it only through docs/prompts | Feed study features (`video_features`/`video_elements`) to Content Studio's features table later via a stable export, not by sharing the DB |
| Scheduler | None | Windows task + `.cmd`, same pattern as the backup task; no Claude-dependent scheduling for data pulls |
| Backups / git | Not covered | Add `research/kalodata/kalodata.db` (SQLite backup API, like studio DBs) and `raw/` to the mirror set; consider tracking small reports/manifests in git |

## 10. Performance

- Query plans [V]: training load `SCAN p` + `SEARCH u USING INTEGER PRIMARY KEY` — 257,600 rows in 0.89 s; video pairs
  `SCAN v USING INDEX ix_videos_key` + temp B-tree for DISTINCT — 28,764 rows in 1.16 s; detail load 1,003 rows ~0 s;
  `seller_names` uses `ix_products_key`. Full scans happen because the filter is `pulls.name LIKE …` (no column for
  list/month/category). Adding those columns and an index on `pulls(list, month)` would make the filters indexed, but
  at this size it is not needed.
- Journal mode `delete`, page size 4096, 101,507 pages, 0 free; `integrity_check` ok [V].
- **SQLite is adequate** for years at the current pace (~30–45 credits/month ≈ 3–5k rows). The heavy cost is pandas
  feature building and model training in Python, not the database **[I: training not run in this audit, it writes
  model files]**.

---

## 11. Prioritized recommendations

| # | Recommendation | Evidence | Effort |
|---|---|---|---|
| 1 | **Back up the market data now**: add `kalodata.db` (online backup) and `research/kalodata/raw`, models, reports to `backup_hub.py`; first copy before any Phase B change | Finding 1; `backup_hub.py:21-24`; `.gitignore:22` | S |
| 2 | **Fix the stale-reload bug**: unique raw names per attempt (timestamp suffix) or reload when file checksum changes; then re-sync the 6 stale weekly comment pulls from raw (free) | Finding 2; `kalodata.py:53-60`, `kalodata_db.py:72-73` | S |
| 3 | **Credit ledger**: one table (`kalodata_calls`: time, run id, endpoint, request hash, credits charged, http/code/message, raw file, sha256) written by `call()`; balance snapshot at run start/end; daily/total reconciliation; mirror USD rows into the Hub cost ledger | Finding 3 | M |
| 4 | **Request-level cache in the client**: before paying, look up the request hash (endpoint + all params) in the ledger/raw; per-endpoint freshness (monthly ranks = forever, last30Day = same day, comments = 28 days); remove the three ad-hoc caches | Finding 4; 12 duplicate files | M |
| 5 | **Richer `pulls` + no name parsing**: columns `requested_at`, `month`, `category_id`, `list`, `page`, `credits`, `checksum`, `run_id`, filled from request params (backfill from `filters`/`date_range` and file mtimes); schema version | Finding 5; four parsers | M |
| 6 | **Reproducible runs**: a manifest per model/report (pull ids or data cut-off, code commit, package versions, params); months derived from data, not literals; weekly cache keyed on data hash; save scored candidates and enrichment so a report rebuilds offline | Finding 6 | M |
| 7 | **Separate derived tables**: move `video_features/elements/audio` into `research/kalodata/analysis.db` (or Content Studio) so `kalodata.db` is rebuildable from `raw/` | §4 | S |
| 8 | **Schedule it the Hub way**: Windows task → `.cmd` → weekly `--scan` with a credit cap and lock file, log to `logs/`, `sync_runs` row, alert on failure; owner approves the monthly credit budget | Finding 7 | M |
| 9 | **One package for the engine** (`scripts/market/`: client, ledger, store, features, scoring, report, video helpers) replacing duplicated cut/tag/whisper/contribution code; retire `pilot_model.py`, generalize `explain_breakouts.py` | §5 | L |
| 10 | **Plug into the Hub**: Intelligence-page Market tab via `/data`; economics via `profit.py`; Shopify ↔ Kalodata mapping; config for categories/filters in `config/hub.json` | Finding 8; §9 | M |
| 11 | **Environment**: `requirements-market.txt` with pinned versions; install `imageio-ffmpeg`/`yt-dlp` where `-I` sees them (or drop `-I` for video tools explicitly) | §6 | S |
| 12 | **Tests**: loader idempotency/reload, ledger reconciliation, name-free parsing, cache freshness, report rebuild offline — all with fixture JSON, no API | §5 | M |
| 13 | Turn the inline-session analyses (seasonality, AI-by-category, video links) into scripts when they are next refreshed | Finding 6 | M |

**Keep unchanged:** the `Budget` stop-before-overspend rule; raw-response-first recording (raw survives a DB failure);
`kalodata_core` resumability; keeping full JSON per record; `mode=ro` reads in training/reporting; the PDF layout and
"why the model picked it" explanation format; secrets via `hub_env`.

**Blocking later phases:** (1) backups before any migration; (2) the stale-reload fix and a ledger before more paid pulls,
otherwise new spend is again unreconcilable; (3) the owner must set a monthly Kalodata credit budget before a scheduled
`--scan` exists; (4) model retraining needs the data-snapshot/manifest step first, or results will not be comparable
with model v1.
