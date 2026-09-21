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
