# Analytics and ML

The target is always **contribution profit from Shopify orders** (revenue minus tax, refunds, COGS,
shipping and fees, then minus ad spend), never what an ad platform claims.

| Time (store tz) | Job | Output |
|---|---|---|
| 02:30 nightly | `creative_metrics` | `creative_metrics` snapshots for each creative over 7 days, 30 days and lifetime |
| 03:30 Sundays | `creative_model` | a new LightGBM version in `ml_models`: `active` only if it passes the gates |
| 06:45 nightly | `budget_bandit` | a `bandit_runs` row, plus budget proposals in the approval queue |
| 08:00 nightly | `daily_report` | the Slack summary, including the bandit's recommendation |

## Creative metrics

Each snapshot has:
* **Hook rate:** 3-second views / impressions. TikTok uses its 2-second views; Google has none.
* **CTR**, and **CPA:** spend / Shopify-attributed orders.
* **Contribution profit per 1,000 spend:** the comparable "how good is this creative" number.

A creative is only judged once it has **≥ 50 spend or ≥ 2,000 impressions** in the window. Before
that it's `learning`. After that:
* `loser`: losing more than 100 per 1,000 spent.
* `winner`: profitable and in the top quartile of judged creatives.
* `neutral`: everything in between.

Snapshots are kept daily, so trends and the ML labels are reproducible.

## Budget bandit (Thompson sampling)

The bandit decides where the next dollar earns the most: the **marginal** ROI after spend per platform.
* **Regression:** with ≥ 14 spend days and enough day-to-day spend variation, the slope of daily
  contribution against daily spend, minus 1. This catches diminishing returns that averages hide.
* **Average:** otherwise, sum(contribution − spend) / sum(spend).
* **Prior only:** under 7 days or 100 spend, the hub knows nothing yet.

The estimate is shrunk toward a skeptical prior, N(0, ±50%), in proportion to how noisy it is. Then
4,000 Thompson draws per platform give *P(best)*. The target split is a 10% exploration floor per
platform, with the rest allocated by P(best). Moves are:
* **total-neutral:** budget only moves between platforms; the total never goes up,
* **within `max_budget_change_pct`** (with a 10% margin),
* **skipped under 5%.**

The bandit **only proposes**. Each budget-holding campaign or ad set gets a `budget_change` proposal
explaining the numbers, listed decreases first, so approve those before the increases. The proposals
pass the same guardrails as anything else. It needs at least two platforms with active budgets.

```bash
docker compose exec api python -m app.cli analytics bandit --dry-run   # see the recommendation, no proposals
docker compose exec api python -m app.cli analytics bandit             # create proposals now
```
From Claude: `get_budget_recommendation`, `propose_budget_reallocation`.

## Creative profit model (LightGBM)

* **Features:** one-hot creative traits (hook type, avatar, angle, length bucket, format, CTA, voiceover,
  kind), duration, and the creative's spend mix across platforms. Values seen fewer than 2 times become `other`.
* **Label:** lifetime contribution profit per 1,000 spend, for creatives with ≥ 100 lifetime spend.
  Samples are weighted by √spend.
* **Gates:** it trains only with **≥ 50 labeled creatives**, and is **activated** only if spend-weighted
  5-fold CV error is at least 5% better than "predict the average". Otherwise the attempt is recorded as
  `inactive` with the reason ("waiting for data: 23/50", or "traits don't explain profit yet").
* **When active:**
  * `generate_creatives` proposals show the predicted profit per 1,000 for each variant, so Claude can
    favour the hooks and angles that have paid off.
  * `get_model_status` shows CV error vs baseline and the top features.

```bash
docker compose exec api python -m app.cli analytics model status
docker compose exec api python -m app.cli analytics model train
docker compose exec api python -m app.cli analytics metrics --date 2026-10-17
```

Read trait insights and model output as **correlation**. Traits that always appear together (for example
one avatar used with one hook) can't be separated until briefs vary them independently. Rotating
`angles` × `hook_types` × `avatar_types` in briefs is what makes the model useful over time.
