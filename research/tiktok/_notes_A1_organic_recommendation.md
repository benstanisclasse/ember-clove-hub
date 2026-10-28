# Checkpoint A, Note A1: How TikTok's organic For You feed recommends content, and what is known about each engagement signal

**Analyst:** A1 (organic recommendation). **Research date:** 2026-10-24. **Scope:** Phase 1.1 (organic side) and the Phase 9 evidence standard.
**Out of scope:** paid delivery, Ads Manager and metric definitions. Analyst A2 covers those. This note only marks where organic and paid differ.

**Evidence labels:**
- **A**: official TikTok documentation.
- **B**: peer-reviewed or credible experiment, including published ByteDance or industry engineering papers.
- **C**: industry, press or practitioner source.
- **D**: hypothesis.

**Access notes.** I opened every source marked "opened" in the evidence table. Sources marked "search result only" are known only from search-engine snippets.
- The NYT article on "TikTok Algo 101" was blocked (WebFetch cannot reach nytimes.com). It is reported here only through Gizmodo and TechTimes.
- support.tiktok.com "How TikTok recommends content" redirects to a JavaScript-rendered page that returned no text, so it was not read.
- The EPJ Data Science page returned HTTP 403. I read the arXiv preprint of the same study instead.
- The WSJ 2021 investigation was not opened. Its findings come from secondary coverage seen in search results.
- No ranking weights appear anywhere in this note, because TikTok has not published any.

---

## 1. Narrative summary

### 1.1 What TikTok officially says (category A)

**Pipeline.** TikTok's Transparency Center page "Introduction to the TikTok recommendation system" (© 2025, undated, opened) is the most detailed official account. It describes these steps:
1. Retrieve a large pool of videos that passed moderation.
2. Predict how likely the viewer is to take each of several interactions.
3. Combine those predictions into one score ("By combining prediction scores for each of these interactions").
4. Rank videos by that score.
5. Run a similarity check that replaces consecutive videos that are "too similar to each other".
6. Apply recommendation rules, such as making under-16 creators' content ineligible.

**Interactions TikTok says it predicts** (appendix, verbatim item wording):
- "Like, share, comment on, or mark a video as 'Not Interested.'"
- "Follow the video's author or interact with their profile."
- "Finish, skip, or favorite a video."
- "Spend a certain amount of time viewing a video."
- "Tap the video's soundtrack."

**Other inputs on the same page:**
- User signals: region, device language, device operating system, recently watched, finished, liked or skipped videos, and follow relationships.
- Video signals: posting time, posting region, the author's language setting, soundtrack, length and hashtags.
- Collaborative filtering: what other users with overlapping engagement went on to watch.

This is the closest TikTok comes to confirming the organic signal list. It names watch time, completion, skip (swipe-away), favorite (save), profile interaction and "Not Interested" as **prediction targets**. It gives no weights.

**The 2020 Newsroom post** ("How TikTok recommends videos #ForYou", 18 June 2020, opened) adds a qualitative weighting principle. A strong signal, finishing a longer video, outweighs a weak one, such as viewer and creator being in the same country. Device and account settings get lower weight because users do not actively express them as preferences. The post also says:
- Follower count and past high-performing videos are not direct factors.
- TikTok does not recommend duplicated content or content the viewer has already seen.
- TikTok deliberately mixes in diversity so the feed does not become homogeneous.

The 1 Nov 2023 regional repost adds "Not Interested", hide-creator and hide-sound controls.

**Later official material:**
- Safety Center, "Making your feed For You" (undated, © 2025): lists "How long you watched a video for" and whether you "moved on to another before it's complete".
- Privacy blog (29 Aug 2025): describes collaborative filtering.
- Newsroom, Dec 2021: rule against back-to-back videos from the same creator or sound, and a commitment to "interrupt repetitive patterns".
- Newsroom, Mar 2023: feed refresh; also lists "products" among the things the For You feed surfaces.
- Newsroom, Dec 2022: the "Why this video" feature.
- Newsroom, 3 Jun 2025: Manage Topics sliders and Smart Keyword Filters.

**Eligibility rules (A).** The Community Guidelines "For You feed Eligibility Standards" (released 25 Aug 2026, effective 24 Sep 2026) make content unsuitable for a broad audience ineligible for For You recommendation. Such content stays visible on the creator's profile and in search. The "Integrity and Authenticity" section, same dates, makes these For You-ineligible:
- "unoriginal or reused material without anything new"
- content that manipulates people into inflating likes or follows

