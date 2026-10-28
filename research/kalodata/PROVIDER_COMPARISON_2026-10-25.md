# TikTok Shop data providers: Kalodata vs FastMoss vs EchoTik (2026-10-25)

Researched from each vendor's own developer docs and pricing pages where possible (two research agents; nothing
signed up for or paid). "Unverified" = vendor claim or third-party only.

| | **Kalodata** (current) | **FastMoss** | **EchoTik** |
|---|---|---|---|
| Bulk access | REST API, pay per call | REST API (~30 endpoints), plus MCP/CLI (55 tools) | REST API (~93 endpoints), plus MCP; CLI announced, no docs found |
| Price model | Credits: 0.1 per 100 rows (≈ $0.10 per 1,000 rows) | $0.01 per call of 10 rows (≈ $1 per 1,000 rows); 500 free calls; volume discounts 10–30% (inferred) | Monthly API plans: $139 for 100K calls, $659 for 500K; 10 rows per call (≈ $0.14 per 1,000 rows); 50–100 free calls. Currency on per-call figures unclear |
| History (tested?) | **≈ 12 months, tested** (Oct 2025 on) | "1,200–1,500+ days" claimed; **untested** | "≥ 2 years" / "1,000 days" claimed; **untested** |
| Past month query | Yes (yyyy-MM) | Yes: day, week or month | Yes: day, week (Mondays) or month |
| Ranking depth | 1,100+ rows (tested) | **500 per ranking query**; search up to 5,000 | Paging to 100,000 pages of 10 |
| Daily sales per product | Not returned in our test | Last 1–28 days only | Up to 180 days |
| Creators / videos per product | Yes, per past month (tested) | In search results (current) | In rankings (counts of creators, videos, lives) |
| Video sales, views | Yes | Yes | Yes |
| Ad vs organic flag | Yes | Yes (`is_ad`) | **No** |
| AI-generated video flag | Yes | **No** | Yes (`created_by_ai`) |
| ROAS estimate | Yes | Not seen | Not seen |
| Reviews / comment analysis | AI summary (1 credit) | Review list | Review text |
| Terms on storing / training | Not yet checked | Terms page behind a bot check; unknown | Chinese-law terms ban commercial use or resale beyond the "authorized scope"; penalties of at least ¥10,000 per breach; the API page itself advertises "model training". Get written permission |
| Accuracy | Estimates; method not published | Estimates; method not published | Estimates from public data; T+1 updates |

## Cost of extra history (if the claims hold)
- **FastMoss:** monthly top-500 products in about 30 categories for 36 months ≈ $500; 1–2M videos ≈ $1–2K. Total
  about $1–5K one-off.
- **EchoTik:** monthly top 10,000 products and 10,000 videos for 36 months ≈ 72K calls, plus 180-day daily trends for
  10,000 products ≈ 180K calls: one to three months of the $139 plan, or one month of the $659 plan. Total about
  $150–700.

## Recommendation
1. Keep **Kalodata** for the 12-month backfill: deepest rankings, cheapest per row, already built and tested.
2. Use a second provider **only to add Oct 2023 – Sep 2025** (seasons and longer-range prediction), and only after a
   free-trial test shows real data for a month such as March 2024.
3. Test both trials (free): one US monthly product ranking for March 2024 and one for March 2025 each.
4. Before any bulk pull, get written confirmation from each provider (Kalodata included) that storing the data and
   training our own models on it is allowed.

Sources: developer.fastmoss.com (docs/home, api/docs/guide/quickStart, api/pricing, payment/endpointsList,
mcp/pricing, cli/overview); fastmoss.com; delzonic.com FastMoss review (Sep 2026, third-party);
echotik.live/pricing, /en/api-service, /en/api/mcp, /en/service-agreement; help.echotik.live articles 6870452 and
7902212; EchoTik API docs mirror 4cfbmm8wtc.apifox.cn.
