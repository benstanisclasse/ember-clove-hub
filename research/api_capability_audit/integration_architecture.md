# Unified Kalodata + CJ data architecture (proposal, 2026-10-31)

Status: **proposal only.** Nothing here has been built, and no existing database was changed. `research/kalodata/kalodata.db`
and `studio/studio.db` / `studio/analytics.db` stay as they are.

## 1. Principles

1. **Raw responses are the record.** Every paid or live call already writes a raw JSON file (Kalodata: `research/kalodata/raw/`).
   CJ calls should do the same (`research/cj/raw/`). The new database is a *derived* store that can be rebuilt from the raw
   files at any time, so its schema can change without a risky migration.
2. **Snapshots, never overwrites.** Anything that changes over time (sales, prices, stock, freight, followers) goes in an
   append-only observation table keyed by *what*, *for which period*, and *when we saw it*. Current-state views are
   computed from the latest observation.
3. **Entities separate from observations.** Stable attributes (name, category, launch date, shop) live in an entity table
   with `first_seen` / `last_seen`. Period metrics live in `*_period` tables.
4. **No shared product id across providers.** Kalodata products and CJ products link only through explicit
   `match_candidate` rows with evidence, confidence and a decision.
5. **Provenance on every row.** Each observation carries `call_id`, which leads to the endpoint, the request, the raw file
   hash, the credit cost and the time.
6. **Estimates are labelled.** Kalodata revenue and units are third-party estimates. CJ "suggested sell price" is
   unreliable (two tools disagree, see `_work/cj_mcp_notes.md`). Column comments and views say so.
7. **Personal data stays out.** No buyer identities (already stripped), and no creator contact fields (`creator_contact_*`
   from `creator/detail`) unless the owner approves a specific outreach use. CJ account, order and address data is not
   copied into research tables.

Proposed file: `research/intel/intel.db` (SQLite, WAL), built by a loader in the style of `scripts/kalodata_db.py`. It is
small enough for SQLite. The current 415 MB mostly holds duplicated `raw_json`, so keep raw JSON on disk, not in rows.

## 2. Entity-relationship overview

```
                 api_call (provenance, cost) ──< every *_obs / *_period row (call_id)
                                │
 kd_category ──< kd_product >── kd_shop            cj_category ──< cj_product ──< cj_variant
      │             │  │  │                                        │                │
      │             │  │  └──< kd_product_period (month/window metrics)            ├──< cj_variant_price_obs
      │             │  ├──< kd_product_media / kd_product_attribute (analysis)      ├──< cj_inventory_obs >── cj_warehouse
      │             │  ├──< kd_review ; kd_insight ──< kd_insight_point              ├──< cj_freight_quote >── cj_logistic_method
      │             │  └──< kd_rank_obs (list membership + position)                └──< cj_media
      │             │
      │   kd_video_product >── kd_video >── kd_creator ──< kd_creator_period
      │   kd_live_product  >── kd_live  >── kd_creator
      └──< kd_category_period
                                       match_candidate (kd_product ⇄ cj_product, evidence, status)
                                              │ accepted
                                       landed_cost (cj_variant + price_obs + freight_quote + fees)
                                              │
                                       opportunity_score (model run) ──> research_run / prediction
```

## 3. Tables (DDL sketch)

### 3.1 API operations

