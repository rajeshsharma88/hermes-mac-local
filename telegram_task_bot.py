#!/usr/bin/env python3
"""Telegram bot — @task/@remind/@inbox/@note/@journal/@done/@list/@search/@help
→ Obsidian vault files (Rajesh Sharma OS). Long polling, no webhook.

Writes TaskNotes-formatted task files into 06 - Tasks/ using the vault's
own frontmatter convention (status/priority/due/projects/contexts/tags/
categories). General chat not wired (no LLM_API_KEY in .env).
"""
from __future__ import annotations
import os, re, sys, logging
from datetime import datetime, date, timedelta
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

ENV_PATH = os.path.expanduser("~/.hermes/.env")

def _load_env():
    env = {}
    try:
        for raw in open(ENV_PATH, encoding="utf-8"):
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    except OSError as e:
        logger.exception("read %s", ENV_PATH)
    return env

_env = _load_env()
BOT_TOKEN = _env.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_USERS = _env.get("TELEGRAM_ALLOWED_USERS", "").strip()
ALLOWED_IDS = set(t.strip() for t in ALLOWED_USERS.split(",") if t.strip()) if ALLOWED_USERS else set()

if not BOT_TOKEN:
    logging.error("No TELEGRAM_BOT_TOKEN in %s", ENV_PATH)
    sys.exit(1)

VAULT_ROOT = Path("/Users/rajeshcsharma/Documents/Obisidian/Rajesh Sharma OS")
TASKS_FOLDER = VAULT_ROOT / "06 - Tasks"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("telegram_task_bot")

# ---------- date parsing ----------
_WEEKDAYS = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
             "friday": 4, "saturday": 5, "sunday": 6}
_DATE_FORMATS = ["%Y-%m-%d", "%b %d", "%b %d, %Y", "%d %b %Y"]

def _next_weekday(twd, after=True):
    today = date.today()
    da = (twd - today.weekday()) % 7
    if da == 0 and after:
        da = 7
    return today + timedelta(days=da)

def _parse_date(s):
    """Explicit date formats + common phrases. Returns None on failure.
    Month+day without a year (e.g. 'Sep 20', '17') resolves to the current
    year; if that date has already passed this year, uses next year (forward-
    looking for due dates). A bare 1-2 digit day number is treated as a day of
    the current month."""
    s = s.strip().lower()
    if not s:
        return None
    if s.isdigit():
        d = int(s)
        now = datetime.now()
        try:
            candidate = date(now.year, now.month, d)
        except ValueError:
            return None
        if candidate < date.today():
            try:
                candidate = date(now.year + 1, now.month, d)
            except ValueError:
                return None
        return candidate
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(s, fmt).date()
        except ValueError:
            continue
        if parsed.year == 1900:
            # month/day without a year — anchor to now's year, roll forward if passed
            now = datetime.now()
            try:
                parsed = parsed.replace(year=now.year)
            except ValueError:
                return None
            if parsed < date.today():
                try:
                    parsed = parsed.replace(year=now.year + 1)
                except ValueError:
                    return None
        return parsed
    if s in _WEEKDAYS:
        return _next_weekday(_WEEKDAYS[s], after=False)
    if s.startswith("next ") and s[5:] in _WEEKDAYS:
        return _next_weekday(_WEEKDAYS[s[5:]], after=True)
    if s.startswith("by ") and s[3:] in _WEEKDAYS:
        return _next_weekday(_WEEKDAYS[s[3:]], after=False)
    m = re.match(r"^in\s+(\d+)\s+days?$", s)
    if m:
        return date.today() + timedelta(days=int(m.group(1)))
    m = re.match(r"^in\s+(\d+)\s+weeks?$", s)
    if m:
        return date.today() + timedelta(weeks=int(m.group(1)))
    if s in ("today", "tonight"):
        return date.today()
    if s == "tomorrow":
        return date.today() + timedelta(days=1)
    if s == "yesterday":
        return date.today() - timedelta(days=1)
    return None

def _first_weekday_in_text(text, prefer_after=True):
    low = text.lower()
    for nm, num in _WEEKDAYS.items():
        if re.search(rf"\b{nm}\b", low):
            return _next_weekday(num, prefer_after)
    return None

_RAW_DUE_PHRASES = [
    "by tomorrow", "due tomorrow", "by next week", "next week",
    "in a week", "in 1 week", "in 2 weeks", "in 3 weeks",
]

