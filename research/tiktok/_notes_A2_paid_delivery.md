# Checkpoint A, analyst notes A2: TikTok paid-ad delivery, optimization and metric definitions

- **Prepared:** 2026-10-24, for Ember & Clove (US Shopify apparel, emberandclove.com)
- **Scope:** Master prompt Phase 1.1 (paid-delivery items), Phase 1.2, Phase 7.2 metric definitions, and the Phase 9 evidence standard. The For You organic recommendation system is out of scope; see `_notes_A1_organic_recommendation.md`.
- **Account context assumed:** New ad account with no spend and no purchases. TikTok pixel installed through the Shopify TikTok app, catalog connected. Planned test budget about $25/day per ad group. Break-even CPA about $31–35, AOV about $45–53. Creative: 15-second AI-presenter UGC-style videos, labelled AI-generated, posted from the brand's TikTok identity.
- **No-spend statement:** Nothing in this research touched the ad account, Shopify, Higgsfield or any campaign. No money was spent.

## Evidence key

| Code | Meaning |
|---|---|
| **A** | Official TikTok documentation (Help Center, TikTok for Business blog, Community Guidelines, Newsroom) |
| **B** | Credible experiment or peer-reviewed research |
| **C** | Industry or practitioner source (agency or vendor blogs, tools) |
| **D** | Our own hypothesis or arithmetic; not verified |

Each recommendation is also tagged with one of three statuses:

- **[currently supported]:** stated in current official documentation.
- **[outdated]:** superseded or contradicted by newer official pages.
- **[verify in account]:** depends on account rollout, the interface, or conflicting pages.

## How the sources were gathered (read this before relying on quotes)

- **Tools.** I used web search and a page-fetch tool. The fetch tool returns a model-generated reading of each page, not raw HTML. Short quotes below are what that tool reported as page text. Spot-check any quote that drives a decision in the live Help Center.
- **Which ads.tiktok.com/help pages opened.** Most `ads.tiktok.com/help/article/<slug>` pages opened and showed a "Last updated" month. Some legacy `?aid=` URLs now redirect to different articles. Example: `aid=11234` now returns the June 2026 learning-phase article, not the older text that search engines still show for that URL.
- **What failed to open:**
  - `business-api.tiktok.com/portal/docs` (Marketing API docs) is JavaScript-rendered. It returned only its title, so API field names below come from third-party connector mirrors (C).
  - The TikTok Support AIGC-label article redirected to a page with no readable content.
  - The PDF "Fundamentals_ENG.pdf" (EMEA SMB Newbie Ecommerce Best Practices One-Pager) was compressed and unreadable.
  - The page `about-updates-to-click-and-conversion-rate-metrics` returned the general reporting overview instead.
- **Search-only items.** Items marked "(search snippet only)" were seen in search results but not opened.

---

## 1. How the ad auction ranks ads

**What TikTok officially says (A):**

- **Ranking.** The bidding-strategies page (updated Sep 2026) says TikTok "ranks ads by how much advertisers bid and how relevant the ads are to users." The bidding-methods page (Aug 2025) says the auction "ranks ads based on bid price and the relevance an ad might have." Both are [currently supported].
- **oCPM.** The bid is still per thousand impressions, but delivery targets people likely to take the chosen action. oCPM is the default for conversion objectives (bidding-methods page and glossary).
- **No published formula.** TikTok does not publish a formula such as bid × estimated action rate × quality. It also does not publish a second-price rule, an "ad relevance diagnostics" score, or a quality-ranking metric. Bidding-methods describes only billing events: CPM/oCPM charged per impression, CPC per click, CPV per 6-second view or interaction.
- **Where the formula comes from.** The common "eCPM = bid × estimated action rate × ad quality" and "winner pays just enough to beat the next bidder" claims come from agency blogs (lseo.com, jemsu.com, tlinky.com; search snippets only). This is **C**. It is plausible by analogy with Meta and Google, but TikTok does not state it. Do not present it as fact.

**Negative feedback (A, partial):**

- The Help Center page "Why some ads are rejected after they're approved" (Nov 2025, search snippet only) says an approved ad can be re-reviewed when people "hide, block, report, or otherwise provide negative feedback." That is a moderation consequence.
- I found no official statement on how negative feedback changes auction rank or price. Any claim that it does is **D**.
- Users can see "About this ad" and hide advertisers (TikTok for Business blog, Aug 2022; ad-preference help page, Feb 2025; search snippets).

**Implications:**

- Creative quality affects delivery through relevance and predicted action. This is officially stated in general terms only, with no weights published (A).
- At a fixed bid, an ad that the system predicts will convert better should win more impressions per dollar. This is the logic of oCPM (A), but the size of the effect is unknown (D).

## 2. Objectives, optimization goals and events

### 2.1 Objectives and goals

- **Upgraded Smart+ experience** (Oct 2026). It supports Sales, Lead Generation, App Promotion and Traffic. Reach and Video Views remain as auction objectives on the bidding-strategies page (Sep 2026). (A)
- **Smart+ Web campaigns** (Mar 2026). Sales objective with a Website destination. Optimization goals listed: **Value, Conversion, Landing Page View, Click**. (A) [currently supported]
- **Traffic objective.** Optimizes for Clicks (the default) or Landing Page View (LPV page, Sep 2026). Traffic best practices (Mar 2026, search snippet) say to match the goal to the customer's consideration cycle. (A)
- **"Consideration signals" toggle.** A third-party claim says a January 21, 2026 Traffic toggle optimizes for "cost per consideration" or "cost per new buyer" (Dataslayer, Feb 2, 2026). TikTok's traffic pages do not mention it. This is **C**. [verify in account]
- **Video Views objective.** Optimizes for **focused view** with three options (Aug 2026), and its bidding method is "cost per focused view." (A)
  - 6-second focused view, for 1–6-second creatives.
  - 15-second focused view, for 7–15-second creatives.
  - 15-second focused view with a completion toggle, for 16–60-second creatives.
- **Implication for our 15-second ads.** A Video Views campaign would buy *15-second focused views*, not purchases. That audience is people the system predicts will watch or interact, not buy (A for what is optimized; D for the downstream effect).

### 2.2 Events (pixel and Shopify)

- **Standard event names** (Apr 2026) include ViewContent, AddToCart, InitiateCheckout, AddPaymentInfo and **Purchase**. The page recommends Purchase "when placing an order and making a purchase are the same." **CompletePayment and PlaceAnOrder no longer appear on the standard-events page.** (A)
- **Legacy names.** Third-party integrators report that legacy names were migrated in 2025 and are "soft-deprecated" (theadspend.com and weltpixel.com, search snippets). This is **C**.
- Older Help pages and reporting columns still use "Complete payment" names, for example "Payments completed (page)" and "Payment completion ROAS (page)" (page-events, Oct 2025). (A)
- **[verify in account]** Check which event names the Shopify TikTok app actually sends (Purchase or CompletePayment). Check which one appears as the "Conversion" optimization event.

### 2.3 What happens with zero conversion history

- **Maximum Results** (the old "Maximum Delivery" / lowest cost) "may see performance fluctuations and higher CPMs before passing the Learning Phase" (bidding-strategies, Sep 2026). (A)
- **New e-commerce advertisers** (page updated Feb 2025). (A) [currently supported but 20 months old; verify]
  - Start with at least 3 events: View Content, Add to Cart, Complete Payment.
  - Use **Add to Cart as the first optimization event**.
  - Use "at least $30 USD per day" for the first ad group.
  - Try Automatic Targeting first.
  - Turn on Automatic Advanced Matching and First Party Cookies.
- **Value optimization (VBO)** is unavailable until the account has "at least 20 attributed unique purchase events with value and currency" in any consecutive 7 days (VBO-for-web specifications, Jul 2025). Bid strategies under VBO are Highest Value and Minimum ROAS. CBO is supported. (A) [currently supported]
  - **For us: VBO, Highest Value and Minimum ROAS are not available at launch.**
- **Search Ads guidance** (Jul 2026, search snippet) advises starting on the most upper-funnel conversion and moving lower after about 14 stable days. It applies to Search Ads only, but it matches the web new-advertiser guidance. (A, different product)

