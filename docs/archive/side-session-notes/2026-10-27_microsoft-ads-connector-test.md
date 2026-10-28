# Microsoft Ads MCP connector test — 2026-10-27

Result: **NOT usable from this Claude Code session — no tools reached the session.** No API calls made, nothing changed in Microsoft Advertising.

## Evidence
- `session_connectors_status`: Microsoft Ads is **absent** (not even listed as disabled/failed/needs_auth).
  Listed connectors: Claude Docs, higgsfield, Gmail, Lovable, TikTok for Business, Shopify (+ google-analytics, google-ads[pending], scheduled-tasks).
- `set_session_connector_enabled("Microsoft Ads MCP")` and by id `f17947e7-231a-4c45-af41-63cf8b848370` both errored verbatim:
  > No claude.ai connector by that name or id is available to this session. Connectors you can toggle: Claude Docs, Gmail, higgsfield, Lovable, Shopify, TikTok for Business. For a connector the user has not installed, use search_mcp_registry / suggest_connectors.
- `mcp-registry list_connectors` (account level) DOES show it:
  `name: "Microsoft Ads"`, `url: "https://partner.api.bingads.microsoft.com"`, `connected: true`, directoryUuid `f17947e7-231a-4c45-af41-63cf8b848370`.
- ToolSearch for microsoft / bing / customer / account: zero Microsoft Ads tools.

## Likely causes (unverified)
1. Saved URL looks like host only — `https://partner.api.bingads.microsoft.com` — missing `/ext/mcp/vnext`.
   Other connectors in the same listing show full paths (Gmail `/mcp/v1`, TikTok `/open_mcp/...`), so the listing does keep paths.
   With no path the server likely exposes no tools, and that fits the known "empty tool list after OAuth" pilot issue.
2. Name is "Microsoft Ads", not "Microsoft Ads MCP", so it may be a different or older entry than the one the owner thinks they added.
3. A connector that is connected but has zero tools seems to be dropped from Code sessions entirely.

Couldn't open claude.ai/settings/connectors to check: the built-in browser isn't signed in to claude.ai.

## Suggested fix
In claude.ai → Settings → Connectors, open "Microsoft Ads", confirm the URL is exactly
`https://partner.api.bingads.microsoft.com/ext/mcp/vnext`. If it isn't, remove the connector and re-add it with the full URL, reconnect (OAuth), then start a NEW Code session and re-test.
