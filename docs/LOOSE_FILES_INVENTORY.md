# Loose files inventory — 2026-10-28

Sweep of Ember & Clove files left outside the Hub, run with `docs/prompts/LOOSE_FILE_SWEEP_PROMPT.md`.
Everything was **copied** from outside the Hub, never moved or deleted there. Each copy keeps its original timestamp and was verified by SHA-256
(source hash = copy hash). Duplicates were checked against every Hub file except `backups/`.

Short names used in the tables:

| Short name | Real folder |
|---|---|
| `~` | `C:\Users\Administrator` |
| `{CHATS}` | `C:\Users\Administrator\AppData\Roaming\Claude\scratch-workspaces\613e1a89-…\5b46794c-…` (each chat's temporary folder) |
| `{PADS}\scratch-…\<id>\scratchpad` | `C:\Users\Administrator\AppData\Local\Temp\claude\C--Users-…-scratch-…\<id>\scratchpad` (a chat session's scratchpad) |
| `%TEMP%` | `C:\Users\Administrator\AppData\Local\Temp` |
| `{NOTES}` | `C:\Users\Administrator\AppData\Roaming\Claude\side-session-notes` |

## Summary

| | Files | Size |
|---|---:|---:|
| Copied into the Hub (verified) | 342 | 13.4 MB |
| Already in the Hub (identical), not copied | 36 | — |
| Secrets, not copied | 4 | — |
| Store-related but left out (owner to decide) | about 980 | about 300 MB |

Where the copies went:

| Hub path | What |
|---|---|
Rule used: text (scripts, notes, JSON, GraphQL) goes to `docs/archive/<date>_<topic>/` and is committed; images go to
`assets/_research/<date>_<topic>/`; brand files to `brand/`. Files first parked in `data/inbox/loose_2026-10-28/` were
moved to these homes the same day (owner: "organize them in the hub"); that inbox folder no longer exists.

| Hub path | What |
|---|---|
| `brand/ember-clove-social-share.png` | Social sharing card from Downloads |
| `brand/ember-clove-favicon-128.png` | 128 px favicon render from the 10-25 catalog build |
| `assets/reference_marketing_studio.mp4` | Higgsfield's Marketing Studio sample clip (striped skirt, yellow tights), the same clip as `assets/reference_marketing_studio_frames.jpg`. A style reference, not a store creative |
| `assets/_research/2026-10-24_product-photo-sheet/` | 6-candidate product photo sheet (37 files) |
| `assets/_research/2026-10-25_p01_sheet.jpg`, `2026-10-25_p02_sheet.jpg` | P01/P02 photo sheets |
| `assets/_research/2026-10-25_catalog-build/` | Product photos used in the 10-25 catalog build (8) |
| `assets/_research/2026-10-26_catalog-expansion-sheets/` | Gallery and description contact sheets of 8 new products (24) |
| `assets/_research/2026-10-26_catalog-photo-quality/` | Photo samples from the quality check (6) |
| `assets/_research/2026-10-26_wardrobe-store-pieces/` | Content Studio wardrobe picks: store pieces, crops, outfit sheets (18) |
| `assets/_research/2026-10-27_heels-sandals_picks/` | Heels/sandals picks from Downloads (8 files) |
| `reports/one-sale-profit_2026-10-25.html` | One-sale profit page |
| `docs/archive/2026-10-19_niche-research/` | Niche research reports, notes and the cat-home financial model (27 files) |
| `docs/archive/2026-10-19_shopify-hub-server/` | Source of the self-hosted "Shopify hub" server (chat "Shopify store hub MCP server"; 146 files; `.venv` and caches not copied). It runs on VM 210, which has its own copy |
| `docs/archive/2026-10-23_social-card/` | Script that made the social sharing card |
| `docs/archive/2026-10-25_catalog-build/` | Catalog build scripts, image lists, GraphQL product and price batches as sent |
| `docs/archive/2026-10-26_catalog-expansion/`, `2026-10-27_catalog-expansion/` | Catalog expansion scripts, product dump, image URL lists |
| `docs/archive/2026-10-26_catalog-photo-quality/` | Photo-quality tools, product lists, scores, media maps (`target.json` not copied: signed upload URL) |
| `docs/archive/2026-10-26_tiktok-accounts-api/` | TikTok Accounts API setup doc, script and its tests |
| `docs/archive/2026-10-26_wardrobe-store-pieces/` | Content Studio one-off scripts that added store pieces and night-out items to the bible, the picks list, a 21-episode plan. Nothing registered in `studio/`; anything for `studio/refs/` goes through `cli.py` |
| `docs/archive/side-session-notes/` | Two side-session notes (Microsoft Ads connector test, TikTok Smart+ research) |

## Owner to decide

1. **FlowFit** (`{CHATS}\scratch-2026-10-26-3c3380\FlowFit-report.md`, `flowfit-posts.csv`, and two report scripts in
   that chat's scratchpad): a report on the TikTok account FlowFit (@reddit.poett), which sits in the same TikTok
   Business Center as Ember & Clove. Not copied, because it is a different account. Say if it should be kept.
2. **Bulk photo downloads left out** (all store-related, about 300 MB, mostly supplier photos that can be downloaded
   again; the chosen photos are already in Shopify and `data/media_originals/`):

   | Folder | Files | Not in Hub | Size | What |
   |---|---:|---:|---:|---|
   | `%TEMP%\ec_q\all` | 581 | 496 | 100 MB | Supplier photos scored for the catalog |
   | `%TEMP%\ec_q\sh` | 54 | 54 | 64 MB | Contact sheets of those photos |
   | `%TEMP%\ec_q\shoes` | 60 | 60 | 22 MB | Shoe supplier photos |
   | `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-…\scratchpad\imgs_b` | 200 | 196 | 34 MB | Product photo downloads, 10-27 |
   | `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-…\scratchpad\imgs` | 169 | 169 | 71 MB | Product photo downloads, 10-26 |

   Copy them only if you want the raw supplier photos kept.
3. **Old "Shopify hub" work files** in `{PADS}\scratch-2026-10-17-c2ad34\1d2ad199-…` (message drafts, `autogen.db`,
   a patch script) and `…\cdb49a0a-…` (before/after copies of the TikTok Smart+ change): in-progress copies; the
   finished code is in `docs/archive/2026-10-19_shopify-hub-server/`. Not copied.
4. **Secrets in Downloads** (not copied, listed by path only): `~\Downloads\key.txt`, `~\Downloads\openrouter_api_key.txt`,
   `~\Downloads\client_secret_579728600010-….apps.googleusercontent.com.json`. Consider moving keys into user environment
   variables and deleting the files (only you should do that).
5. **Left in place on purpose**: the four Ember & Clove scheduled tasks in `~\.claude\scheduled-tasks\`
   (`ads-dashboard-refresh`, `emberandclove-domain-https-check`, `tiktok-catalog-match-recheck`,
   `tiktok-verification-check`) are live settings, not loose files; Claude's memory notes for the store chats in
   `~\.claude\projects\…-scratch-2026-10-23-2ef2f6\memory\`; and the scratchpads of sessions still active on 10-27/28
   (`c3d054ec`, `a60d1d08`, `1b04f661`, `6410b0bd`, `ce9a1435`, `19f638ed`, `de1e6b5e`), which those sessions own.

## Which chats are safe to delete

The files in these chats' temporary folders are now all in the Hub (or are listed above as your decision):

| Chat | Temporary folder | Safe to delete? |
|---|---|---|
| E-commerce niche research and validation | `scratch-2026-10-19-d818cc` | Yes: all 27 files copied |
| Shopify store hub MCP server; Migrate hub TikTok ad creation to Smart+ APIs | `scratch-2026-10-17-c2ad34` | Yes: source copied (the `.venv` can be reinstalled). Its scratchpads hold only in-progress copies (item 3) |
| TikTok account visibility | `scratch-2026-10-26-3c3380` | Yes, unless you want the FlowFit files (item 1) |
| TikTok Research Insights API access | `scratch-2026-10-25-953d17` | Yes: the folder is empty |
| emberandclove.com https check; TikTok verification check; TikTok catalog match-rate recheck | share `scratch-2026-10-23-2ef2f6` | Their folder's files are all in the Hub. Do **not** delete "Shopify, TikTok, Higgsfield connections" or its forks: they still work in that folder |

Not store-related (skipped; deleting them is a separate decision): `scratch-2026-09-09-39e06a` (account lockouts),
`scratch-2026-09-23-38b47c` (server/VPN scripts), `scratch-2026-09-28-2b2a0d` (Minecraft/AI Town),
`scratch-2026-10-13-05507e` (trading research; one transcript mentions the store in passing),
`scratch-2026-10-22-064a4a` / `-127e5d` / `-76fa5c` (BridgeMark, Google Analytics, Lovable), and the empty folders
`-09-28-1abbae`, `-10-05-746fca`, `-10-06-289a3a`, `-10-14-51aeba`, `-10-17-406b85`, `-10-22-08bd52`, `-10-22-0c3eaa`,
`-10-23-5cba26`. Other user-folder files in Downloads/Desktop/Documents (trading papers, BridgeMark CSVs, Shogun2,
vertexV2) are not store files. Pictures and Videos hold no store files.

## How the sweep was done

- Chat temporary folders: searched every file for the store words; checked each folder's top level.
- Transcripts (`~\.claude\projects\*\*.jsonl`): 29 transcripts mention the store. Every file path they wrote to or named
  outside the Hub was checked on disk; that is how the `%TEMP%\ec_q`, `%TEMP%\ec_sheet`, `%TEMP%\claude_store`,
  scratchpad and side-note files were found.
- User folders: Downloads, Desktop, Documents (not the Hub), Pictures, Videos by name and date.
- Secrets/personal data: every text file was scanned for keys, tokens, signed URLs, passwords and e-mail addresses before
  copying. None copied. Two niche-research notes contain public supplier contact addresses (business, not customers).

## Per-folder detail

### `~\Downloads`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `~\Downloads\ember-clove-social-share.png` | 435,114 | `b43c714c3ab9` | copied → `brand/ember-clove-social-share.png` | Social sharing card (1200x630-style), made 10-23 by social_card.py |
| `~\Downloads\Marketing Studio • Higgsfield.mp4` | 1,968,842 | `91841e48382e` | copied → `assets/reference_marketing_studio.mp4` | Video downloaded from Higgsfield Marketing Studio 10-24 (content not checked) |

### `~\Downloads\Ember-Clove-heels-sandals`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `~\Downloads\Ember-Clove-heels-sandals\1-studded-block-heel-sandals-black.jpg` | 280,929 | `b77d89ace145` | copied → `assets/_research/2026-10-27_heels-sandals_picks/1-studded-block-heel-sandals-black.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\2-pointed-stiletto-mules-gold.jpg` | 80,388 | `db3a6e25edc1` | copied → `assets/_research/2026-10-27_heels-sandals_picks/2-pointed-stiletto-mules-gold.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\3-croc-slingback-stilettos-black_AI.jpg` | 227,096 | `062f5f651130` | copied → `assets/_research/2026-10-27_heels-sandals_picks/3-croc-slingback-stilettos-black_AI.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\4-rose-strappy-stilettos-red_AI.jpg` | 202,282 | `e4d43580d671` | copied → `assets/_research/2026-10-27_heels-sandals_picks/4-rose-strappy-stilettos-red_AI.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\5-toe-loop-slides-black.jpg` | 373,909 | `fe202336e76b` | copied → `assets/_research/2026-10-27_heels-sandals_picks/5-toe-loop-slides-black.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\6-double-band-buckle-sandals-tan.jpg` | 411,281 | `eb732637345f` | copied → `assets/_research/2026-10-27_heels-sandals_picks/6-double-band-buckle-sandals-tan.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\7-rhinestone-h-band-slides-black.jpg` | 226,034 | `6c7a3aa8123e` | copied → `assets/_research/2026-10-27_heels-sandals_picks/7-rhinestone-h-band-slides-black.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |
| `~\Downloads\Ember-Clove-heels-sandals\_preview.jpg` | 149,691 | `9a0e1d24950a` | copied → `assets/_research/2026-10-27_heels-sandals_picks/_preview.jpg` | Heels/sandals catalog picks downloaded for the owner 10-27 (_AI = AI-cleaned photo) |

### `{CHATS}\scratch-2026-10-26-3c3380`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{CHATS}\scratch-2026-10-26-3c3380\SETUP-tiktok-api.md` | 3,457 | `3b0b13313d6d` | copied → `docs/archive/2026-10-26_tiktok-accounts-api/SETUP-tiktok-api.md` | How to set up TikTok Accounts API access for Ember & Clove analytics |
| `{CHATS}\scratch-2026-10-26-3c3380\tiktok_insights.py` | 15,078 | `b01013372bd2` | copied → `docs/archive/2026-10-26_tiktok-accounts-api/tiktok_insights.py` | Standard-library script that pulls TikTok account/post analytics (needs config + tokens, none copied) |

### `{PADS}\scratch-2026-10-26-3c3380\017f46a5-72c1-493e-b24b-730bd3f0247a\scratchpad`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{PADS}\scratch-2026-10-26-3c3380\017f46a5-72c1-493e-b24b-730bd3f0247a\scratchpad\test_insights.py` | 3,881 | `717f0b2b6734` | copied → `docs/archive/2026-10-26_tiktok-accounts-api/test_insights.py` | Tests for tiktok_insights.py |

### `%TEMP%\ec_sheet`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `%TEMP%\ec_sheet\cable0.jpg` | 12,604 | `76286044490f` | copied → `assets/_research/2026-10-24_product-photo-sheet/cable0.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\cable1.jpg` | 19,508 | `c4a7297f3fd7` | copied → `assets/_research/2026-10-24_product-photo-sheet/cable1.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\cable2.jpg` | 19,747 | `ce4a21fbf141` | copied → `assets/_research/2026-10-24_product-photo-sheet/cable2.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\cable3.jpg` | 20,951 | `186b91b7d21f` | copied → `assets/_research/2026-10-24_product-photo-sheet/cable3.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\cable4.jpg` | 19,984 | `6fc35b4136fa` | copied → `assets/_research/2026-10-24_product-photo-sheet/cable4.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\cable5.jpg` | 25,759 | `01dc843ec915` | copied → `assets/_research/2026-10-24_product-photo-sheet/cable5.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\highneck0.jpg` | 14,865 | `15cfe9083bd9` | copied → `assets/_research/2026-10-24_product-photo-sheet/highneck0.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\highneck1.jpg` | 27,832 | `086bcb6ab2bb` | copied → `assets/_research/2026-10-24_product-photo-sheet/highneck1.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\highneck2.jpg` | 16,734 | `a18f9a900f3d` | copied → `assets/_research/2026-10-24_product-photo-sheet/highneck2.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\highneck3.jpg` | 17,838 | `72a22839e6e0` | copied → `assets/_research/2026-10-24_product-photo-sheet/highneck3.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\highneck4.jpg` | 19,330 | `d1d016b61ac4` | copied → `assets/_research/2026-10-24_product-photo-sheet/highneck4.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\highneck5.jpg` | 25,201 | `0e124606517e` | copied → `assets/_research/2026-10-24_product-photo-sheet/highneck5.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\map.json` | 4,155 | `3bcd4186633d` | copied → `assets/_research/2026-10-24_product-photo-sheet/map.json` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\pleat0.jpg` | 12,668 | `b09d835e3c55` | copied → `assets/_research/2026-10-24_product-photo-sheet/pleat0.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\pleat1.jpg` | 22,965 | `a46ee81cfa97` | copied → `assets/_research/2026-10-24_product-photo-sheet/pleat1.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\pleat2.jpg` | 20,803 | `640b88fbde17` | copied → `assets/_research/2026-10-24_product-photo-sheet/pleat2.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\pleat3.jpg` | 21,833 | `463be65f7aa4` | copied → `assets/_research/2026-10-24_product-photo-sheet/pleat3.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\pleat4.jpg` | 22,900 | `cbfbdda52bf9` | copied → `assets/_research/2026-10-24_product-photo-sheet/pleat4.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\pleat5.jpg` | 28,675 | `84a30ce7936e` | copied → `assets/_research/2026-10-24_product-photo-sheet/pleat5.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\ruffle0.jpg` | 10,114 | `ac3cbbacd271` | copied → `assets/_research/2026-10-24_product-photo-sheet/ruffle0.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\ruffle1.jpg` | 20,860 | `e18a2bfc50c8` | copied → `assets/_research/2026-10-24_product-photo-sheet/ruffle1.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\ruffle2.jpg` | 22,461 | `ff3fa6e721ca` | copied → `assets/_research/2026-10-24_product-photo-sheet/ruffle2.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\ruffle3.jpg` | 21,437 | `ca29549bc31e` | copied → `assets/_research/2026-10-24_product-photo-sheet/ruffle3.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\ruffle4.jpg` | 20,229 | `3ddc1f18e372` | copied → `assets/_research/2026-10-24_product-photo-sheet/ruffle4.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\ruffle5.jpg` | 29,731 | `f9b14916784a` | copied → `assets/_research/2026-10-24_product-photo-sheet/ruffle5.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\sheet.jpg` | 269,542 | `bf29b1ef2319` | copied → `assets/_research/2026-10-24_product-photo-sheet/sheet.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\velvet0.jpg` | 18,147 | `1a96a0bdd672` | copied → `assets/_research/2026-10-24_product-photo-sheet/velvet0.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\velvet1.jpg` | 26,526 | `fd89f16ac3bc` | copied → `assets/_research/2026-10-24_product-photo-sheet/velvet1.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\velvet2.jpg` | 28,681 | `1ca6d211d6ec` | copied → `assets/_research/2026-10-24_product-photo-sheet/velvet2.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\velvet3.jpg` | 31,825 | `87f74164b917` | copied → `assets/_research/2026-10-24_product-photo-sheet/velvet3.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\velvet4.jpg` | 35,246 | `1cb6261d2bb8` | copied → `assets/_research/2026-10-24_product-photo-sheet/velvet4.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\velvet5.jpg` | 34,334 | `f7e51bf8ff8b` | copied → `assets/_research/2026-10-24_product-photo-sheet/velvet5.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\wrap0.jpg` | 8,079 | `d8f3a919b21e` | copied → `assets/_research/2026-10-24_product-photo-sheet/wrap0.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\wrap1.jpg` | 13,721 | `78dd630a8360` | copied → `assets/_research/2026-10-24_product-photo-sheet/wrap1.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\wrap2.jpg` | 7,250 | `5b73ebfa7134` | copied → `assets/_research/2026-10-24_product-photo-sheet/wrap2.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\wrap3.jpg` | 6,159 | `f38af1150005` | copied → `assets/_research/2026-10-24_product-photo-sheet/wrap3.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |
| `%TEMP%\ec_sheet\wrap4.jpg` | 13,201 | `e4458fbedaf2` | copied → `assets/_research/2026-10-24_product-photo-sheet/wrap4.jpg` | Product photo comparison sheet, 10-24: 6 candidates (cable, highneck, pleat, ruffle, velvet, wrap) x 6 photos |

### `%TEMP%\claude_store`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `%TEMP%\claude_store\add_store_pieces.py` | 11,006 | `9a0331fc8fa8` | copied → `docs/archive/2026-10-26_wardrobe-store-pieces/add_store_pieces.py` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\awning.jpg` | 13,372 | `a0e903651002` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/awning.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\cardigan.jpg` | 29,810 | `8b7e14fe7556` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/cardigan.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\crops.jpg` | 41,484 | `5474b81f960c` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/crops.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\crops2.jpg` | 24,836 | `edfe2c71ab6a` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/crops2.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\fetch.py` | 3,508 | `c686efc7c959` | copied → `docs/archive/2026-10-26_wardrobe-store-pieces/fetch.py` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\frame_vs_face.jpg` | 281,523 | `18861439a764` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/frame_vs_face.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\front.jpg` | 69,964 | `f9ae366935e1` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/front.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\lake.jpg` | 89,194 | `b1466770cda0` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/lake.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\night_bible.py` | 5,965 | `47ac7609d2b0` | copied → `docs/archive/2026-10-26_wardrobe-store-pieces/night_bible.py` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\night_pieces.jpg` | 73,121 | `40eedeb5f88f` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/night_pieces.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\p02.jpg` | 12,204 | `288a3e79bdec` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/p02.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\picks.json` | 15,732 | `1e1cffb3ed86` | copied → `docs/archive/2026-10-26_wardrobe-store-pieces/picks.json` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\plan.txt` | 3,778 | `356cc824daae` | copied → `docs/archive/2026-10-26_wardrobe-store-pieces/plan.txt` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\ruffle_grid.jpg` | 40,937 | `6acf3eed1a24` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/ruffle_grid.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\sheet1.jpg` | 107,049 | `806d337676ac` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/sheet1.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\sheet2.jpg` | 216,913 | `c85336128bcb` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/sheet2.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\sheet3.jpg` | 162,144 | `6fb4994ad5ac` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/sheet3.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\sheet4.jpg` | 110,355 | `bf8010b9eba3` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/sheet4.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\shoes2.jpg` | 48,029 | `33b0b8bcb292` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/shoes2.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\sidewalk.jpg` | 118,956 | `c5e57502851b` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/sidewalk.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\sunglasses.jpg` | 45,893 | `e293781e2c8d` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/sunglasses.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |
| `%TEMP%\claude_store\tort.jpg` | 20,867 | `4c042804d891` | copied → `assets/_research/2026-10-26_wardrobe-store-pieces/tort.jpg` | Content Studio wardrobe work 10-26: store-piece picks, crops, outfit sheets, 21-episode plan |

### `%TEMP%\ec_q`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `%TEMP%\ec_q\tool\addmedia.json` | 4,546 | `a1e7de992a15` | copied → `docs/archive/2026-10-26_catalog-photo-quality/addmedia.json` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\args.txt` | 64,676 | `7a2e910d0591` | copied → `docs/archive/2026-10-26_catalog-photo-quality/args.txt` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\merge.py` | 1,068 | `17544ea73850` | copied → `docs/archive/2026-10-26_catalog-photo-quality/merge.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\parse.py` | 825 | `342332070978` | copied → `docs/archive/2026-10-26_catalog-photo-quality/parse.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\products.json` | 81,489 | `13f868de0963` | copied → `docs/archive/2026-10-26_catalog-photo-quality/products.json` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\products2.json` | 97,776 | `dc053a8a4b9a` | copied → `docs/archive/2026-10-26_catalog-photo-quality/products2.json` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\q.py` | 1,556 | `d25b2ea52bbd` | copied → `docs/archive/2026-10-26_catalog-photo-quality/q.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\rows.json` | 201,944 | `ae694a3ce068` | copied → `docs/archive/2026-10-26_catalog-photo-quality/rows.json` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\rows2.json` | 271,467 | `c19e94836677` | copied → `docs/archive/2026-10-26_catalog-photo-quality/rows2.json` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\runall.py` | 648 | `e25e0c18b862` | copied → `docs/archive/2026-10-26_catalog-photo-quality/runall.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\scores.tsv` | 30,021 | `80815dfe32be` | copied → `docs/archive/2026-10-26_catalog-photo-quality/scores.tsv` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\sheets.py` | 2,018 | `677ba18d9672` | copied → `docs/archive/2026-10-26_catalog-photo-quality/sheets.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\staged_upload.py` | 440 | `30a4c8d87eac` | copied → `docs/archive/2026-10-26_catalog-photo-quality/staged_upload.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\thumbs.py` | 376 | `dbc8bf460343` | copied → `docs/archive/2026-10-26_catalog-photo-quality/thumbs.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\varmedia.json` | 9,124 | `7f7d9f4be3f6` | copied → `docs/archive/2026-10-26_catalog-photo-quality/varmedia.json` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\write_csv.py` | 4,940 | `c5ebb90dd3b9` | copied → `docs/archive/2026-10-26_catalog-photo-quality/write_csv.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\tool\zoom.py` | 1,604 | `1b159ff8b27b` | copied → `docs/archive/2026-10-26_catalog-photo-quality/zoom.py` | Catalog photo-quality queue 10-26/27: scripts, product lists, scores, media maps |
| `%TEMP%\ec_q\img\braid.jpg` | 66,023 | `1e760155344b` | already in Hub at `data/media_originals/braided-cord-sandals/01_41293287555311.jpg` |  |
| `%TEMP%\ec_q\img\card1.jpg` | 78,709 | `80a2bcc9ec61` | already in Hub at `data/media_originals/ribbon-lace-cardigan/01_41318286885103.jpg` |  |
| `%TEMP%\ec_q\img\card2.jpg` | 79,765 | `aa8aef54a0d8` | already in Hub at `data/media_originals/ribbon-lace-cardigan/02_41318286917871.jpg` |  |
| `%TEMP%\ec_q\img\card3.jpg` | 82,006 | `fea76c082485` | already in Hub at `data/media_originals/ribbon-lace-cardigan/03_41318286950639.jpg` |  |
| `%TEMP%\ec_q\img\card4.jpg` | 91,588 | `a0e099772e77` | already in Hub at `data/media_originals/ribbon-lace-cardigan/04_41318286983407.jpg` |  |
| `%TEMP%\ec_q\img\card5.jpg` | 98,906 | `69f82393724e` | already in Hub at `data/media_originals/ribbon-lace-cardigan/05_41318287016175.jpg` |  |
| `%TEMP%\ec_q\img\cardv1.jpg` | 444,530 | `4f7109e2e818` | copied → `assets/_research/2026-10-26_catalog-photo-quality/cardv1.jpg` | Catalog photo samples |
| `%TEMP%\ec_q\img\cardv2.jpg` | 348,776 | `859d96f90912` | copied → `assets/_research/2026-10-26_catalog-photo-quality/cardv2.jpg` | Catalog photo samples |
| `%TEMP%\ec_q\img\coat1.jpg` | 52,009 | `7d22dee06a7b` | copied → `assets/_research/2026-10-26_catalog-photo-quality/coat1.jpg` | Catalog photo samples |
| `%TEMP%\ec_q\img\coat2.jpg` | 200,192 | `756833923b4e` | copied → `assets/_research/2026-10-26_catalog-photo-quality/coat2.jpg` | Catalog photo samples |
| `%TEMP%\ec_q\img\croc.jpg` | 149,864 | `bf849ca5436a` | already in Hub at `data/media_originals/croc-stiletto/01_41293285523695.jpg`, `studio/refs/store/stiletto-slingback-black.jpg` |  |
| `%TEMP%\ec_q\img\henley1.jpg` | 99,867 | `6ac75ce6f032` | copied → `assets/_research/2026-10-26_catalog-photo-quality/henley1.jpg` | Catalog photo samples |
| `%TEMP%\ec_q\img\henley2.jpg` | 86,640 | `94439a6c329a` | copied → `assets/_research/2026-10-26_catalog-photo-quality/henley2.jpg` | Catalog photo samples |
| `%TEMP%\ec_q\img\mesh.jpg` | 48,061 | `dd554a9d0619` | already in Hub at `data/media_originals/ruffle-mesh-dress/01_41293103857903.jpg` |  |
| `%TEMP%\ec_q\img\mock.jpg` | 31,927 | `c2f8b0fb7fbd` | already in Hub at `data/media_originals/mock-neck-pleat-dress/01_41318211977455.jpg` |  |
| `%TEMP%\ec_q\img\rose.jpg` | 113,640 | `69a0e656522d` | already in Hub at `data/media_originals/rose-stiletto/01_41293284344047.jpg` |  |
| `%TEMP%\ec_q\img\skirt.jpg` | 72,392 | `b2131d95f7c3` | already in Hub at `data/media_originals/ruffle-slit-knit-skirt/01_41293104840943.jpg` |  |

### `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\p01_sheet.jpg` | 86,454 | `25c1ca607ce2` | copied → `assets/_research/2026-10-25_p01_sheet.jpg` | P01 product photo sheet |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\p02_sheet.jpg` | 62,308 | `03a7ddd98e31` | copied → `assets/_research/2026-10-25_p02_sheet.jpg` | P02 product photo sheet |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\build.py` | 11,473 | `30b98e1657f0` | copied → `docs/archive/2026-10-25_catalog-build/build.py` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\build_00.py` | 65,653 | `7915978557b0` | copied → `docs/archive/2026-10-25_catalog-build/build_00.py` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\dump.py` | 467 | `3e05e246f6b3` | copied → `docs/archive/2026-10-25_catalog-build/dump.py` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\fav32.png` | 2,098 | `6a1730527359` | copied → `brand/ember-clove-favicon-128.png` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\gen_mut.py` | 5,197 | `48b9cafbbc9b` | copied → `docs/archive/2026-10-25_catalog-build/gen_mut.py` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\grab.py` | 1,160 | `47a982b6b06c` | copied → `docs/archive/2026-10-25_catalog-build/grab.py` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\imgs.json` | 28,036 | `53b953609e2c` | copied → `docs/archive/2026-10-25_catalog-build/imgs.json` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\imgs2.json` | 3,256 | `37f0c0017009` | copied → `docs/archive/2026-10-25_catalog-build/imgs2.json` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\sheets.py` | 1,050 | `7c2097861348` | copied → `docs/archive/2026-10-25_catalog-build/sheets.py` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p1.jpg` | 33,399 | `afa6744d1e0b` | copied → `assets/_research/2026-10-25_catalog-build/p1.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p2.jpg` | 61,691 | `72e5d673d79d` | copied → `assets/_research/2026-10-25_catalog-build/p2.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p3.jpg` | 43,751 | `2c2e06ab33ee` | copied → `assets/_research/2026-10-25_catalog-build/p3.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p4.jpg` | 41,625 | `d555f4e80a2b` | copied → `assets/_research/2026-10-25_catalog-build/p4.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p5.jpg` | 71,168 | `9c38502871a0` | copied → `assets/_research/2026-10-25_catalog-build/p5.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p6.jpg` | 61,677 | `18775994351a` | copied → `assets/_research/2026-10-25_catalog-build/p6.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p7.jpg` | 76,520 | `16b4c4785379` | copied → `assets/_research/2026-10-25_catalog-build/p7.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\img\p8.jpg` | 76,864 | `02a8b453fd9a` | copied → `assets/_research/2026-10-25_catalog-build/p8.jpg` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\mut\changes.json` | 17,265 | `85d1b75e8f9c` | already in Hub at `reports/redesign/product_changes_2026-10-24.json` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\mut\chunk1.graphql` | 13,119 | `e341ca660857` | copied → `docs/archive/2026-10-25_catalog-build/mut/chunk1.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\mut\chunk2.graphql` | 12,918 | `a8e19247328a` | copied → `docs/archive/2026-10-25_catalog-build/mut/chunk2.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\mut\chunk3.graphql` | 12,520 | `0d4a0b9251d1` | copied → `docs/archive/2026-10-25_catalog-build/mut/chunk3.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\mut\chunk4.graphql` | 13,663 | `c08140b54cb9` | copied → `docs/archive/2026-10-25_catalog-build/mut/chunk4.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\price\c1.graphql` | 13,434 | `ad4518ae573f` | copied → `docs/archive/2026-10-25_catalog-build/price/c1.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\price\c2.graphql` | 14,249 | `0e78992af90b` | copied → `docs/archive/2026-10-25_catalog-build/price/c2.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\price\c3.graphql` | 14,913 | `abc5798b6f40` | copied → `docs/archive/2026-10-25_catalog-build/price/c3.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\price\c4.graphql` | 11,619 | `4b508b456960` | copied → `docs/archive/2026-10-25_catalog-build/price/c4.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |
| `{PADS}\scratch-2026-10-23-2ef2f6\326f46f7-0e9a-46eb-bfdb-d027a4f0bce0\scratchpad\price\c5.graphql` | 10,853 | `4d2f5ca9ec0d` | copied → `docs/archive/2026-10-25_catalog-build/price/c5.graphql` | Catalog build 10-25: product page builder, image lists, GraphQL product/price batches as sent |

### `{PADS}\scratch-2026-10-23-2ef2f6\f8ff9dc6-54d7-4dfc-a166-f26640f2aca1\scratchpad`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{PADS}\scratch-2026-10-23-2ef2f6\f8ff9dc6-54d7-4dfc-a166-f26640f2aca1\scratchpad\one-sale-profit.html` | 20,988 | `aba4326fbb12` | copied → `reports/one-sale-profit_2026-10-25.html` | One-sale profit explainer page (HTML), 10-25 |

### `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad\dl.py` | 2,119 | `67da346f5450` | copied → `docs/archive/2026-10-27_catalog-expansion/dl.py` | Catalog expansion 10-27: image download/generation scripts and contact sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad\gen.py` | 18,478 | `eecaf5e6306d` | copied → `docs/archive/2026-10-27_catalog-expansion/gen.py` | Catalog expansion 10-27: image download/generation scripts and contact sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad\scripts\dl.py` | 941 | `8d312b271fe8` | copied → `docs/archive/2026-10-27_catalog-expansion/scripts/dl.py` | Catalog expansion 10-27: image download/generation scripts and contact sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad\scripts\extract.py` | 1,018 | `13e40a56cede` | copied → `docs/archive/2026-10-27_catalog-expansion/scripts/extract.py` | Catalog expansion 10-27: image download/generation scripts and contact sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad\scripts\sheet.py` | 912 | `be72dc448f92` | copied → `docs/archive/2026-10-27_catalog-expansion/scripts/sheet.py` | Catalog expansion 10-27: image download/generation scripts and contact sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\8c9e0c1d-b1f0-4939-9d94-c197791e41d2\scratchpad\scripts\titles.py` | 940 | `3db7e3fec6d2` | copied → `docs/archive/2026-10-27_catalog-expansion/scripts/titles.py` | Catalog expansion 10-27: image download/generation scripts and contact sheets |

### `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\dump.txt` | 28,918 | `acf2555a9610` | copied → `docs/archive/2026-10-26_catalog-expansion/dump.txt` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\urls.json` | 22,800 | `3082b723ae33` | copied → `docs/archive/2026-10-26_catalog-expansion/urls.json` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\build.py` | 11,057 | `982c9daa4f7c` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/build.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\build_c.py` | 12,223 | `68fb36979fde` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/build_c.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\cat.py` | 551 | `7cda2909947a` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/cat.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\crop.py` | 553 | `50fbfd7cc785` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/crop.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\diff.py` | 220 | `618478ffe186` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/diff.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\dl.py` | 1,311 | `10fa6541fda3` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/dl.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\dump.py` | 892 | `006a41be4792` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/dump.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\sheet.py` | 1,130 | `f40bcb78601d` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/sheet.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\scripts\summ.py` | 1,414 | `2a950de3479e` | copied → `docs/archive/2026-10-26_catalog-expansion/scripts/summ.py` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889153775_desc0.jpg` | 96,920 | `56b01d67332b` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889153775_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889153775_desc1.jpg` | 74,977 | `696c016e1572` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889153775_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889153775_gallery.jpg` | 86,073 | `2161b2f3d600` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889153775_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889252079_desc0.jpg` | 113,420 | `c074309038f2` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889252079_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889252079_desc1.jpg` | 62,626 | `d1bacde9f484` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889252079_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889252079_gallery.jpg` | 75,171 | `2cfcc1eb19b7` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889252079_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889612527_desc0.jpg` | 136,139 | `c65419a61d13` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889612527_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889612527_desc1.jpg` | 49,829 | `f9a3b1037307` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889612527_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889612527_gallery.jpg` | 33,821 | `99e7a4d4c224` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889612527_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889874671_desc0.jpg` | 111,460 | `3a2d2e9af789` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889874671_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756889874671_gallery.jpg` | 82,592 | `fed773f4ccb0` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756889874671_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756890005743_desc0.jpg` | 97,947 | `4500826481a8` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756890005743_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756890005743_desc1.jpg` | 33,145 | `bd87cfd83cce` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756890005743_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756890005743_gallery.jpg` | 41,079 | `345f91f69f92` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756890005743_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756901933295_desc0.jpg` | 96,853 | `fb570ebe6f68` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756901933295_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756901933295_desc1.jpg` | 43,514 | `a24d113e03ce` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756901933295_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756901933295_gallery.jpg` | 38,886 | `7370dc1c3d61` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756901933295_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756905537775_desc0.jpg` | 92,803 | `18ac9e03a93a` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756905537775_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756905537775_desc1.jpg` | 38,720 | `5f7c990b0c8d` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756905537775_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756905537775_gallery.jpg` | 55,723 | `bbb7657e98f7` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756905537775_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756949676271_desc0.jpg` | 149,615 | `1787dc367b67` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756949676271_desc0.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756949676271_desc1.jpg` | 63,101 | `bac6be6c8e0a` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756949676271_desc1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\9756949676271_gallery.jpg` | 111,985 | `7b6d65fdf751` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/9756949676271_gallery.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |
| `{PADS}\scratch-2026-10-23-2ef2f6\ea77365e-6afb-494c-ac26-ea8ff0def684\scratchpad\sheets\crop1.jpg` | 8,054 | `be1938248812` | copied → `assets/_research/2026-10-26_catalog-expansion-sheets/crop1.jpg` | Catalog expansion 10-26: product dump, image URLs, build scripts, gallery/description sheets |

### `{PADS}\scratch-2026-10-17-c2ad34\527ba8f1-466e-4414-9071-2a13471cbc13\scratchpad`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{PADS}\scratch-2026-10-17-c2ad34\527ba8f1-466e-4414-9071-2a13471cbc13\scratchpad\social_card.py` | 2,529 | `62e94b06b663` | copied → `docs/archive/2026-10-23_social-card/social_card.py` | Script that generated ember-clove-social-share.png |

### `{NOTES}\local_6371be1b-443f-4777-888b-3f01313c354c`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{NOTES}\local_6371be1b-443f-4777-888b-3f01313c354c\microsoft-ads-connector-test.md` | 2,191 | `5cc2e39b9e78` | copied → `docs/archive/side-session-notes/2026-10-27_microsoft-ads-connector-test.md` | Side-session note: Microsoft Ads MCP connector test, 10-27 |

### `{NOTES}\local_99bfea7e-efc4-4642-9f74-20793f2538a9`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{NOTES}\local_99bfea7e-efc4-4642-9f74-20793f2538a9\tiktok-smart-plus-research.md` | 4,089 | `abca7cd208c4` | copied → `docs/archive/side-session-notes/2026-10-19_tiktok-smart-plus-research.md` | Side-session note: TikTok Upgraded Smart+ API research, 10-19 |

### `{CHATS}\scratch-2026-10-19-d818cc`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{CHATS}\scratch-2026-10-19-d818cc\models\Cat home financial model.xlsx` | 205,240 | `d9013e52e6b9` | copied → `docs/archive/2026-10-19_niche-research/models/Cat home financial model.xlsx` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\reports\Cat home financial model.md` | 81,876 | `1d52b9ac95ab` | copied → `docs/archive/2026-10-19_niche-research/reports/Cat home financial model.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\reports\Category brand subscription deep dive.md` | 97,443 | `004743986061` | copied → `docs/archive/2026-10-19_niche-research/reports/Category brand subscription deep dive.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\reports\Ecommerce niche discovery checkpoint 1.md` | 115,335 | `0f719cef62f5` | copied → `docs/archive/2026-10-19_niche-research/reports/Ecommerce niche discovery checkpoint 1.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\reports\Espresso and cat validation.md` | 86,872 | `adae45307a57` | copied → `docs/archive/2026-10-19_niche-research/reports/Espresso and cat validation.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Cat home financial model\acquisition_retention.md` | 37,749 | `21db25fb754d` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Cat home financial model/acquisition_retention.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Cat home financial model\cost_inputs.md` | 46,244 | `b28a7113a015` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Cat home financial model/cost_inputs.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Cat home financial model\model_outputs.md` | 22,190 | `795cab4b93fa` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Cat home financial model/model_outputs.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\car_detailing.md` | 37,354 | `75fb9e468d22` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/car_detailing.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\cat_home.md` | 34,257 | `da6a72906b33` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/cat_home.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\hard_water_and_dog_home.md` | 42,253 | `3ff4f9b1b4ae` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/hard_water_and_dog_home.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\home_barista.md` | 33,970 | `fc2a1491929f` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/home_barista.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\miniature_painting.md` | 40,717 | `993a2587a4c5` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/miniature_painting.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\pickleball.md` | 38,299 | `90fd4abec149` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/pickleball.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Category brand subscription deep dive\subscription_operations.md` | 44,279 | `586964f2fcc9` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Category brand subscription deep dive/subscription_operations.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\beauty_personal_care.md` | 47,645 | `cd01c6ff530a` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/beauty_personal_care.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\fitness_baby_travel_workspace.md` | 36,753 | `ae5affb29903` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/fitness_baby_travel_workspace.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\food_kitchen_garden.md` | 35,355 | `52867c3ad539` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/food_kitchen_garden.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\hobby_outdoor_auto.md` | 38,831 | `df0404bfbb80` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/hobby_outdoor_auto.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\home_cleaning_sleep.md` | 33,286 | `4a983deb011f` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/home_cleaning_sleep.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\macro_subscription_landscape.md` | 36,856 | `625be60ec856` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/macro_subscription_landscape.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Ecommerce niche discovery checkpoint 1\pets_aquarium.md` | 44,563 | `2294b84cecaa` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Ecommerce niche discovery checkpoint 1/pets_aquarium.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Espresso and cat validation\cat_competition_marketing.md` | 29,378 | `a924d626a5a0` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Espresso and cat validation/cat_competition_marketing.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Espresso and cat validation\cat_suppliers.md` | 53,667 | `3cded4a43c0f` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Espresso and cat validation/cat_suppliers.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Espresso and cat validation\espresso_competition_marketing.md` | 35,659 | `c28f13130ba9` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Espresso and cat validation/espresso_competition_marketing.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Espresso and cat validation\espresso_suppliers.md` | 45,053 | `6313ef9aae3e` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Espresso and cat validation/espresso_suppliers.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |
| `{CHATS}\scratch-2026-10-19-d818cc\research_notes\Espresso and cat validation\live_demand_signals.md` | 33,222 | `1aab58df13d5` | copied → `docs/archive/2026-10-19_niche-research/research_notes/Espresso and cat validation/live_demand_signals.md` | E-commerce niche research 10-19 (chat "E-commerce niche research and validation"), before the store niche was chosen |

### `{CHATS}\scratch-2026-10-17-c2ad34`

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{CHATS}\scratch-2026-10-17-c2ad34\.dockerignore` | 138 | `2b4bb1c9f3e5` | copied → `docs/archive/2026-10-19_shopify-hub-server/.dockerignore` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\.env.example` | 8,225 | `ac6825372a1d` | copied → `docs/archive/2026-10-19_shopify-hub-server/.env.example` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\.gitattributes` | 36 | `41c906784939` | copied → `docs/archive/2026-10-19_shopify-hub-server/.gitattributes` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\.gitignore` | 378 | `0d918a78aacb` | copied → `docs/archive/2026-10-19_shopify-hub-server/.gitignore` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\alembic.ini` | 618 | `3d252947f831` | copied → `docs/archive/2026-10-19_shopify-hub-server/alembic.ini` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docker-compose.yml` | 3,649 | `1bc3a41184a7` | copied → `docs/archive/2026-10-19_shopify-hub-server/docker-compose.yml` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\Dockerfile` | 1,025 | `f5b756136188` | copied → `docs/archive/2026-10-19_shopify-hub-server/Dockerfile` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\pyproject.toml` | 1,614 | `06f9c60c0ecd` | copied → `docs/archive/2026-10-19_shopify-hub-server/pyproject.toml` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\README.md` | 8,273 | `737972e7503f` | copied → `docs/archive/2026-10-19_shopify-hub-server/README.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tiktok-smart-plus.diff` | 38,106 | `bec17ed90d99` | copied → `docs/archive/2026-10-19_shopify-hub-server/tiktok-smart-plus.diff` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\actions.py` | 3,917 | `502416db0f2e` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/actions.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\alerts.py` | 2,656 | `d7c48e21b72c` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/alerts.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\approvals.py` | 14,810 | `c60280734d30` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/approvals.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\attribution.py` | 8,502 | `d336a1dec7bd` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/attribution.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\business_settings.py` | 6,186 | `7fd8b033928f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/business_settings.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\cli.py` | 28,858 | `df579f5c43ce` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/cli.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\collect.py` | 3,752 | `8b700896fb0f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/collect.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\config.py` | 10,857 | `ed642d3243fb` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/config.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\daily_report.py` | 6,716 | `60f1fb4fdc91` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/daily_report.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\db.py` | 1,500 | `0ce097052552` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/db.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\guardrails.py` | 10,224 | `a331cc60504c` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/guardrails.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\health.py` | 5,680 | `9046dc3bc8ac` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/health.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\log.py` | 5,220 | `d070f7c41bf7` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/log.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\main.py` | 3,351 | `7fafdaef7ea7` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/main.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\profit.py` | 4,113 | `1c6dc922ec3d` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/profit.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\queue.py` | 559 | `6b4029e34439` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/queue.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\scheduler.py` | 2,441 | `cb1ef8c098a5` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/scheduler.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\storage.py` | 3,212 | `2ddb1f6465b0` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/storage.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\webhooks.py` | 6,280 | `5810d563cc9f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/webhooks.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\worker.py` | 798 | `abb63abe6f1b` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/worker.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\__init__.py` | 73 | `c61e3e9554ec` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\analytics\periods.py` | 2,740 | `6697134b7c00` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/analytics/periods.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\analytics\reports.py` | 19,786 | `372d814644dc` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/analytics/reports.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\analytics\__init__.py` | 93 | `9a9cc222f238` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/analytics/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\conversions\events.py` | 5,721 | `037806de87bf` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/conversions/events.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\conversions\hashing.py` | 1,401 | `b1a51cadfad5` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/conversions/hashing.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\conversions\senders.py` | 9,905 | `8330ed97c4e0` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/conversions/senders.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\conversions\service.py` | 16,099 | `2a0b291637cb` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/conversions/service.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\conversions\signals.py` | 1,561 | `ba86a6b69216` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/conversions/signals.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\conversions\__init__.py` | 778 | `05cc8989cd92` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/conversions/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\creatives\briefs.py` | 6,444 | `53b534675e36` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/creatives/briefs.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\creatives\media.py` | 3,347 | `357d45b5345f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/creatives/media.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\creatives\pipeline.py` | 19,550 | `fb6c4f5c6dbb` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/creatives/pipeline.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\creatives\__init__.py` | 96 | `308bd37a098d` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/creatives/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\google_oauth.py` | 3,759 | `e0f7d14a5d1c` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/google_oauth.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\higgsfield.py` | 9,232 | `ec4c6640206f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/higgsfield.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\http.py` | 3,170 | `cc24bd97a129` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/http.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\__init__.py` | 74 | `2871bb1a5873` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\base.py` | 9,274 | `249a470a0b8c` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/base.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\google.py` | 22,145 | `22d3c591241b` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/google.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\meta.py` | 16,988 | `bbcaf4563c43` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/meta.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\registry.py` | 1,293 | `090e808771c8` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/registry.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\sync.py` | 6,700 | `b124b7cbee34` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/sync.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\tiktok.py` | 25,338 | `c72dd4fd5937` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/tiktok.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\ads\__init__.py` | 91 | `6c59a87dd8b0` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/ads/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\shopify\auth.py` | 3,957 | `1e722e7f1a0c` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/shopify/auth.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\shopify\client.py` | 5,470 | `5c0a5b1f4b31` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/shopify/client.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\shopify\mapping.py` | 7,872 | `127887d7be49` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/shopify/mapping.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\shopify\queries.py` | 3,578 | `2e9ad1bed6c9` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/shopify/queries.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\shopify\sync.py` | 11,649 | `3cbb98ccfe37` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/shopify/sync.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\integrations\shopify\__init__.py` | 70 | `fab394b17604` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/integrations/shopify/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\ads.py` | 1,357 | `66f539d62326` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/ads.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\analytics.py` | 1,374 | `d0ae15f58a0e` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/analytics.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\conversions.py` | 2,421 | `f021d769a27f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/conversions.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\creatives.py` | 1,130 | `baba1cd31634` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/creatives.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\housekeeping.py` | 1,140 | `b9b952218236` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/housekeeping.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\registry.py` | 4,382 | `29fea9ece14f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/registry.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\reports.py` | 551 | `78c7585c23ce` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/reports.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\shopify.py` | 4,826 | `890e510036f2` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/shopify.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\tracking.py` | 2,217 | `66828f1981db` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/tracking.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\watchdog.py` | 2,006 | `230d7f699583` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/watchdog.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\jobs\__init__.py` | 23 | `7f0010ead249` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/jobs/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\mcpserver\oauth.py` | 19,390 | `a2fbf42938e0` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/mcpserver/oauth.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\mcpserver\server.py` | 22,659 | `cf7bf38bcb69` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/mcpserver/server.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\mcpserver\__init__.py` | 166 | `74ab91bc86ce` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/mcpserver/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\ml\bandit.py` | 14,930 | `e9fc4656a58d` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/ml/bandit.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\ml\creative_metrics.py` | 5,114 | `9b35b146d458` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/ml/creative_metrics.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\ml\model.py` | 11,001 | `5d64cac47197` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/ml/model.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\ml\__init__.py` | 222 | `80b7daab0d5b` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/ml/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\models\ads.py` | 5,892 | `dbb5ce790ca6` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/models/ads.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\models\base.py` | 3,923 | `063b37e8c1ed` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/models/base.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\models\commerce.py` | 9,885 | `7f4bfaca9b2f` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/models/commerce.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\models\creatives.py` | 7,604 | `3244641c2414` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/models/creatives.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\models\ops.py` | 11,709 | `dc44f29e0303` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/models/ops.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\app\models\__init__.py` | 1,546 | `908b968f0ecd` | copied → `docs/archive/2026-10-19_shopify-hub-server/app/models/__init__.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\Caddyfile` | 939 | `07ee96656040` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/Caddyfile` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\garage\garage.toml.template` | 750 | `84092a6105de` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/garage/garage.toml.template` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\systemd\shopify-hub-backup.service` | 287 | `ae0653336ce9` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/systemd/shopify-hub-backup.service` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\systemd\shopify-hub-backup.timer` | 187 | `dbf68410c58f` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/systemd/shopify-hub-backup.timer` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\systemd\shopify-hub-restore-test.service` | 231 | `772cd781b118` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/systemd/shopify-hub-restore-test.service` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\systemd\shopify-hub-restore-test.timer` | 140 | `5312f2ddbc6c` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/systemd/shopify-hub-restore-test.timer` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\deploy\systemd\shopify-hub.service` | 527 | `dca28d40fc7e` | copied → `docs/archive/2026-10-19_shopify-hub-server/deploy/systemd/shopify-hub.service` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\ad-platforms.md` | 9,367 | `b1060d1df5bc` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/ad-platforms.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\backups.md` | 4,298 | `e072f2bac688` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/backups.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\cloudflare-tunnel.md` | 2,466 | `99a0760b5f70` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/cloudflare-tunnel.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\conversions.md` | 5,529 | `050ec58128e3` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/conversions.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\creatives.md` | 3,817 | `4caa2a17e2f1` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/creatives.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\guardrails.md` | 3,598 | `ff0237024f11` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/guardrails.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\mcp.md` | 4,554 | `7064f4aceba9` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/mcp.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\ml.md` | 4,290 | `fc8211d85609` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/ml.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\proxmox.md` | 3,701 | `927ddea3bf02` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/proxmox.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\shopify.md` | 5,049 | `08e59dafb0dd` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/shopify.md` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\docs\examples\brief.json` | 479 | `919862fc2dba` | copied → `docs/archive/2026-10-19_shopify-hub-server/docs/examples/brief.json` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\env.py` | 1,691 | `548c062e334f` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/env.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\script.py.mako` | 616 | `412ad6a828a6` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/script.py.mako` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\versions\0001_initial_schema.py` | 48,535 | `2091556ed7c2` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/versions/0001_initial_schema.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\versions\0002_sync_state_webhook_events.py` | 2,588 | `fdd8282bcf77` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/versions/0002_sync_state_webhook_events.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\versions\0003_conversions.py` | 4,034 | `595c2143230e` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/versions/0003_conversions.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\versions\0004_mcp_oauth.py` | 2,957 | `966640beeb7d` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/versions/0004_mcp_oauth.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\migrations\versions\0005_analytics_ml.py` | 4,816 | `782d6a4cf1ef` | copied → `docs/archive/2026-10-19_shopify-hub-server/migrations/versions/0005_analytics_ml.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\backup.sh` | 3,592 | `bd022055b48c` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/backup.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\deploy-web-pixel.sh` | 1,809 | `4fa021010ac0` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/deploy-web-pixel.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\deploy.sh` | 2,066 | `a5426ce31250` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/deploy.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\garage-init.sh` | 2,277 | `9f8b29a3f877` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/garage-init.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\lib.sh` | 2,326 | `dc986d4b19b9` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/lib.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\restore-test.sh` | 2,465 | `1691f73e0de5` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/restore-test.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\set-secret.sh` | 677 | `546398c4fd8a` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/set-secret.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\scripts\setup.sh` | 3,673 | `d1e04caf4e49` | copied → `docs/archive/2026-10-19_shopify-hub-server/scripts/setup.sh` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\shopify-app\package.json` | 107 | `e20074ba0b1b` | copied → `docs/archive/2026-10-19_shopify-hub-server/shopify-app/package.json` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\shopify-app\shopify.app.toml.template` | 678 | `90020ed7e0a6` | copied → `docs/archive/2026-10-19_shopify-hub-server/shopify-app/shopify.app.toml.template` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\shopify-app\extensions\hub-pixel\package.json` | 165 | `5456f52e5c5f` | copied → `docs/archive/2026-10-19_shopify-hub-server/shopify-app/extensions/hub-pixel/package.json` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\shopify-app\extensions\hub-pixel\shopify.extension.toml` | 519 | `f33dd888f728` | copied → `docs/archive/2026-10-19_shopify-hub-server/shopify-app/extensions/hub-pixel/shopify.extension.toml` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\shopify-app\extensions\hub-pixel\src\index.js` | 3,683 | `9e9e119ab45c` | copied → `docs/archive/2026-10-19_shopify-hub-server/shopify-app/extensions/hub-pixel/src/index.js` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\ads_mock.py` | 2,133 | `6788f9dd5fbf` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/ads_mock.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\conftest.py` | 4,210 | `a924896871bb` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/conftest.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\shopify_fixtures.py` | 5,027 | `b9aa9bcf385c` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/shopify_fixtures.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_actions.py` | 3,009 | `8cd1fba2c642` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_actions.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_ads_google.py` | 12,083 | `64dfee4e4a4b` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_ads_google.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_ads_meta.py` | 8,931 | `7c4dd5b71903` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_ads_meta.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_ads_sync.py` | 4,922 | `0a21e030e5b6` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_ads_sync.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_ads_tiktok.py` | 17,039 | `22db33317c8a` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_ads_tiktok.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_attribution.py` | 4,530 | `01062f5b94a8` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_attribution.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_conversions.py` | 18,747 | `5579ef21a60f` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_conversions.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_creatives.py` | 17,645 | `e724da1f3bb4` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_creatives.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_guardrails.py` | 9,793 | `5ae70b325f64` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_guardrails.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_higgsfield.py` | 5,459 | `ef07527fa758` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_higgsfield.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_logging.py` | 1,974 | `a9f43531a1df` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_logging.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_mcp.py` | 23,058 | `c494f22731ea` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_mcp.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_migrations_and_settings.py` | 3,650 | `fc42fe828c61` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_migrations_and_settings.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_ml.py` | 10,233 | `a3440f79805c` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_ml.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_ops.py` | 7,269 | `7227742bdcce` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_ops.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_profit.py` | 2,414 | `ea70f573af9f` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_profit.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_profit_views.py` | 6,662 | `32db4599c4e0` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_profit_views.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_shopify_client.py` | 8,216 | `68062b79b89b` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_shopify_client.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_shopify_sync.py` | 7,780 | `2eb0d21ad3aa` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_shopify_sync.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |
| `{CHATS}\scratch-2026-10-17-c2ad34\tests\test_webhooks.py` | 5,849 | `091747e989ba` | copied → `docs/archive/2026-10-19_shopify-hub-server/tests/test_webhooks.py` | Self-hosted Shopify hub server source (chat "Shopify store hub MCP server"), 10-17..10-19; .venv/caches not copied |

### `{CHATS}\scratch-2026-10-23-2ef2f6` (chat "Dashboard 2.0" and its forks; filed earlier on 10-28, rechecked now)

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P01-A02-base-cable-knit-dress.mp4` | 19,348,528 | `f78e092fa49c` | already in Hub at `assets/EC-P01-A02-H01-V01/base_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P01-A02-frames.jpg` | 352,292 | `0b0b53e44bbd` | already in Hub at `assets/EC-P01-A02-H01-V01/review_frames.jpg` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P01-A03-frames.jpg` | 982,326 | `bc0cffa1cd6d` | already in Hub at `assets/EC-P01-A03-H01-V01/review_frames.jpg` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P01-A03-tryon-ad-cable-knit-dress.mp4` | 18,446,543 | `ef31c61e8cf2` | already in Hub at `assets/EC-P01-A03-H01-V01/tryon_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P01-A05-H01-V02.mp4` | 11,209,820 | `e1998e77378c` | already in Hub at `assets/EC-P01-A05-H01-V02/tryon_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P01-A06-H01-V02.mp4` | 11,768,241 | `12620804d4d4` | already in Hub at `assets/EC-P01-A06-H01-V02/tryon_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P02-A03-tryon-ad-sweater-dress.mp4` | 13,401,222 | `e1dd16f6f8ae` | already in Hub at `assets/EC-P02-A03-H01-V01/tryon_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P02-A05-H01-V02.mp4` | 17,416,943 | `fe074aad1445` | already in Hub at `assets/EC-P02-A05-H01-V02/tryon_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\EC-P02-A06-H01-V02.mp4` | 12,630,424 | `30939e336490` | already in Hub at `assets/EC-P02-A06-H01-V02/tryon_raw.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\backup-candidates.jpg` | 186,318 | `1c57b3431a33` | already in Hub at `assets/_research/2026-10-24_backup_candidates.jpg` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\cover_1640x624.png` | 34,101 | `612e37b8b4cd` | already in Hub at `brand/facebook/cover_1640x624.png` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\ember-clove-logo.jpg` | 81,821 | `4c1cffc7253d` | already in Hub at `brand/ember-clove-logo.jpg` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\ember-clove-logo.png` | 76,950 | `2fd143ee136d` | already in Hub at `brand/ember-clove-logo.png`, `brand/facebook/profile_1000.png` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\ember-clove-logo.svg` | 394 | `0198f8646550` | already in Hub at `brand/ember-clove-logo.svg` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\hub-2.0-creative-testing-engine-prompt.md` | 13,530 | `1d33cacabcf9` | already in Hub at `docs/archive/hub-2.0-creative-testing-engine-prompt_2026-10-23_first-draft.md` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\profile_1000.png` | 76,950 | `2fd143ee136d` | already in Hub at `brand/ember-clove-logo.png`, `brand/facebook/profile_1000.png` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\test-product-photos.jpg` | 246,069 | `75b4dfd76e45` | already in Hub at `assets/_research/2026-10-24_product_picks_P01_P02_backup.jpg` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\tiktok_upload\EC-P01-A03-H01-V01.mp4` | 7,445,446 | `472c7746636f` | already in Hub at `assets/EC-P01-A03-H01-V01/EC-P01-A03-H01-V01_tiktok.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\tiktok_upload\EC-P01-A05-H01-V02.mp4` | 7,322,857 | `29996224a50e` | already in Hub at `assets/EC-P01-A05-H01-V02/EC-P01-A05-H01-V02_tiktok.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\tiktok_upload\EC-P01-A06-H01-V02.mp4` | 7,528,317 | `efc860c768c2` | already in Hub at `assets/EC-P01-A06-H01-V02/EC-P01-A06-H01-V02_tiktok.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\tiktok_upload\EC-P02-A03-H01-V01.mp4` | 7,303,454 | `89a9e1250ab8` | already in Hub at `assets/EC-P02-A03-H01-V01/EC-P02-A03-H01-V01_tiktok.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\tiktok_upload\EC-P02-A05-H01-V02.mp4` | 7,424,043 | `83578e109c9b` | already in Hub at `assets/EC-P02-A05-H01-V02/EC-P02-A05-H01-V02_tiktok.mp4` |  |
| `{CHATS}\scratch-2026-10-23-2ef2f6\tiktok_upload\EC-P02-A06-H01-V02.mp4` | 7,409,090 | `7d64d82d6bec` | already in Hub at `assets/EC-P02-A06-H01-V02/EC-P02-A06-H01-V02_tiktok.mp4` |  |

### `{CHATS}\scratch-2026-10-26-3c3380` — remaining files

| Source | Bytes | SHA-256 | Result | Description |
|---|---:|---|---|---|
| `{CHATS}\scratch-2026-10-26-3c3380\FlowFit-report.md` | 13,564 | `da0589dc029f` | owner to decide (not copied) | Report on the FlowFit TikTok account (@reddit.poett), a different account in the same Business Center |
| `{CHATS}\scratch-2026-10-26-3c3380\flowfit-posts.csv` | 8,170 | `022c59820c35` | owner to decide (not copied) | FlowFit post list |
| `{PADS}\scratch-2026-10-26-3c3380\017f46a5-72c1-493e-b24b-730bd3f0247a\scratchpad\add_stats.py` | 3,602 | `afe44ab99447` | owner to decide (not copied) | FlowFit report helper |
| `{PADS}\scratch-2026-10-26-3c3380\017f46a5-72c1-493e-b24b-730bd3f0247a\scratchpad\build_flowfit.py` | 9,664 | `4844760c6f9a` | owner to decide (not copied) | Builds the FlowFit report |

### Secrets (listed by path only, not copied, not hashed into this file)

| Source | Result |
|---|---|
| `~\Downloads\key.txt` | secret, not copied |
| `~\Downloads\openrouter_api_key.txt` | secret, not copied |
| `~\Downloads\client_secret_579728600010-….apps.googleusercontent.com.json` | secret, not copied |
| `%TEMP%\ec_q\tool\target.json` | secret (signed Shopify upload URL), not copied |