```sql
CREATE TABLE endpoint_catalog (            -- loaded from kalodata_endpoints.json / cj_endpoints.json
  provider TEXT, endpoint TEXT, method TEXT, module TEXT, access_status TEXT, safety_class TEXT,
  credit_cost REAL, cost_unit TEXT, rate_limit TEXT, doc_url TEXT, catalog_version TEXT,
  PRIMARY KEY (provider, endpoint));

CREATE TABLE api_call (
  call_id INTEGER PRIMARY KEY, provider TEXT NOT NULL, endpoint TEXT NOT NULL, request_json TEXT NOT NULL,
  request_hash TEXT NOT NULL,              -- sha256 of canonical request: dedupe and cache key
  called_at TEXT NOT NULL, http_status INTEGER, success INTEGER, error_code TEXT, error_message TEXT,
  n_records INTEGER, credits_expected REAL, cached_flag INTEGER, latency_ms INTEGER,
  raw_path TEXT, raw_sha256 TEXT, run_tag TEXT,         -- e.g. market:monthly-2026-10
  FOREIGN KEY (provider, endpoint) REFERENCES endpoint_catalog);
CREATE INDEX ix_call_hash ON api_call(provider, endpoint, request_hash, called_at);

CREATE TABLE credit_ledger (               -- from Kalodata credit/logs (free): truth for spend
  provider TEXT, charged_at TEXT, source_type TEXT, credits REAL, matched_call_id INTEGER,
  PRIMARY KEY (provider, charged_at, source_type, credits));

CREATE TABLE refresh_policy (              -- what to refresh, how often, budget
  dataset TEXT PRIMARY KEY, provider TEXT, endpoint TEXT, cadence TEXT, max_credits_per_run REAL,
  enabled INTEGER DEFAULT 0, approved_by TEXT, approved_quote TEXT);

CREATE VIEW data_freshness AS              -- newest successful observation per dataset
  SELECT provider, endpoint, MAX(called_at) AS last_ok, COUNT(*) AS calls
  FROM api_call WHERE success = 1 GROUP BY provider, endpoint;
```

### 3.2 Market intelligence (Kalodata)

`period_key` is `YYYY-MM` for months, or `last30Day@2026-10-31` for rolling windows (window + observation date).
`region` is `US` for now.

