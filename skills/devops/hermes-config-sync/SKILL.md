---
name: hermes-config-sync
description: "Back up or restore the Hermes config to/from a git repo."
---

# Hermes Config Sync

Backing up the shareable subset of `~/.hermes` to a git repo, and restoring the user's config from that repo to a fresh install. Trigger on: "sync/back up my hermes config", "restore config from github", "push my config up".

## The setup (this user's convention)

- A repo mirrors **only the shareable subset** of `~/.hermes`: `SOUL.md`, `memories/MEMORY.md`, `skills/`, and top-level `*.py` helper scripts (e.g. the Telegram→Obsidian bot). Durable clone lives at `~/hermes-mac-local`, remote `github.com/<user>/<name>`, branch `main`.
- A versioned `sync.sh` in the repo drives the one-way backup. Run it with `~/hermes-mac-local/sync.sh`; schedule with cron if the user wants automation.
- Drive git with `gh` CLI (typically already authed to the account that owns the repo — `gh auth status` to confirm). Clone to a **durable path, never /tmp** (pruned after 72h).

## sync.sh — the proven shape

```bash
cd "$REPO"
git pull --rebase --autostash origin main        # avoid conflicts before push
cp "$SRC/SOUL.md" "$REPO/SOUL.md"
mkdir -p "$REPO/memories" && cp "$SRC/memories/MEMORY.md" "$REPO/memories/"
rsync -a "$SRC/skills/" "$REPO/skills/"          # copy add/update, NEVER --delete
for f in "$SRC"/*.py; do [ -e "$f" ] && cp "$f" "$REPO/"; done
git add -A && git diff --cached --quiet || (git commit -m "config sync: $(date '+%F %T')" && git push origin main)
```

Principles baked in:
- **Non-destructive**: use `cp`/`rsync` without `--delete`, and avoid force-push. A backup should add/update, never prune — a bad sync must not erase the repo.
- **Pull before push** (`--rebase --autostash`) so a concurrent change on GitHub doesn't reject the push.
- **Secrets stay out**: `.env`, `auth.json`, `config.yaml`, `shared/nous_auth.json`, `*.lock` are gitignored and never committed. Verify a candidate file has no embedded tokens (bot code should read tokens from env, not literals) before copying.

## Restore (pull old config → fresh install)

1. Clone to a durable path and inspect the tree first — the gitignore tells you what was never backed up.
2. `config.yaml` is usually **gitignored**, so a restore has nothing to put back for it — say so plainly instead of implying you overwrote it. Same for `.env`/`auth.json` (and you must not restore those from a repo anyway).
3. **Merge `memories/MEMORY.md`, do NOT replace**: the old backup usually has the user's personal/identity entries; the fresh install has environment notes or newer entries. Keep both, joined by `§`, and verify the section count afterward. A fresh install frequently lost the personal memory — that is the highest-value thing being restored.
4. **Diff skills before copying** — compare `SKILL.md` paths: `comm -23 <(find "$REPO/skills" -name SKILL.md | sort) <(find "$SRC/skills" -name SKILL.md | sed 's|.*/skills/|skills/|' | sort)`. Copy only what the local install is missing. Never clobber a newer local skill the repo lacks (e.g. `hermes-agent`) — treat local-newer as authoritative.
5. `SOUL.md` is frequently the stock system prompt — check it isn't a no-op diff before copying.
6. Re-verify with the real remote: `git log origin/main -1`, `git ls-tree -r --name-only origin/main | grep <expected>`. `git show --stat HEAD` output is truncated by `tail` — don't conclude from a partial listing.

## Pitfalls

