# Stage D: data-licensing review (Kalodata Open API, CJ Dropshipping API)

Prepared 2026-11-01 for the Demand Signal Intelligence viability assessment. This is a careful reading of public
terms, **not legal advice**. Where the text is unclear, it is marked ambiguous and left unresolved. No sign-up,
log-in, trial, form submission or contact took place. Quotes are kept to 15 words or fewer, with at most one per
item. Translations from Chinese are mine and are marked as such.

## 1. Summary

- **Kalodata: we could not read the current terms. The terms we could read block the product as designed.**
  - Every kalodata.com page we tried returned HTTP 403 behind a Cloudflare bot challenge (`cf-mitigated: challenge`).
    That covers the terms, pricing, Open Center home, Open Center docs, blog and knowledge base. We did not try to
    get around the challenge.
  - The only readable terms are two Kalodata Terms of Service copies on `kalodata.gitbook.io`, dated Aug 9, 2023 and
    Nov 6, 2023. Both predate the Open API, which launched in 2026.
  - Those terms bar:
    - distributing, selling, renting or leasing the Services (cl. 4.1.3, 4.1.4)
    - derivative works (4.1.2)
    - building the Services into another product (4.1.7)
    - commercial use without written consent (4.1.5, 10.3)
    - in the controlling Chinese text, providing the Services to any third party (4.1.5)
  - We found no public Open API licence, so whether a separate API agreement overrides these terms is unknown.
  - Governing law is PRC (mainland), with disputes going to Shenzhen Court of International Arbitration (SCIA)
    arbitration. The Chinese text prevails.
- **CJ Dropshipping: the public terms are built for a dropshipper using the API on its own account.**
  - The User Agreement (effective Oct 4, 2025) makes the account "for your personal use only" without consent
    (III.2). Without written permission, it bars:
    - commercial use of platform information content (IX.3(1))
    - re-arranging that content and displaying it off-platform (IX.3(2))
  - The Terms of Service (§2) bar reselling or exploiting any portion of the Service without written permission.
  - The developer docs say a key "can only view the data under the current account". They also cap each IP address
    at 3 users.
  - API access is suspended after 30 consecutive days with no CJ transactions.
  - We found no public developer, ISV or partner agreement.
  - Governing law is Mainland China, with exclusive jurisdiction of a Chinese court at CJ's location (Yiwu).
- **Launch blockers:** all five priority Kalodata items (1, 3, 4, 6, 7) are blockers until written terms say
  otherwise, and so is CJ's restriction on serving third parties. See section 5.

## 2. Access log and document status

| Provider | Document | Status (2026-11-01) |
|---|---|---|
| Kalodata | kalodata.com (home, /terms, /pricing, /open-center/home, /open-center/docs, /knowledge.html, blog) | **Blocked**: HTTP 403, Cloudflare challenge. Not bypassed. |
| Kalodata | Terms of Service, GitBook copy "Last updated: Aug 9, 2023" (English + Chinese) | Read in full. |
| Kalodata | Terms of Service, GitBook copy "Last updated: November 6, 2023" (adds cl. 13, SMS) | Read; key clauses match the Aug 2023 text. |
| Kalodata | Privacy Policy | **Not found**. Referenced in ToS cl. 6.1, but no public copy was reachable. |
| Kalodata | Open API / Open Center agreement or API terms | **Not found publicly**. Probably behind the Open Center login, which was not attempted. |
| Kalodata | API pricing / plan terms | Only in third-party reports (see notes). Not verified on kalodata.com. |
| CJ | User Agreement (version update Sep 26, 2025, effective Oct 4, 2025), Yiwu Cujia Trade Co., Ltd. | Read in full. |
| CJ | Terms of Service (undated, ©2026) | Read in full. |
| CJ | Store Authorization Agreement (undated) | Read. |
| CJ | Privacy Policy (undated) | Read for data-use sections. |
| CJ | Developer docs: Overview, Introduction, Development, API key, Interface Call Restrictions, Points Resource Rules, Notice | Read. No developer agreement or terms link appears in the docs. |
| CJ | "CJ Dropshipping Agreement 2024.12.23" (PDF on oss.cjdropshipping.com) | **Not read**. The fetch tool could not extract text from the compressed PDF. It auto-cached a copy in the session tool-results folder, which was not opened. Its embedded links point to the User Agreement. |
| CJ | Developer / ISV / partner programme terms | **Not found publicly**. |

**Caveats on authenticity.** The Kalodata GitBook pages sit on a `kalodata` subdomain and link to kalodata.com,
but we cannot confirm that Kalodata currently endorses them or that they match the live terms. Third-party
descriptions of the Kalodata API conflict with one another:

- Scavio: Enterprise-only, about $570/month or more, application required.
- Open Center snippet and community CLI READMEs: self-serve keys, 0.1 points (credits) per call.

## 3. Per-provider table

Key: **A** = allowed, **P** = prohibited (as written, absent written consent), **S/A** = silent or ambiguous.

| # | Item | Kalodata (ToS 2023, GitBook) | CJ Dropshipping (UA 2025, ToS, docs) |
|---|---|---|---|
| 1 | Display raw records to third-party users | **P**: cl. 4.1.3 "distribute, license, transfer, or sell, in whole or in part, any of the Services" | **P** without written permission: UA IX.3(2) "followed by displaying it on channels other than the source pages" |
| 2 | Display derived metrics | **P/S-A**: cl. 4.1.2 "create any derivative works of the Services or any content included therein" | **S/A** (written permission needed on a plain reading): UA IX.3(1) "utilize the platform's information content for any form of commercial purposes" |
| 3 | Predictive rankings / scores | **P/S-A**: cl. 4.1.7 "incorporate the Services or any portion thereof into any other program or product" | **S/A**: nothing specific. Same IX.3(1) issue if CJ data feeds the scores. |
| 4 | Store historical data indefinitely | **S/A**: silent on storage. Cl. 4.1.2 bars "make unauthorised copies". | **S/A**: silent. UA I.1.1 "Product information is subject to the real-time details displayed". |
| 5 | Cache API responses | **S/A**: silent. No public API terms. | **S/A**: silent. The points system makes caching practical, but nothing permits it in writing. |
| 6 | Multi-tenant sharing across customers | **P**: cl. 4.1.5 (Chinese, controlling) "将服务提供给任何第三方" ("providing the Services to any third party", my translation) | **P** (operator account): UA III.2 "Without our consent, your account is for your personal use only." |
| 7 | Sell subscriptions to derived intelligence | **P**: cl. 4.1.4 "market, rent or lease the Services for a fee or charge" | **P** without written permission: ToS §2 "reproduce, duplicate, copy, sell, resell or exploit any portion of the Service" |
| 8 | Build a competing product | **S/A**: no non-compete. Cl. 4.1.2 bars trying to "determine any source code, algorithms, methods or techniques". | **S/A**: silent. UA IX.3(3) bars "directing, diverting, or hijacking transactions". |
| 9 | Attribution requirements | **S**: none stated | **S**: none stated |
| 10 | Retention / deletion on termination | **S**: user's duties not stated. Cl. 3.4 says "you will not be able to reactivate your account or retrieve any of the content". | **S**: user's duties not stated. The Store Authorization Agreement says "CJ will regularly clear the store data" (CJ's own duty). |
| 11 | Use data to train models | **S/A**: silent. Cl. 5.1 "We reserve all intellectual property rights and ownership related to the services". | **S/A**: silent. UA XII.2 says the compilation of content "is the exclusive property of CJ". |

### Other terms

| Topic | Kalodata | CJ Dropshipping |
|---|---|---|
| Governing law / forum | PRC mainland law (12.1). Negotiation, then SCIA arbitration (12.2). Chinese text prevails (12.3). | Mainland China law excluding HK, Macao and Taiwan (UA XX.1). Negotiation, then exclusive jurisdiction of the competent Chinese court at CJ's location (XX.2). **Inconsistent:** the UA also says a "UK (Simplified) version" prevails and cites "UK and international laws", and the ToS §12(c) cites "France's regulations". |
| Per-breach penalties | No fixed or liquidated amount. Uncapped indemnity for "all losses" (cl. 8). Account disablement (3.3). | No fixed amount. Compensation claims for multi-user use (III.11) and losses, including fines and reputation (XV.4). Account freeze (XIV.1). Penalties for bribery (II.13). |
| Personal / non-transferable | Cl. 5.1: "limited, non-transferable right to use, restricted to the agreed scope". | Account not transferable, lendable or licensable (III.2). No sharing outside your own business entity (III.6). Terms not assignable by the user (II.12). |
| Rate / volume limits tied to licence | No public terms. Third parties report credit or points pricing (about 0.1 points per call) and Enterprise gating. Unverified. | 10 req/s per IP; 30 req/s for non-login endpoints; **3 users per IP**. Per-user 1, 2, 4 or 6 req/s by level (Free/Plus/Prime/Advanced). Daily points: 50,000 base plus 100 per US$1 of recent transactions. 10 to 1,000 points per call. HTTP 429 when exhausted. **Suspension after 30 consecutive days of zero CJ transactions.** CJ may adjust limits. |
| Own use vs serving others | Commercial use and providing the Services to third parties both need express written consent (4.1.5, 10.3). | Docs: a key "can only view the data under the current account". The UA's "API Usage Specifications" (IX.4) describe linking your own store. No ISV or partner path is published. |
| Other incorporated terms | Cl. 1.1 makes use "also subject to the terms of our partners", naming the TikTok Developer Terms of Service. | The UA incorporates the Store Authorization Agreement, Privacy, Dispute and Cookie policies, and "all types of rules" CJ publishes later. |

## 4. Clause notes

### Kalodata

- **The 2023 terms describe a dashboard, not an API licence.** Cl. 4.1.7 bars building the Services into "any other
  program or product". Cl. 4.1.8 bars "automated scripts to collect information". Read literally, both conflict with
  any use of a paid API. Kalodata now sells the Open API, so it almost certainly has separate API terms behind the
  Open Center login. Until we have them, assume the general terms apply.
- **Commercial use.** Cl. 4.1.5 bars commercial use "without our express written consent". Cl. 10.3 (all caps)
  says users agree not to use the platform for any commercial or business purposes. This sits oddly with cl. 1.2,
  which assumes business users. **Ambiguous**, but on its face it rules out a paid SaaS built on Kalodata data.
- **The Chinese text is broader and controls (12.3).**
  - Chinese 4.1.5 adds two bans: using the software services beyond the agreed scope, and providing the Services to
    any third party.
  - Chinese 4.1.8 adds a ban on crawling, copying, tampering with, spreading or illegally using "our data, code,
    technology and resources" (my translation).
  - Chinese 4.1.8 is the closest the terms come to addressing model training or bulk storage.
- **Ownership of data.** Cl. 5.1 lists "data" and "any derivative works" among the rights Kalodata reserves. A
  "derivative works" ban (4.1.2) that covers "any content included therein" could reach computed metrics and
  scores. Whether a statistical transform is a "derivative work" is a legal question we have not answered:
  **ambiguous, treat as restricted**.
- **Confidentiality (cl. 7).** Users must keep confidential any "trade secrets and sensitive information" learned
  through the service. This could arguably cover non-public sales estimates. **Ambiguous.**
- **Upstream TikTok terms.** Cl. 1.1 makes use subject to partner terms, including the TikTok Developer Terms. Any
  Kalodata API licence may therefore carry TikTok's own redistribution limits. These were not reviewed here.
- **Liability.** Kalodata caps its own liability at amounts paid (10.2). The user's indemnity (cl. 8) has no cap.

### CJ Dropshipping

- **Account is personal (III.2, III.6, III.11).** Without consent, the account is for personal use only. It may not
  be "made available to third parties or jointly controlled/used with third parties". Use by several users outside
  your business entity can lead to compensation claims. So one operator account serving all subscribers is
  prohibited without consent.
- **Information content (IX.3).** Without CJ's written permission, users may not copy, read or use platform
  information content "for any form of commercial purposes". Nor may they edit or arrange it and then display it on
  channels other than CJ's source pages. Ordinary dropshipping, such as listing CJ products in your own store through
  CJ's tools, is plainly expected. Whether a third-party intelligence product that shows CJ prices, stock and
  freight falls under IX.3 is **ambiguous**. On a plain reading it needs written permission.
- **Use limited to permitted purposes (II.4).** "Any content, materials, or information obtained from the CJ
  website shall only be used for purposes permitted by the CJ website."
- **ToS §2** separately bars reproducing, selling, reselling or exploiting any portion of the Service without
  express written permission. ToS §12(i) bars spidering, crawling or scraping. This does not cover the API itself,
  but it shows CJ's general stance.
- **Technical signals about intended use.**
  - The 3-users-per-IP cap means one SaaS server holding many subscribers' own CJ keys would hit the cap after 3
    users. This needs CJ's confirmation or a partner arrangement.
  - Points scale with your own transaction volume.
  - API access is cut off after 30 days with no transactions.
  - Together these show the API is meant for active buyers working on their own accounts.
- **CJ's rights over data.** UA XII.6: CJ keeps "independent usage rights" over competitively valuable data. Store
  data from an authorised store may be collected (XI.1(5)). CJ may also share non-personal information with third
  parties (Privacy Policy).
- **Partners (X).** CJ names partners such as Shopify, Shopmaster and ShipStation. That suggests a partner route
  exists, but no public partner or ISV terms were found.
- **Retention.** The user's obligations on termination are not stated. The Privacy Policy says CJ keeps personal
  data only "for as long as required" and gives no specific periods.

## 5. Launch blockers

**Kalodata.** Each item stays a blocker until a written API licence permits it.

| # | Item | Status |
|---|---|---|
| 1 | Display raw records | Prohibited (4.1.3, 4.1.5). **Blocker.** |
| 3 | Predictive rankings | Prohibited or ambiguous (4.1.2 derivative works, 4.1.7). **Blocker.** |
| 4 | Indefinite history | Silent or ambiguous (4.1.2 copies; Chinese 4.1.8 copying of data). **Blocker** until confirmed. |
| 6 | Multi-tenant | Prohibited (Chinese 4.1.5 third parties; 4.1.4). **Blocker.** |
| 7 | Resale of derived intelligence | Prohibited (4.1.4, 4.1.5, 10.3). **Blocker.** |

Also blocking:

- Current terms and the API licence could not be read (Cloudflare wall; no public API terms).
- PRC law with SCIA arbitration and an uncapped indemnity raises the cost of getting this wrong.

**CJ Dropshipping.**

- **Serving third parties is a blocker** until CJ confirms in writing. The grounds are:
  - personal-use account (III.2/III.6)
  - written permission needed for commercial use and off-platform display of information content (IX.3(1)–(2))
  - ToS §2 resale ban
  - current-account-only API scope
  - 3-users-per-IP cap
- **Operational risk, not a legal bar:** the operator account loses API access after 30 days with no transactions.
- The model has two workable shapes, both needing confirmation:
  - CJ grants written permission, or a partner/ISV agreement, to show CJ catalogue data to subscribers.
  - Each subscriber connects their own CJ key or account and sees only their own data. This still needs CJ to
    confirm that a third-party app may hold those keys, given the IP cap.

Not blockers on current evidence, but they need answers:

- Kalodata 2, 5, 8, 9, 10, 11
- CJ 3, 4, 5, 8, 9, 10, 11

## 6. Questions to send for written clarification

Send these only with the owner's approval. Nothing has been sent.

### To Kalodata (Open Center / Enterprise sales)

1. Please send the full, current agreement that governs the Open API (Open Center), with its effective date. Does it
   replace or add to the website Terms of Service, and which version prevails?
2. May an API customer show raw API records to its own paying, unaffiliated end users inside a web application?
   Raw records include product revenue estimates, units sold and category or shop rankings. If yes, are there
   limits on volume, granularity or freshness?
3. May we compute and show derived metrics and our own predictive rankings or scores, built from API data, to paying
   end users? Does Kalodata treat these as "derivative works" under ToS cl. 4.1.2 or "incorporation" under
   cl. 4.1.7?
4. May one API account serve many separate customer organisations from shared storage (multi-tenant)? Or does each
   end-customer need their own Kalodata licence or key?
5. Does ToS cl. 4.1.5 (in particular the Chinese text on providing the Services to third parties) and cl. 10.3 (no
   commercial or business purposes) apply to API customers? If so, what written consent or plan would permit a
   commercial subscription product?
6. May we store API responses indefinitely to build a historical time series, and keep using them after a
   subscription ends? Are there caching time limits or refresh requirements?
7. What must we do with stored Kalodata data on termination (delete, return, certify)?
8. Is attribution required (for example "Data: Kalodata") on displayed records or derived scores?
9. May API data be used to train or fit statistical or machine-learning models? May the trained models or their
   outputs be used commercially after termination?
10. Are there restrictions on products that overlap with Kalodata's own offering, such as TikTok Shop
    product-research tools?
11. Which upstream partner terms (for example TikTok's) apply to API data, and do they restrict redistribution to end
    users?
12. Which plan includes API access, at what price? What are the per-call credit costs, rate and daily limits, and
    the consequences of exceeding them?
13. Is API access personal or non-transferable? Could it be assigned to a company we form later?
14. Can disputes for a non-Chinese customer be heard somewhere other than SCIA under PRC law? Is there an English
    version that prevails for API customers?

### To CJ Dropshipping (developer / partnership team)

1. Is there a developer, ISV or partner agreement for third-party applications that use the CJ API to serve other
   users? Please send it.
2. May a third-party SaaS show CJ product data to its own paying subscribers? This covers product data, prices,
   stock, warehouse and freight quotes. Does this need written permission under User Agreement IX.3(1)–(2) and ToS
   §2? If so, how do we apply?
3. May one company account's API key serve many subscribers? Or must each subscriber link their own CJ account or
   key? Is a third-party app allowed to store and use subscribers' keys or tokens?
4. The limit "Each IP address is limited to 3 users": how should a hosted application serving many CJ users comply?
   Is there a partner allowance?
5. May we cache and store CJ API responses (prices, stock, freight) historically, and for how long? Must displayed
   prices or stock be refreshed within a set time?
6. May we show margins we calculate from CJ prices and freight next to third-party sales estimates? May we include
   CJ data in scores or rankings?
7. Are there attribution or branding rules (CJ name or logo, links back to CJ product pages)?
8. What must we do with CJ data on termination or de-authorisation?
9. May CJ API data be used to train or fit models?
10. The 30-day zero-transaction suspension rule: does it apply to an integration or partner account that does not
    place orders itself? Is there an exemption for partners?
11. Which document and governing law apply to API use? The User Agreement (Mainland China courts) refers to a "UK
    (Simplified) version", and the ToS refers to French regulations.

## 7. Sources

All accessed 2026-11-01.

1. Kalodata Terms of Service (GitBook copy, "Last updated: Aug 9, 2023", English and Chinese):
   https://kalodata.gitbook.io/untitled/terms-of-service (Markdown: https://kalodata.gitbook.io/untitled/terms-of-service.md)
2. Kalodata Terms of Service (GitBook copy, "Last updated: November 6, 2023"): https://kalodata.gitbook.io/termsofservice
3. Kalodata website and terms (blocked, HTTP 403, Cloudflare challenge): https://www.kalodata.com/ and https://www.kalodata.com/terms
4. Kalodata pricing (blocked, 403): https://www.kalodata.com/pricing
5. Kalodata Open Center home and docs (blocked, 403; content seen only as a search-engine snippet):
   https://www.kalodata.com/open-center/home and https://www.kalodata.com/open-center/docs
6. Kalodata blog, "How to Access TikTok Shop API in 2026" (blocked, 403):
   https://www.kalodata.com/blog/kalodata/how-to-access-tiktok-shop-api-in-2026/
7. Kalodata Knowledge Base (blocked, 403): https://www.kalodata.com/knowledge.html
8. Scavio blog, "Kalodata API: Launched but $570/Mo Enterprise-Only" (third party, unverified):
   https://scavio.dev/blog/tiktok-shop-product-research-api-vs-kalodata-2026
9. Dashboardly, "FastMoss vs Kalodata Pricing & API" (third party, competitor):
   https://www.dashboardly.io/post/fastmoss-vs-kalodata-the-2025-battle-for-tiktok-shop-analytics-supremacy
10. ClawHub Kalodata skill (third party; secret-key header, Open Center account URL): https://hub.openclaw.ai/maosen-sgy/skills/kalodata
11. GitHub sailtonight/kalodata-skill (third party, not shown to be official): https://github.com/sailtonight/kalodata-skill
12. CJdropshipping User Agreement (update Sep 26, 2025, effective Oct 4, 2025): https://cjdropshipping.com/user-agreement/en
13. CJdropshipping Terms of Service (undated): https://cjdropshipping.com/termsofservice
14. CJdropshipping Store Authorization Agreement (undated): https://cjdropshipping.com/storeAuthorizationAgreement
15. CJdropshipping Privacy Policy (undated): https://cjdropshipping.com/privacyPolicy
16. CJ developer docs, Overview: https://developers.cjdropshipping.com/en/summary/
17. CJ developer docs, API Introduction: https://developers.cjdropshipping.com/en/api/introduction.html
18. CJ developer docs, Development ("current account" scope; token validity): https://developers.cjdropshipping.com/en/api/start/development.html
19. CJ developer docs, How to Get API Key: https://developers.cjdropshipping.com/en/api/start/apikey.html
20. CJ developer docs, Interface Call Restrictions: https://developers.cjdropshipping.com/en/api/start/limit.html
21. CJ developer docs, Points Resource Rules: https://developers.cjdropshipping.com/en/api/api2/standard/points.html
22. CJ developer docs, Notice: https://developers.cjdropshipping.com/en/publication/notice.html
23. CJ Dropshipping Agreement 2024.12.23 (PDF; not readable through the fetch tool, not reviewed):
    https://oss.cjdropshipping.com/pdf/CJ%20Dropshipping%20Agreement%202024.12.23.pdf
24. TikTok Developer Terms of Service (incorporated by Kalodata ToS cl. 1.1; not reviewed):
    https://www.tiktok.com/legal/page/global/tik-tok-developer-terms-of-service/en