The 2025 EU DSA risk report also says diversification rules stop the For You feed from recommending a run of **Shop content**.

**What TikTok values for monetised creators (A, indirect).** The Creator Rewards Program (Newsroom, 18 Mar 2024) rewards four things: originality, play duration ("watch time and finish rate"), search value, and audience engagement (likes, comments, shares). This is a payout formula, not the recommender. It still shows which outcomes TikTok publicly treats as quality.

### 1.2 Leaked "TikTok Algo 101" (Dec 2021), as reported, not current

The NYT article (5 Dec 2021, Ben Smith) was blocked. According to Gizmodo (6 Dec 2021, opened) and TechTimes (6 Dec 2021, opened):
- The document gave a "highly simplified" scoring equation: Plike×Vlike + Pcomment×Vcomment + Eplaytime×Vplaytime + Pplay×Vplay. That is, predicted probabilities of each action, and expected playtime, each multiplied by a value.
- The real equation was described as "much more complicated".
- The stated goals were "retention" and "time spent", in service of growing daily active users.
- TikTok confirmed the document was authentic and said it was written for non-technical employees.

**Caveats:**
- Neither outlet published the document, and Gizmodo could not verify it.
- It is five years old.
- It contains no actual values (V terms).

Its main use is structural. It agrees with the 2025 Transparency Center description: many predicted actions are combined into one score. It does not support any specific weighting.

### 1.3 ByteDance engineering papers (category B, engineering)

- **Monolith** (arXiv 2209.07663, Sep 2022, ORSUM@RecSys 2022). Describes ByteDance's real-time online-training recommender framework, deployed in BytePlus Recommend. It supports the idea that models update from feedback in close to real time. It does not report a TikTok For You latency figure, and it is not proof of TikTok For You internals.
- **RankMixer** (arXiv 2507.15551, Jul 2025, ByteDance; v3 opened):
  - The Douyin ranking model is evaluated offline on **Finish** and **Skip** labels.
  - Online, after full deployment, it reports gains on the Douyin app of +0.29% Active Days, +1.08% Duration, +2.39% Like, +1.99% Finish and +0.79% Comment.
  - Low-activity users gained the most.
  - The same architecture was tested in **advertising** and reported ad-specific metrics (ΔAUC, ADVV), so feed and ads ranking share modelling technology.
  - This concerns Douyin, the Chinese app, not TikTok.
- **Douyin long-sequence paper** (arXiv 2511.06077, Nov 2025, revised May 2026). Says it is deployed at full traffic on Douyin and improves "key engagement metrics". The abstract names no specific objectives.
- **Watch-time debiasing literature:**
  - D2Q (arXiv 2206.06003, 2022) was deployed on **Kuaishou**, a competitor, not ByteDance. It shows that raw watch time is confounded by video length and that systems become "biased towards videos with long duration" unless corrected.
  - Relative Advantage Debiasing (arXiv 2508.11086, 2025). Its abstract calls watch time "widely used as a proxy for user satisfaction". It reports online gains without naming the platform. A search snippet suggested ByteDance authors, but the abstract page did not confirm affiliation.
  - Practical implication: modern short-video rankers probably normalise watch time against video length and user norms. "Make it longer to get more watch time" is therefore not a safe inference (D).

### 1.4 Independent audits (category B)

- **Boeker & Urman, WWW 2022** (arXiv 2201.12271). Sock-puppet bots on TikTok web, roughly 20 runs per scenario, locations US, Canada and Germany.
  - Every tested factor (follow, like, view rate, language, location) changed recommendations.
  - Follow was strongest.
  - The paper contradicts itself on second place: the abstract ranks like second, the conclusion ranks view rate second.
  - Location mattered more than language.
- **Vombatkere et al., WWW 2024** (arXiv 2403.12410). Data donations from 347 users (220 analysed) plus 5 bots.
  - Personalisation ("exploitation") accounts for about **30–50%** of the first 1,000 recommended videos; the rest is exploration.
  - In real-user data, following had the strongest effect, then liking, then watch percentage (medium effect, p≈0.03).
  - Early skip rate was not significant.
