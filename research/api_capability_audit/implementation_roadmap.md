# Implementation roadmap (recommendation, 2026-10-31)

Nothing in this roadmap has been started. Items marked **[owner]** need an explicit owner decision or approval first.
They spend credits, change an account or store setting, or start a schedule. Costs: Kalodata credits (≈ $0.10 each) and
CJ points (a free daily quota).

## Phase 0: free wins from data we already paid for (no API calls)

| # | Work | Why | Effort |
|---|---|---|---|
| 0.1 | **Break out fields hidden in `raw_json`:** `product/detail.product_description` (text + image URIs), `video/rank.creator_debut`, `comment/insight.original_comments` → review rows, `cached_at`, `key_review_id` | We paid for these; they're unusable as JSON blobs. Reviews give raw complaint text for 24 products; descriptions are the best text for CJ matching | small |
| 0.2 | **Keep raw CJ responses** (`research/cj/raw/<date>/…json`) for every CJ call, as Kalodata already does | Today only 18-25 hand-picked fields survive and variant-level data is lost | small |
| 0.3 | **Credit reconciliation:** call `credit/logs` (free) after each paid run, store it in a ledger and compare with the Budget estimate | The log shows ~150 more 0.1 charges than successful responses: failed and unsaved calls are billed | small |
| 0.4 | Load the endpoint catalogue (`kalodata_endpoints.json`, `cj_endpoints.json`) into code as the **single cost table**, replacing the literals in each caller | Costs are currently typed per call site (`MARKET_ENGINE_AUDIT.md` §3) | small |

## Phase 1: cheap verification **[owner: ~0.5 credits]**

| # | Test | Cost | Answers |
|---|---|---|---|
| 1.1 | `product/detail` with `need_extra: true, need_image: 1` for one known product | 0.1 | Does `revenue_trend` (a daily series) fill? Does `master_image_url` fill? If yes, every future detail call gets both at no extra cost |
| 1.2 | `product/rank` with `need_category`-style options and `need_image: 1`, 1 page of 10 | 0.1 | Whether `pri/sec/ter_category` and images come back on rank rows |
| 1.3 | One page each of `shop/rank` and `creator/rank` (10 rows) | 0.2 | Are the never-used endpoint families enabled for our key? The docs hint at per-API enablement |
| 1.4 | `product/comments` page 1 for one product | 0.01 | Raw review shape and depth vs what the insight bundles |
| 1.5 | CJ: `get_logistics_timeliness` once, on its own (1/s limit) | 0 | Delivery-time data beyond freight quotes |

## Phase 2: foundation (rebuildable store)

| # | Work | Notes |
|---|---|---|
| 2.1 | Build `research/intel/intel.db` per `integration_architecture.md`, with a loader that rebuilds from raw files | No change to `kalodata.db`. Back up first (`scripts/backup_hub.py`) anyway |
| 2.2 | `api_call` provenance and `data_freshness` view; record runs in `analytics.db` `sync_runs` so Ops/Health shows them | |
| 2.3 | **Seed `match_candidate`** from the 145 existing CJ match records (`match`, `match_note`, pid, SPU) and the photo-check CSVs | Keeps past accept/reject decisions |
| 2.4 | CJ snapshot collector (free): for every accepted match, weekly variant prices, inventory split, and freight for the chosen method | Price and stock history only exist if we snapshot. Respect the 1/s logistics limit |

## Phase 3: richer market data **[owner: credit envelope]**

Per `automation_opportunities.md`. Recommended order and monthly cost:
1. A1 monthly core refresh (30, already budgeted)
2. A3 category snapshot + `category/detail` for niche subcats (~2.3)
3. A2 new-product radar (~1.6)
4. A7/A8 reviews, attributes and images for candidates only (~1-5 per batch)
5. A6 watchlist detail with daily trend, if 1.1 confirms it (~16)
6. A4/A5 shops and creators in our niche (~2.8)

Total: **~60 credits/month (≈ $6)** at full scope vs 30 today.

## Phase 4: matching and economics

| # | Work |
|---|---|
| 4.1 | Matching pipeline: CJ keyword recall → evidence scoring (title, attributes from `product/analysis`, image hash, price ratio, weight) → human accept/reject |
| 4.2 | Per-variant **landed cost** (CJ price + chosen freight + Hub fee model). Clearly labelled **DDU: duties not included** |
| 4.3 | Margin-compression and stock-out alerts from the snapshots |
| 4.4 | Prediction ledger: store monthly opportunity scores, fill outcomes the next month |

## Owner decisions this audit surfaces

1. **Kalodata budget:** keep ~30 credits/month, or move to ~60 to add categories, reviews, shops and creators? The balance is 470.9.
2. **Approve the ~0.5-credit verification tests** in Phase 1.
3. **CJ access:** keep only the MCP connector, whose URL token silently expires, or add a CJ REST API key as a Windows user
   environment variable (Hub secret) for scheduled collectors?
4. **CJ suspension rule:** the docs say 30 days with no CJ transactions suspends API access. We have no CJ orders. Watch for error `1600014`.
5. **CJ Shopify-type shop shows status 4 / "please reauthorize"**: reauthorize it in CJ or leave it? This is a store setting.
6. **CJ account level:** image search needs Level 3+. Check our level before planning on image matching.
7. **CJ webhooks:** they need a public HTTPS receiver. Enabling them is an account change. Polling weekly is fine until then.
8. **Creator contact fields** (`creator/detail` returns email/WhatsApp/etc.): exclude them, as the default, unless there's an approved outreach use.
