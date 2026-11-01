# Phase F analysis plan: Kalodata demand × CJ sourcing and contribution economics (frozen 2026-11-01, before any Phase F CJ data is pulled)

**Labels:**
- Everything in Phase F is **descriptive, current-snapshot evidence** (CJ prices, stock and freight as of 2026-11-01).
  CJ has no price history, so nothing here says what margins were in the past.
- Kalodata's TikTok Shop figures are not our Shopify CAC. **No CAC is measured here.** Break-even and target CAC/ROAS
  are what the economics would *allow*, not what ads would cost.
- Hypothesis: H-F1 (descriptive).
- Cost: CJ API points only (free quota, 50,000/day). No orders, carts, payments, listings, product connections,
  sourcing requests, webhooks or settings. No Kalodata credits. CJ image search is **not** used (needs approval).

Two probe calls were made while writing this plan to learn the response formats. Both used the already-matched product
CJ 1942875414726483970 (an October picking-sheet item):
- variants and inventory;
- freight from CN (zip 10001) and from US (zip 99501).

They showed two things that shaped the design: freight from the US warehouse depends on the destination zip, and a
response lists 3-25 shipping methods. No candidate data was looked at.

## F1. Candidate list (Step 1: start from demand, not from the catalogue)

**Source:** the frozen September-2026 forward files from Phase C. These predictions were made with validated models
before Phase F and are not refitted here.

| Pool | Universe | Score | Per category |
|---|---|---|---|
| **A: retainers** | ranks 101-500 at 2026-09 (`forward_test_2026-09.csv`, primary universe) | `T4_M1`, the predicted chance of staying in the top 500 for 3 more months (Phase C: P@50 92% vs 62% for rank) | top 2 |
| **B: break-ins** | ranks 501-1,000 (`forward_test_band_2026-09.csv`) | `enter_M1`, the predicted chance of entering the top 500 (H-N2/H-N2b replicated) | top 1 |

**Eligibility rules**, applied before ranking:
- **Excluded categories:**

  | Category | Why excluded |
  |---|---|
  | Food & Beverages | ingestible, regulated |
  | Books, Magazines & Audio | media and IP |
  | Pre-Owned | single used items |
  | Collectibles | licensed cards and figures, not sourceable as the same item |

  That leaves 24 categories.
- **Excluded titles**, in any category, matching (case-insensitive): supplement, capsule, gummies, gummy, vitamin,
  probiotic, creatine, protein powder, collagen, tea, coffee, drink, oral, tablet (as in pills), medicine, cbd, nicotine,
  vape, ozempic. These are ingestible or regulated products the store won't sell.
- **ASP at least $15** (Sep 2026, revenue ÷ units). Below that, one order can't cover shipping and ads. Bundles would be
  a separate study.
- When a product is excluded, the next-highest-scoring product takes its place.

**Expected size:** 24 × 3 = **72 candidates**, saved as `_work/phase_f_candidates.csv` before any CJ call.

## F2. Matching (Step 2)

Existing saved matches are reused first. If a candidate's Kalodata id is in `data/kalo_cj/*` or
`research/kalodata/EASY_WINS_2026-10-31.csv`, its saved CJ pid is evaluated first. Alternatives are still searched.

**For each candidate:**
1. **Search.** Up to 2 keyword searches (`search_products`, 20 results each). The keywords are generic: the brand is
   removed and they describe function and form.
2. **Shortlist.** Up to 3 plausible results are opened (`get_product_detail`) and compared on function, form, material,
   dimensions/specs, colours, sizes, pack quantity and packaging.
3. **Pick.** The best one is chosen. Each considered alternative gets a short reason for rejection.

**Match confidence:**

| Score | Meaning |
|---|---|
| 3 | Same product: same function, form, material, key specs, pack size. Generic (unbranded) item. **Needs photo verification**, so no candidate can reach 3 in this phase (see below). |
| 2 | Close substitute: same function and form; differs in secondary details (colour range, minor design, sizes). |
| 1 | Same function, materially different (other form factor, material, pack size, quality tier). |
| 0 | No acceptable match on CJ. |

- **No photo comparison is possible here.** Kalodata images were not pulled (0.01 credit each, not approved for
  Phase F), so the comparison is title/description/spec only and **the maximum score is 2**.