- **Zannettou et al., CHI 2024** (arXiv 2301.04945). Same donation cohort, 9.2M video views.
  - About 45% of views were watched to the end. Median attention was 82% of video length.
  - 24% of views were skipped before 20% of the video.
  - Completion stayed stable over 120 days while time spent roughly doubled.
- **Mosnar et al., SIGIR 2025** (arXiv 2504.18140). Re-ran the Boeker & Urman and Vombatkere audits in Jan–Feb 2025.
  - Watching was the **strongest** personalisation factor, ahead of following, which reverses the 2022 finding.
  - Watching under 100% had little effect. Watching 400% (rewatching) had a strong effect.
  - Feed overlap between control bots fell from about 35% to about 11%, suggesting more diversity.
  - Authors' conclusion: one-off audit findings "often hold only in the short term".
- **Baumann et al., arXiv 2503.20231** (Mar 2025; peer-reviewed version in EPJ Data Science 2026, which was blocked). 42 US bots, Jun–Aug 2024.
  - Interest-aligned content was amplified within about 66–140 videos and made up 52–67% of the feed.
  - Exploration of new hashtags fell as amplification rose.
  - The bots combined like, rewatch and follow, so the effect of each signal cannot be separated.
- **WSJ, July 2021** (secondary coverage only). Study of 100 bot accounts. Reported that how long a user lingers on a video was the dominant signal and that interests were learned within hours. TikTok disputed how representative it was.

**What the audits mean together:**
- Watch behaviour, follows and likes all measurably shift the viewer-side feed.
- Which of them matters most has **changed between studies over 2021–2025**. Any ranking of signals should be treated as time-bound.
- All of these audits measure **viewer-side personalisation**: what a bot is shown. None measures **creator-side distribution**: how far a given video travels. The second question is the one that matters for Ember & Clove, and no independent study I found addresses it directly.

### 1.5 Organic versus paid (pointer for A2)

- **Spark Ads.** The Business Help Center (updated June 2026) says "all views, comments, shares, likes, and follows gained from boosting the video" are attributed to the organic post (A).
- **Promote.** The TikTok for Business blog (21 Jun 2022) says Promote does not reduce organic views on other, non-promoted videos (A). It also says promoted videos "will continue to have some positive effects" after the promotion ends. That last line is vague and not a statement about the recommender.
- **Not found:** No official statement says whether paid engagement feeds organic For You ranking. Whether boosting raises later organic reach is **unknown** (D).
- **Ad frequency and ad fatigue** are paid concepts (A2). On the organic side, TikTok officially avoids showing a viewer already-seen or duplicated content and spreads out similar content (A). Repeated exposure of the same organic video to the same viewer is avoided by design, not tuned.
- **Conversion signals.** None of the organic documentation lists click-through, landing-page visits, add-to-cart, purchase or conversion value as For You prediction targets. These are paid optimisation and reporting events (A2).
- **US context (C).** Marketing Dive (23 Jan 2026) reports that the new TikTok USDS Joint Venture says it "will retrain, test, and update" the recommendation algorithm on US user data. It is unknown how much US For You behaviour will diverge from what was documented or audited earlier.

---

## 2. Per-signal table (organic focus)

Column key:
- **Official?** Whether TikTok officially confirms the signal's role.
- **Scope.** Organic, paid, or both.
- **Role.** OT = optimisation or prediction target; RM = reporting metric; IF = hypothesised indirect factor.
- **Weight known?** Whether its relative importance is known.
- **Experimental evidence.** Credible studies linking the signal to outcomes.
- **How to test.** How Ember & Clove could test its practical relevance.

