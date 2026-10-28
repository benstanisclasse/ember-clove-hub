# TIKTOK_ALGORITHM_INTELLIGENCE

**Checkpoint A — research foundation.** Ember & Clove, prepared 2026-10-24/25.
Scope: master prompt Phase 1 (organic recommendation, paid delivery, signals, Ads Manager), the Phase 7.2 metric
definitions, and a read-only check of our own ad account. Full working notes, with every source row:
`_notes_A1_organic_recommendation.md` (31 sources), `_notes_A2_paid_delivery.md` (58 evidence rows, ~62 URLs),
`_notes_A3_account_verification.md` (our account, via the TikTok Marketing API).

**Evidence categories** (Phase 9): **A** officially documented by TikTok (or observed in our own account) ·
**B** peer-reviewed or credible experiment · **C** industry or practitioner · **D** hypothesis or our own arithmetic.
C and D are never stated as fact here. **Status tags** for Ads Manager guidance: *supported* (current official
page), *outdated* (superseded), *verify* (depends on account rollout or conflicting pages).

Nothing in this checkpoint created, changed, published or spent anything.

---

## 1. Executive summary

1. **Nobody outside TikTok knows the ranking weights, and we will not pretend to.** TikTok officially says the
   For You feed predicts how likely each viewer is to like, share, comment, mark "Not interested", follow or visit
   the profile, finish, skip, favorite (save), watch for a certain time, or tap the sound, then **combines those
   predictions into one score** (A, Transparency Center, © 2025, re-checked by us). No weights are published.
   The leaked 2021 "Algo 101" formula has the same shape and no values (C).
2. **Watching is the strongest documented organic signal, but only full or repeated watches move it much.**
   TikTok calls finishing a longer video "a strong indicator of interest" (A, 2020). The 2025 SIGIR replication
   audit found watching was the strongest personalisation factor, with watching under 100% having little effect
   and rewatching a strong one (B, re-checked by us). Audit rankings of signals changed between 2022 and 2025, so
   any fixed "signal hierarchy" is unreliable (B).
3. **Paid delivery is a different system with a different goal.** Ads are ranked by "how much advertisers bid
   and how relevant the ads are to users" (A, Sep 2026). With oCPM, TikTok shows the ad to people it predicts
   will take **the event we choose to optimize for** (A). So for a Sales campaign, the decisive "signal" is the
   pixel event, not views or likes. A Video Views campaign buys people likely to watch, not to buy (A + D).
4. **Our planned budget is far below TikTok's own guidance for purchase optimization.** TikTok's budget page
   (Aug 2026, re-checked by us) sets a minimum of **10× current CPA, $200 floor** for Add to Cart or Purchase
   optimization; volatility "starts to decline after about 25 campaign results or 7 days" (Jun 2026, re-checked).
   At $25/day and a $31–35 break-even CPA, a purchase-optimized ad group gets roughly 5 purchases a week at best,
   a fifth of that guideline (D arithmetic). The old "50 conversions in 7 days" rule is **outdated**.
   TikTok's page for new e-commerce advertisers recommends **Add to Cart as the first optimization event** and
   at least $30/day for the first ad group (A, Feb 2025, *verify*). This is the biggest decision this checkpoint
   surfaces (section 9).
5. **Value/ROAS bidding is not available to us yet** (A, our account: `vo_status = NO_VALUE`); it needs 20
   purchases with value in 7 days (A, Jul 2025). Start with Maximum Results (A).
6. **Several common metrics are traps.** Default conversion rate is per *impression*, not per click; 6-second
   views also count anyone who interacted in the first 6 s; average play time includes replays (A, Nov 2025 /
   Oct 2025). Our account can pull a **second-by-second retention and drop-off curve** per video through the API
   (A, our account), which the public Help Center does not document. That is our best hook diagnostic.
7. **AI labelling for our setup works through the organic post.** We advertise from @emberandclove, which makes
   our ads Spark Ads; Custom Identity (non-Spark) is being phased out (A, Apr 2026). The Ads Manager "AI-generated
   content" toggle excludes Spark Ads, so **the AI-generated label must be set on the organic post itself**
   before boosting (A, Sep 2025). TikTok's Community Guidelines (effective 24 Sep 2026) require labels on
   realistic AI people and ban fake reviews (A).