```sql
CREATE TABLE kd_category (category_id TEXT PRIMARY KEY, name TEXT, level INTEGER, parent_id TEXT,
  first_seen TEXT, last_seen TEXT);
CREATE TABLE kd_category_period (category_id TEXT, region TEXT, period_key TEXT, call_id INTEGER,
  revenue REAL, units INTEGER, growth_pct REAL, top3_shop_share REAL, avg_revenue REAL,
  shop_number INTEGER, active_product_number INTEGER, video_revenue REAL, live_revenue REAL,
  affiliate_revenue REAL, self_operate_revenue REAL, mall_revenue REAL, revenue_trend_json TEXT,
  PRIMARY KEY (category_id, region, period_key, call_id));

CREATE TABLE kd_shop (shop_id TEXT PRIMARY KEY, name TEXT, shop_type TEXT, seller_type TEXT, region TEXT,
  first_seen TEXT, last_seen TEXT);
CREATE TABLE kd_shop_period (shop_id TEXT, region TEXT, period_key TEXT, call_id INTEGER,
  revenue REAL, units INTEGER, growth_pct REAL, unit_price REAL, on_sale_products INTEGER,
  affiliate_revenue REAL, self_revenue REAL, mall_revenue REAL, creator_number INTEGER,
  video_number INTEGER, live_number INTEGER, top3_product_ids TEXT, revenue_trend_json TEXT,
  PRIMARY KEY (shop_id, region, period_key, call_id));

CREATE TABLE kd_product (product_id TEXT PRIMARY KEY, name TEXT, shop_id TEXT REFERENCES kd_shop,
  cat1 TEXT, cat2 TEXT, cat3 TEXT, launch_date TEXT, delivery_type TEXT, sku_count INTEGER,
  first_seen TEXT, last_seen TEXT);
CREATE TABLE kd_product_period (product_id TEXT, region TEXT, period_key TEXT, call_id INTEGER,
  source TEXT,                             -- 'rank' or 'detail' (detail has more fields)
  revenue REAL, units INTEGER, unit_price REAL, min_price REAL, max_price REAL, growth_pct REAL,
  commission_pct REAL, video_revenue REAL, live_revenue REAL, showcase_revenue REAL,
  creator_number INTEGER, video_number INTEGER, live_number INTEGER, review_count INTEGER,
  revenue_trend_json TEXT,                 -- daily series when need_extra returns it (to be verified)
  PRIMARY KEY (product_id, region, period_key, source, call_id));
CREATE INDEX ix_kpp_period ON kd_product_period(period_key, product_id);

CREATE TABLE kd_rank_obs (                 -- membership + position in a ranked list
  call_id INTEGER, list_kind TEXT, filters_hash TEXT, period_key TEXT, position INTEGER,
  entity_type TEXT, entity_id TEXT, PRIMARY KEY (call_id, position));
CREATE INDEX ix_rank_entity ON kd_rank_obs(entity_type, entity_id, period_key);

CREATE TABLE kd_product_media (product_id TEXT, kind TEXT, url TEXT, expires_at TEXT, local_path TEXT,
  call_id INTEGER, PRIMARY KEY (product_id, kind, url));   -- images expire: store hashes/thumbnails if kept
CREATE TABLE kd_product_attribute (product_id TEXT, key TEXT, value TEXT, region TEXT, language TEXT,
  call_id INTEGER, PRIMARY KEY (product_id, key, call_id));  -- product/analysis attributes
CREATE TABLE kd_product_highlight (product_id TEXT, key_word TEXT, text TEXT, call_id INTEGER);

CREATE TABLE kd_review (review_id TEXT PRIMARY KEY, product_id TEXT, sku_id TEXT, sku_spec TEXT,
  rating INTEGER, text TEXT, review_ts TEXT, source_name TEXT, country TEXT, has_media INTEGER,
  first_call_id INTEGER);                  -- no buyer identity, ever
CREATE TABLE kd_insight (product_id TEXT, country TEXT, cached_at TEXT, summary TEXT, call_id INTEGER,
  PRIMARY KEY (product_id, country, cached_at));
CREATE TABLE kd_insight_point (product_id TEXT, cached_at TEXT, kind TEXT,  -- pain / positive / scenario
  point TEXT, mentions INTEGER, key_review_id TEXT, PRIMARY KEY (product_id, cached_at, kind, point));

CREATE TABLE kd_creator (creator_id TEXT PRIMARY KEY, handle TEXT, nickname TEXT, region TEXT,
  creator_type TEXT, belonged_shop_id TEXT, first_seen TEXT, last_seen TEXT);  -- no contact fields
CREATE TABLE kd_creator_period (creator_id TEXT, region TEXT, period_key TEXT, call_id INTEGER,
  followers INTEGER, new_followers INTEGER, revenue REAL, units INTEGER, video_revenue REAL,
  live_revenue REAL, video_views INTEGER, video_gpm REAL, live_gpm REAL, video_number INTEGER,
  live_number INTEGER, product_number INTEGER, shop_number INTEGER, top3_product_ids TEXT,
  PRIMARY KEY (creator_id, region, period_key, call_id));

CREATE TABLE kd_video (video_id TEXT PRIMARY KEY, creator_id TEXT REFERENCES kd_creator, caption TEXT,
  publish_ts TEXT, duration_s REAL, ai_video INTEGER, first_seen TEXT, last_seen TEXT);
CREATE TABLE kd_video_period (video_id TEXT, region TEXT, period_key TEXT, call_id INTEGER,
  revenue REAL, units INTEGER, views INTEGER, likes INTEGER, shares INTEGER, comments INTEGER,
  growth_pct REAL, ad INTEGER, ads_roas REAL, ad_revenue_share REAL, ad_view_share REAL,
  ads_views INTEGER, ad_cpa REAL, ads_period INTEGER, gpm REAL, PRIMARY KEY (video_id, region, period_key, call_id));
CREATE TABLE kd_video_product (video_id TEXT, product_id TEXT, period_key TEXT, call_id INTEGER,
  PRIMARY KEY (video_id, product_id, period_key));   -- from video/rank filtered by product_id
                                                     -- or product/rank filtered by video_id

CREATE TABLE kd_live (live_id TEXT PRIMARY KEY, creator_id TEXT, title TEXT, start_ts TEXT, end_ts TEXT,
  duration_s INTEGER, record_type TEXT);
CREATE TABLE kd_live_period (live_id TEXT, period_key TEXT, call_id INTEGER, revenue REAL, unit_price REAL,
  views INTEGER, viewers INTEGER, gpm REAL, product_number INTEGER, top3_product_ids TEXT,
  PRIMARY KEY (live_id, period_key, call_id));
CREATE TABLE kd_live_product (live_id TEXT, product_id TEXT, call_id INTEGER, PRIMARY KEY (live_id, product_id));

-- Derived video analysis keeps its current shape, moved or attached, never mixed with API columns:
-- video_features, video_elements, video_audio (origin = hub_derived, model + version on every row).
```