| Signal | Official? (source) | Scope | Role | Weight known? | Experimental evidence | How to test |
|---|---|---|---|---|---|---|
| Initial swipe-away / skip | **A, yes.** Transparency Center lists "skip" as a predicted interaction. Safety Center says the system notes if you "moved on to another before it's complete". | Organic (prediction target). Paid equivalents are view-rate metrics, A2. | OT for organic | No | **B, mixed.** Vombatkere 2024: early skip rate not significant for viewer personalisation. RankMixer uses a Skip label (Douyin). | Compare 2-second and early-retention curves in TikTok Studio across hook variants posted in matched pairs. Paid: split-test hooks, A2. |
| 2-second / 6-second views | **Not in organic docs.** These are paid reporting metrics; A2 owns definitions. | Paid (reporting) | RM | n/a | None found for organic | Paid split test (A2). Organically, use Studio retention at seconds 2 and 6 as a proxy. Metric availability needs checking in the account. |
| Average watch duration | **A, yes.** "Spend a certain amount of time viewing a video" is a predicted interaction. Safety Center: "How long you watched". | Both | OT (organic); RM (paid) | No | **B.** Mosnar 2025: watching is the strongest personalisation factor (2025). WSJ 2021 (C, secondary): lingering dominant. Industry papers normalise watch time for length. | Within-account comparison of average watch time against reach for videos of similar length. Do not compare across lengths without normalising. |
| % watched | **A, partly.** Implied by watch time plus finish. No "percent" signal is named. | Both | OT (implied); RM | No | **B.** Vombatkere 2024: watch percentage has a medium effect. D2Q and Relative Advantage: rankers adjust watch time for duration. | Track % watched by video length band and test same-length variants. |
| Completion | **A, yes.** "Finish" is predicted. 2020 post: finishing a longer video is "a strong indicator of interest". Creator Rewards uses finish rate. | Both | OT (organic); RM (paid) | Qualitatively "strong"; no number | **B.** RankMixer reports online Finish gains (Douyin). Mosnar: below 100% watched had little effect. Zannettou: about 45% of real views complete. | Compare "watched full video" % against For You traffic share across matched variants. |
| Replays / rewatch | **A, weak.** 2020 and 2023 Newsroom: early "replays" shape a new user's feed. Not in the 2025 appendix list. | Organic | OT/IF (unclear) | No | **B.** Mosnar 2025: 400% watch has a strong effect. Baumann 2025 bots rewatched (effect confounded). | Studio's rewatch metric, if shown (C: third-party guides name a "watched more than once" metric; not verified). Test loopable edits against linear edits. |
| Likes | **A, yes.** Predicted interaction in all official sources. | Both | OT (organic); RM (paid) | No | **B.** Boeker 2022 and Vombatkere 2024: likes shift viewer recommendations. Mosnar: like effect grows after about 1,000 videos. | Like rate per 1,000 views against later reach, in matched pairs. Correlational only. |
| Shares | **A, yes.** Predicted interaction. | Both | OT; RM | No | No independent audit isolated shares (Boeker did not test them). | Share rate against reach, correlational. Test share-prompting CTAs, staying within engagement-bait rules (A: manipulating likes or follows makes content ineligible). |
| Saves / favorites | **A, yes.** "Favorite" is a predicted interaction. Safety Center lists favorites. | Both | OT; RM | No | None isolated | Favorite rate in Studio. Test "save for later" utility content, such as style guides, against pure product shots. |
| Comments | **A, yes.** Predicted interaction. Leaked 2021 formula included Pcomment. | Both | OT; RM | No | RankMixer reports online Comment gains (Douyin). No TikTok audit isolated comments. | Comment rate in matched pairs. Watch for engagement-bait rules. |
| Profile visits | **A, yes.** "Follow the video's author or interact with their profile." | Organic (paid has its own profile-visit metrics, A2) | OT | No | None isolated | Profile views per 1,000 views in Studio, compared with reach and bio-link clicks. |
| Follows | **A, yes.** Predicted interaction and a user signal (follow graph). 2020: follower *count* is not a direct factor. | Both | OT | No | **B.** Follow was strongest in Boeker 2022 and Vombatkere 2024. Second in Mosnar 2025. | Follows per 1,000 views. Follower count itself should not be treated as a distribution lever. |
| CTR | **Not an organic For You target in any official source.** | Paid | Paid OT/RM (A2); organic IF | n/a | None organic | Paid only (A2). Organically, bio-link click-through via UTM-tagged links in Shopify analytics. |
| Landing-page visits | Not organic. Paid event (A2). | Paid | Paid OT/RM | n/a | None | UTM-tagged bio links, Shopify sessions by source |
| Add-to-cart | Not organic | Paid | Paid OT/RM | n/a | None | Paid events (A2). Shopify funnel from TikTok-referred sessions. |
| Purchases | Not organic for external stores. TikTok Shop content has its own diversification rule (DSA report). | Paid (and Shop) | Paid OT | n/a | None for organic | Paid (A2). Organic: Shopify orders attributed through UTM or discount code. Expect weak attribution. |
| Conversion value | Not organic. RankMixer's ads test reports an advertiser-value metric (ADVV), confirming ads ranking models advertiser value (B). | Paid | Paid OT (A2) | n/a | n/a | A2 |
| Negative feedback ("Not interested", hide, report) | **A, yes.** Predicted interaction. User control (2023, 2025). Creator Rewards excludes views marked not interested (C, third-party). | Both (ads have their own feedback, A2) | OT (negative) | No | No audit isolated it | Not visible to creators. Indirect read: sudden reach drop after polarising content. |
| Repeated exposure / frequency | **A.** Organic avoids already-seen and duplicated content, avoids back-to-back same creator or sound, and disperses "concentrated content". | Organic: avoided by design. Paid frequency: A2. | Rule or constraint, not a target | n/a | Baumann 2025: diversity falls as amplification rises | Organic "creative fatigue" shows up as falling reach on reposts or near-duplicates. Make each post materially new (also required by the originality rule). |
| Duplicate / unoriginal / low-quality | **A.** "unoriginal or reused material without anything new" is For You-ineligible (CG, eff. 24 Sep 2026). 2020: duplicated content is not recommended. | Organic | Eligibility filter | n/a | n/a | Check Studio for an ineligibility notice. Never repost supplier or other-brand footage unchanged. |
| Device / account settings, location, language | **A.** Lower weight (2020). Region rules (2025). | Organic | Input feature | Qualitatively "lower" | **B.** Boeker 2022 and Mosnar 2025: location has a strong effect. | Post from a US-registered account and device. Expect a US audience. |
| Video information (sound, hashtags, length, caption, post time) | **A.** Video signals in the 2025 appendix. | Organic | Input feature | No | Not isolated | Matched tests on sound and hashtag choice. Do not expect large effects (D). |

