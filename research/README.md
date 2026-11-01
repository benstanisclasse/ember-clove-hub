# research/

Market research for Ember & Clove: Kalodata (TikTok Shop US) data and studies, Meta Ad Library and TikTok Top Ads
notes. Plans and audits: `docs/MARKET_ENGINE_V2_ROADMAP.md` and the `docs/MARKET_*` audits.

## What is where

| Path | Contents | Git | Backup |
|---|---|---|---|
| `kalodata/kalodata.db` | Every raw response loaded into SQLite (`scripts/kalodata_db.py`) | no (size) | `backups/research_db/`, newest 4 copies |
| `kalodata/raw/` | Raw paid API responses, the record of every call | no | `backups/research_mirror/` (append-only) |
| `kalodata/model_*/` | Model outputs (panels, scores, joblib) | no | mirror |
| `kalodata/audit/`, `*.md`, small CSVs | Reports, audits, evaluation scripts | yes | mirror + daily |
| `kalodata/videos/`, `tiktok/ads/` | Transcripts, tags and frame sheets of studied videos | no | mirror |
| `api_capability_audit/` | Kalodata + CJ API capability audit (2026-10-31): endpoint/field catalogues, costs, gap analysis, proposed architecture. Start at `API_CAPABILITY_REPORT.md` | yes | mirror + daily |
| `winning_products/` | Winning-product research programme (2026-10-31): phase reports, pre-registered definitions and hypotheses, experiment registry. Start at `PHASE_A_DATA_INTEGRITY.md` | yes | mirror + daily |

## Rules

- **Third-party media:** videos are research material only. Keep downloaded video/audio for at most 30 days, then keep
  only derived data (transcripts, tags, frame sheets, logs). On 2026-10-28 all 280 stored videos (1.56 GB) were moved
  to the Recycle Bin (owner decision D2).
- **Personal data:** no buyer, commenter or creator personal details beyond what a public video link needs. Buyer
  identities (`review_user`) are stripped before raw responses are written or loaded (owner decision D2).
- **Raw files are the record:** don't edit them by hand. The only rewrite so far was the D2 redaction
  (`kalodata_db.py redact-raw`), which kept each file's modified time.
- **Paid calls:** Kalodata credits are paid. Check the database and `raw/` before any new call; stay within the
  owner's monthly budget (D1: ~30 credits/month for the refresh, a weekly scan only on request).
- **Facts vs estimates:** Kalodata revenue and units are third-party estimates, not audited sales. Model scores are
  rankings unless a calibration test says otherwise.
