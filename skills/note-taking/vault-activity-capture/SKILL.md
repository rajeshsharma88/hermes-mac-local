---
name: vault-activity-capture
description: Scheduled PC-activity snapshots into an Obsidian vault.
version: 1.0.0
---

# Vault Activity Capture (Daily PC Context)

Build/maintain scheduled data-capture jobs that summarize a day's computer activity into a note inside the user's Obsidian vault. This is the pattern behind the nightly "Daily PC context snapshot" cron job.

## Existing setup (Rajesh's Mac)

- **Job:** Hermes cron `9f94f60e6e97` ("Daily PC context snapshot"), `no_agent`, `every day at 8pm`, `deliver=local`. Keep it `no_agent` — collection needs no LLM.
- **Script:** `~/.hermes/scripts/daily_context.py`. It scans Obsidian notes touched, files changed under work dirs, and git commits since midnight, then writes `08 - Daily Context/YYYY-MM-DD.md`.
- **Vault:** `/Users/rajeshcsharma/Documents/Obisidian/Rajesh Sharma OS`. Note the type in the path (`Obisidian`, not `Obsidian`) — copy it exactly; there is a second vault at `Time-Garden-Vault` and a separate business vault under `~/Project/Obsidian`, do not conflate them.

## Procedure for modifying or re-scheduling

1. Edit the script at `~/.hermes/scripts/daily_context.py`, then test it directly before re-scheduling: `python3 ~/.hermes/scripts/daily_context.py` and read the generated note for correct format.
2. Test the parsing against YESTERDAY's real history (`git log --since="2 days ago" --name-only`), not today's — at the start of a day all three counts are legitimately 0 and prove nothing about the logic.
3. Re-schedule with `cronjob_manage`: keep `no_agent=true`, `script=<basename>.py`, `deliver='local'` (this TUI session has no live delivery channel — never promise a cron output will message the user here). `deliver='local'` saves output only; the note landing in the vault IS the deliverable.
4. `schedule` accepts natural language ("every day at 8pm") — no need to compute cron syntax. User is IST (UTC+05:30); interpret times in local tz.
5. Fire it once (`cronjob_manage action='run'`) to prove the cron path works end-to-end; results re-enter the conversation async.

## Registering structural changes (user convention, ALWAYS)

The vault enforces a Working Agreement: any structural/design decision must be written back to the vault's `CLAUDE.md` (folder-structure section) **and** `log.md` (newest entry at top) in the same session. A new folder or schema change without both updates is an incomplete job. Follow the vault's `categories:`/`subjects:`/`type:`/`status:`/`created:` YAML property schema when writing notes.

## Pitfalls

- **obsidian-git auto-commit noise:** this vault has `obsidian-git` (`autoBackupAfterFileChange`) committing generic "Auto-sync" messages every ~minute. Commit messages carry zero signal. To find which notes changed in a window, run `git log --since=midnight --name-only` and dedupe the filenames — never read the messages.
- **Folder numbering collision:** always `ls -d */` the vault root before picking a numbered folder. `07 - Daily Context` collided with the existing `07 - PARA/`; used `08` instead. Choose the next free number.
- **Scope the scan tightly:** when walking work dirs, prune `.git`, `node_modules`, `venv`, `__pycache__` and the vault's `.obsidian`; cap per-dir listing (e.g. 40) or the note explodes.
- **Discover nested repos, don't assume roots:** repos live one+ levels deep (`~/Project/aarogyaindia.hospital`, `~/Shopify_pro/DawnTest`, `~/TST Catalogue Website/TST-TECHNOLOGIES-CATALOGUE`) — hardcoding top-level paths misses them. Walk for `.git` dirs.
- **Per-invocation no-op guard:** empty stdout on hard failure so the cron system treats a broken run as "nothing to report" rather than delivering junk; print a one-line confirmation with counts on success.
- **Zero results are not a bug:** at day start all counts are 0. Verify logic against a known-active past window, not the current (empty) day.

## Diagnosing a mystery string in a Hermes surface

Before attributing any UI text to an app, read the actual rendered content, not grepped source. If the string exists in the server's rendered DOM it is real app content; if the DOM is clean but the client shows foreign text, it is browser-injected (e.g. Chrome auto-translate — detect the browser's own translation banner on the page). A Polish/other-language label in a dashboard whose DOM is entirely English is client-side translation, not a Hermes feature. The Hermes dashboard runs on `localhost:9119` and can be inspected directly with `browser_exec`.