def _scan_raw_due(text):
    """Find a due date in free text without an explicit due: prefix.
    Checks raw phrases first, then a lone weekday mention."""
    low = text.lower().strip()
    for phrase in _RAW_DUE_PHRASES:
        if low == phrase or low.endswith(" " + phrase):
            if phrase.startswith("in "):
                m = re.match(r"^in\s+(\d+)\s+weeks?$", phrase)
                if m:
                    return date.today() + timedelta(weeks=int(m.group(1)))
                return date.today() + timedelta(weeks=1)
            if phrase in ("by tomorrow", "due tomorrow"):
                return date.today() + timedelta(days=1)
            if phrase in ("by next week", "next week"):
                return date.today() + timedelta(days=7)
    # lone weekday (forward-looking)
    return _first_weekday_in_text(text, prefer_after=True)

# ---------- task parsing ----------
_STATUS_KEYWORDS = {
    "done": "done", "completed": "done",
    "open": "open",
    "in-progress": "in-progress", "inprogress": "in-progress", "ip": "in-progress",
    "high": "high", "normal": "normal", "low": "low",
}

def _tokenize(text):
    """Yield tokens from `text`. Three token shapes, all consuming their chars:
    - [[...]] blocks (optionally followed by :role, folded into ONE token)
    - key:value pairs where key is [a-z]+ and ':' appears before the next space
      or '[' (e.g. "due:Sep 20", "priority:high") — value absorbs one trailing
      bare word if it completes a date phrase
    - plain words otherwise (no ':' and no '[' in the span)

    Each iteration MUST advance `i` past the yielded token; otherwise the loop
    is infinite."""
    i, n = 0, len(text)
    while i < n:
        # skip whitespace between tokens
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break

        # ---- [[...]] block (with optional :role) ----
        if text[i] == "[":
            end = text.find("]]", i)
            if end == -1:
                yield text[i:]
                break
            j = end + 2                       # end of "]]"
            # fold a following :role into the same token
            if j < n and text[j] == ":":
                j += 1
                while j < n and not text[j].isspace():
                    j += 1
            yield text[i:j]
            i = j
            continue

        # ---- key:value pair: a run of [a-z] letters, then ':', then value ----
        if text[i].isalpha():
            key_end = i
            while key_end < n and text[key_end].isalpha():
                key_end += 1
            if key_end < n and text[key_end] == ":":
                # this is a key:value pair — absorb value, optionally one more
                # continuation word (e.g. "20" in "due:Sep 20")
                val_start = key_end + 1
                j = val_start
                # first value word (no spaces, no '[')
                while j < n and not text[j].isspace() and text[j] != "[":
                    j += 1
                # optionally absorb a second word if it completes a date phrase
                sp = j
                while sp < n and text[sp].isspace():
                    sp += 1
                if sp < n and text[sp] != "[" and (text[sp].isalpha() or text[sp].isdigit()):
                    # peek: is the next bare word itself a new key: ?
                    k = sp
                    while k < n and text[k].isalpha():
                        k += 1
                    if k < n and text[k] == ":":
                        # it's a new key:value — stop after the first value word
                        pass
                    else:
                        # absorb the second word (e.g. "20" in "Sep 20",
                        # "Monday" in "next Monday")
                        second = sp
                        while second < n and not text[second].isspace() and text[second] != "[":
                            second += 1
                        if second > sp:
                            j = second
                yield text[i:j]
                i = j
                continue
            continue

        # ---- plain word (no ':' and no '[' in the span) ----
        start = i
        while i < n and not text[i].isspace() and text[i] != "[" and text[i] != ":":
            i += 1
        if i > start:
            yield text[start:i]
            continue
        # nothing consumed (i landed on ':' or '[' with no preceding word) —
        # advance past the delimiter so the loop makes progress
        i += 1

