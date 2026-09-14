---
name: telegram-vault-bridge
description: Telegram bot writing/reading markdown into Obsidian vault.
version: 1.0.0
author: Hermes Agent
tags: [Telegram, Obsidian, Vault, Bot, Automation]
---

# Telegram → Obsidian Vault Bridge

Use this skill when building or maintaining a Telegram bot that captures messages into an Obsidian vault as markdown files — tasks, inbox captures, notes, journal entries, etc. — and/or reads vault content back to the user.

## Architecture

Single standalone Python process, long-polling (no public webhook / SSL needed). Reads the bot token and allowed user IDs from `~/.hermes/.env`. Vault path is a concrete absolute path; resolve it before passing to file tools.

## Config

Put bot credentials in `~/.hermes/.env`:

```
TELEGRAM_BOT_TOKEN=<bot token from @BotFather>
TELEGRAM_ALLOWED_USERS=<Telegram user ID, comma-separated if multiple>
```

Use `python-telegram-bot` (install with `pip3 install python-telegram-bot`). Long-polling via `Application.builder().token(...).build()` and `app.run_polling()`.

## Vault path

Resolve the vault path before any file operation. The documented convention is `OBSIDIAN_VAULT_PATH` from env; fall back to `~/Documents/Obsidian Vault`. Use `terminal` only to resolve an unknown path; once known, switch to file tools (`read_file`, `write_file`, `patch`, `search_files`).

The actual path may contain a typo in the directory name (e.g. `Obisidian` not `Obsidian`) — always verify with `ls`/terminal before writing.

## Command parsing

Each `@command` gets its own handler with a regex filter so they don't step on each other. Register them individually:

```python
app.add_handler(MessageHandler(filters.Regex(r"^@task"), handle_task))
app.add_handler(MessageHandler(filters.Regex(r"^@inbox"), handle_inbox))
...
```

Do NOT register multiple handlers with the shared `filters.TEXT & ~filters.COMMAND` — the dispatcher stops at the first matching handler, so only the first one ever fires for any text message.

## `.hermes/.env` is a protected file

File tools (`read_file`, `patch`, `write_file`) are blocked on `~/.hermes/.env`. To read or write it, use `terminal` with `sed`, `python3 -c`, or `printf`. Never attempt a direct file-tool write — it will be refused with a protected-file error.

## Pitfalls

### TaskNotes files must match the vault's actual YAML convention

When the target vault uses the TaskNotes community plugin, the `@task` handler's `write_task_file` output must match **both** TaskNotes' own expected frontmatter **and** any vault-specific conventions layered on top — a bot authored for a generic vault will silently produce files that don't show up where the user expects.