---

## 2. How the organic For You feed recommends content

**Pipeline (A, Transparency Center, © 2025):** retrieve a large pool of moderated videos → predict the
probability of each interaction for this viewer → combine into one score → rank → replace runs of overly similar
videos → apply eligibility rules.

**Inputs TikTok names (A):** viewer signals (region, device language and OS, recently watched / finished / liked /
skipped videos, follows), video signals (post time and region, language, sound, length, hashtags) and
collaborative filtering (what similar viewers went on to watch). Device and account settings carry lower weight
than active behaviour (A, 2020). Follower count and past hits "are not direct factors" (A, 2020).

**Eligibility before ranking (A, Community Guidelines released 25 Aug 2026, effective 24 Sep 2026):** content
unsuitable for a broad audience, "unoriginal or reused material without anything new", and content that
manipulates people into inflating likes or follows is not eligible for For You. TikTok also spreads out
TikTok Shop content so it does not cluster (A, 2025 EU DSA risk report).

**What independent research adds (B):**
- Real users: about 45% of views are watched to the end; about 24% are skipped before 20% of the video
  (Zannettou et al., CHI 2024, data donations).
- Personalisation accounts for roughly 30–50% of the first 1,000 recommendations; the rest is exploration
  (Vombatkere et al., WWW 2024).
- Signal importance shifts over time: follow strongest in 2022 and 2024 studies; watching strongest in 2025
  (Mosnar et al., SIGIR 2025: one-off audit findings "often hold only in the short term").
- ByteDance's own Douyin ranker trains on Finish and Skip labels and reports online gains in Finish, Like and
  Comment (RankMixer, 2025; Douyin, not TikTok). Industry rankers normalise watch time for video length
  (Kuaishou D2Q 2022), so "make it longer to bank watch time" is not a safe inference (D).

**What nobody outside TikTok knows (gaps):** the weights; how a brand-new video gets its first audience; whether
paid boosting lifts later organic reach; how far the US algorithm diverges after the January 2026 US joint
venture said it "will retrain, test, and update" it (C, Marketing Dive, 23 Jan 2026).

---

## 3. How paid ads are delivered

- **Auction (A, Sep 2026 / Aug 2025):** ads are ranked on bid and relevance. TikTok publishes **no** formula; the
  popular "eCPM = bid × estimated action rate × quality" and second-price claims come from agency blogs (C).
- **oCPM (A):** billed per 1,000 impressions, delivered to people predicted to take the optimization event.
  At a fixed bid, an ad the system predicts converts better should win more impressions per dollar (A logic;
  size of effect unknown, D).
- **Same modelling family as the feed (B):** RankMixer's ads test reports advertiser-value metrics, so feed and
  ads ranking share technology, but the objective differs (advertiser outcome vs. viewer satisfaction).
- **Negative feedback (A, partial):** hides and reports can trigger re-review of an approved ad; no official
  statement on auction price effects (D).
- **Creative fatigue (A):** TikTok names falling delivery and falling daily new users as refresh signals; Smart
  Creative detects fatigue within 3–5 days. **No official frequency threshold exists**; any "frequency > X" rule
  is C or D.
- **Spark Ads (A, Jun 2026):** promote an organic post; all views, likes, comments, shares and follows from the
  boost are credited to that organic post. Whether that improves the post's later organic ranking is
  undocumented (D). Promote does not reduce organic reach of other videos (A, 2022).
- **TikTok Shop vs. our website (A, Mar 2026):** GMV Max is the only campaign type for TikTok Shop ads since
  Jul 2025 and is irrelevant to us. We use Sales → Website with the pixel and Events API.

---

## 4. Signal-by-signal (Phase 1.1)

Role: **OT** optimization/prediction target · **RM** reporting metric · **IF** hypothesised indirect factor.
"Importance known?" is "No" for every signal: TikTok publishes no weights.