## 3. Smart+, Upgraded Smart+, creative automation: current versus deprecated

| Product | Status (2025–2026) | Source and date | Category |
|---|---|---|---|
| **Upgraded Smart+ experience** | Merges manual and Smart+ setup into one flow: "full automation, partial automation, or fully manual." Rolling out; "may not be available to you yet." | about-updates-to-smart-plus (Oct 2026); how-to-create… (Oct 2026) | A [verify in account] |
| Fully automated mode | Automatic campaign budget. All ad groups must share the same optimization goal, event and budget settings. Automatic targeting and automatic placement are the defaults, and placement may include Pangle (the TikTok Ad Network). | how-to-create… (Oct 2026) | A |
| Manual mode inside upgraded flow | Ad group budgets, custom targeting ("Switch to custom targeting") and placement selection are available. | same | A |
| Ads as "asset groups" | "Ads will be generated based on combinations of your videos and ad texts." To force an exact pairing, add only one video and one text to an ad. Asset limits are inconsistent: one page says "up to 50" for both asset groups and creative assets. | same; about-updates (Oct 2026) | A (limits unclear) |
| **Smart+ Web Campaigns** (legacy Smart+) | Sales and Website destination. Placement is automatic only; to exclude Pangle you need a non-Smart+ campaign. Spark and non-Spark ads cannot be mixed. Up to 30 extra videos or images on catalog campaigns. | about-smart-plus-web-campaigns (Mar 2026) | A |
| **Smart+ Catalog Ads / Catalog Ads** | For Sales (Website/App), Traffic (upgraded Smart+) and Smart+. Formats: Carousel, Single video, Catalog video, Image Catalog Carousel. A search snippet of the how-to page says at least 4 in-stock, approved products are needed. | about-catalog-ads (Oct 2026); how-to-create-video-shopping-ads-catalog (snippet) | A |
| **Video Shopping Ads naming** | For website catalogs, the product is now "Catalog Ads." The "video-shopping-ads" URL slug survives. With TikTok Shop as destination, VSA can no longer be created (see GMV Max); VSA remains only with a Showcase destination. | gmv-max-migration (Mar 2026) | A |
| **Smart Creative** | Still documented. Combines assets, tests the most differentiated videos for 3–5 days at no more than 10% of budget, pauses fatigued videos and swaps in queued ones. A successor called **"Automate Creative"** is "to be rolled out over time." | smart-creative (Nov 2025) | A [verify in account] |
| **Automated Creative Optimization (ACO)** | The glossary still defines it. No 2025–2026 page found describing it as a current standalone feature. A search snippet mentions a 16-creatives-per-ad-group limit without ACO. Likely being absorbed into Smart Creative and Upgraded Smart+ asset combination. | glossary (date not captured) | A (definition only) [verify in account] |
| Auto-selected creatives / Creative Upgrades (formerly Creator+) | Auto-selection covers Smart+ App and Lead Gen campaigns per an Apr 2026 help snippet and a Jul 2026 product preview. Creative Upgrades bundles top past creatives, trending videos and AI assets, and assets can be reviewed or excluded before launch. | product preview blog (Jul 28, 2026) | A |
| "Recommended" tab and AI-generated assets | In eligible Web Traffic campaigns, generated assets can be set to "Add upon my approval," "Auto-add and notify," or "Don't Add." Automatic enhancements include AI CTA text, resizing and dubbing. | how-to-create… (Oct 2026) | A |
| **GMV Max** | Since Jul 2025 it is "the default and only supported campaign type" for TikTok Shop ads. It is **not relevant to external-website ads** and is not available in Canada. | gmv-max-migration (Mar 2026); product preview (Jul 2026) | A |
| **Custom Identity** (non-Spark display name and avatar) | "TikTok is phasing out the use of Custom Identity." With Identity on, only Spark Ads are possible. Trade press reports new campaigns must launch from linked accounts from early 2026. | identity (Apr 2026); ppc.land (Jan 27, 2026) | A + C [verify in account] |

**Implications for Ember & Clove:**

1. **Turn off AI asset auto-add.** If the account has the upgraded flow, set any AI asset generation or "Recommended" assets to "Add upon my approval" or "Don't Add." Otherwise TikTok-generated AI assets could run unreviewed against our claims rules. (A for the option exists; [verify in account].)
2. **Check the AIGC label on generated assets.** Smart+ or Symphony AI assets may carry their own AI labels. TikTok said in 2024 it auto-labels content made with its own AI tools (search snippet of press coverage). This is C. [verify in account]

## 4. Learning phase

**Current official text** ("About Learning Phase," updated **June 2026**) (A) [currently supported]:

- **Definition:** "a period during which our ad system identifies the best users" for the campaign target.
- **Stabilization:** "volatility starts to decline after about 25 campaign results or 7 days." This is described as when volatility eases, **not a formal exit rule**.
- **To complete learning, avoid three things:**
  - pausing campaigns or ad groups;
  - "Edits that retriggers the learning phase status" (the page does not say which edits);
  - "Unreasonable budget setting or creative volumes."
- **Automation campaigns.** The bidding best-practices page links to the learning article with link text referencing "7 days for automation campaigns" (Aug 2026). (A, indirect)

**Older guidance, now probably superseded** [outdated]. These come from search snippets for the same legacy URL `aid=11234`, which now serves the June 2026 article:

- "usually an oCPM ad group can expect a stable CPA after achieving 50 conversions"
- "50 conversions [is] the most significant indicator of passing the learning phase"
- fewer than 20 conversions in the first 10 days means a high chance of not passing
- a budget-jump example: $100 to $110 is fine, $100 to $300 restarts learning

Practitioner sources still repeat "50 conversions in 7 days" (Journify, Nestscale, Megadigital; search snippets). The 7-day window was never in the official text I saw. Treat **50 per 7 days as outdated or unofficial**. The current anchor is about 25 results or 7 days, and it is a volatility guideline, not a gate.

**"Learning limited" or "learning failed" status labels.** I found no official current page naming these statuses. [verify in account] Check what status text Ads Manager shows on an ad group in learning.

**Budget guidance for learning** (A, pages conflict; see section 5):

- "Tips to select your budget" (Aug 2026) sets minimum budgets by optimization type:
  - deep conversion (Add to Cart, Purchase): **10× current CPA, $200 floor**;
  - shallow conversion (for example Page View) and other high-funnel events: **50× CPA/CPR, $100 floor**;
  - installs: 20× CPA, $200 floor.
  - The page does not explicitly say these are daily amounts.
- "Bidding & Budget Solutions" (Aug 2026): ad group daily budget = **target CPA × 10 conversions**, "enough to get through the Learning Phase."
- Bidding best practices (Aug 2026): Maximum Results daily budget of 10× the average daily CPA from the past 7 days. Target Cost per Result budget of at least 10× the CPA bid.

**Arithmetic for our plan (D):**

- At $25/day and a break-even CPA of $31–35, a Purchase-optimized ad group buys about 0.7–0.8 purchases per day at break-even. That is about 5 per 7 days, roughly a fifth of the 25-result volatility guideline.
- TikTok's deep-conversion guidance implies $310–350 per ad group (10× CPA), or at least the $200 floor. **$25/day is roughly 8–14× below TikTok's stated minimum for Purchase optimization:** 8× below the $200 floor alone, and 12–14× below 10× CPA ($310–350).
- **Add to Cart optimization at $25/day:** reaching about 25 ATCs in 7 days needs an ATC cost of about $7 or less. Our ATC cost is unknown. Measure it in the first days (D).
- **Consequence:** at $25/day per ad group, expect the ad group to remain in learning and CPA to be volatile for the whole test. Treat early CPA and ROAS as directional (D, consistent with A).

## 5. Bidding, budgets, campaign structure, creative counts and refresh

### 5.1 Bid strategy names changed in 2026 (A) [currently supported; verify labels in account]