---

## 3. Evidence table

All dates are publication dates unless "updated" is stated. Confidence: H/M/L.

| # | Source | URL | Date | Method | Cat. | Main finding | Limitation | Conf. | Implication for Ember & Clove |
|---|---|---|---|---|---|---|---|---|---|
| 1 | TikTok Transparency Center, "Introduction to the TikTok recommendation system" (opened) | https://www.tiktok.com/transparency/en-us/recommendation-system/ | Undated (© 2025) | Official description | A | Predicts like/share/comment/not interested, follow/profile, finish/skip/favorite, time spent, sound tap; combines into one score; similarity check | No weights; no new-video seeding detail | H | Optimise for genuine watch-through and saves/shares. No single lever. |
| 2 | TikTok Newsroom, "How TikTok recommends videos #ForYou" (opened) | https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you | 18 Jun 2020 | Official blog | A | Finishing a longer video is a strong signal; follower count not a direct factor; no duplicates; diversity | Six years old | M | Completion matters qualitatively. Small accounts are not structurally barred. |
| 3 | Newsroom repost (en-MY) of #2 (opened) | https://newsroom.tiktok.com/how-tik-tok-recommends-video-for-you?lang=en-MY | 1 Nov 2023 | Official blog | A | Adds Not Interested, hide creator/sound; replays as an early signal; no back-to-back same sound/creator | Regional repost | M | Negative feedback is real and creator-invisible. |
| 4 | TikTok Safety Center, "Making your feed For You" (opened) | https://www.tiktok.com/safety/en/making-your-feed-for-you | Undated (© 2025) | Official guide | A | Watch duration, finish vs moving on, likes/shares/favorites/comments, follows | No weights | H | Confirms watch time and skip as inputs. |
| 5 | TikTok Privacy blog, "The For You feed" (opened) | https://www.tiktok.com/privacy/blog/the-for-you-feed/en | 29 Aug 2025 | Official blog | A | Collaborative filtering; refresh resets to popular content | General | M | Audience similarity drives spread. Niche consistency may help (D). |
| 6 | TikTok Community Guidelines, "For You feed Eligibility Standards" (opened) | https://www.tiktok.com/community-guidelines/en/fyf-standards | Released 25 Aug 2026, effective 24 Sep 2026 | Official policy | A | Unsuitable content is For You-ineligible but still searchable; low views do not imply a violation | Category details are on linked pages | H | Check Studio eligibility before diagnosing creative. |
| 7 | Community Guidelines, "Integrity and Authenticity" (opened) | https://www.tiktok.com/community-guidelines/en/integrity-authenticity | Same as #6 | Official policy | A | Unoriginal or reused material, and manipulated engagement, are For You-ineligible | No "low quality" threshold given | H | No reposted supplier videos or engagement bait. |
| 8 | Newsroom, "An update on our work to safeguard and diversify recommendations" (opened) | https://newsroom.tiktok.com/an-update-on-our-work-to-safeguard-and-diversify-recommendations?lang=en | 16 Dec 2021 | Official blog | A | No two in a row from the same creator or sound; intersperses content outside preferences | Older | M | Posting many near-identical videos back to back is unlikely to stack (D). |
| 9 | Newsroom, "Introducing a way to refresh your For You feed" (opened) | https://newsroom.tiktok.com/en-ie/safeguarding-recommendations-update | 16 Mar 2023 | Official blog | A | Refresh; avoids already-seen content; feed surfaces "products" among other things | General | M | Organic repeat exposure per viewer is limited. |
| 10 | Newsroom, "Learn why a video is recommended For You" (opened) | https://newsroom.tiktok.com/learn-why-a-video-is-recommended-for-you?lang=en | 20 Dec 2022 | Official blog | A | Reasons: interactions, follows, regional recency and popularity | Vague | M | Regional popularity is a distribution path. |
| 11 | Newsroom, "More ways to discover new content and creators you love" (opened) | https://newsroom.tiktok.com/more-ways-to-discover-new-content-and-creators-you-love | 3 Jun 2025 | Official blog | A | Manage Topics sliders; Smart Keyword Filters (limit 200) | Viewer-side | M | Viewers can down-weight whole topics (e.g. fashion). Reach is ceilinged by viewer controls. |
| 12 | Newsroom, "Introducing the new Creator Rewards Program" (opened) | https://newsroom.tiktok.com/introducing-the-new-creator-rewards-program?lang=en | 18 Mar 2024 | Official blog | A (indirect) | Rewards originality, play duration (watch time plus finish rate), search value, engagement | Payout formula, not the ranker | M | Shows TikTok's stated quality concepts. Search value suggests searchable topics matter (D). |
| 13 | TikTok DSA Systemic Risk Assessment Report 2025 (OpenTermsArchive copy; about 200k of 242k characters read) | https://raw.githubusercontent.com/OpenTermsArchive/dsa-reports-versions/refs/heads/main/TikTok/Systemic%20Risks%20%E2%80%94%202025.md | 28 Aug 2025 | Regulatory filing | A | Signals: interactions, content info (sounds, hashtags, view counts), user info; EU non-personalised option; dispersion; Shop-content diversification | EU-focused; no weights; not fully read | M | Shop or commercial content is capped from clustering. Expect sales content to be interleaved, not chained. |
| 14 | European Commission press release on TikTok addictive design (search result only) | https://digital-strategy.ec.europa.eu/en/news/commission-preliminarily-finds-tiktoks-addictive-design-breach-digital-services-act | 6 Feb 2026 | Regulator preliminary finding | A- (regulator, not TikTok) | Flags infinite scroll, autoplay and the personalised recommender; proposes adapting the recommender | Preliminary; EU only | M | Regulatory risk of recommender changes. Re-check periodically. |
| 15 | TechCrunch on DSA non-personalised feed (search result only) | https://techcrunch.com/2023/08/04/tiktok-algorithm-dsa/ | 4 Aug 2023 | Press | C | EU users can switch off personalisation (popular regional content) | Not US | M | Irrelevant to US targeting. Shows a popularity-based fallback exists. |
| 16 | TikTok Business Help Center, "About Spark Ads" (opened) | https://ads.tiktok.com/help/article/spark-ads?lang=en | Updated Jun 2026 | Official help | A | Boost engagement is attributed to the organic post | Silent on effect on organic ranking | H | Spark keeps social proof on the post. Organic lift is unproven. |
| 17 | TikTok for Business blog, "3 common questions about TikTok's Promote feature" (opened) | https://ads.tiktok.com/business/th/blog/common-questions-promote-feature | 21 Jun 2022 | Official blog | A | Promote does not reduce organic reach; "some positive effects" after promotion ends | Old and vague | L–M | Do not plan on a "boost → organic halo". Test it. |
| 18 | Gizmodo on NYT "TikTok Algo 101" (opened); NYT original blocked | https://gizmodo.com/leaked-tiktok-doc-reveals-its-obvious-secret-to-an-addi-1848166901 | 6 Dec 2021 | Press report of a leak | C | Simplified weighted sum of P(like), P(comment), E(playtime), P(play); goals are retention and time spent; TikTok confirmed authenticity | Unverified; 2021; no values | L–M (structure only) | Supports a multi-signal model. Gives no weights. |
| 19 | TechTimes on the same leak (opened) | https://www.techtimes.com/articles/269024/20211206/tiktok-algo-101-leaked-document-tiktok-secret-algorithm-tiktok.htm | 6 Dec 2021 | Press | C | Same formula | Secondary | L | Corroborates #18 only |
| 20 | Liu et al., "Monolith" (opened) | https://arxiv.org/abs/2209.07663 | Sep 2022 | Engineering paper | B (eng.) | Real-time online training; deployed in BytePlus Recommend | Not TikTok For You specifically | M | Feedback is likely absorbed quickly (D for TikTok). |
| 21 | ByteDance, "RankMixer" (opened, v3) | https://arxiv.org/html/2507.15551v3 | Jul 2025 | Engineering paper with online A/B | B (eng.) | Douyin ranker uses Finish and Skip labels; online gains in duration, like, finish, comment; also used in ads | Douyin, not TikTok; no weights | M | Finish and skip are core labels in ByteDance feed ranking. |
| 22 | Guan et al., Douyin 10K-sequence paper (opened) | https://arxiv.org/abs/2511.06077 | Nov 2025 (rev. May 2026) | Engineering paper | B (eng.) | Long user histories used at full traffic on Douyin | Abstract only | L–M | Long-term viewer history shapes what the viewer is shown. |
| 23 | Zhan et al., "D2Q" (opened) | https://arxiv.org/abs/2206.06003 | Jun 2022 | Engineering paper, deployed on Kuaishou | B | Watch time is confounded by duration; rankers correct for it | Competitor platform | M | Do not lengthen videos just to raise raw watch time. |
| 24 | Liu et al., "Relative Advantage Debiasing" (opened) | https://arxiv.org/abs/2508.11086 | Aug 2025 (rev. Nov 2025) | Engineering paper | B | Watch time is a satisfaction proxy, compared against user and item reference distributions | Platform unnamed; affiliation unverified | L–M | Watch time likely judged relative to similar videos. |
| 25 | Boeker & Urman, WWW '22 (opened) | https://arxiv.org/abs/2201.12271 | Jan 2022 | Sock-puppet audit | B | Follow strongest; like and view rate next (internally inconsistent order); location > language | Web only; small; 2021 data | M (for 2021) | Historical baseline only |
| 26 | Vombatkere et al., WWW '24 (opened) | https://arxiv.org/html/2403.12410 | Mar 2024 | Data donation (347/220 users) plus 5 bots | B | 30–50% exploitation; follow > like > watch %; early skip n.s. | Non-representative; 2022–23 data | M | Half or more of For You is exploration: room for cold reach to non-followers. |
| 27 | Zannettou et al., CHI '24 (opened) | https://arxiv.org/html/2301.04945v2 | Mar/May 2024 | Data donation | B | About 45% of views watched to the end; 24% skipped before 20% | Viewer behaviour, not distribution | M | Benchmark: most videos lose many viewers early. The hook window matters (B for behaviour, D for ranking). |
| 28 | Mosnar et al., SIGIR '25 (opened) | https://arxiv.org/html/2504.18140v1 | Apr 2025 (SIGIR Jul 2025) | Replication audit | B | Watch now strongest; <100% watch weak, 400% strong; findings short-lived | Bots; hashtag heuristics | M–H | Watch-through and rewatch probably matter most now, but re-check over time. |
| 29 | Baumann et al. (arXiv opened; EPJ DS 2026 version blocked) | https://arxiv.org/html/2503.20231v1 | Mar 2025 | 42-bot audit, US | B | Amplification within about 66–140 videos; diversity falls | Bundled signals; two topics; one week | M | Viewers who engage with fashion get more fashion quickly. Interest pools are reachable. |
| 30 | WSJ investigation, via Tubefilter and Marketing Magazine (search result only) | https://tubefilter.com/2021/07/21/tiktok-recommendation-algorithm-wall-street-journal-guillaume-chaslot/ | 21 Jul 2021 | Journalistic bot audit | C | Lingering time dominant; rabbit holes within hours | Not opened; TikTok disputed | L | Historical support for the importance of watch time |
| 31 | Marketing Dive, TikTok USDS JV (opened) | https://www.marketingdive.com/news/tiktok-confirms-joint-venture-to-comply-with-us-law/810329/ | 23 Jan 2026 | Press report of an official statement | C | US algorithm to be retrained on US data in Oracle cloud | Status of retraining unknown | M | Pre-2026 audits may not describe current US behaviour. |