| Signal | Officially confirmed? | Organic / paid | Role | Experimental evidence | How Ember & Clove can test it |
|---|---|---|---|---|---|
| Initial swipe-away / skip | **A** — "skip" is a predicted interaction (Transparency Center); Safety Center: system notes if you "moved on" early | Organic OT; paid has no skip column | OT (organic) | B mixed: early skip not significant for viewer personalisation (Vombatkere 2024); Douyin ranker uses Skip | **Per-second drop-off curve** from our API (A3) across hook variants; 2-s view rate |
| 2-s / 6-s views | Paid reporting metrics only (A, video-play, Nov 2025). **6-s counts any interaction in the first 6 s** | Paid | RM | none | 2-s ÷ impressions = stop rate; for watch claims use 2-s and % views, not 6-s |
| Average watch duration | **A** — "spend a certain amount of time viewing" is predicted. Paid "average play time" **includes replays** | Both | OT organic; RM paid | B: watching strongest in 2025 audit; rankers normalise for length | Compare only within the same video length (all ours are 15 s) |
| % watched | A, implied (watch time + finish) | Both | OT (implied); RM | B: watch % medium effect (2024) | 25/50/75/100% views ÷ video views |
| Completion | **A** — "finish" predicted; "strong indicator" (2020) | Both | OT organic; RM paid | B: finish is a Douyin training label; <100% weak, rewatch strong (2025) | 100% views ÷ video views, by hook variant |
| Replays | A, weak (2020/2023 mentions; not in 2025 list) | Organic | OT/IF unclear | B: 400% watch strong effect (2025) | Not reported in Ads Manager; inflates average play time |
| Likes | **A** predicted | Both | OT; RM | B: shift viewer feed (2022, 2024) | Likes per 1,000 impressions; correlational only |
| Shares | **A** predicted | Both | OT; RM | none isolated | Shares per 1,000; never bait (engagement manipulation is ineligible) |
| Saves (favorites) | **A** predicted | Both | OT; RM | none isolated | Organic Studio metric; test "save this outfit" style utility |
| Comments | **A** predicted | Both | OT; RM | Douyin online comment gains | Comments per 1,000; read them for objections |
| Profile visits / follows | **A** predicted ("follow… or interact with their profile") | Both | OT | B: follow strongest in 2022/2024 | Profile visits and follows per 1,000 (API `profile_visits`, `follows`) |
| CTR (destination) | Paid only (A) | Paid | OT (Click goal) / RM | none | Clicks (destination) ÷ impressions |
| Landing-page visits | Paid only; computed by TikTok on click + successful load (A, Sep 2026) | Paid | OT (LPV goal) / RM | none | LPV ÷ clicks shows page-load loss |
| Add to cart | Pixel event (A; our pixel `ON_WEB_CART`) | Paid | OT / RM | none | Candidate first optimization event |
| Purchases | Pixel event (A; our pixel `SHOPPING`) | Paid | OT / RM | none | The business outcome; compare with Shopify orders |
| Conversion value | Pixel value (A); VBO needs 20 valued purchases / 7 days | Paid | OT (VBO) / RM | n/a | Not available yet (A, our account) |
| Negative feedback | **A** predicted ("Not interested"); ads: hide/report → re-review | Both | OT (negative) | none isolated | Not visible to us; watch comments and sudden delivery drops |
| Repeated exposure | Organic: avoided by design (A). Paid: frequency is reported, no official fatigue threshold | Both | Constraint / RM | B: diversity falls as amplification rises | Frequency vs. CTR trend over days; refresh when delivery falls (A) |

---

## 5. Ads Manager today: what is supported, outdated, or to verify