def parse_task_text(text):
    """Parse `@task <title> [due:DATE] [priority:LEVEL] [status:STATE]
    [[Project]] [[Context]]:context ...`

    Single-pass scan: everything before the first structured token (a [[...]]
    block or a key:value pair) is the title; structured tokens after it set
    due/priority/status/projects/contexts. Plain words in the structured part
    are ignored."""
    n = len(text)
    i = 0
    # skip leading whitespace
    while i < n and text[i].isspace():
        i += 1
    if i >= n:
        return {"title": "", "due": None, "priority": "normal",
                "projects": [], "contexts": [], "status": "open"}

    def _is_letter(c):
        return c.isalpha()

    def _is_word_char(c):
        return c.isalnum() or c in "-."

    def _absorb_bare_word():
        """Absorb one bare word from text[i] (no spaces, no '[').
        Return the word."""
        nonlocal i
        start = i
        while i < n and _is_word_char(text[i]) and text[i] != "[":
            i += 1
        return text[start:i]

    def _absorb_link_with_role():
        """Absorb [[...]] optionally followed by :role from text[i].
        Return (label, kind) where kind is the role after ':' or ''."""
        nonlocal i
        # text[i] == '['
        start = i
        end = text.find("]]", i)
        i = end + 2 if end != -1 else n
        label = text[start + 2:end] if end != -1 else text[start + 2:i]
        kind = ""
        if i < n and text[i] == ":":
            i += 1
            kind_start = i
            while i < n and not text[i].isspace():
                i += 1
            kind = text[kind_start:i]
        return label, kind

    def _parse_key_value():
        """Absorb key:value from text[i] where key is [a-z]+.
        Value absorbs one bare word; if a second bare word completes a date
        phrase and isn't itself a new key: or [[, absorb it too.
        Return (key, value_string)."""
        nonlocal i
        key_start = i
        while i < n and _is_letter(text[i]):
            i += 1
        key = text[key_start:i]
        # skip ':'
        i += 1  # text[i] == ':' guaranteed by caller
        val_start = i
        _absorb_bare_word()
        val = text[val_start:i]
        # maybe a second word?
        j = i
        while j < n and text[j].isspace():
            j += 1
        if j < n and text[j] != "[" and (text[j].isalpha() or text[j].isdigit()):
            # peek: is it a new key: ?
            k = j
            while k < n and _is_letter(text[k]):
                k += 1
            if k >= n or text[k] != ":":
                # not a new key: — absorb it
                i = j
                _absorb_bare_word()
                val = text[val_start:i]
        return key, val

    # ---------- collect title ----------
    title_parts = []
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        ch = text[i]
        if ch == "[":
            break  # [[...]] — structured; title ends
        if _is_letter(ch):
            k = i
            while k < n and _is_letter(text[k]):
                k += 1
            if k < n and text[k] == ":":
                break  # key:value — structured; title ends
            # plain word — part of the title
            title_parts.append(_absorb_bare_word())
            continue
        # any other char — stop title collection
        break

    if not title_parts:
        # no structured token was found — the whole string is the title
        return {"title": text.strip(), "due": None, "priority": "normal",
                "projects": [], "contexts": [], "status": "open"}

    title = " ".join(title_parts)

    # ---------- parse structured tokens ----------
    due = None
    priority = "normal"
    projects = []
    contexts = []
    status = "open"

    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        ch = text[i]
        if ch == "[":
            label, kind = _absorb_link_with_role()
            if kind == "context":
                contexts.append(label)
            else:
                projects.append(label)
            continue
        if _is_letter(ch):
            k = i
            while k < n and _is_letter(text[k]):
                k += 1
            if k < n and text[k] == ":":
                key, val = _parse_key_value()
                if key == "due":
                    due = _parse_date(val) or _first_weekday_in_text(val, True)
                elif key == "priority":
                    priority = _STATUS_KEYWORDS.get(val, "normal")
                elif key == "status":
                    status = _STATUS_KEYWORDS.get(val, "open")
                continue
            # plain word in structured region — skip it
            _absorb_bare_word()
            continue
        # unexpected char — skip
        i += 1

    return {"title": title, "due": due, "priority": priority,
            "projects": projects, "contexts": contexts, "status": status}

# ---------- file helpers ----------
def _filename_from_title(title):
    """TaskNotes taskFilenameFormat: title — keep the title as the filename,
    lightly sanitised for the filesystem."""
    s = title.strip()
    s = s.replace("\0", "")
    # drop path separators so a title can't escape the folder
    s = s.replace("/", "-").replace("\\", "-")
    s = s.rstrip(" .")
    return s[:120] or "untitled"

def _ensure_folder(p):
    p.mkdir(parents=True, exist_ok=True)