| Current label (Sep 2026) | Earlier label | Definition (official) |
|---|---|---|
| **Maximum Results** | Maximum Delivery / Lowest Cost | "a spend-based strategy which aims to deliver the highest volume of conversions within your defined budget." CPA will fluctuate. |
| **Target Cost per Result** | Cost Cap | "optimizes delivery towards a cost per action defined by the advertiser." Actual CPA "can be slightly higher or lower." Default for Reach and Video Views. |
| Bid Cap | Bid Cap | Glossary: a maximum cost per result. It is not on the Sep 2026 bidding-strategies page, which lists only the two strategies above. [verify] |
| Highest Value / Minimum ROAS | Same | Only under VBO, after 20 purchases with value in 7 days. |
| Hybrid bidding | n/a | Switch from Maximum Results to Target Cost per Result while spending. Set the target to the prior 3-day average CPA (Sep 2026 page, search snippet). |

- **Mapping caution.** The mapping old to new is my inference from matching definitions (D). TikTok does not say "renamed" on the pages I opened.

### 5.2 Budget rules (A; pages conflict) [verify in account]

- **Minimums:** campaign daily budget over $50, ad group daily budget over $20. Lifetime ad group minimum is $20 × days. The campaign budget should not be lower than the ad group budget. Budget type (daily or lifetime) cannot be switched after launch (budget page, Jul 2026).
  - **Our $25/day ad group clears the $20 minimum.**
  - **Campaign-level budget:** if one is set it must exceed $50/day. Leave it open, or use ad group budgets.
- **Budget-change rules disagree across current pages:**
  - Budget page (Jul 2026): no more than 40% per change during learning, no more than 30% after, no more often than every 2 days.
  - Budget best practices (Aug 2026): "within the 50% range" of the previous budget after learning. Wait at least 2 days between targeting, bid or budget changes. Avoid changes before learning passes.
  - Bidding best practices (Aug 2026): after learning, raise the budget "by at least 20%" at a time.
  - **Conservative synthesis (D):** do not change budgets during the test. If scaling later, use steps of about 20–30%, at least 2 days apart.
- **Budget types:** "For your campaign budget, leave it open initially" and "Use the daily budget instead of lifetime budget" for ad groups (Aug 2026). (A)
- **CBO.** Upgraded Smart+ calls it "Automatic campaign budget." It forces the same budget and bid strategies across ad groups (Oct 2026). (A)
  - **For a creative test, CBO reallocates spend toward early leaders.** That confounds comparisons. Use ad group budgets for controlled tests (D, consistent with Phase 7.4).

### 5.3 Structure and creative counts (A; pages differ)

- **Creative best practices** (Jun 2025): "between 3-5 different creatives per ad group." Use "3-5 diversified ad groups per campaign." Creatives "with large differences" work better when testing.
  - Refresh when delivery shows "a consistently declining trend" or daily new users are low.
  - Add new creatives to the existing ad group rather than creating a new one.
- **Search snippet** of a creative help article (not opened):
  - no more than 5 new creatives during exploration without Smart Creative;
  - update creative "every 7 days at least";
  - limit of 16 creatives per ad group without ACO.
- **Recommendations page** (snippet): goal of 3–5 unique creatives per ad group.
- **Account structure** (Feb 2025): run "diverse ad groups at the same time" and keep a balance of learning and post-learning ad groups. **Don't duplicate or bulk-copy freshly created ad groups**, "especially in accounts with weak performance history."
- **Implication (D):** 3–5 creatives × 3–5 ad groups × $25 = $75–125/day. That is above our test budget, so pick which official recommendation to compromise on. Recommended: **one ad group per hypothesis with 3–5 strongly differentiated creatives**, rather than many ad groups each starved of data.

### 5.4 Creative fatigue (A, C)

- Smart Creative detects fatigue in the first 3–5 days and swaps creatives (Nov 2025). (A)
- The creative best-practices page names falling delivery and falling daily new users as signals (Jun 2025). (A)
- No official frequency threshold for fatigue was found. Any threshold such as "frequency above X" is C or D.

## 6. Attribution, conversion counting, Events API and match quality

### 6.1 Attribution windows

- **Defaults.** TikTok Pixel and Web Events API advertisers default to **7-day click / 1-day view**. Options are click 1/7/14/28 days and view off/1/7 days (TikTok for Business blog, Jun 23, 2022). (A, old)
  - The ad-group-level attribution page (search snippet) says that if Attribution Manager was never changed, "new defaults apply, 7dc/1dv for web and app." (A)
  - The current opened version (Nov 2025) lists the same options but does not restate the default. **[verify in account]**
- **Windows lock at publish.** "Attribution settings cannot be changed once the ad group has been published." A new ad group is needed to change the window or event count (Nov 2025). (A) [currently supported]
  - **Decide the window before launch.** Changing it later means a new ad group and a restart of learning.
- **Event count.** "Every" applies to purchase optimization and VBO. "Once" applies to installs and non-purchase optimization (Nov 2025). (A)
- **Engaged view-through attribution (EVTA)** (Aug 2025). (A)
  - It "assigns credit to an ad when a user watches at least 6 seconds of the ad." For videos shorter than 6 seconds, the full duration counts.
  - Windows: Off, 1-day, 7-day or 28-day, "customizable during campaign setup."
  - EVTA conversions **are included in the Conversions column**. Custom columns can split conversions into click-through (CTA), view-through (VTA) and EVTA.
  - The page does not say whether EVTA is used for optimization, its default for web, or the priority between click, EVTA and VTA. **[verify in account]**
  - An older help page (Feb 2025, search snippet) listed CTA 1/7 days, EVTA 1/7 days and VTA off/1 day.
- **Effect on optimization.** No official statement found that the attribution window changes what delivery optimizes for. Meta's documentation does say this; for TikTok it is **D**.
- **TikTok counts versus Shopify** (D, with B support):
  - TikTok counts attributed conversions, including view-through and EVTA, by event time within its windows.
  - Shopify counts orders.
  - Expect TikTok "Purchases" to differ from Shopify orders. Reasons include view-through credit, cross-device matching, deduplication failures, and time-zone and attribution-date differences.
  - Peer-reviewed field experiments at Facebook found observational attribution methods frequently fail to recover the causal effect, sometimes by a factor of 3 or more (Gordon et al., *Marketing Science* 2019; abstract via search). (**B**, different platform)
  - Ad ROI is extremely noisy even in very large experiments (Lewis & Rao, *QJE* 2015; abstract via search). (**B**)
  - **Implication:** report TikTok-attributed and Shopify-observed numbers side by side, and never treat TikTok-attributed ROAS as causal.
- **Third-party claims.** One vendor says "79% of TikTok-attributed conversions were missing from last-click" models, citing internal TikTok surveys without a URL (Dataslayer, Feb 2026). This is **C** and unverifiable. Do not use it.

### 6.2 Events API, Shopify app and match quality (A)