| Topic | Current guidance | Evidence / date | Status |
|---|---|---|---|
| Objectives | Sales (Website), Traffic (Click or Landing Page View), Video Views (focused view), Reach. Video Views on 7–15 s creatives buys **15-s focused views** | A, Aug–Sep 2026 | supported |
| Smart+ | **Upgraded Smart+** merges manual and automated setup ("full automation, partial automation, or fully manual"); rolling out, "may not be available to you yet". Legacy Smart+ Web: placement automatic only | A, Oct 2026 / Mar 2026 | verify (rollout) |
| AI asset auto-add | Upgraded flow can add TikTok-generated assets: "Add upon my approval", "Auto-add and notify", "Don't Add" | A, Oct 2026 | verify; **set to approval or off** |
| Smart Creative / ACO | Smart Creative documented (3–5 day fatigue swap, ≤10% exploration); successor "Automate Creative" rolling out; ACO only in the glossary | A, Nov 2025 | verify |
| Optimization events | Our pixel offers ViewContent, AddToCart, InitiateCheckout, AddPaymentInfo, Purchase (`SHOPPING`), Search, Landing Page View | A, our account | supported |
| First event for a new store | Add to Cart first, ≥$30/day first ad group, automatic targeting, advanced matching on | A, Feb 2025 | supported; verify (page is 20 months old) |
| Learning phase | Volatility declines after "about 25 campaign results or 7 days"; don't pause, make retriggering edits, or set "unreasonable" budgets | A, Jun 2026 (re-checked) | supported |
| "50 conversions in 7 days" | Older text and practitioner blogs | A (old) / C | **outdated** |
| Budget minimums | Ad group > $20/day; campaign > $50/day if set; deep-conversion guidance 10× CPA, $200 floor (page does not say daily); another page: daily budget = target CPA × 10 | A, Jul–Aug 2026 | supported (pages differ) |
| Budget changes | Pages conflict: ≤40% in learning / ≤30% after; "within 50%"; "at least 20%"; wait ≥2 days | A, Jul–Aug 2026 | verify; **we won't change budgets mid-test** |
| Bid strategies | **Maximum Results** (was lowest cost) and **Target Cost per Result** (was cost cap); Highest Value / Min ROAS only under VBO | A, Sep 2026 | supported (labels: verify) |
| VBO | Needs 20 attributed purchases with value in 7 days; **not available to us** | A, Jul 2025; A, our account | supported |
| Campaign budget optimization | Reallocates toward early leaders, which confounds creative tests | A (feature) + D | use ad group budgets for tests |
| Structure | 3–5 strongly different creatives per ad group; 3–5 ad groups per campaign; don't duplicate fresh ad groups | A, Jun 2025 / Feb 2025 | supported |
| Attribution | Default 7-day click / 1-day view; options click 1/7/14/28, view off/1/7; **locks at publish**; engaged-view-through (≥6 s watched) counts in Conversions | A, Nov 2025 / Aug 2025 | supported; verify defaults |
| Events API / match quality | Shopify app levels Standard (pixel only) / Enhanced (+Events API) / Maximum; dedupe by event_id; EMQ has no official threshold | A, Feb–Nov 2025 | verify level in Shopify app |
| Our pixel setup | Active; first-party cookies on; expanded data sharing on; automatic advanced matching (email, phone, name, address, external ID) | A, our account | supported |
| Placements | TikTok, Lemon8, TikTok Ad Network (ex-Pangle), Global App Bundle; locks at creation; automatic may shift budget to one placement | A, Sep 2026 | supported |
| Identity / Spark | Custom Identity being phased out; with Identity on, only Spark Ads | A, Apr 2026 | supported |
| AI label | Ads Manager toggle for non-Spark ads only; Spark Ads follow Community Guidelines (label the organic post); toggle resets on duplication | A, Sep 2025 | supported |
| "Mandatory AI ad disclosure from 21 Jul 2026" + penalty tiers | Reported by agencies without a TikTok link | C | verify |
| Split testing | Ad-group-level split tests (creative / targeting / bidding) with even budget; campaign-level allowlist-only | A, our account (API) | supported |

---

## 6. Metric definitions that matter, and their traps