def write_task_file(task):
    """Write a TaskNotes .md file into 06 - Tasks/ using the vault's
    frontmatter convention. Returns the Path."""
    _ensure_folder(TASKS_FOLDER)
    dest = TASKS_FOLDER / f"{_filename_from_title(task['title'])}.md"
    links = "\n".join(f'  - "[[{p}]]"' for p in task["projects"])
    ctxs = "\n".join(f'  - "[[{c}]]"' for c in task["contexts"])
    due_str = task["due"].isoformat() if task["due"] else ""
    sched_str = due_str  # vault convention: scheduled mirrors due
    body = f"""---
status: {task['status']}
priority: {task['priority']}
due: {due_str}
scheduled: {sched_str}
projects:
{links}
contexts:
{ctxs}
tags:
  - task
categories:
  - "[[Tasks]]"
---

"""
    dest.write_text(body, encoding="utf-8")
    logger.info("wrote task %s -> %s", task["title"], dest.name)
    return dest

def md_title(path):
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem

def today_daily_path():
    d = date.today()
    folder = VAULT_ROOT / "05 - Periodic Notes" / "Daily"
    pat = re.compile(rf"^{d.isoformat}\(.*\)\.md$", re.I)
    if folder.exists():
        for c in folder.iterdir():
            if c.is_file() and pat.match(c.name):
                return c
    _ensure_folder(folder)
    day = d.strftime("%a")[:2]
    return folder / f"{d.isoformat()}({day}).md"

# ---------- command handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    await update.message.reply_text(_START_TEXT)

_START_TEXT = (
    "Rajesh Sharma OS vault bridge.\n\n"
    "Commands:\n"
    "@task <title> [due:DATE] [priority:high|normal|low] [status:open|in-progress|done] [[Project]] [[Ctx]]:context\n"
    "@remind <text> — like @task but scans natural-language dates (tomorrow, Friday, in 3 days)\n"
    "@inbox <text> — raw capture into 00 - Inbox/\n"
    "@note <text> — permanent note into 01 - Notes/ under [[Permanent Notes]]\n"
    "@journal <text> — append to today's Daily note\n"
    "@done <keyword> — mark a matching open task done\n"
    "@list — today's open tasks\n"
    "@search <keyword> — search notes/tasks across the vault\n"
    "@help — this message"
)

async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    text = update.message.text.strip()
    if not text.startswith("@task"):
        return
    payload = text[len("@task"):].strip()
    if not payload:
        await update.message.reply_text(
            "`@task` needs a description.\n"
            "Example: `@task Build Lovable CRM due:Sep 20 priority:high [[2026-Q3]]`")
        return
    task = parse_task_text(payload)
    if not task["title"]:
        await update.message.reply_text("I couldn't read a title from that. Try:\n`@task <title> due:tomorrow`")
        return
    if "due" in payload.lower() and not task["due"]:
        await update.message.reply_text(
            f"Couldn't parse the due date in `_{payload}_`. "
            "Try `due:tomorrow`, `due:Friday`, `due:Sep 20`, or `due:17`.")
        return
    try:
        dest = write_task_file(task)
    except Exception as exc:
        logger.exception("Failed to write task file")
        await update.message.reply_text(f"Sorry — couldn't save the task: {exc}")
        return
    parts = [f"✓ Task saved: *{task['title']}*"]
    det = []
    if task["due"]:
        det.append(f"due {task['due'].strftime('%b %d')}")
    if task["priority"] != "normal":
        det.append(f"priority {task['priority']}")
    if task["projects"]:
        det.append("project " + ", ".join(f"[[{p}]]" for p in task["projects"]))
    if task["contexts"]:
        det.append("context " + ", ".join(f"[[{c}]]" for c in task["contexts"]))
    if det:
        parts.append("(" + ", ".join(det) + ")")
    parts.append(f"→ `06 - Tasks/{dest.name}`")
    await update.message.reply_text("\n".join(parts), parse_mode="Markdown")