- **Branded or licensed items** (a brand's own design, a character, a patented mechanism) get at most 1. A lookalike is
  not the same product, and selling it may infringe.
- Only matches scoring **≥ 2 go on to economics**. Products scoring 1 are reported as "substitute only", products scoring 0 as "not on CJ".

## F3. Variants (Step 3)

`get_product_variants` for the chosen pid. For every variant we record:
- vid, SKU, key (colour/size), weight, L/W/H;
- CJ sell price and CJ suggested sell price.

Economics are computed **per variant**. Product-level summaries report the min, median and max across the in-stock variants.

## F4. Inventory (Step 4)

`get_product_inventory` for the chosen pid, per variant and country:
- total stock, **CJ-owned** stock, **factory** stock, `verifiedWarehouse`.

**Fulfilment confidence**, per product, over the variants in stock:

| Level | Rule |
|---|---|
| **High** | CJ-owned stock ≥ 100 units in total **and** ≥ 50% of variants have CJ-owned stock |
| **Medium** | otherwise, total stock (CJ + factory) ≥ 500 units and ≥ 80% of variants have some stock |
| **Low** | anything else |

High reported factory stock is **not** treated as proof of fulfilment.

## F5. Freight (Step 5)

**Calls** (`calculate_freight`, quantity 1):
- **Variant:** the heaviest variant (conservative). The lightest is added only when it weighs < 70% of the heaviest.
- **Origins:** CN and, if the product has US stock, US.
- **Destination scenarios:**

  | Zip | City |
  |---|---|
  | 10001 | New York (East) |
  | 60601 | Chicago (Central) |
  | 90001 | Los Angeles (West) |

**Rate limit:** ≈ 1 logistics request per second (calls are sequential, with ≤ 6 collectors running at once).

**For each quote we record** method, delivery days (min-max), price, total postage fee, clearance fee, taxes fee, remote
fee and any error.

**Method chosen for the economics (frozen):**
- the **cheapest method whose upper delivery bound is ≤ 12 days**;
- if none qualifies, the cheapest overall, flagged "slow";
- the fastest method is also reported.

**Shipping cost per variant:**
- **Base:** the mean of the three zips.
- **Stress:** the maximum of the three.
- Remote zips (Alaska, Hawaii) are out of scope.

## F6. Contribution economics (Step 6)

Per variant, per origin. Price `P` = the product's **observed Kalodata Sep-2026 ASP** (the market price).

| Item | Base | Stress | Source / status |
|---|---|---|---|
| Product cost | CJ variant sell price | same | CJ, current |
| Shipping (we pay; free shipping to the customer, as the store does since 2026-10-29) | mean of 3 zips | max of 3 zips | CJ quote, DDU |
| Card processing | 2.9% × P + $0.30 | same | store model (`test_product_economics.py`) |
| Returns and refunds | 5% × P | 10% × P for apparel and shoes (Womenswear, Menswear, Kids', Muslim Fashion, Shoes; Phase E sizing complaints) | **assumption** (store model uses 5%) |
| Duties on China-origin parcels | as quoted (`taxesFee`), usually 0 | **+30% of product cost** | **assumption, unverified**: CJ quotes are DDU and the duty treatment is unclear |
| Other variable fulfilment costs | $0 known | — | none on record; flagged |

Definitions:
- **Contribution before ads (CBA)** = P − all of the above.
- **Break-even CAC** = CBA.
- **Target CAC** = CBA − **$10 target contribution profit** (the store's picking-sheet rule).
- **Break-even ROAS** = P / CBA, and **target ROAS** = P / target CAC. Neither is computed when its denominator is ≤ 0.
- **Shipping-inclusive cost** = product + freight + quoted fees. Duties are excluded unless the quote shows them. It
  is **never called "fully landed"**.

## F7. Price competitiveness (Step 7)

**Required price** for break-even ROAS 2.0 (ads can take half of revenue):

    P* = (cost + shipping + $0.30) / (1 − 0.5 − 0.029 − r)

Here r is the returns rate.

- **Premium needed** = P* / market ASP − 1.
- We **don't assume** we can charge above the market ASP. A product that needs a premium over ~10% is "price-constrained".

## Classification (H-F1)

Rules apply to the **median in-stock variant**, at the market ASP, base case, best origin. We also report the
**worst in-stock variant** and the stress case.

| Class | Rule |
|---|---|
| **Feasible** | match ≥ 2, fulfilment ≥ Medium, break-even ROAS ≤ 2.0 **and** target CAC > 0 |
| **Marginal** | match ≥ 2, fulfilment ≥ Medium, break-even ROAS between 2.0 and 3.0 |
| **Not viable** | break-even ROAS > 3.0 or CBA ≤ 0 |
| **Not sourceable** | match < 2, or fulfilment Low |

- The ROAS thresholds are **planning heuristics, not measured CAC**. For context only: the median Kalodata ad-video ROAS
  is 2.56 (Phase D), and our current test product needs 2.36.
- **H-F1** is answered as the shares of the 72 candidates in each class, overall and by pool and category, with Wilson 95% CIs.

## Descriptive questions (no significance claims; n is small)

- **Q1.** Does feasibility rise with ASP? (Spearman, ASP vs CBA, and the feasible share by ASP tercile.)
- **Q2.** Do pools A and B differ in feasibility?
- **Q3.** "Cheap supplier products are poorer matches." Is the CJ cost/ASP ratio related to match score?
- **Q4.** How far are product-level figures from variant-level ones? (The spread of CBA across variants; how often the
  cheapest variant overstates the median CBA by > $2.)
- **Q5.** US warehouse vs China: the share of candidates with US stock, and the delivery-days and cost difference.

## Data handling and quality checks

- CJ is reachable only through the MCP connector. There is no direct client, so collection runs through agents that
  write one JSON file per candidate under `_work/cj/`. The file keeps **field-complete extracts** of every response:
  - **search:** pid, name, price, listed count, warehouse flags;
  - **variants and inventory:** all fields listed above;
  - **freight:** all non-null fields of every method.

  Byte-for-byte raw responses are not kept. That is a deviation from "preserve raw", forced by MCP-only access, and recorded.
- **Transcription check:** after collection, 10% of candidates (seed 20261101, at least 7) are re-queried directly. Their
  variant prices, weights, CJ stock and one freight quote are compared with the saved files.
  - **Pass:** every price, weight and quote exact; stock within ±5% (stock moves).
  - **On failure:** the affected agent's batch is re-collected.
- **Points:** the rate-limit status is read before and after. The cap is 30,000 points for Phase F.