| Metric | Official meaning | Trap / how we use it |
|---|---|---|
| Video views | Times the video **started** to play | Not attention. Denominator only. |
| 2-second views | ≥2 s in one impression; replays excluded | Best "stop" metric: 2-s ÷ impressions |
| 6-second views | ≥6 s **or** full if shorter **or any interaction in first 6 s** | Not pure watch time |
| Focused views (6 s / 15 s) | Same logic; split into "paid views" (watch) and "paid interactions" | Use the paid-views split for watch claims |
| Average play time per view | Average play time **including replays** | Inflated by loops on 15-s videos |
| 25/50/75/100% views | Plays reaching that share of length; replays excluded | Our retention proxy; state denominator |
| Per-second retain / drop-off (API) | Retention and drop-off by second, first 60 s, 1-hour latency | **Best hook diagnostic** (A, our account) |
| Clicks (all) vs. Clicks (destination) | All includes likes and profile taps; destination = website clicks | Use destination only |
| CTR (destination) | Destination clicks ÷ impressions | Verify tooltip |
| Landing page views | Click + page loaded (TikTok-computed) | LPV ÷ clicks = load loss |
| Conversion rate | **Conversions ÷ impressions** | Use "CVR (clicks)" or purchases ÷ destination clicks |
| CPA, Payment completion ROAS | TikTok-attributed (includes view-through and engaged-view) | Always report next to Shopify orders and contribution margin |
| Reach / frequency | Reach is **estimated** | Don't sum reach across days |

"Hook rate" and "hold rate" are tool-defined ratios, not TikTok columns (C); we state our formula whenever we use
them: **stop rate = 2-s views ÷ impressions; hold = 100% views ÷ 2-s views; plus the per-second curve.**

---

## 7. Why watch time and sales can disagree

**Strong watch time, poor sales**
1. Wrong objective: Video Views buys predicted watchers, not buyers (A + D).
2. Inflated metrics: 6-s views count interactions; average play time counts loops (A definitions; D effect).
3. Entertaining but not relevant: the hook stops people who will never buy; strong hold + weak CTR = weak value
   proposition or CTA; strong CTR + weak conversion = page, price, trust or checkout (C diagnostics).
4. Placement and audience mix: automatic placement can move spend to lower-intent inventory (A behaviour; D effect).
5. Measurement loss: ad blockers stop the pixel; without Events API, real orders go unseen (A; D size).

**Low engagement, strong purchase efficiency**
1. oCPM finds buyers even for a creative few people like or share (A mechanism).
2. Direct-response clicks end views early, lowering completion (C).
3. Warm or retargeted viewers convert with little engagement (D).
4. Attribution credit capture: view-through and engaged-view credit can go to people who would have bought
   anyway; observational ad attribution can be badly biased (B, Gordon et al., Marketing Science 2019).
5. Small samples: at ~5 purchases a week, "winners" are often noise (B, Lewis & Rao, QJE 2015).

---

## 8. Our ad account, verified (A, read-only, 2026-10-25)

- Enabled auction account, US, USD; **balance $0** (payment method still needed); 50 active ad-group quota.
- Reporting time zone is fixed UTC-5 (matches Eastern only after daylight saving ends on 1 Nov).
- Pixel active with the events listed in section 5; VBO not available (`NO_VALUE`).
- Available through our API connection: split tests, per-second video retention, benchmarks once an ad has
  ≥1,000 impressions, automated rules (usable as stop-loss rules, with owner approval).
