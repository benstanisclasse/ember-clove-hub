# TikTok Upgraded Smart+ (v1.3) research notes, 2026-10-19

Source: business-api.tiktok.com/portal/docs (read in the browser; pages are SPA).

## Create (replace campaign/create, adgroup/create, ad/create)
- POST smart_plus/campaign/create/ - required: advertiser_id, request_id (string of a 64-bit int; idempotency key),
  objective_type (APP_PROMOTION | WEB_CONVERSIONS | LEAD_GENERATION), campaign_name; sales_destination required for
  WEB_CONVERSIONS (WEBSITE). budget_optimize_on defaults true (CBO); false = ad-group budgets (omit campaign budget_mode/budget).
  operation_status ENABLE|DISABLE (default ENABLE). Response data.campaign_id.
- POST smart_plus/adgroup/create/ - required: advertiser_id, request_id, campaign_id, adgroup_name, promotion_type (WEBSITE),
  optimization_goal (CONVERT), pixel_id + optimization_event (when CONVERT/VALUE), bid_type (BID_TYPE_NO_BID|BID_TYPE_CUSTOM),
  billing_event (OCPM; CPC for CLICK), schedule_type, schedule_start_time, targeting_spec{location_ids (required), age_groups...}.
  targeting_optimization_mode AUTOMATIC (default; only location/spc_audience_age/languages/os/excluded audiences) or MANUAL (age_groups, gender...).
  When CBO off: budget_mode required = BUDGET_MODE_DYNAMIC_DAILY_BUDGET or BUDGET_MODE_TOTAL (NO BUDGET_MODE_DAY; dynamic daily may spend 125%/day, avg over week) + budget.
  SCHEDULE_FROM_NOW only with dynamic daily budget. Automatic placement = omit placement_type/placements. Response data.adgroup_id.
- POST smart_plus/ad/create/ - advertiser_id, adgroup_id, ad_name, operation_status, creative_list[{creative_info{ad_format SINGLE_VIDEO,
  video_info{video_id}, image_info[{web_uri: image_id}], identity_type, identity_id, identity_authorized_bc_id (BC_AUTH_TT)}}],
  ad_text_list[{ad_text}], landing_page_url_list[{landing_page_url}], ad_configuration{call_to_action_id}. No request_id. Response data.smart_plus_ad_id.
  * Custom identity (CUSTOMIZED_USER) non-Spark ads are no longer supported on TikTok placement (all accounts; new accounts since 2026-01-15).
    Spark identity (TT_USER, BC_AUTH_TT, AUTH_CODE) goes in creative_info; Spark Ads Push = video_id + cover with TT_USER/BC_AUTH_TT.
  * With a Spark identity, WEB_CONVERSIONS and auto placement, a dynamic CTA (call_to_action_id = CTA creative portfolio id) is REQUIRED;
    call_to_action_list (standard CTA) is not allowed.
- Dynamic CTA: GET creative/cta/recommend/?new_version=true&objective_type=WEB_CONVERSIONS&promotion_type=WEBSITE&language=en
  -> data.recommend_assets[{asset_ids[], asset_content}]; POST creative/portfolio/create/ {creative_portfolio_type: CTA,
  portfolio_content:[{asset_content, asset_ids}]} -> data.creative_portfolio_id.

## Read / update
- Legacy campaign/get and adgroup/get return Upgraded Smart+ entities (field campaign_automation_type = UPGRADED_SMART_PLUS).
- Legacy ad/get returns Smart+ ads at creative level (campaign_automation_type UPGRADED_SMART_PLUS_CREATIVE, ad_id = creative id,
  smart_plus_ad_id = the ad). Filter ad_ids_v2 returns asset-group level (ad_id_v2) with only id/name/automation type fields.
- smart_plus/{campaign,adgroup,ad}/get/ exist (filters campaign_ids / adgroup_ids / smart_plus_ad_ids); ad rows have smart_plus_ad_id, operation_status, secondary_status.
- report/integrated/get: dimension ad_id_v2 = manual ad id OR Upgraded Smart+ ad id (asset group); ad_id = creative id for Smart+.
- Smart+ writes: smart_plus/campaign/update/ (budget), smart_plus/adgroup/budget/update/ (same body as legacy),
  smart_plus/{campaign,adgroup}/status/update/ (campaign_ids/adgroup_ids), smart_plus/ad/status/update/ (smart_plus_ad_ids). Legacy endpoints for manual entities.
- File uploads unchanged (file/video/ad/upload/, file/image/ad/upload/).

## Scopes
Permission-scope table (Appendix > Permission scope) does not list any smart_plus/* endpoint. CTA endpoints
(creative/cta/recommend, creative/portfolio/create) are Creative Management > Creative Recommendation > CTA Recommendation.
No new top-level scope; first-level Ads Management + Creative Management cover the children.