### 3.3 Supplier intelligence (CJ)

```sql
CREATE TABLE cj_category (category_id TEXT PRIMARY KEY, name TEXT, level INTEGER, parent_id TEXT);
CREATE TABLE cj_product (pid TEXT PRIMARY KEY, spu TEXT, name_en TEXT, name_cn TEXT, category_id TEXT,
  material TEXT, packing TEXT, product_type TEXT, logistics_props TEXT,   -- productProEnSet, needed for freight
  customs_code TEXT, customs_name TEXT, has_video INTEGER, url TEXT, first_seen TEXT, last_seen TEXT);
CREATE TABLE cj_product_obs (pid TEXT, observed_at TEXT, call_id INTEGER, status TEXT, listed_num INTEGER,
  sell_price_text TEXT, warehouse_inventory_num INTEGER, verified_warehouse INTEGER,
  PRIMARY KEY (pid, observed_at));
CREATE TABLE cj_variant (vid TEXT PRIMARY KEY, pid TEXT REFERENCES cj_product, sku TEXT, name TEXT,
  key_attrs TEXT, color TEXT, size TEXT, weight_g REAL, pack_weight_g REAL, length REAL, width REAL,
  height REAL, image_url TEXT, barcode TEXT, first_seen TEXT, last_seen TEXT);
CREATE TABLE cj_variant_price_obs (vid TEXT, observed_at TEXT, call_id INTEGER, cost_usd REAL,
  currency TEXT DEFAULT 'USD', min_qty INTEGER DEFAULT 1, PRIMARY KEY (vid, observed_at, min_qty));
CREATE TABLE cj_warehouse (warehouse_id TEXT PRIMARY KEY, country TEXT, name TEXT, kind TEXT);  -- CJ vs factory
CREATE TABLE cj_inventory_obs (vid TEXT, warehouse_id TEXT, country TEXT, observed_at TEXT, call_id INTEGER,
  cj_qty INTEGER, factory_qty INTEGER, total_qty INTEGER, PRIMARY KEY (vid, warehouse_id, observed_at));
CREATE TABLE cj_logistic_method (name TEXT PRIMARY KEY, carrier TEXT, ddu INTEGER, notes TEXT);
CREATE TABLE cj_freight_quote (quote_id INTEGER PRIMARY KEY, vid TEXT, qty INTEGER, from_country TEXT,
  to_country TEXT, to_zip TEXT, method TEXT REFERENCES cj_logistic_method, total_usd REAL, base_usd REAL,
  markup_pct REAL, clearance_fee REAL, taxes_fee REAL, days_min INTEGER, days_max INTEGER,
  observed_at TEXT, call_id INTEGER, UNIQUE (vid, qty, from_country, to_country, to_zip, method, observed_at));
CREATE TABLE cj_review (review_id TEXT PRIMARY KEY, pid TEXT, rating INTEGER, text TEXT, review_ts TEXT,
  has_media INTEGER);                       -- no reviewer identity
CREATE TABLE cj_media (pid TEXT, vid TEXT, kind TEXT, url TEXT, PRIMARY KEY (pid, vid, kind, url));
CREATE TABLE quality_observation (pid TEXT, observed_at TEXT, source TEXT,  -- 'sample order', 'photo check', 'cj reviews'
  verdict TEXT, notes TEXT, PRIMARY KEY (pid, observed_at, source));
```

### 3.4 Research intelligence