- Still to check in the Ads Manager interface (the API can't show these): Upgraded Smart+ availability, bid
  strategy labels, attribution defaults incl. engaged-view-through, AI asset auto-add settings, Shopify app
  data-sharing level and Event Match Quality, "Show through ads only" for Spark posts.

---

## 9. What this means for Ember & Clove (recommendations, with evidence)

| # | Recommendation | Evidence |
|---|---|---|
| 1 | **Re-decide the test budget and optimization event before launch.** At $25/day, purchase optimization will stay volatile all test. Options: (a) optimize for **Add to Cart** at ≥$30/day per ad group (TikTok's new-store advice), moving to Purchase once volume exists; (b) fewer ad groups with more budget each; (c) accept purchase optimization and treat results as directional only. Owner decision (money). | A (Feb 2025, Jun & Aug 2026) + D |
| 2 | Use **Sales → Website, Maximum Results**, no cost target, no value bidding yet. | A + A (our account) |
| 3 | For controlled creative tests: **ad-group budgets (no campaign budget optimization), TikTok-only placement, same broad/automatic targeting in every arm**, or TikTok's ad-group split test. | A (features) + D (design) |
| 4 | **3–5 strongly different creatives per ad group** (different ICP angles, not wording tweaks). Matches our ICP-angle plan. | A, Jun 2025 |
| 5 | **Don't pause, edit, duplicate or change budgets during a test.** Decide attribution window and placement before publishing; they lock. | A, Jun 2026, Nov 2025, Sep 2026 |
| 6 | **Measure attention with 2-s views, % views and the per-second curve**, never plain 6-s views or average play time. Use CVR on clicks, not the default. Report TikTok-attributed and Shopify numbers side by side. | A + B |
| 7 | **Label every ad AI-generated on the organic post** (Spark), confirm it shows in the ad preview; AI presenter never framed as a real customer. | A, Sep 2025; CG Sep 2026 |
| 8 | **Turn TikTok's AI asset auto-add to approval-only or off**, so no generated assets run unreviewed. | A, Oct 2026 |
| 9 | Make every post materially new; no reposting supplier footage unchanged (For You eligibility). | A, Sep 2026 |
| 10 | Confirm the Shopify TikTok app is on **Enhanced or Maximum** data sharing (Events API) before spending. | A, Feb 2025 |

---

## 10. Evidence table (key sources)

Full tables: A1 notes §3 (31 rows), A2 notes §14 (58 rows). "Re-checked" = opened again by the lead researcher.
Confidence H/M/L.

| # | Source | URL | Date | Cat. | Main finding | Conf. | Implication |
|---|---|---|---|---|---|---|---|
| 1 | Transparency Center, recommendation system (re-checked) | https://www.tiktok.com/transparency/en-us/recommendation-system/ | © 2025 | A | Predicts like/share/comment/not interested/follow/profile/finish/skip/favorite/time/sound; combines into one score; no weights | H | Optimise for genuine watching and saving, not one metric |
| 2 | Newsroom, "How TikTok recommends videos #ForYou" | https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you | 18 Jun 2020 | A | Finishing a longer video is a strong signal; follower count not a direct factor | M (old) | Completion matters; don't chase follower count |
| 3 | Safety Center, "Making your feed For You" | https://www.tiktok.com/safety/en/making-your-feed-for-you | © 2025 | A | Watch duration and moving on early are noted | H | Early drop-off matters |
| 4 | Community Guidelines, For You eligibility | https://www.tiktok.com/community-guidelines/en/fyf-standards | eff. 24 Sep 2026 | A | Broad-audience suitability required | H | Keep ads broadly suitable |
| 5 | Community Guidelines, Integrity & Authenticity | https://www.tiktok.com/community-guidelines/en/integrity-authenticity | eff. 24 Sep 2026 | A | Unoriginal reused content ineligible; label realistic AI; no fake reviews | H | Original posts; AI label; no testimonials |
| 6 | Mosnar et al., SIGIR 2025 (re-checked) | https://arxiv.org/abs/2504.18140 | Apr 2025 | B | Watching strongest; <100% weak; rewatch strong; findings short-lived | M | Completion > partial watch; re-test over time |
| 7 | Vombatkere et al., WWW 2024 | https://arxiv.org/html/2403.12410 | Mar 2024 | B | 30–50% exploitation; follow > like > watch %; early skip n.s. | M | Signal order is not fixed |
| 8 | Zannettou et al., CHI 2024 | https://arxiv.org/html/2301.04945v2 | 2024 | B | ~45% of views completed; ~24% skipped before 20% | M | Baseline for viewer behaviour |
| 9 | Boeker & Urman, WWW 2022 | https://arxiv.org/abs/2201.12271 | Jan 2022 | B | All tested factors matter; follow strongest then | M | Historical |
| 10 | RankMixer (ByteDance) | https://arxiv.org/html/2507.15551v3 | Jul 2025 | B (eng.) | Douyin ranker uses Finish/Skip; ads use same architecture | M | Finish/skip are real modelled labels |
| 11 | D2Q (Kuaishou) | https://arxiv.org/abs/2206.06003 | Jun 2022 | B | Watch time confounded by length; rankers correct | M | Don't lengthen videos to farm watch time |
| 12 | Gizmodo on "TikTok Algo 101" leak | https://gizmodo.com/leaked-tiktok-doc-reveals-its-obvious-secret-to-an-addi-1848166901 | 6 Dec 2021 | C | Weighted sum of predicted actions; no values | L | Structure only |
| 13 | Marketing Dive, US joint venture | https://www.marketingdive.com/news/tiktok-confirms-joint-venture-to-comply-with-us-law/810329/ | 23 Jan 2026 | C (reports A) | US algorithm to be retrained | M | Older findings may drift in the US |
| 14 | About Learning Phase (re-checked) | https://ads.tiktok.com/help/article/learning-phase | upd. Jun 2026 | A | Volatility declines after ~25 results or 7 days | H | Plan tests around 7 days / 25 results |
| 15 | Tips to select your budget (re-checked) | https://ads.tiktok.com/help/article/budget-best-practices | upd. Aug 2026 | A | Deep conversion: 10× CPA, $200 floor; use daily ad-group budgets | H | $25/day is far below for purchase optimization |
| 16 | New e-commerce web advertisers | https://ads.tiktok.com/help/article/best-practices-for-new-e-commerce-web-conversion-advertisers?lang=en | upd. Feb 2025 | A | Add to Cart first; ≥$30/day; automatic targeting | M (age) | Candidate launch setup |
| 17 | Available bidding strategies | https://ads.tiktok.com/help/article/bidding-strategies | upd. Sep 2026 | A | Ranks by bid and relevance; Maximum Results / Target Cost per Result | H | Start Maximum Results |
| 18 | VBO for web specifications | https://ads.tiktok.com/help/article/specifications-for-value-based-optimization-for-web | upd. Jul 2025 | A | 20 valued purchases / 7 days | H | No ROAS bidding yet |
| 19 | About budgets | https://ads.tiktok.com/help/article/budget | upd. Jul 2026 | A | Ad group > $20/day; campaign > $50 | H | $25 ad group is allowed |
| 20 | Creative best practices | https://ads.tiktok.com/help/article?aid=11953 | upd. Jun 2025 | A | 3–5 different creatives per ad group | M | One ad group per hypothesis, 3–5 angles |
| 21 | Attribution at ad-group level | https://ads.tiktok.com/help/article/attribution-settings-at-the-ad-group-level?lang=en | upd. Nov 2025 | A | Windows lock at publish | H | Decide before launch |
| 22 | Engaged view-through attribution | https://ads.tiktok.com/help/article/about-engaged-view-through-attribution | upd. Aug 2025 | A | ≥6 s watched → credit; in Conversions | H | Split CTA/VTA/EVTA in reports |
| 23 | Video play metrics | https://ads.tiktok.com/help/article/video-play?lang=en | upd. Nov 2025 | A | 2-s, 6-s (incl. interactions), play time incl. replays | H | Metric rules in §6 |
| 24 | Basic metrics | https://ads.tiktok.com/help/article/basic-data?lang=en | upd. Oct 2025 | A | Default CVR per impression | H | Use CVR (clicks) |
| 25 | Landing page view | https://ads.tiktok.com/help/article/landing-page-view | upd. Sep 2026 | A | Click + successful load | H | Page-load loss check |
| 26 | Data sharing, TikTok app on Shopify | https://ads.tiktok.com/help/article/data-sharing-tiktok-app-shopify?lang=en | upd. Feb 2025 | A | Standard / Enhanced / Maximum | H | Confirm Enhanced+ |
| 27 | Events Manager diagnostics | https://ads.tiktok.com/help/article/tiktok-events-manager-monitor-and-diagnose | upd. Nov 2025 | A | EMQ weighted coverage; no threshold | H | Check EMQ, no magic number |
| 28 | About Spark Ads | https://ads.tiktok.com/help/article/spark-ads?lang=en | upd. Jun 2026 | A | Engagement credited to organic post | H | Our ads are Spark |
| 29 | Learn about Identity | https://ads.tiktok.com/resources/help/article/identity | upd. Apr 2026 | A | Custom Identity phased out | H | Brand account only |
| 30 | Add disclaimers to ads | https://ads.tiktok.com/help/article/add-disclaimers-to-ads | upd. Sep 2025 | A | AI toggle non-Spark only; Spark → organic label | H | Label on the post |
| 31 | Upgraded Smart+ | https://ads.tiktok.com/help/article/how-to-create-a-campaign-in-the-upgraded-smart-experience | upd. Oct 2026 | A | Unified flow; AI asset auto-add options | H | Set approval-only |
| 32 | Smart Creative | https://ads.tiktok.com/help/article/smart-creative?lang=en | upd. Nov 2025 | A | 3–5 day fatigue swap | M | Optional; keep off for clean tests |
| 33 | Eligible placements | https://ads.tiktok.com/help/article/automatic-select-placement | upd. Sep 2026 | A | Placements; lock at creation | H | TikTok-only for tests |
| 34 | GMV Max migration | https://ads.tiktok.com/help/article/gmv-max-migration-tiktok-shop-ads?lang=en | upd. Mar 2026 | A | Shop ads only | H | Not relevant |
| 35 | Gordon et al., Marketing Science | https://doi.org/10.1287/mksc.2018.1135 | 2019 | B | Observational attribution often far from causal | M | Don't treat ROAS as causal |
| 36 | Lewis & Rao, QJE | https://doi.org/10.1093/qje/qjv023 | 2015 | B | Ad ROI very noisy even in huge experiments | M | Small tests are directional |
| 37 | Motion metrics cheat sheet | https://help.motionapp.com/en/articles/7730931-metrics-cheat-sheet | 15 Apr 2026 | C | Hold-rate definitions vary by tool | L | State formulas |
| 38 | Stellar Search, AI ad disclosure | https://www.stellarsearch.co.uk/insight/tiktoks-ai-ad-disclosure-rules-are-live-what-brands-running-ai-creative-need-to-know | 12 Aug 2026 | C | Claims mandatory AI ad label from 21 Jul 2026 | L | We label anyway; verify policy |
| 39 | Our ad account via Marketing API | (internal: advertiser XXX) | 25 Oct 2026 | A (observed) | Pixel events; VBO NO_VALUE; per-second retention; split tests; quota 50; balance $0 | H | See §8 |

Sources that could not be opened: the NYT "Algo 101" original, the Marketing API docs (JavaScript-rendered),
TikTok's support article on AI labels, and some peer-reviewed full texts (abstracts only). These are marked in
the notes.

---

## 11. Remaining uncertainties

- Ranking weights (organic and paid): unknowable from outside.
- Cold start: how a new ad or post gets its first impressions; whether boosting helps later organic reach.
- How much the US algorithm changes after the 2026 joint-venture retraining.
- Whether the attribution window changes what delivery optimizes toward (documented for Meta, not TikTok).
- Our real costs: CPM, cost per add to cart, CPA. Unknown until ads run; every budget calculation here is
  arithmetic on assumptions (D).
- Account-interface items listed in §8.

---

## 12. Checkpoint A report and next steps

**Findings in one line each**
1. TikTok combines many predicted actions into one score; no weights are public (A).
2. Full watches and rewatches are the best-supported organic signals; signal rankings drift over time (A + B).
3. Paid delivery optimizes for the pixel event we pick; the creative's job is to help the system find buyers (A).
4. $25/day is far below TikTok's guidance for purchase optimization; Add to Cart first is TikTok's advice for
   new stores (A, re-checked).
5. Several standard metrics mislead (CVR per impression, 6-s views, play time); we have a per-second retention
   curve to use instead (A).
6. AI labels go on the organic post for our Spark-style ads (A).

**Confidence:** high on documentation and account facts; medium on audit-based signal findings (they drift);
low on anything from agencies.

**Prioritised next steps**
1. **Owner decision:** test budget and first optimization event (section 9, recommendation 1).
2. **Owner checks in Ads Manager / Shopify** (no spend): data-sharing level, Event Match Quality, Upgraded Smart+,
   attribution defaults, AI asset auto-add, payment method.
3. **Checkpoint B (awaiting approval):** attention psychology, retention, persuasion and real ad examples
   (TikTok Creative Center / Top Ads via our API's `discovery_*` tools), delivering
   ATTENTION_PSYCHOLOGY_PLAYBOOK.md and the creative intelligence database.
