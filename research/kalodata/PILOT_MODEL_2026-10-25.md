# Pilot: can August numbers predict which products keep selling in September? (2026-10-25)

**Status: a pipeline test, not a decision tool.** It uses one category and one month-to-month step (500 products).
It shows the data is in the right shape and gives a first read on which signals matter. Re-run it on the full-year
pull before trusting it.

## Setup
- **Data:** Kalodata, US, Womenswear & Underwear (category 601152), top 500 products by sales for Aug 2026 and
  Sep 2026 (10 rank pulls, 1.0 credit; 0.8 left). Stored in `research/kalodata/kalodata.db` (pulls named
  `pilot_womenswear_2026-0X_pN`).
- **Question:** given a product's August figures, will it still be selling at least as much in September?
- **"Won"** = in September's top 500 **and** September sales ≥ August sales. Result: 172 of 500 won (34%).
  Of the rest, 201 dropped out of the top 500 (below ≈ $80K for the month) and 127 stayed in but sold less.
- **August features (12):** sales, units, price, growth vs July, commission rate, share of sales from videos, lives
  and the shop page, product age, SKU count, rank, and how many of the seller's products are in the top 500.
- **Models:** logistic regression and gradient-boosted trees, scored with 5-fold cross-validation (every product is
  predicted by a model that never saw it).
- **Code:** `scripts/pilot_model.py`. Outputs: `research/kalodata/pilot_model_2026-10-25/` (feature table with
  predictions, results).

## Results
| Method | AUC | Hit rate, top 25 picks | Top 50 | Top 100 |
|---|---|---|---|---|
| Random pick | 0.50 | 34% | 34% | 34% |
| Biggest sellers in August | 0.55 | 40% | 44% | 43% |
| Fastest growing in August (one column, no model) | 0.69 | 40% | 44% | 49% |
| **Logistic model (all 12 features)** | **0.70** | **48%** | **54%** | **56%** |
| Boosted trees | 0.68 | 48% | 52% | 52% |

AUC is the chance the model ranks a random winner above a random loser (0.5 = coin flip, 1.0 = perfect).
0.70 is a real but modest signal.

**What that means:** if you picked the model's top 50 products in August, about 27 kept growing in September,
against about 17 for a random 50. Only growth adds much on its own; the other features add a few points on top.

## What predicted a win
**Growth momentum is by far the strongest signal.** It accounts for most of the boosted trees' accuracy.

| August vs July | Won |
|---|---|
| Down more than 20% | 14% |
| Down 0–20% | 22% |
| Up 0–25% | 40% |
| Up 25–75% | 55% |
| Up more than 75% | 51% |

Weaker signals (small samples, treat as hints):
- **Price:** $30–45 products won most often (42%); under $20 won least (25%). Cheap products churn.
- **Sales channel:** products selling 50–95% through videos won more (≈ 40%) than those relying on lives or the shop
  page (22% when videos are under half), or on videos alone (32% when over 95%).
- **Rank:** the top 150 held up better (40–44%) than the rest (28–34%).
- **Age:** no clear pattern; products under 2 months old won slightly less (26%, only 31 of them).
- In the logistic model, sales and units point in opposite directions because they move together (sales ≈ units ×
  price). Read them together: at the same sales level, higher-priced products did better.

## Limits
- **One step, one category:** August → September may be a seasonal effect (back-to-school, early autumn), not a
  general rule. The full year gives 11 steps across 29 categories.
- **Top-500 only:** we can't see products below about $80K a month, which is where a new store's products sit. The
  growth-sorted pulls in the year plan (item C) cover risers further down.
- **No breadth signals yet:** creator count, video count and reviews come from product details (item E in the year
  plan). The winning-product definition says these should matter most, and they aren't in this pilot.
- **Kalodata sales are estimates.**

## What it tells us for the full build
- The data works for this: one row per product per month, a forward label, and the model runs end to end.
- Momentum is a strong baseline. Any fuller model has to beat "sort by growth" to be worth it (0.69 here).
- Worth adding: breadth (creators, videos), growth over 2–3 months rather than one, price band against our margin,
  and a longer horizon (still selling 2–3 months later), which matters more to us than one month.

## Other patterns in the same data (Sep 2026 top 500, Womenswear & Underwear)
Product types come from keyword matching on product names, so they're approximate.
- **Fall has arrived.** Change in total sales by type from Aug to Sep: jackets and coats ×2.0, dresses ×1.34,
  skirts ×2.4 (only 5 products); shorts ×0.57, tops and tees ×0.76.
- **The category is mostly basics.** Underwear, bras and leggings/pants make up 62% of sales. Dresses are 7%.
- **Price isn't a barrier.** $30–45 is the biggest band (33% of sales), and $45–60 products have the highest median
  sales per product ($142K). P01 at $52.99 and P02 at $44.99 sit in bands that sell.
- **Churn is high.** 201 of September's top 500 weren't in August's. 107 had launched since June and already took
  17% of sales, so new products break in fast and drop out fast.
- **No one dominates.** There are 243 sellers, and the top 10 have 25% of sales. Repeat winners run many products at
  once: Comfrt (20), FeelinGirl (14), Cider (13).
- **Video is the channel:** 90% of sales, against 9% from lives and 2% from the shop page.
- **Affiliate commission is 7–10%** (median 9%).
- **Recurring dress theme:** occasion dresses ("wedding guest", "going out") at $40–60 hold the top spots (Athena
  knit maxi, satin one-shoulder, mermaid maxi, tulle mini). A cable-knit long cardigan launched in July at $27.83
  made $213K in September.