async def handle_remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    text = update.message.text.strip()
    if not text.startswith("@remind"):
        return
    payload = text[len("@remind"):].strip()
    if not payload:
        await update.message.reply_text(
            "`@remind` needs something to remind you about.\n"
            "Example: `@remind Call Vicky tomorrow priority:high`")
        return
    # @remind scans the raw text for a date phrase even without due: prefix
    task = parse_task_text(payload)
    if not task["due"]:
        scanned = _scan_raw_due(payload)
        if scanned:
            task["due"] = scanned
    if not task["title"]:
        await update.message.reply_text("I couldn't read a title from that.")
        return
    try:
        dest = write_task_file(task)
    except Exception as exc:
        logger.exception("Failed to write remind task")
        await update.message.reply_text(f"Sorry — couldn't save: {exc}")
        return
    parts = [f"✓ Reminder saved: *{task['title']}*"]
    if task["due"]:
        parts.append(f"due {task['due'].strftime('%b %d')}")
    if task["priority"] != "normal":
        parts.append(f"priority {task['priority']}")
    parts.append(f"→ `06 - Tasks/{dest.name}`")
    await update.message.reply_text("\n".join(parts), parse_mode="Markdown")

async def handle_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    raw = update.message.text.strip()
    if not raw.startswith("@inbox"):
        return
    text = raw[len("@inbox"):].strip()
    if not text:
        await update.message.reply_text(
            "`@inbox` needs something to capture.\nExample: `@inbox Idea for YouTube thumbnails`")
        return
    folder = VAULT_ROOT / "00 - Inbox"
    _ensure_folder(folder)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    fname = f"{ts.replace(' ', '_')}_capture.md"
    dest = folder / fname
    body = f"---\nsource: telegram\ntype: inbox-capture\ncreated: {ts}\n---\n\n{text}\n"
    dest.write_text(body, encoding="utf-8")
    await update.message.reply_text(
        f"✓ Saved to inbox → `00 - Inbox/{dest.name}`", parse_mode="Markdown")

async def handle_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    raw = update.message.text.strip()
    if not raw.startswith("@note"):
        return
    text = raw[len("@note"):].strip()
    if not text:
        await update.message.reply_text(
            "`@note` needs content.\nExample: `@note Obsidian is a markdown-based knowledge base`")
        return
    folder = VAULT_ROOT / "01 - Notes"
    _ensure_folder(folder)
    slug = re.sub(r'[^\w\s-]', '', text.split()[0].lower()) if text.split() else "note"
    slug = re.sub(r'[\s_]+', '-', slug).strip('-') or "note"
    dest = folder / f"{slug}.md"
    cn = date.today().isoformat()
    first_line = text.splitlines()[0] if text.splitlines() else slug.title()
    body = f"""---
categories: [[Permanent Notes]]
created: {cn}
---

# {first_line}

{text}
"""
    if dest.exists():
        await update.message.reply_text(
            f"Note exists — not overwriting `01 - Notes/{dest.name}`")
        return
    dest.write_text(body, encoding="utf-8")
    await update.message.reply_text(
        f"✓ Note created → `01 - Notes/{dest.name}`", parse_mode="Markdown")

async def handle_journal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    raw = update.message.text.strip()
    if not raw.startswith("@journal"):
        return
    text = raw[len("@journal"):].strip()
    if not text:
        await update.message.reply_text(
            "`@journal` needs an entry.\nExample: `@journal Meditated 20 min today`")
        return
    dest = today_daily_path()
    _ensure_folder(dest.parent)
    existing = dest.read_text(encoding="utf-8", errors="ignore") if dest.exists() else ""
    ts = datetime.now().strftime("%H:%M")
    entry = f"- {ts}: {text}\n"
    if "## Notes / Journal" not in existing:
        existing += f"\n## Notes / Journal\n{entry}"
    else:
        existing += entry
    dest.write_text(existing, encoding="utf-8")
    await update.message.reply_text(
        f"✓ Journal updated → `{dest.relative_to(VAULT_ROOT)}`", parse_mode="Markdown")

async def handle_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    raw = update.message.text.strip()
    if not raw.startswith("@done"):
        return
    kw = raw[len("@done"):].strip()
    if not kw:
        await update.message.reply_text(
            "`@done` needs a task keyword.\nExample: `@done Lovable CRM`")
        return
    hits = []
    for src in sorted(TASKS_FOLDER.glob("*.md")):
        try:
            txt = src.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"(?m)^status:\s*done\b", txt, re.I):
            continue
        title = md_title(src)
        if kw.lower() in title.lower():
            hits.append((src, title, txt))
    if not hits:
        await update.message.reply_text(
            f"No open task matching `_{kw}_` found. Run `@list` to see current tasks.")
        return
    if len(hits) > 1:
        names = "\n".join(f"  _{t}_" for _, t, _ in hits[:10])
        await update.message.reply_text(
            f"Multiple matches (showing first {min(len(hits), 10)}):\n{names}\n\n"
            "Please be more specific or run `@done <exact title>`.")
        return
    src, orig, txt = hits[0]
    if "status:" in txt:
        new = re.sub(r"(?m)^status:\s*.+$", "status: done", txt, count=1)
    else:
        new = f"---\nstatus: done\n---\n\n{txt}"
    src.write_text(new, encoding="utf-8")
    await update.message.reply_text(
        f"✓ Marked *{orig}* as done → `{src.name}`", parse_mode="Markdown")

