"""Conversions: report purchases and storefront events to Meta, TikTok and Google.

* Browser side: a Shopify web pixel (``shopify-app/extensions/hub-pixel``) posts storefront
  events to ``/collect/pixel``. No PII: just event, product ids, cookies (_fbp/_fbc/_ttp),
  IP and user agent, which the hub forwards to Meta CAPI / TikTok Events API in batches.
* Server side: every real order is sent **once per platform** as a purchase (unique row in
  ``conversion_events``), enriched with that checkout's browser signals and, if enabled,
  SHA-256 hashed email + phone fetched transiently from Shopify (never stored).
* Google gets click conversions (orders with gclid / gbraid / wbraid).

Everything is off until ``conversions_enabled`` is set, and the kill switch stops it.
"""
