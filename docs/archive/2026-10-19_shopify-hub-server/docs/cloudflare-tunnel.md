# Public HTTPS with Cloudflare Tunnel

Shopify webhooks, the ad platforms' OAuth callbacks and Claude (MCP) need to reach the hub
over HTTPS. Cloudflare Tunnel provides that with **no router port forwarding**: the
`cloudflared` container dials out to Cloudflare, and Cloudflare sends traffic back down that connection.

```
Internet ──HTTPS──> Cloudflare edge ──tunnel──> cloudflared ──> caddy:8080 ──> api:8000
                                                                 (allow-list)
LAN ──> 192.168.1.210:8081 ──> caddy:8081 ──> api:8000   (admin + health; not reachable via tunnel)
```

Only these paths are answered publicly (`deploy/Caddyfile`); everything else returns 404:
`/healthz`, `/webhooks/*`, `/oauth/*`, `/mcp`, `/.well-known/oauth-*`.
Postgres, Redis, Garage and the admin routes have no public route at all.

## Setup (one time, about 10 minutes)

Prerequisite: `[my-domain.com]` uses Cloudflare DNS (its nameservers point to Cloudflare).

1. Cloudflare dashboard > **Zero Trust > Networks > Tunnels > Create a tunnel**.
   Choose **Cloudflared**, name it `shopify-hub`.
2. On the *Install connector* screen, pick **Docker** and copy only the token, the long string
   after `--token`. Put it in `.env` on the VM:
   ```bash
   nano ~/shopify-hub/.env      # CLOUDFLARE_TUNNEL_TOKEN=eyJ...
   ```
3. **Public hostname** tab > *Add a public hostname*:
   * Subdomain `hub`, domain `my-domain.com`, path empty
   * Service type **HTTP**, URL **`caddy:8080`**

   Cloudflare creates the `hub.my-domain.com` CNAME for you.
4. Set `PUBLIC_BASE_URL=https://hub.my-domain.com` in `.env`, then deploy:
   ```bash
   cd ~/shopify-hub && scripts/deploy.sh      # starts cloudflared automatically once the token is set
   ```
5. Check from anywhere:
   ```bash
   curl https://hub.my-domain.com/healthz            # {"status":"ok"}
   curl -i https://hub.my-domain.com/admin/settings  # 404 -- admin is not public
   ```

## Recommended hardening (Cloudflare dashboard)

* **SSL/TLS > Edge Certificates**: Always Use HTTPS on, minimum TLS 1.2.
* **Security > WAF > Custom rules**: block requests to `hub.my-domain.com` whose path doesn't
  start with one of the public prefixes above. That's a second allow-list, enforced at Cloudflare's edge.
* Leave Cloudflare Access off for `/webhooks/*` and `/mcp`: Shopify and Claude can't log in.
  Those routes authenticate themselves (HMAC signatures and bearer/OAuth tokens).