async def handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    raw = update.message.text.strip()
    if not raw.startswith("@list"):
        return
    today = date.today().isoformat()
    rows = []
    for src in sorted(TASKS_FOLDER.glob("*.md")):
        try:
            txt = src.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"(?m)^status:\s*done\b", txt, re.I):
            continue
        m_title = re.search(r"(?m)^#\s+(.+)$", txt)
        title = m_title.group(1) if m_title else src.stem
        m_due = re.search(r"(?m)^due:\s*(.+)$", txt)
        due = m_due.group(1).strip() if m_due else ""
        m_pri = re.search(r"(?m)^priority:\s*(.+)$", txt)
        pri = m_pri.group(1).strip() if m_pri else ""
        if due == today or due == "":
            rows.append((due, pri, title, src.name))
    if not rows:
        await update.message.reply_text("No open tasks for today.")
        return
    rows.sort(key=lambda r: (r[0] != today, r[0], r[2]))
    lines = ["*Today's open tasks:*"]
    for due, pri, title, fname in rows[:20]:
        tag = ""
        if pri == "high":
            tag = " 🔴"
        elif pri == "low":
            tag = " 🟢"
        due_txt = due if due else ""
        lines.append(f"  - {title}{tag}" + (f"  (due {due_txt})" if due_txt else ""))
    if len(rows) > 20:
        lines.append(f"  ...and {len(rows) - 20} more")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    raw = update.message.text.strip()
    if not raw.startswith("@search"):
        return
    kw = raw[len("@search"):].strip()
    if not kw:
        await update.message.reply_text("`@search` needs a keyword.\nExample: `@search Lovable`")
        return
    hits = []
    for src in VAULT_ROOT.rglob("*.md"):
        try:
            txt = src.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(re.escape(kw), txt, re.I):
            rel = src.relative_to(VAULT_ROOT)
            title = md_title(src)
            hits.append((str(rel), title))
    if not hits:
        await update.message.reply_text(f"No matches for `_{kw}_`.")
        return
    lines = [f"*Found {len(hits)} match(es) for `_{kw}_`:*"]
    for rel, title in hits[:15]:
        lines.append(f"  - __{title}__\n    `{rel}`")
    if len(hits) > 15:
        lines.append(f"  ...and {len(hits) - 15} more")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback: any text that starts with @ but didn't match a handler."""
    text = update.message.text.strip()
    if not text.startswith("@"):
        return
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised.")
        return
    await update.message.reply_text(
        f"Unknown command `_{text.split()[0]}_`. Send `@help` for the command list.",
        parse_mode="Markdown")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("telegram handler error")

# ---------- main ----------
def main():
    app = (Application.builder()
           .token(BOT_TOKEN)
           .concurrent_updates(False)
           .build())
    app.add_handler(CommandHandler("start", start))
    # Command-style @handlers via regex MessageHandlers so they don't collide.
    app.add_handler(MessageHandler(filters.Regex(r"^@task\b"), handle_task))
    app.add_handler(MessageHandler(filters.Regex(r"^@remind\b"), handle_remind))
    app.add_handler(MessageHandler(filters.Regex(r"^@inbox\b"), handle_inbox))
    app.add_handler(MessageHandler(filters.Regex(r"^@note\b"), handle_note))
    app.add_handler(MessageHandler(filters.Regex(r"^@journal\b"), handle_journal))
    app.add_handler(MessageHandler(filters.Regex(r"^@done\b"), handle_done))
    app.add_handler(MessageHandler(filters.Regex(r"^@list\b"), handle_list))
    app.add_handler(MessageHandler(filters.Regex(r"^@search\b"), handle_search))
    app.add_handler(MessageHandler(filters.Regex(r"^@help\b"), start))
    # Catch-all for any other @-prefixed text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
    app.add_error_handler(error_handler)
    logger.info("bot starting — long polling")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