Before shipping `@task`, inspect a real task note already in `06 - Tasks/` (or the vault's `06 - Tasks/CLAUDE.md`) and confirm each field:

- **`categories: [[Tasks]]`** — TaskNotes 4.x does not inject arbitrary custom frontmatter automatically. If the vault's category hub (`02 - Categories/Tasks.md`) relies on a `categories:` wikilink query to surface task notes, every `@task`-created file must carry it or the note is invisible there. Add it in the bot's template, not as a post-step.
- **`projects:` / `contexts:`** — these are usually **bulleted lists of wikilinks** (`- "[[Project]]"`), not comma-joined strings. A bot that writes `projects: [[A]], [[B]]` produces YAMLTaskNotes can't parse as a list.
- **No `title:` frontmatter** — TaskNotes identifies tasks by folder + `#task` tag + note title, not by a `title:` YAML key. Writing `title:` is harmless to TaskNotes but clutters the file; omit it unless the vault explicitly uses it.
- **No stray markdown comment blocks** — wrapper comment lines like `# HAPPENED [[…]]` inside the body are not part of any TaskNotes schema and will show up as literal text in the note.
- **Filename must match `taskFilenameFormat` setting** — TaskNotes' `taskFilenameFormat` controls how task files are named (commonly `title` or a zettel ID). If the bot writes files with a different naming scheme than what the plugin expects, the plugin won't see them. Verify the setting via `obsidian eval` or check existing task filenames in `06 - Tasks/`.
- **Common schema mismatches to catch** — a bot that writes `title:` in frontmatter, uses comma-joined `projects: [[A]], [[B]]` instead of bulleted lists, adds wrapper comment blocks like `# HAPPENED [[…]]` in the body, or omits `categories: [[Tasks]]` will all produce files that either don't show in TaskNotes views or don't appear in the vault's category hub. The fix is to write `write_task_file`'s body from a real vault task note as a template.

The fix is to write the bot's `write_task_file` body from a real vault task note as a template, not from a generic example.

### Duplicate bot processes cause 409 conflicts

Running the bot more than once — or failing to kill a prior process before relaunching — produces Telegram 409 Conflict errors (`terminated by other getUpdates request`). The bot log shows `ok: False` and messages get silently dropped. Symptoms: the bot appears to be running (polling logs show HTTP 200s) but messages sent to it get no reply.

**Diagnosis:** `pgrep -fl telegram_task_bot` — if it returns more than one PID, you have duplicates. Also check the log for 409s.

**Fix:** `pkill -f telegram_task_bot`, wait 2 seconds, verify `pgrep -fl telegram_task_bot` shows ≤1 process, then relaunch a single process.

When replacing the bot script, always kill before relaunching — never rely on the old process dying on its own.

### Bot may be running but not processing — verify with a real message, not log inspection

After relaunching, don't assume the bot works because the log shows polling started.

**Diagnosis:** `pgrep -fl telegram_task_bot` — if it shows no process or more than one, the bot isn't correctly live. If exactly one process is running and the log shows `Bot starting — long polling` + HTTP 200s for `getUpdates`, the process is healthy but messages may still not be delivered.

**Fix sequence:**
1. Kill all duplicates: `pkill -f telegram_task_bot`, wait, verify `pgrep -fl telegram_task_bot` shows ≤1.
2. Relaunch a single process.
3. Wait for the log to show `Bot starting — long polling`.
4. Send a test message from Telegram (`@help`) and confirm you get a reply.
5. If no reply and the process is healthy, check `TELEGRAM_ALLOWED_USERS` contains your actual user ID (not the bot's own ID) — get it from `@userinfobot`.

A bot that is running but not processing is indistinguishable from a bot that isn't running unless you send a test message. Log inspection alone is not sufficient.

### Duplicate processes fight the token

Starting the bot more than once (or not cleanly killing a prior process) produces 409 Conflict errors: `terminated by other getUpdates request`. The bot log shows `ok: False` and rejected messages. Kill all duplicates with `pkill -f telegram_task_bot` (or the script name), verify no stragglers with `pgrep -fl`, then launch a single process. Confirm with a log tail showing `Bot starting — long polling` and no 409s.

### Allowed user ID is not the bot's own ID

The bot's own Telegram ID (from `@BotFather` / token ownership) often gets mistaken for the human user's ID. The correct user ID comes from a bot like `@userinfobot` — message it and it replies with your numeric ID. Set `TELEGRAM_ALLOWED_USERS` to that number; the bot will reject messages from anyone else.

### Natural-language due dates in task commands

Task commands like `@task Finish CRM due:tomorrow` need a date parser that handles both explicit formats (`due:Sep 20`, `due:2026-09-20`, `due:17`) and natural language (`due:tomorrow`, `due:Friday`, `due:next Monday`, `due:by Friday`, `due:in 3 days`, `due:in 2 weeks`). A plain weekday like "Friday" when today is Saturday should resolve to the *coming* Friday, not the one that just passed — due dates are forward-looking.

If the user writes a date phrase without the `due:` prefix (e.g. `@remind Call Vicky tomorrow`), scan the raw text for the phrase and resolve it. If no `due:` and no natural-language phrase is found, do not guess — reply asking for a clearer date.

### Don't send a "thinking…" message and edit it to empty

Sending a placeholder "thinking…" message and then editing it to blank text triggers a silent `400 Bad Request` from Telegram (it rejects empty-body edits). Either skip the thinking indicator entirely, or delete the message after the real reply arrives — don't edit to empty.

### LLM provider quirks — extract the right field

When routing general chat to an LLM API, inspect the actual response shape. Some models return `choices[0].message.content` as `null` and put the answer in a separate field (e.g. `reasoning`). Read the response, don't assume `content` is always populated. Test the endpoint with `curl` directly before wiring it into the bot.

### LLM base URL must resolve on this machine

Before committing to an LLM base URL, verify it resolves with `nslookup` or a direct `curl`. A URL that returns `NXDOMAIN` (e.g. a subdomain that doesn't resolve) is a DNS problem, not a credentials problem — switch to a resolvable host. For OpenRouter, the working base URL on some machines is `https://openrouter.ai/api/v1`, not `https://api.openrouter.ai/v1`.

## Command catalog (suggested)

Common commands for a vault bridge bot:

- `@task <title> [due:DATE] [priority:LEVEL] [status:STATE] [project:[[Name]]]` — write a TaskNotes file into `06 - Tasks/` with YAML that matches the vault's convention (see the TaskNotes schema pitfall above); include `categories: [[Tasks]]` if the vault's category hub requires it
- `@remind <text>` — like `@task` but with stronger natural-language date extraction
- `@inbox <text>` — raw capture into `00 - Inbox/`
- `@note <text>` — permanent note into `01 - Notes/`
- `@journal <text>` — append to today's Daily note under `Notes / Journal`
- `@done <keyword>` — mark a matching open task as done
- `@list` — show today's open tasks
- `@search <keyword>` — search notes/tasks across the vault
- `@today` — snapshot of upcoming tasks + recent journal
- `@weather [city]` — current weather (e.g. wttr.in)
- `@news [topic]` — latest headlines on a topic (e.g. HN RSS)
- `@help` — list all commands

General chat (anything without an `@` command) routes to the LLM.

## Restart pattern

After changing the bot script: kill the old process, launch the new one, wait for the log to show polling started, then test.

```bash
pkill -f telegram_task_bot
sleep 2
cd /path/to/bot && python3 -u telegram_task_bot.py > telegram_bot.log 2>&1 &
```

Verify: `pgrep -fl telegram_task_bot` shows one process; `tail telegram_bot.log` shows no 409s.