```sql
CREATE TABLE match_candidate (
  kd_product_id TEXT REFERENCES kd_product, cj_pid TEXT REFERENCES cj_product, found_by TEXT,  -- keyword/image/manual
  query TEXT, score REAL, evidence_json TEXT,  -- title tokens, attribute overlap, image similarity, price ratio, weight
  status TEXT CHECK (status IN ('candidate','accepted','rejected','needs_sample')), decided_by TEXT,
  decided_at TEXT, reason TEXT, PRIMARY KEY (kd_product_id, cj_pid));
CREATE TABLE landed_cost (kd_product_id TEXT, cj_vid TEXT, computed_at TEXT, cost_usd REAL, freight_usd REAL,
  fees_usd REAL, landed_usd REAL, price_obs_at TEXT, quote_id INTEGER, assumptions_version TEXT,
  excludes TEXT DEFAULT 'import duties (DDU), returns, ads', PRIMARY KEY (kd_product_id, cj_vid, computed_at));
CREATE TABLE opportunity_score (kd_product_id TEXT, run_id TEXT, period_key TEXT, score REAL, rank INTEGER,
  inputs_json TEXT, PRIMARY KEY (kd_product_id, run_id));
CREATE TABLE prediction (run_id TEXT, entity_id TEXT, target TEXT, horizon TEXT, predicted REAL,
  made_at TEXT, outcome REAL, outcome_at TEXT, PRIMARY KEY (run_id, entity_id, target));
-- research_run: keep the existing research_runs table shape (it already records seed, commit, holdout use).
CREATE TABLE experiment (experiment_id TEXT PRIMARY KEY, question TEXT, design TEXT, started TEXT, ended TEXT,
  result TEXT, decision TEXT);
```

## 4. Matching Kalodata products to CJ (Phase 21)

There is no shared identifier, so matching is a pipeline that keeps several candidates per product:

1. **Recall.** CJ keyword search (`/product/listV2`) on a cleaned Kalodata title (brand words, emoji and sizes removed)
   plus the mapped CJ category. The quota list also names `/product/queryProductsByImage`. If the docs confirm it, add
   image search with the Kalodata main image (`need_image=1` or `product/images`, 0.01 credit).
2. **Evidence per candidate** (stored in `evidence_json`): title token overlap, attribute overlap
   (`product/analysis` attributes vs CJ material/size/color), price ratio (CJ cost vs TikTok ASP, expect 10-40%), weight
   plausibility, image similarity (perceptual hash / embedding), variant coverage (sizes/colors we need).
3. **Decision.** An automated score proposes. A person (or the photo check already in `data/kalo_cj/photo_check_*.csv`)
   accepts or rejects with a reason. Sample orders write `quality_observation`.
4. **History.** Rejected candidates stay, so a product is never re-matched to a known-bad SKU.

The 145 existing match records (`data/kalo_cj/*.jsonl`, `data/cj_compare/*.jsonl`) can seed `match_candidate` directly.
They already carry `match`, `match_note`, `cj_pid` and `cj_sku`.

## 5. Landed cost (and what it does not include)

`landed = CJ variant cost (latest price obs) + freight quote (chosen method, qty 1, to US) + per-order fees`

- **Included:** the variant price CJ returns and the CJ freight total. The freight total already contains the customs-clearance
  operation fee on lines that have one.
- **Not included:** import duties and taxes. CJ quotes are DDU, `taxesFee` is 0 or null, and carrier notes say the buyer pays
  duties. Returns, payment fees and ad cost are added by the Hub's existing per-order model
  (`scripts/pricing_study.py` / `config/hub.json` economics), not by CJ.
- Always compute per **variant**. The heaviest or dearest variant sets the worst case, as `cj_compare.py` already does.

## 6. Storage estimate

| Data | Rows/month (current scope) | Size |
|---|---|---|
| kd_product_period from 31 categories × 5 pages × 100 | ~15,500 | ~3 MB |
| kd_rank_obs | ~25,000 | ~2 MB |
| kd_video_period (31 cats × 3 pages + 125 products × 1 page) | ~22,000 | ~4 MB |
| reviews (100 products × 1 page) | 10,000 | ~5 MB |
| CJ snapshots (200 variants weekly: price + stock + 3 quotes) | ~4,000 | <1 MB |

Without `raw_json` duplicated in rows, a year fits in well under 200 MB. Raw files stay on disk and in the backup mirror.
