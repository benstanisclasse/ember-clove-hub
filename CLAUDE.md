# Ember & Clove Hub: rules for any Claude session

## Character-account content: use the conveyor, nothing else
- All content for the character account goes through `python scripts/studio/cli.py` (see `studio/README.md`).
- Never generate character videos with one-off scripts (`make_*.py`) or by calling video APIs directly.
- Never edit `studio/studio.db` by hand, and never move an episode's stage except through `cli.py`.
- Never pass `--actor owner` unless the owner wrote the approval in this conversation; put their exact words in
  `--quote`. Never approve a bible file, episode or rule change on your own judgement.
- Never weaken a rule in `studio/bible/rules.yaml` to make something pass; fix the script or ask the owner.
- When a video fails for a new reason, add it to `rules.yaml` (`tts_avoid`, `banned_phrases`) and tell the owner.
- Realism is the owner's call: report machine checks as checks, not as a verdict that a video looks real.

## Standing owner rules (all work)
- AI presenter, labelled as AI. No testimonials or "I bought" claims. No prices or delivery times in spoken lines
  or captions. No post-production edits unless approved. Don't publish, spend or change live store settings without
  approval. Never print or store API keys; keys live in user environment variables (`config/hub.json` secrets).
- Log every material action in `log.md`.

## Code, history and backups (since 2026-10-27)
- The Hub is a git repository with a **private** GitHub remote (`origin` = github.com/benstanisclasse/ember-clove-hub-private,
  branch `master`). After changing code, config or docs, commit with a clear message and `git push`.
- A **public** copy lives at github.com/benstanisclasse/ember-clove-hub. Never push to it directly: after `git push`, run
  `python -I scripts/publish_public.py`, which replaces emails and account/ad IDs with XXX. New private IDs go in
  `config/hub.json` (`*_id` keys) or the untracked `config/public_redact.json` before publishing.
  Never commit secrets; `.gitignore` keeps out media, raw exports, databases, backups and logs.
- `studio/analytics.db` holds history (post snapshots, followers, ad days) and sync health; `studio/studio.db` stays the
  conveyor. Reporting days are Eastern: use `studio.analytics.local_day()`.
- Nightly backups (Windows task "Ember Hub Nightly Backup", `scripts/backup_hub.py`) go to `backups/`. Run it by hand
  before any database migration.
- Dashboard 2.0 plan and audit: `docs/`. Tests: `python -m pytest -q scripts/studio`.
