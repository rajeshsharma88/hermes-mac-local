#!/usr/bin/env bash
# One-way backup sync: push shareable config from ~/.hermes up to this GitHub repo.
# Safe by design: adds/updates changed files, NEVER deletes anything from the repo,
# and only touches the shareable assets below — secrets (.env, auth.json, config.yaml)
# and runtime state (logs, caches, *.db) are excluded by .gitignore.
set -euo pipefail

REPO="$HOME/hermes-mac-local"
SRC="$HOME/.hermes"
cd "$REPO"

echo "== pulling latest to avoid conflicts =="
git pull --rebase --autostash origin main 2>&1 | tail -3 || git pull origin main 2>&1 | tail -3

# --- shareable assets (mirrors repo .gitignore intent) ---
cp "$SRC/SOUL.md" "$REPO/SOUL.md" 2>/dev/null || true
mkdir -p "$REPO/memories"
cp "$SRC/memories/MEMORY.md" "$REPO/memories/MEMORY.md" 2>/dev/null || true
rsync -a "$SRC/skills/" "$REPO/skills/" 2>/dev/null || cp -R "$SRC/skills/." "$REPO/skills/" 2>/dev/null || true
# Telegram/Obsidian bot + helper scripts at the top level of ~/.hermes
for f in "$SRC"/*.py; do [ -e "$f" ] && cp "$f" "$REPO/"; done

echo "== staging =="
git add -A
if git diff --cached --quiet; then
  echo "Nothing to sync — working tree already matches GitHub."
  exit 0
fi

git commit -m "config sync: $(date '+%Y-%m-%d %H:%M:%S')" >/dev/null
echo "== pushing =="
git push origin main
echo "Pushed to origin/main ✓"