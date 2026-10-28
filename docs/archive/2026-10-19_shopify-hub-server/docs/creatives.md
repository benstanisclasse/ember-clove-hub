# Creatives: Higgsfield generation to ads

```
brief ──> N variants (+ ML traits) ──estimate──> monthly cap check ──> Higgsfield jobs
     ──(poll every minute / webhook nudge)──> output copied to Garage ──> creative READY
     ──(on approval) launch──> upload to Meta / TikTok / YouTube ──> PAUSED ad ──> creative ↔ ad link
```

## Setup

1. console.higgsfield.ai > **API keys**: put the key ID in `HIGGSFIELD_API_KEY` and the secret in
   `HIGGSFIELD_API_SECRET`. Credits are bought in the console; the API spends them.
2. Pick a **video model** in the console (for example an image-to-video Kling or Seedance endpoint) and copy
   its id into `HIGGSFIELD_VIDEO_MODEL`. The image default `higgsfield-ai/soul/v2/standard` works as is.
   Higgsfield has no public model list, so models live in config: `HIGGSFIELD_EXTRA_MODELS` adds more, and
   `higgsfield models` checks which ones your account can use.
3. **Set a monthly cap.** Generation is blocked until you do:
   ```bash
   docker compose exec api python -m app.cli settings set higgsfield_monthly_cap_usd 100
   ```
4. Webhooks are automatic once `PUBLIC_BASE_URL` is your public https URL. The hub registers
   `/webhooks/higgsfield/<secret token>` with each job. Without them, the hub still polls every minute.
5. For Google video ads, upload a square logo once and copy the printed line into `.env`:
   ```bash
   docker compose exec -T api python -m app.cli ads upload-logo logo.png < logo.png
   ```

## Making creatives

A brief (see [examples/brief.json](examples/brief.json)) lists angles, hook types, avatars and optional
literal hook lines. `n` variants rotate through every combination, and each variant's traits are saved to
`creative_traits` for the Phase 7 model.

```bash
docker compose exec -T api python -m app.cli higgsfield estimate --n 4 < brief.json   # free: cost + cap headroom
docker compose exec -T api python -m app.cli creatives generate --n 4 < brief.json     # spends credits
docker compose exec api python -m app.cli creatives list
```

* Model-specific fields (resolution, seed, motion strength...) go in `extra_params` and are passed through.
  The free estimate call rejects wrong fields before anything is spent.
* `reference_image_url` (for example your Shopify product photo URL) is sent as `image_url` for image-to-video models.
* To iterate on a winner, set `parent_creative_id` in the brief.

**Money guards:** read-only and the kill switch block generation. The whole batch's estimate must fit under
the monthly cap, or nothing is submitted. Each job carries an idempotency key, so a retried request can't
charge twice. Failed, moderated and cancelled jobs count as $0, because Higgsfield refunds them. Jobs
running longer than `HIGGSFIELD_JOB_TIMEOUT_MINUTES` are cancelled and marked failed.

Higgsfield keeps outputs for only about 7 days. The hub copies each file into Garage as soon as the job
completes (`creatives/<creative id>/<job id>.mp4`). Backups include that bucket.

## Launching (on approval)

```bash
docker compose exec api python -m app.cli creatives launch 12 --platforms meta tiktok google \
  --budget 20 --url https://your-store.com/products/x --text "Glow in 7 days" --headline "Real results"
```

For each platform the hub uploads the video, plus a thumbnail made with ffmpeg (Meta and TikTok require
one) or your logo (Google). If you don't pass `--ad-set platform=ID`, it also creates a new campaign and ad
set with `--budget` per day. It then creates the ad and links creative to ad, so profit per creative appears
in `v_creative_daily_profit` once the ad spends.

Everything is created **PAUSED**. Turning ads on is a separate approved action (Phase 5), and the spend limits
come in Phase 6. Read-only blocks launching, like every other write.