**Count:** 31 sources. 27 were opened. 4 are known from search results only (#14, #15, #30, and the NYT original behind #18).

---

## 4. Key takeaways for the Checkpoint A report

1. **Official multi-signal prediction model (A).** TikTok confirms it predicts per-viewer probabilities of finish, skip, time spent, like, share, comment, favorite, follow or profile interaction, sound tap and "Not interested", then combines them. There are no public weights. The leaked 2021 formula (C) has the same structure.
2. **Completion and watch time are the only signals TikTok has qualitatively called "strong" (A, 2020).** The most recent replication audit, Mosnar SIGIR 2025 (B), found watching to be the strongest personalisation factor, with only full or repeated watches having much effect. ByteDance's Douyin ranker trains on Finish and Skip labels (B, engineering).
3. **Signal rankings from audits are unstable over time (B).** Follow was strongest in 2021–23 and watch was strongest in 2025. Any fixed "algorithm hierarchy" in practitioner content should be rejected.
4. **Eligibility filters come before ranking (A).** Unoriginal or reused material, engagement manipulation, and content unsuitable for a broad audience are For You-ineligible under the guidelines effective 24 Sep 2026. Commercial (Shop) content is diversified so it does not cluster (A, DSA report).
5. **Organic and paid are linked only by attribution, not by documented ranking (A plus a gap).** Spark Ads engagement accrues to the organic post (A). TikTok says Promote does not hurt organic reach (A, 2022). No official source says paid engagement improves organic For You ranking. Organic For You documentation contains no conversion signals (CTR, landing page, add-to-cart, purchase).

## 5. Open questions (genuinely unknown)

- The relative weights of any signals, today or historically. Not public and not reverse-engineerable from audits.
- How a **new video** gets its first distribution. No official document describes a test or seed batch. Practitioner claims of fixed initial batch sizes are unverified (D).
- Whether paid views or engagement from Spark Ads change later **organic** For You distribution.
- Whether the US For You recommender has diverged since the USDS joint venture retraining (announced Jan 2026). Every pre-2026 audit may be stale for the US.
- Whether watch time is normalised by video length in TikTok's ranker. Strongly suggested by industry papers (B) but not confirmed for TikTok (D).
- How "low quality" is operationalised. The guidelines say "without anything new" but give no threshold.
- How heavily "Not interested", hides and reports suppress a creator's later distribution, as opposed to only that viewer's feed.
- Exact creator-analytics metric names and definitions in TikTok Studio (average watch time, watched full video, rewatch, traffic source). Only third-party guides seen (C). Verify in the account.
- Whether external-link (bio-link) clicks or off-TikTok outcomes feed organic ranking. No evidence either way.
- The EU recommender remedies proposed by the Commission (Feb 2026). Their final outcome and any global spill-over are unknown.

## 6. Suggested tests (to feed Checkpoint D; none run, no spend)

- **Matched-pair organic posts.** Same product, same length band, one variable changed (hook or loopability). Compare For You traffic share, average watch time, % watched full, and favorites/shares per 1,000 views. Expect high noise. Treat results as directional only.
- **Eligibility check.** Before diagnosing weak creative, confirm in Studio that a low-view post was not marked ineligible.
- **Spark boost halo test.** Boost half of a set of comparable organic posts with a small fixed budget, after owner approval and outside this note's scope. Compare organic-only views on the boosted and unboosted posts after the boost ends. Note confounding: Spark metrics combine organic and paid.
- **Length-normalised watch analysis.** Report % watched and completion by duration band, never raw watch seconds across lengths.
