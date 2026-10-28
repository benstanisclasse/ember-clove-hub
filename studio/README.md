# Ember Studio: the content conveyor

Content for the character account moves through one fixed line. Every step is enforced in code, so the result does
not depend on who (or which Claude session) runs it.

```
BIBLE (owner-approved) ─► PLAN ─► SCRIPT ─► GENERATE ─► QA ─► OWNER APPROVAL ─► SCHEDULE ─► POST ─► MEASURE
```

## The bible: `studio/bible/`
| File | Holds | Approval needs |
|---|---|---|
| `rules.yaml` | posting slots, content mix, rotation, soft follow lines, banned phrases, words the voice mispronounces, model, cost caps, QA thresholds | owner |
| `character.yaml` | name, look, personality, voice, jewelry, things she never says, **face reference images** | owner + a face image |
| `world.yaml` | city, home, **each room with a reference image**, props, side characters | owner + every room image |
| `wardrobe.yaml` | her plain basics plus the Ember & Clove store pieces (category, color, season; store pieces also carry the Shopify product, one listing photo and an exact description). The planner builds every outfit from it, always with exactly one store piece | owner |
| `products.yaml` | each store product: prompt description, reference photos, **the only facts scripts may claim**. Needs approval only once selling is on (`rules.mix.product_share_max` > 0) | owner |
| `series.yaml` | recurring formats (value vs product), rooms, follow-line policy | owner |

Approve a file only through `cli.py bible-approve FILE --actor owner --quote "<owner's words>"`. That command
refuses incomplete files (for example a character with no face image) and writes `approvals.log`.

## The stages: `studio/studio.db`
`PLANNED → SCRIPTED → GENERATED → QA_PASSED / QA_FAILED → APPROVED / REJECTED → SCHEDULED → POSTED → MEASURED`

| Gate | Enforced by |
|---|---|
| Plan | posts per day; no product posts while `mix.product_share_max` is 0 (audience first), otherwise at most one a day and the value share per 7 days; no product or room twice in a row; at most 1 soft follow line in any 3 posts; every post gets a seeded random, in-season outfit with exactly one Ember & Clove piece (its listing photo is sent as a reference image) with no full repeat within 21 days and no base piece (dress, top, bottom) reused within 4 posts. Scripts cannot change the planned outfit |
| Script | exactly 4 lines + 4 shot actions; 41–53 words for 14 s; no banned phrase or pattern (prices, delivery, testimonials, urgency, "follow me"); no word the voice mispronounces; product posts name ≥ 2 listed facts and end with the product line; soft line only where planned |
| Generate | bible approved (or `--test`, whose videos can never be approved); prompt built **only** from `templates/video_prompt.j2` + bible, hashed and saved; face + room + product reference images; per-video, daily and weekly cost caps; attempt limit |
| QA | transcript must match the script word for word; length ±0.6 s; speech ≥ 70%; frame sheet saved for the owner |
| Approve / reject | owner only, with the owner's words quoted; test videos refused |
| Schedule | any caption (owner 2026-10-26: no "AI-generated" text required); schedule again to change it |
| Posted | confirm the post is disclosed as AI (`--ai-label-on`). 2026-10-27: TikTok flagged the unlabelled first post as a Community Guidelines violation and labelled it; it does not label by itself |
| Every move | must follow the allowed path; logged in `transitions` (who, when, why) |

Proof the gates hold: `python -m pytest scripts/studio/test_studio.py -q` (17 tests).

## Commands
`python scripts/studio/cli.py <validate | plan | script | generate | qa | approve | reject | schedule | posted |
board | bible-approve>` (details in the file's docstring).

## Changing the rules
Edit the YAML, then the owner re-approves it. When a video fails for a new reason (a mispronounced word, a recurring
glitch), add it to `rules.yaml` (`tts_avoid`, `banned_phrases`) so it can't happen again.

## Approvals are locked to content

When the owner approves a file, `bible-approve` stores a hash of its settings (`approved_hash`). Any later edit, other than to
comments, turns the file back to draft until the owner approves it again, so nobody can change an approved rule quietly.

## Publishing and the dashboard (PostZen)

- `cli.py publish EP --mode draft|scheduled` sends an approved, scheduled episode to PostZen (api.postzen.dev) for its
  planned slot on the Ember & Clove TikTok account. `draft`: at the slot time it lands in the TikTok app's drafts and the
  owner posts it there with TikTok's AI-generated label on. `scheduled`: PostZen posts it publicly by itself; PostZen
  cannot set TikTok's AI flag (is_aigc), so the caption must disclose it; owner-only (`--actor owner --quote`).
- `cli.py sync` pulls post status, TikTok video metrics, followers and daily totals from PostZen and writes the
  dashboard's data files to `studio/dashboard/` (schedule, followers, spend, caps as JSON; tiktok_videos, post_timeline and
  daily_metrics as CSV so an empty table keeps its columns).
- Dashboard: "Ember Studio Control Room", https://claude.ai/artifact/E1BKotHzjjV1BQ6jQymzwe (Dashboard type). After a
  sync, each file is uploaded to the dashboard as an asset and its dataset's `url` and `updated` are updated.
- Key: POSTZEN_API_KEY (config secrets.postzen_api); account ids in config `postzen`.
- LAN dashboard: scheduled task "Ember Studio Dashboard" runs it at PC startup. scripts/studio/run_dashboard.cmd starts scripts/studio/dashboard_server.py on port 8790 (all interfaces),
  serving the control room at http://192.168.1.215:8790 and /metrics (TikTok + Facebook numbers) and running the PostZen sync every 15 minutes. GET only; no keys,
  prompts or write endpoints are served. Windows Firewall needs an inbound rule for TCP 8790 from the local subnet.