- **Shopify app data-sharing levels** (Feb 2025):
  - **Standard:** pixel only. "Browser-based ad blockers can prevent the pixel" from collecting data.
  - **Enhanced:** pixel plus Events API and Advanced Matching.
  - **Maximum:** adds Shopify APIs, plus In-App Shopify Checkout (beta; it is shown when TikTok's delivery system decides, and merchants can opt out).
  - **[verify in account]** Confirm the Shopify app is on Enhanced or Maximum. Decide whether to opt in to In-App Shopify Checkout. It changes where checkout happens and may affect Shopify analytics (D).
- **Deduplication** (May 2025): event_id must be sent "through both Pixel and Events API." Deduplication requires a matching event name and event_id. Windows are 48 hours, with specific 5-minute and 48-hour rules for pixel and server overlap. A third-party snippet mentions a _ttp-cookie fallback; it is not on the opened page.
- **Event Match Quality (EMQ)** (Events Manager diagnostics page, Nov 2025):
  - the score is "a weighted average of your match key coverages";
  - **no official threshold is published**;
  - connection method is shown as "browser only," "server only," or "server & browser";
  - "Active" means the event was received in the last 7 days.
  - Third-party thresholds such as "above 7 is strong" come from Journify (C) and are not official.

## 7. Placements

- **Placement options** (eligible-placements page, Sep 2026). (A) Availability varies by country and objective.
  - **TikTok** (including TikTok Lite and PineDrama where available);
  - **Lemon8** (some countries);
  - **Global App Bundle** (CapCut, Fizzo; labelled Indonesia-only on that page; a Nov 2025 snippet lists CapCut, Fizzo and Melolo);
  - **TikTok Ad Network** (formerly TikTok Pangle).
- **Automatic placement** uses "smart calculations." It allocates budget by placement performance and may shift most traffic to one placement. Placement "cannot be changed after" the ad group is created. (A) [currently supported]
- **Smart+ Web** placement is automatic only. To exclude Pangle you need a non-Smart+ campaign (Mar 2026). (A)
  - In the upgraded flow, manual mode allows "Select placement" (Oct 2026). (A)
- **Implication (D):**
  - For a creative test where TikTok-feed watch behaviour is the subject, a manual TikTok-only placement keeps the conditions comparable.
  - Ad Network inventory is different apps with different viewing contexts, so its watch metrics are not comparable to TikTok-feed watch metrics.
  - The AI-content disclaimer for standard and clickable disclaimers requires "TikTok as the only selected placement" (add-disclaimers page, Sep 2025). That is another reason to pick TikTok-only placement. (A)

## 8. Spark Ads versus non-Spark ads, and TikTok Shop / GMV Max versus website

- **Spark Ads** (Jun 2026) are "a native ad format" that promotes organic posts from your own account or from authorized creators. (A)
  - Views, comments, shares, likes and follows earned while boosting are **credited to the original organic post**.
  - The authorization-code duration can be customized.
  - An Ads Manager account can hold up to 10,000 Spark Ads. Videos can be up to 10 minutes.
  - The page lists no performance statistics.
- **Identity** (Apr 2026). With Identity on, only Spark Ads are possible (own posts or authorized posts). Custom Identity, the only route for non-Spark ads, is being phased out. (A)
  - **For Ember & Clove:** we post from the brand's TikTok identity, so we are effectively on Spark Ads. **The AIGC disclosure route differs** (see section 10).
- **Trade press** (C) describes a "Show Through Ads Only" setting that keeps paid posts off the public profile (ppc.land, Jan 2026). **[verify in account]**
- **Whether paid boosting affects organic For You distribution** is not documented. Treat it as **D** and coordinate with the A1 notes.
- **TikTok Shop versus website.** GMV Max is the only Shop-ads campaign type since Jul 2025 (A). It is irrelevant while we sell on emberandclove.com. External-site sales use the Sales objective with a Website destination (Smart+ or manual) and the pixel/Events API (A).

## 9. Metric definitions (Phase 7.2)

These are from Help Center pages unless noted. "Ads Manager" means a reporting column exists on the cited page. API field names could not be read from the official API docs (JavaScript-rendered), so they come from third-party mirrors (C). **[verify]** them in the API before building pipelines.

| Metric | Official definition (paraphrase; short quotes) | Notes and traps | Source (updated) | Ads Manager | API field (C, unverified) |
|---|---|---|---|---|---|
| **Video views** | "Number of times your video started to play." Counted per impression; replays not counted. | This is a *play start*, not a watch. Do not use it as an attention metric. | video-play (Nov 2025) | Yes | `video_play_actions` (C) |
| **2-second video views** | Plays of at least 2 s in one impression session; replays excluded. Swiping away and back counts as a new impression and a new view. | Best available "stop" metric. Rate = 2-s views ÷ impressions (our derived ratio, not a TikTok column). | video-play (Nov 2025) | Yes | `video_watched_2s` (C) |
| **6-second video views** | Plays of at least 6 s, **or** played in full if under 6 s, **or** "received at least 1 engagement within the first 6 seconds." | **Not pure 6-s watch time.** Engagement can trigger it. A Rockerbox mirror describes the API field as a plain 6-s count, which conflicts with the official text. | video-play (Nov 2025) | Yes | `video_watched_6s` (C) |
| **6-second focused views** | Views of at least 6 s (or full if shorter) **or** an interaction in the first 6 s. Qualifying interactions: likes, follows, shares, clicks, hashtag, music, anchor and add-on clicks. Only for focused-view products. | Same trap. TikTok splits it into **"paid views"** (watch-only) and **"paid interactions"** (interaction without 6 s of watching). Use the paid-views split for watch analysis. | video-play (Nov 2025); video-views-objective (Aug 2026) | Focused-view advertisers only | `engaged_view` (C) |
| 15-second focused views (and paid views / paid interactions splits) | Same logic with a 15-s threshold. Billing basis for 15-s focused-view optimization. | Relevant if we ever run Video Views with 15-s creatives. | same | Focused-view advertisers only | `engaged_view_15s` (C) |
| Focused view 6-s / 15-s view rate | % of focused-view paid impressions viewed for 6 s / 15 s or in full. | Only for focused-view campaigns. | video-play (Nov 2025) | Same | n/a |
| **Average play time per video view** | Average play time per single view, **including replay time**. | Loops inflate it, especially in short (15-s) videos. Not the same as a share of the video watched. | video-play (Nov 2025) | Yes | `average_video_play` (C) |
| **Average play time per user** | Average total play time per user, **including replays**. | Rises with frequency and loops. | video-play (Nov 2025) | Yes | `average_video_play_per_user` (C) |
| **Video views at 25/50/75/100%** | Plays reaching that share of the video's length; per impression; replays not counted. 100% means "played 100% of its length." | Our best retention-curve proxy. Divide by video views or impressions ourselves; state the denominator. | video-play (Nov 2025) | Yes | `video_views_p25` / `_p50` / `_p75` / `_p100` (C) |
| **Impressions** | "Number of times ads were shown." | n/a | basic-data (Oct 2025) | Yes | `impressions` |
| **Reach** | "Number of unique users who saw ads at least once." The glossary says it is **estimated**. | Estimated, so do not sum it across days or ad groups. | basic-data (Oct 2025); glossary | Yes | `reach` (C) |
| **Frequency** | "Average number of times each user saw an ad over a given time period." | Depends on the date range. | basic-data (Oct 2025) | Yes | `frequency` (C) |
| **Clicks (all)** | Clicks "including social interactions." | Includes likes, profile and other taps, so it is not traffic. | basic-data (Oct 2025) | Yes | n/a |
| **Clicks (destination)** | "Number of clicks leading to a specified destination." The glossary adds: websites, apps, app store. | Our traffic metric. | basic-data (Oct 2025); glossary (snippet) | Yes | `clicks` (C) |
| **CTR (destination)** | Glossary (search snippet): % of times the ad was seen and clicked through to the destination. | The opened basic-data page did not show the CTR definition. The search snippet shows a July rename notice ("Total Engagements" became "Clicks (All)"; CTR (Destination) a name change only). **[verify]** the tooltip in Ads Manager. | glossary (snippet) | Yes | `ctr` (C) |
| CTR (all) | No official definition found. A third party (Databox) says it is all clicks ÷ impressions. | C. Don't use it for traffic decisions. | n/a | Likely | n/a |
| **Landing page view (LPV)** | Computed by TikTok when "the ad is clicked and the landing page loads successfully." Not a pixel event; distinct from ViewContent. Multiple page views in one session count as one LPV. | It is an optimization goal under Traffic (and listed for Smart+ Web Sales), and can be added via custom columns for any ad group. Expect it to differ from Google Analytics. | landing-page-view (Sep 2026) | Custom column | n/a |
| **CPM** | Cost per thousand impressions, used for bidding and reporting (glossary). | n/a | glossary | Yes | `cpm` (C) |
| **CPC (destination)** | "Average cost of each click to a specified destination." | n/a | basic-data (Oct 2025) | Yes | `cpc` (C) |
| Cost per 1,000 people reached | "Average cost to reach 1,000 unique users." | n/a | basic-data (Oct 2025) | Yes | n/a |
| **Conversions** | "Number of times an ad resulted in the selected optimization event." Includes EVTA conversions within the attribution settings (EVTA page). | Depends on the window, event count and optimization event. Split it into CTA/VTA/EVTA with custom columns. | basic-data (Oct 2025); EVTA (Aug 2025) | Yes | `conversion` (C) |
| **Conversion rate (CVR)** | "Percentage of conversions received out of all **impressions**." | **Trap: the default CVR denominator is impressions, not clicks.** | basic-data (Oct 2025) | Yes | `conversion_rate` (C) [verify the denominator] |
| **Conversion rate (CVR, clicks)** | "...out of all destination clicks." | Use this, or compute purchases ÷ clicks (destination) ourselves. | basic-data (Oct 2025) | Yes | n/a |
| **Cost per conversion (CPA)** | "Average amount spent per conversion." | TikTok-attributed. Compare it with Shopify-observed orders. | basic-data (Oct 2025) | Yes | `cost_per_conversion` (C) |
| Adds to cart / Checkouts initiated / Payments completed (page) | "The number of page add to cart [etc.] actions attributed to your ads." | Attributed counts, not Shopify counts. | page-events (Oct 2025) | Yes | n/a |
| Unique payment completion rate (page) | % of page complete-payment actions "from all clicks attributed to your ads." | Denominator: attributed clicks. | page-events (Oct 2025) | Yes | n/a |
| **Payment completion ROAS (page)** | "The return on ad spend (ROAS) from page complete payment actions." The value metric is "Payment completion value (page)." | TikTok-attributed revenue ÷ spend, not Shopify revenue and not margin. | page-events (Oct 2025) | Yes | `complete_payment_roas` (C) |
| CPV billing | Charged at the first of: a 6-s view, a 6-s accelerated view, or an interaction in the first 6 s. | Applies to CPV bidding only. | bidding-methods (Aug 2025) | n/a | n/a |

**Metrics we did not find documented.** No swipe-away or skip rate, no second-by-second retention curve, no replay count, and no "hook rate" or "hold rate" columns.

- **Hook rate and hold rate are tool-defined ratios (C).** Motion's cheat sheet (Apr 15, 2026) defines TikTok hold rate as "% of users who watched the first 6s, or completely played." Other tools define hold rate as 6-s views ÷ 2-s views.
- **Reporting rule:** state the formula whenever we report one of these ratios. Because of the engagement route, use the focused-view "paid views" split (or 2-s and percentage views) rather than plain 6-s views when the claim is about watch time.

## 10. AI-generated content in ads: labelling and policy

- **Ads Manager AIGC toggle** (add-disclaimers page, Sep 2025). (A) [currently supported]
  - The toggle reads "This ad contains AI-generated content." It is eligible when the ad is a TikTok ad, **is not a Spark ad**, and contains image, video or audio that is "fully AI-generated or significantly modified by AI."
  - It cannot be changed after submission unless the media changes.
  - **Creating or duplicating a campaign resets the toggle.**
- **Disclaimer categories** (about-ad-disclaimers, Sep 2025). (A)
  - AI-generated, synthetic or manipulated media is listed under **"Mandatory disclaimers."** The label shows at the bottom of the in-feed ad for its full duration.
  - The feature may need a sales representative to enable it.
- **Spark Ads (our case).** Spark Ads are excluded from the Ads Manager toggle. Because they run as organic posts, they must follow the Community Guidelines' AI-disclosure rules, using the organic AIGC label set when posting (add-disclaimers page, Sep 2025). (A)
  - **For Ember & Clove:** the "labelled AI-generated" requirement must be met on the organic post itself before it is boosted. Verify the label shows on the ad preview.
  - **Re-check the toggle on every new or duplicated campaign** for any non-Spark ad.
- **Community Guidelines** (released Aug 25, 2026; effective Sep 24, 2026). (A)
  - "we require creators to label AI-generated or significantly edited content that shows realistic-looking scenes or people."
  - "Unlabeled content may be removed, restricted, or labeled by our team."
  - The Deceptive Behaviors section prohibits impersonation and "fake reviews."
  - **Implication:** an AI presenter must never be presented as a real customer giving a testimonial, even when labelled. Labelling does not cure deception (A for the policies; the application to testimonials is our reading).
- **C2PA auto-labelling.** TikTok Newsroom (May 9, 2024; search snippets and press coverage) says TikTok reads C2PA Content Credentials to auto-label AIGC uploaded from some other platforms. It also said it would attach credentials to TikTok-made content. (A, old; current rollout unverified)
  - **Implication (D):** Higgsfield or other generator exports may carry C2PA metadata and be auto-labelled anyway.
- **Mandatory AI disclosure for ads from July 21, 2026, and penalty tiers.** Agency blogs report both (Stellar Search, Aug 12, 2026; Common Thread Collective, search snippet). Neither cites a TikTok URL. This is **C**. **[verify]** in TikTok Advertising Policies. The four-tier penalty ladder is especially unverified.
- **Virtual presenters.** TikTok sells licensed-actor stock avatars through Symphony (2024 press coverage, search snippets). The Jul 2026 product preview mentions upgraded UGC-style Symphony Avatars. (A for existence)
  - No official ad-policy page specifically on third-party virtual presenters was found. The applicable rules are the AIGC label, the realistic-people labelling requirement, and the misleading/fake-review prohibitions.
  - 2023 coverage of the Community Guidelines says synthetic likenesses of private figures, and endorsements by synthetic public figures, are not allowed (search snippets). That is C, reporting older A text not opened.
  - **Implication (D):** avoid AI presenters that resemble real people.

## 11. Mechanisms: strong watch time but poor sales, and the reverse

None of these is quantified by TikTok. Categories are given per mechanism.

### Strong watch time, poor sales

1. **Objective mismatch.** Video Views optimizes for focused views and delivers to people predicted to watch or interact, not to buy. (A for what is optimized; D for the downstream gap)
2. **Metric inflation.** 6-s and focused views count interactions. Average play time includes replays, so a looping 15-s video inflates "watch time" without more attention to the product. (A for the definitions; D for the effect)
3. **Entertainment without product relevance or offer.** A loud hook can stop the scroll without relevance to the product. If hook and hold are strong but CTR is weak, the CTA or value proposition is weak. If CTR is strong but CVR is weak, look at the landing page, offer, price, trust or checkout. (C: Nestscale, Coupler, Motion; matches Phase 7.3 diagnostic rules)
4. **Audience and placement composition.** Automatic placement shifts budget toward placements where creatives perform well. Ad Network inventory may show different watch behaviour. The auction may serve cheap-impression audiences with low purchase intent. (A for allocation behaviour; D for the effect)
5. **Measurement loss.** Ad blockers prevent pixel collection, and without the Events API some purchases go unseen. Sales then look poor in TikTok while Shopify records them. (A for pixel blocking; D for size)

### Low engagement, strong purchase efficiency

1. **oCPM optimization.** It targets people "likely to take" the action. A Sales/Conversion ad group can find buyers even when its creative gets few social interactions. (A for the mechanism; D for the size)
2. **Early click-outs.** High-CTR assets "may have a lower thruplay if people are clicking out early" (Motion, C). Low completion can be a symptom of effective direct response.
3. **Warm and retargeting delivery.** Catalog carousel is "ideal for… prospecting, or retargeting" (A). Warm users may convert with little engagement (D).
4. **Attribution credit capture.** View-through and EVTA credit can be assigned to people who would have bought anyway. Observational attribution can be badly biased (B, Gordon et al. 2019). Strong reported efficiency may partly be credit capture, not causation (D for TikTok specifically).
5. **Small samples.** With about 5 purchases a week, a "winner" is often noise (B, Lewis & Rao 2015; D in application).

## 12. Recommendations for a new $25/day account with zero conversions

| # | Recommendation | Evidence | Status |
|---|---|---|---|
| R1 | Expect a $25/day Purchase-optimized ad group to stay in learning. Treat early CPA and ROAS as directional. TikTok's deep-conversion minimum is 10× CPA with a $200 floor. | A (Aug 2026) + D arithmetic | currently supported |
| R2 | Consider Add to Cart (or Initiate Checkout) as the first optimization event, moving to Purchase once volume exists. TikTok's new-advertiser page recommends ATC first and at least $30/day for the first ad group. | A (Feb 2025) | currently supported; verify in account |
| R3 | Use Maximum Results (no target) at launch. Target Cost per Result needs budget of at least 10× the bid. VBO, Highest Value and Minimum ROAS need 20 purchases with value in 7 days. | A (Sep 2026, Aug 2026, Jul 2025) | currently supported |
| R4 | Choose the attribution window and event count before publishing. They lock per ad group. Record whether EVTA is on and its window. Report CTA, VTA and EVTA separately. | A (Nov 2025, Aug 2025) | currently supported; verify defaults in account |
| R5 | For controlled creative tests, use manual ad group budgets (not automatic campaign budget), TikTok-only placement, and broad or automatic targeting held constant across arms. | A (features) + D (design) | verify in account (upgraded flow rollout) |
| R6 | Don't pause, edit, duplicate or bulk-copy during learning. Don't change budgets during the test. | A (Jun 2026, Feb 2025) | currently supported |
| R7 | Use 3–5 strongly differentiated creatives per ad group. Add new creatives to the same ad group rather than making new ones. | A (Jun 2025) | currently supported |
| R8 | "50 conversions in 7 days to exit learning" | Older A, now replaced by "~25 results or 7 days" volatility guidance | outdated |
| R9 | Confirm the Shopify app is on Enhanced or Maximum data sharing (Events API). Confirm the Purchase event name, value and currency, and deduplication via event_id. Check "server & browser" status and EMQ. | A (Feb 2025, May 2025, Nov 2025, Apr 2026) | verify in account |
| R10 | Use CVR (clicks) or our own purchases ÷ destination clicks, never default CVR. It is per impression. | A (Oct 2025) | currently supported |
| R11 | Use focused-view "paid views", 2-s views and percentage views for watch claims, not plain 6-s views. | A (Nov 2025) | currently supported |
| R12 | Apply the AIGC label on the organic post for Spark Ads. Use the Ads Manager toggle for any non-Spark ad, and re-check it on every new or duplicated campaign. Never frame an AI presenter as a real customer. | A (Sep 2025, Community Guidelines Aug/Sep 2026) | currently supported |
| R13 | Turn off auto-add of TikTok-generated AI assets ("Add upon my approval" or "Don't Add"). | A (Oct 2026) | verify in account |
| R14 | GMV Max applies only to TikTok Shop and is irrelevant for website ads. | A (Mar 2026) | currently supported |
| R15 | Bid-change and budget-step rules: pages say at least 20%, no more than 30–40%, and within 50%. | A, conflicting | verify in account |

## 13. What to verify inside our ad account (read-only checks, no spend)

- [ ] Is the **Upgraded Smart+ experience** live for this account (one unified flow with manual and automated modes), or the legacy flow?
- [ ] Exact **bid strategy labels** offered: Maximum Results / Target Cost per Result, or Lowest Cost / Cost Cap. Is Bid Cap present?
- [ ] **Optimization goals** under Sales → Website (Conversion, Value, LPV, Click). Which **events** are selectable as the Conversion event: Purchase, CompletePayment, AddToCart, InitiateCheckout?
- [ ] **Attribution defaults** shown at ad group creation: click, view and EVTA windows, and event count. Is EVTA on by default, and with which window? Has Attribution Manager ever been changed on this account?
- [ ] **Placement options** shown: TikTok, Lemon8, Global App Bundle, TikTok Ad Network. Can we pick TikTok-only in the chosen campaign type?
- [ ] **Identity**: is Identity on? Is Custom Identity still available? Is the brand account linked and verified in Business Center? Does a "Show Through Ads Only" option exist?
- [ ] **AIGC**: does the "This ad contains AI-generated content" toggle appear for non-Spark ads, or does it need sales-rep enablement? For Spark posts, confirm the organic AI-generated label is set and visible in the ad preview.
- [ ] **AI asset auto-add** settings (Recommended tab, Automatic enhancements, catalog enhancements, Creative Upgrades). Set them to approval-only or off.
- [ ] **Smart Creative / Automate Creative / ACO** availability and defaults (on or off).
- [ ] **Events Manager**: pixel status "Active"; connection "server & browser"; event names received (Purchase versus CompletePayment); value and currency present; event_id deduplication; EMQ score per event; open Diagnostics issues.
- [ ] **Shopify TikTok app**: data-sharing level (Standard, Enhanced or Maximum); In-App Shopify Checkout opt-in status.
- [ ] **Catalog**: at least 4 in-stock, approved, activated products; content_ids in pixel events match catalog IDs (for Catalog Ads).
- [ ] **Learning status text** on an ad group (whatever label Ads Manager shows), and whether a learning-progress indicator exists.
- [ ] **Reporting columns**: that 2-s views, 6-s views, focused-view paid-views and paid-interactions splits, percentage views, average play time, CVR (clicks), LPV and Payment completion ROAS (page) are available in custom columns. Note each column's tooltip definition.
- [ ] **Budget minimums** enforced in the interface (ad group over $20/day; campaign over $50/day if set).
- [ ] **API**: if a reporting pipeline is planned, confirm metric field names in the Marketing API reporting docs (JS-rendered; not readable here).

## 14. Evidence table

Method key: **H** = Help Center page opened; **B** = TikTok for Business blog opened; **S** = seen in search results only; **P** = peer-reviewed abstract via search; **T** = third-party page opened.

| # | Source | URL | Date | Method | Cat. | Finding | Limitation | Confidence | Implication |
|---|---|---|---|---|---|---|---|---|---|
| 1 | About Learning Phase | https://ads.tiktok.com/help/article/learning-phase | Upd. Jun 2026 | H | A | Volatility declines after ~25 results or 7 days; avoid pausing, retriggering edits, unreasonable budgets | No formal exit rule; triggers not listed | High | Plan tests around about 7 days and about 25 results |
| 2 | Legacy learning-phase text (aid=11234) | https://ads.tiktok.com/help/article?aid=11234 | Older; now redirects | S | A (old) | 50 conversions for stable CPA; under 20 in 10 days means likely fail | URL now serves the Jun 2026 page | Low (outdated) | Treat 50/7d as outdated |
| 3 | Tips to select your budget | https://ads.tiktok.com/help/article/budget-best-practices | Upd. Aug 2026 | H | A | Deep conversion min 10× CPA, $200 floor; shallow 50×, $100 floor; daily ad group budgets; changes within 50% after learning | "Minimum budget" period not explicit | High | $25/day is far below Purchase-optimization guidance |
| 4 | Best practices for bidding strategies | https://ads.tiktok.com/help/article/bidding-best-practices | Upd. Aug 2026 | H | A | Maximum Results budget 10× average CPA; Target CPR budget at least 10× bid; raise budget at least 20% | Needs CPA history | High | Use Maximum Results first |
| 5 | Bidding & Budget Solutions | https://ads.tiktok.com/help/article/bidding-budget-solutions-drive-tiktok-auction-ad-performance | Upd. Aug 2026 | H | A | Daily budget = target CPA × 10 to pass learning | Mixed 10 and 50 language | Medium | Same as row 3 |
| 6 | Available Bidding Strategies | https://ads.tiktok.com/help/article/bidding-strategies | Upd. Sep 2026 | H | A | Two strategies: Maximum Results, Target Cost per Result; ads ranked by bid and relevance | No formula | High | Auction is bid × relevance in general terms only |
| 7 | Available bidding methods | https://ads.tiktok.com/help/article/bidding-methods | Upd. Aug 2025 | H | A | oCPM, CPM, CPC, CPV definitions; CPV charged at 6-s view or interaction | No pricing rule | High | CPV and focused view include interactions |
| 8 | About Smart+ Web Campaigns | https://ads.tiktok.com/help/article/about-smart-plus-web-campaigns | Upd. Mar 2026 | H | A | Goals Value, Conversion, LPV, Click; automatic placement only; no Spark/non-Spark mix | Pre-upgrade description | High | Smart+ Web cannot exclude Pangle |
| 9 | About upgrades to Smart+ | https://ads.tiktok.com/help/article/about-updates-to-smart-plus | Upd. Oct 2026 | H | A | Unified flow: full, partial or manual automation; may not be available yet | Limits inconsistent | High | Check rollout in account |
| 10 | Create Upgraded Smart+ Campaign | https://ads.tiktok.com/help/article/how-to-create-a-campaign-in-the-upgraded-smart-experience | Upd. Oct 2026 | H | A | Manual vs automated rules; asset combinations; AI asset approval controls; auto placement may include Pangle | No numeric limits | High | Use manual mode for controlled tests |
| 11 | TikTok Product Preview Q2 2026 | https://ads.tiktok.com/business/en/blog/tiktok-product-preview | Jul 28, 2026 | B | A | Creative Upgrades (formerly Creator+), Catalog auto-crawl, Symphony Agent and Avatars, GMV Max Pro, GA integration | Announcements; allowlists | Medium | Tooling context |
| 12 | About EVTA | https://ads.tiktok.com/help/article/about-engaged-view-through-attribution | Upd. Aug 2025 | H | A | At least 6-s watch before conversion; windows Off/1/7/28; included in Conversions; CTA/VTA/EVTA split | Default and priority not stated | High | Split conversions by type |
| 13 | Attribution Metrics | https://ads.tiktok.com/help/article/attribution-manager?lang=en | Upd. Feb 2026 | H | A | CTA/VTA metric families; web requires pixel | Defaults not stated | Medium | n/a |
| 14 | Flexible attribution windows blog | https://ads.tiktok.com/business/de/blog/flexible-attribution-windows-campaign-measurement | Jun 23, 2022 | B | A (old) | Web default 7-day click / 1-day view; options | Old | Medium | Verify defaults in account |
| 15 | Attribution windows for ad group | https://ads.tiktok.com/help/article/attribution-settings-at-the-ad-group-level?lang=en | Upd. Nov 2025 | H | A | Locked after publish; event count Every or Once; options | Default not restated | High | Decide the window before launch |
| 16 | Video play metrics | https://ads.tiktok.com/help/article/video-play?lang=en | Upd. Nov 2025 | H | A | Exact definitions for views, 2-s, 6-s, focused views (paid views and paid interactions), percentage views, play time incl. replays | Some replay handling unstated | High | Metric dictionary |
| 17 | Video views objective & focused view | https://ads.tiktok.com/help/article/video-views-objective | Upd. Aug 2026 | H | A | 6-s and 15-s focused view options by creative length; cost per focused view | n/a | High | Video Views buys watchers, not buyers |
| 18 | Basic metrics and definitions | https://ads.tiktok.com/help/article/basic-data?lang=en | Upd. Oct 2025 | H | A | CVR per impression; CVR (clicks); Clicks (destination/all); Reach; Frequency; CPA | CPM and CTR not on page | High | Use CVR (clicks) |
| 19 | All reporting metrics | https://ads.tiktok.com/resources/help/article/all-metrics | Upd. Apr 2025 | H | A | Metric category index | No definitions | Medium | n/a |
| 20 | Landing Page View | https://ads.tiktok.com/help/article/landing-page-view | Upd. Sep 2026 | H | A | Counted on click plus successful load; computed by TikTok; one per session | Traffic objective focus | High | LPV is a quality-traffic metric |
| 21 | Page Events metrics | https://ads.tiktok.com/help/article/page-events?lang=en | Upd. Oct 2025 | H | A | Payments completed, Payment completion ROAS and value (page); rates per attributed clicks | "Complete payment" naming legacy | High | ROAS is TikTok-attributed |
| 22 | Ads Manager Glossary | https://ads.tiktok.com/help/article/tiktok-ads-manager-glossary-terms?lang=en | Date not captured | H | A | CPM, Reach (estimated), Frequency, oCPM, Spark, ACO, Bid cap, Cost cap | Date unknown; mixed old terms | Medium | Definitions backup |
| 23 | Data Sharing on TikTok App on Shopify | https://ads.tiktok.com/help/article/data-sharing-tiktok-app-shopify?lang=en | Upd. Feb 2025 | H | A | Standard, Enhanced, Maximum; ad blockers affect pixel; In-App Checkout beta | No deduplication detail | High | Use Enhanced or Maximum |
| 24 | About Event Deduplication | https://ads.tiktok.com/help/article/event-deduplication?lang=en | Upd. May 2025 | H | A | event_id via both pixel and Events API; 48-h and 5-min rules | _ttp fallback not on page | High | Check deduplication |
| 25 | Events Manager diagnostics | https://ads.tiktok.com/help/article/tiktok-events-manager-monitor-and-diagnose | Upd. Nov 2025 | H | A | EMQ = weighted match-key coverage; no thresholds; connection method; Active = 7 days | No targets | High | Monitor EMQ trend, not a magic number |
| 26 | Standard Events and Parameters | https://ads.tiktok.com/help/article/standard-events-parameters?lang=en | Upd. Apr 2026 | H | A | Purchase is the standard event; CompletePayment and PlaceAnOrder absent | Migration not explained | High | Verify the Shopify app event names |
| 27 | Event rename (CompletePayment to Purchase) | https://theadspend.com/blog/tiktok-conversion-tracking ; https://weltpixel.com/blogs/magento/tiktok-events-api-on-magento-2-server-side-setup-and-the-event-name-churn | 2025–2026 | S | C | Legacy names soft-deprecated | Vendor claims | Low | Verify in account |
| 28 | About Spark Ads | https://ads.tiktok.com/help/article/spark-ads?lang=en | Upd. Jun 2026 | H | A | Engagement accrues to the organic post; auth duration; 10,000 cap | No performance data | High | Our ads are Spark ads |
| 29 | Learn About Identity | https://ads.tiktok.com/resources/help/article/identity | Upd. Apr 2026 | H | A | Custom Identity being phased out; Identity on means Spark only | No timeline | High | Non-Spark route shrinking |
| 30 | PPC Land, Custom Identity phase-out | https://ppc.land/tiktok-kills-custom-identity-as-brands-must-link-verified-accounts/ | Jan 27, 2026 | T | C | Announced Jan 22, 2026; early-2026 cutoff; "Show Through Ads Only" | No TikTok URL cited | Medium | Verify in account |
| 31 | About ad disclaimers | https://ads.tiktok.com/help/article/about-ad-disclaimers-in-tiktok-ads-manager?lang=en | Upd. Sep 2025 | H | A | AIGC is a mandatory disclaimer category; label at bottom of ad | May need rep enablement | High | Label every AI ad |
| 32 | Add disclaimers to ads | https://ads.tiktok.com/help/article/add-disclaimers-to-ads | Upd. Sep 2025 | H | A | Toggle only for non-Spark; Spark follows Community Guidelines; duplication resets toggle; TikTok-only placement for disclaimers | n/a | High | Label on the organic post for Spark |
| 33 | Community Guidelines, Integrity & Authenticity | https://www.tiktok.com/community-guidelines/en/integrity-authenticity | Released Aug 25, 2026; effective Sep 24, 2026 | H | A | Must label realistic AI people and scenes; unlabeled content may be removed; fake reviews and impersonation banned | Labelling method in linked article not read | High | No fake-testimonial framing |
| 34 | TikTok Newsroom, C2PA | https://newsroom.tiktok.com/partnering-with-our-industry-to-advance-ai-transparency-and-literacy?lang=en | May 9, 2024 | S | A (old) | Auto-labels AIGC via Content Credentials | Old; rollout status unknown | Medium | Generator exports may be auto-labelled |
| 35 | Stellar Search, AI ad disclosure | https://www.stellarsearch.co.uk/insight/tiktoks-ai-ad-disclosure-rules-are-live-what-brands-running-ai-creative-need-to-do-now | Aug 12, 2026 | T | C | Says ad AI disclosure mandatory since Jul 21; penalty tiers | No official citation | Low | Verify in ad policy |
| 36 | GMV Max migration | https://ads.tiktok.com/help/article/gmv-max-migration-tiktok-shop-ads?lang=en | Upd. Mar 2026 | H | A | GMV Max is the only Shop-ads type since Jul 2025; VSA remains only via Showcase | Shop only | High | Not applicable to the website |
| 37 | About eligible placements | https://ads.tiktok.com/help/article/automatic-select-placement | Upd. Sep 2026 | H | A | TikTok, Lemon8, Global App Bundle, TikTok Ad Network; auto allocation; locked after creation | Country variance | High | Pick TikTok-only for tests |
| 38 | About Catalog Ads | https://ads.tiktok.com/help/article/about-catalog-ads-in-tiktok-ads-manager | Upd. Oct 2026 | H | A | Eligible objectives and formats; carousel for prospecting and retargeting | No requirements listed | High | Catalog option exists |
| 39 | Creative best practices (performance) | https://ads.tiktok.com/help/article?aid=11953 | Upd. Jun 2025 | H | A | 3–5 creatives per ad group; 3–5 ad groups per campaign; fatigue signals; add to the same ad group | Not budget-aware | High | Fewer ad groups, more distinct creatives |
| 40 | About Smart Creative | https://ads.tiktok.com/help/article/smart-creative?lang=en | Upd. Nov 2025 | H | A | 3–5 day fatigue detection, ≤10% exploration spend; Automate Creative successor | Signals undisclosed | Medium | Avoid in controlled tests |
| 41 | New e-commerce web conversion advertisers | https://ads.tiktok.com/help/article/best-practices-for-new-e-commerce-web-conversion-advertisers?lang=en | Upd. Feb 2025 | H | A | ATC first; at least $30/day; automatic targeting; advanced matching; first-party cookies | 20 months old | Medium | Start event choice |
| 42 | VBO for web specifications | https://ads.tiktok.com/help/article/specifications-for-value-based-optimization-for-web | Upd. Jul 2025 | H | A | 20 purchases with value in 7 days; Highest Value / Min ROAS; CBO supported | n/a | High | VBO not available at launch |
| 43 | Available optimization objectives | https://ads.tiktok.com/help/article/available-optimization-objectives?lang=en | Upd. Jul 2025 | H | A | Web: CPC/LPV, Web Conversion, Web VBO, retargeting | Older taxonomy | Medium | n/a |
| 44 | Account structure best practices | https://ads.tiktok.com/help/article/account-structure-best-practices | Upd. Feb 2025 | H | A | Diverse ad groups; no bulk copying in weak-history accounts | No numbers | Medium | Don't clone ad groups |
| 45 | About budgets | https://ads.tiktok.com/help/article/budget | Upd. Jul 2026 | H | A | Ad group over $20/day; campaign over $50; CBO change ≤40% in learning, ≤30% after; every 2 days | Conflicts with row 3 | High | $25/day is allowed |
| 46 | Low-impressions troubleshooting | https://ads.tiktok.com/help/article?aid=11970 | Upd. Feb 2025 | H | A | Checklist (approval, funds, bid, broaden targeting) | Snippet attributes other content to this aid | Low | Troubleshooting only |
| 47 | Why ads rejected after approval | https://ads.tiktok.com/help/article/why-ads-rejected-after-approved?lang=en | Upd. Nov 2025 | S | A | Negative feedback can trigger re-review | Not opened | Medium | Negative feedback has a policy consequence |
| 48 | Search Ads optimization | https://ads.tiktok.com/help/article/search-ads-optimization | Upd. Jul 2026 | S | A | ~20× CPA; 3–7 day calibration; start upper-funnel and move after ~14 days | Search Ads only | Low (different product) | Consistent with ATC-first |
| 49 | Traffic best practices | https://ads.tiktok.com/help/article/best-practices-for-getting-started-with-traffic-campaigns | Upd. Mar 2026 | S | A | Match Click vs LPV to the consideration cycle | Not opened | Medium | Traffic tests should use LPV |
| 50 | Dataslayer 2026 changes | https://dataslayer.ai/blog/tiktok-ads-2026-auto-select-creative-consideration-signals-attribution-changes | Feb 2, 2026 | T | C | Consideration-signals toggle (Jan 21, 2026); auto-select limited to Smart+ App; unsourced 79% claim | Statistics unsourced | Low | Verify toggle in account |
| 51 | Motion metrics cheat sheet | https://help.motionapp.com/en/articles/7730931-metrics-cheat-sheet | Apr 15, 2026 | T | C | Hold rate definition; high CTR can lower thruplay; CPA and ROAS capture the full journey | Tool-specific definitions | Medium | State ratio formulas |
| 52 | Coupler / Nestscale diagnostics | https://www.coupler.io/ai-agent-skills/tiktok-ads-creative-analysis ; https://nestscale.com/blog/detect-patterns-in-top-performing-tiktok-ads.html | 2026 | S | C | Hook/hold/CTR/CVR diagnostic map; hook rate does not guarantee conversions | Vendor content | Low–Medium | Supports Phase 7.3 rules |
| 53 | Practitioner learning-phase blogs | https://www.journify.io/resources/tiktok-ads-not-optimizing/ ; https://nestscale.com/blog/tiktok-ads-learning-phase.html | 2025–2026 | S | C | Repeat "50 conversions / 7 days" | Not official | Low | Outdated framing |
| 54 | Agency auction explainers | https://lseo.com/paid-media/paid-social-media-marketing/understanding-tiktoks-ad-auction-delivery-system/ | n.d. | S | C | bid × EAR × quality; second-price-like pricing | Not TikTok-stated | Low | Don't present as fact |
| 55 | Gordon, Zettelmeyer, Bhargava, Chapsky | https://doi.org/10.1287/mksc.2018.1135 | 2019 | P | B | Observational ad-effect estimates often differ greatly from randomized experiments | Facebook, not TikTok; abstract only | High (for the general point) | Don't treat attributed ROAS as causal |
| 56 | Lewis & Rao | https://doi.org/10.1093/qje/qjv023 | 2015 | P | B | ROI is very hard to measure even in large experiments | Large retailers, display ads | High (for the general point) | Small tests are directional only |
| 57 | Marketing API docs | https://business-api.tiktok.com/portal/docs?id=1751443967255553 | n/a | Failed (JS-rendered) | n/a | Could not read | n/a | n/a | API field names unverified |
| 58 | API field mirrors | https://help.rockerbox.com/docs/schema-data-warehouse-platform-performance-tiktok ; https://portermetrics.com/en/connectors/fields/tiktok-ads/ | n.d. | S | C | Field names (video_watched_6s, average_video_play, complete_payment_roas) | Third-party | Low–Medium | Verify before building a pipeline |

**Source count:**

- **58 evidence rows.** Rows 27, 52, 53 and 58 each bundle two URLs, so they cover about 62 distinct URLs.
- **About 46 pages opened.** 39 are official TikTok pages (Help Center, Business blog, Community Guidelines), and the rest are third-party.
- **About 12 rows seen in search results only**, including 2 peer-reviewed abstracts.
- **4 rows failed to open:** row 57 (Marketing API docs) plus the TikTok Support AIGC article, the Fundamentals PDF and the click/CVR-update page, which are not in the table.

## 15. Open questions

1. **Exit rule.** What is the current *exit rule* for learning, and what status label does Ads Manager show? The June 2026 page gives only a volatility guideline. (Verify in account.)
2. **EVTA.** Is EVTA on by default for web Sales ad groups in 2026, with which window, and is it used for optimization or only reporting?
3. **Attribution and delivery.** Do attribution-window choices change *delivery*, or only reporting? Not documented for TikTok.
4. **Shopify event mapping.** Does the Shopify TikTok app send `Purchase` or legacy `CompletePayment` for this store, and which appears as the Conversion event?
5. **Bid Cap.** Is Bid Cap still offered for web Sales, given the September 2026 page lists only two strategies?
6. **Budget-step rules.** Which rule applies: at least 20%, no more than 30–40%, or within 50%? Pages updated Jul–Aug 2026 conflict.
7. **Ads AIGC policy.** Is there an official TikTok *Advertising Policy* page (not the Help Center disclaimer page) on AI-generated ads? The reported July 21, 2026 mandatory-label change and penalty tiers are unverified. Does it cover third-party virtual presenters specifically?
8. **Organic effects of Spark.** Does boosting a Spark post change its organic For You distribution, positively or negatively? Undocumented; coordinate with A1.
9. **Negative feedback.** Does negative feedback (hide, "not interested", report) affect auction rank or price beyond re-review? Undocumented.
10. **ACO.** Is ACO still a separate toggle in manual campaigns, or fully replaced by Smart Creative, Automate Creative or Upgraded Smart+ asset combination?
11. **Consideration signals.** Does the "consideration signals" / "cost per new buyer" Traffic toggle exist in this account? It is reported by a third party only.
12. **API field names.** What are the exact Marketing API names and definitions for focused-view paid-views and paid-interactions splits, CVR (clicks) and LPV? The official docs could not be read here.
13. **Budget against learning.** Given $25/day against a 10× CPA ($200+) guideline, should the owner move to fewer ad groups with more budget each, or to a shallower event? This is a Checkpoint D decision; this note supplies the constraints only.