- **`.gitignore` dir patterns match at ANY depth.** `hermes-agent/` in the gitignore — intended to exclude a top-level install dir — silently also excludes `skills/autonomous-ai-agents/hermes-agent/SKILL.md`, dropping a skill from the backup. Anchor it to the repo root with a leading slash (`/hermes-agent/`) when a nested dir shares the name, and confirm with `git check-ignore -v <path>` before trusting a path is tracked.
- **A successful push ≠ the file is on the remote.** `git push` returning clean can be a no-op if a gitignore silently excluded the file from `git add -A`. Always verify the specific path on `origin/main`.
- `write_file` refuses to overwrite a file the session only `cat`'d (not `read_file`'d) — read it via `read_file` first when restoring MEMORY.md.
- `find ... -maxdepth N -name SKILL.md` under-reports nested skill trees; list paths at the correct depth or the diff will look empty/wildly off.
- **`~/.hermes/config.yaml` blocks direct file edits but NOT `hermes config set`.** `patch` and `write_file` both refuse it ('Refusing to write to Hermes config file... security-sensitive configuration'). The sanctioned path — `hermes config set <dotpath> <value>`, e.g. `hermes config set display.show_reasoning false` — works, and verify after with `hermes config get <dotpath>`. If `hermes config set` also refuses, hand the user the exact line + path (`config.yaml:NN`) and have them edit it themselves. In-session edits never hot-reload: `hermes gateway restart` is required, and multiplex restarts the whole supervised process, so every profile drops together — confirm with `hermes gateway status` first and time it for a quiet window.
- **`hermes config set` warns "unrecognized config key" for keys the gateway reads fine — do not treat the warning as the key being dead.** The CLI validates against `DEFAULT_CONFIG`, which the gateway runtime does NOT use (`gateway/` reads YAML raw via its own loaders, e.g. `gateway/display_config.py`). `display.tool_progress` is absent from `DEFAULT_CONFIG` (only `tool_progress_command`/`tool_progress_grouping` are), yet the gateway resolves it per platform and honors it. On such a warning, grep the actual runtime resolver rather than trusting either the CLI notice or `hermes doctor`, then verify empirically: load the real YAML and call the resolver against the real config (e.g. `resolve_tool_progress(cfg, 'telegram')`) before concluding the key does nothing.
- **Global `display.*` keys apply to BOTH the CLI and messaging — they are not messaging-only.** A global `display.tool_progress: new` silences/quietens your own CLI too. Messaging-only overrides use `display.platforms.<platform>.<key>`. Platform defaults and tier presets (HIGH/MEDIUM/LOW/MINIMAL) live in `_PLATFORM_DEFAULTS`/`_TIER_*` in `gateway/display_config.py` — read them to pick a sane value, since some platforms default quieter than you'd guess (`telegram` and `slack` default `tool_progress: off`, so `new` is noisier than both).
- **`~/.hermes/AGENTS.md` loads ONLY if the gateway's cwd chain includes `~/.hermes`.** Unlike `SOUL.md` (always read from `HERMES_HOME`), `AGENTS.md` discovers from the session's cwd chain (`agent/prompt_builder.py::_agents_md_directory_chain`), which is cwd-only outside a git repo. This user's launchd plist sets `WorkingDirectory` to `~/.hermes`, so it resolves — verify with `discover_context_files(Path('~/.hermes'))` before assuming it loads. Under multiplex the other profile homes each have their own single-element cwd chain, so AGENTS.md there is default-profile-only; copy or symlink per profile if a satellite needs it.
- **The current session does not see config changes until restart.** After the user edits `config.yaml`, probe the new value with a cheap test (add+remove a memory entry and read the `usage` field) before reporting success — the tool may still report the pre-restart limit.
- **Remote/Hermes-hosted UI behind a proxy (Coolify, docker port) shows as a login wall, not a Hermes surface.** When the user shares a Hermes URL that redirects to a Coolify/panel login, don't assume it's the Hermes UI; it's likely the deployment host. This session type (Telegram headless) also cannot prompt for credentials — `browser_vault_save_login` returns `prompt_unavailable`. Tell the user to save the login themselves via Desktop → Settings → Passwords & Logins or `hermes vault add`, then continue.
