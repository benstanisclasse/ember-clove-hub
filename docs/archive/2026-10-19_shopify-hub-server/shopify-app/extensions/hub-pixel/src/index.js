// Shopify hub web pixel: forwards storefront events to the hub's /collect/pixel endpoint.
// Runs in Shopify's strict sandbox. Sends NO personal data: event names, product ids,
// prices, ad cookies (_fbp/_fbc/_ttp) and the user agent only. Never throws.
import { register } from "@shopify/web-pixels-extension";

register(({ analytics, browser, settings }) => {
  const collectUrl = settings.collectUrl;
  if (!collectUrl) return;

  async function adCookies() {
    const [fbp, fbc, ttp] = await Promise.all([
      browser.cookie.get("_fbp"),
      browser.cookie.get("_fbc"),
      browser.cookie.get("_ttp"),
    ]);
    let browserId = fbp;
    if (!browserId) {
      // Meta accepts advertiser-set _fbp in its documented format.
      browserId = `fb.1.${Date.now()}.${Math.floor(Math.random() * 1e10)}`;
      try {
        await browser.cookie.set(`_fbp=${browserId}; path=/; max-age=7776000; SameSite=Lax`);
      } catch (e) {
        /* cookie writes can be blocked; the id is still sent for this event */
      }
    }
    return { fbp: browserId, fbc: fbc || null, ttp: ttp || null };
  }

  async function send(name, event, extra) {
    try {
      const ctx = event.context || {};
      const body = {
        name,
        id: event.id,
        ts: event.timestamp,
        clientId: event.clientId,
        url: ctx.document && ctx.document.location ? ctx.document.location.href : null,
        referrer: ctx.document ? ctx.document.referrer : null,
        ua: ctx.navigator ? ctx.navigator.userAgent : null,
        ...(await adCookies()),
        ...extra,
      };
      await fetch(collectUrl, {
        method: "POST",
        body: JSON.stringify(body),
        keepalive: true,
        headers: { "Content-Type": "text/plain" }, // simple request: no CORS preflight
      });
    } catch (e) {
      /* never break the storefront */
    }
  }

  const amount = (m) => (m && m.amount != null ? m.amount : null);
  const item = (variant, quantity) =>
    variant
      ? {
          id: variant.product && variant.product.id ? variant.product.id : variant.id,
          quantity: quantity || 1,
          price: amount(variant.price),
        }
      : null;

  analytics.subscribe("page_viewed", (e) => send("PageView", e, {}));

  analytics.subscribe("product_viewed", (e) => {
    const v = e.data && e.data.productVariant;
    send("ViewContent", e, {
      value: amount(v && v.price),
      currency: v && v.price ? v.price.currencyCode : null,
      items: [item(v, 1)].filter(Boolean),
    });
  });

  analytics.subscribe("product_added_to_cart", (e) => {
    const line = e.data && e.data.cartLine;
    const total = line && line.cost ? line.cost.totalAmount : null;
    send("AddToCart", e, {
      value: amount(total),
      currency: total ? total.currencyCode : null,
      items: [item(line && line.merchandise, line && line.quantity)].filter(Boolean),
    });
  });

  analytics.subscribe("checkout_started", (e) => {
    const c = e.data && e.data.checkout;
    send("InitiateCheckout", e, {
      value: amount(c && c.totalPrice),
      currency: c ? c.currencyCode : null,
      items: ((c && c.lineItems) || []).map((li) => item(li.variant, li.quantity)).filter(Boolean),
    });
  });

  // Not forwarded directly: the hub stores these browser signals and merges them into the
  // single server-side Purchase it sends after the order arrives (no double counting).
  analytics.subscribe("checkout_completed", (e) => {
    const c = e.data && e.data.checkout;
    send("Purchase", e, {
      orderId: c && c.order ? c.order.id : null,
      value: amount(c && c.totalPrice),
      currency: c ? c.currencyCode : null,
    });
  });
});
