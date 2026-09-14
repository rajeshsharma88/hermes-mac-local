# ---------- command handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised."); return
    await update.message.reply_text(_START_TEXT)

_KNOWN_COMMANDS = {
    "@task": "Create a TaskNotes task in 06 - Tasks/ (supports due:, priority:, status:, project:)",
    "@remind": "Create a task with natural-language due date (e.g. `@remind Call Vicky due:Friday priority:high`)",
    "@inbox": "Drop a raw capture into 00 - Inbox/",
    "@note": "Create a permanent note in 01 - Notes/ under [[Permanent Notes]]",
    "@journal": "Append to today's Daily note under Notes / Journal",
    "@done": "Mark a task as done by keyword (e.g. `@done Lovable CRM`)",
    "@list": "Show today's open tasks",
    "@search": "Search notes and tasks across the vault by keyword",
    "@today": "Show your day at a glance — upcoming tasks + recent journal",
    "@weather": "Current weather for a city (default: Delhi). E.g. `@weather Mumbai`",
    "@news": "Latest Hacker News headlines on a topic (default: ai). E.g. `@news llm`",
    "@help": "Show this list",
}

async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised."); return
    text = update.message.text.strip()
    if not text.startswith("@task"): return
    payload = text[len("@task"):].strip()
    if not payload:
        await update.message.reply_text("`@task` needs a description. Example: `@task Build Lovable CRM due:Sep 20 priority:high`")
        return
    task = parse_task_text(payload)
    if "due" in payload.lower() and not task["due"]:
        await update.message.reply_text(f"Couldn't parse the due date in `_{payload}_`. Try a clearer format like `due:tomorrow`, `due:Friday`, `due:Sep 20`, or `due:17`.")
        return
    try:
        dest = write_task_file(task)
    except Exception as exc:
        logger.exception("Failed to write task file")
        await update.message.reply_text(f"Sorry — couldn't save the task: {exc}"); return
    parts = [f"✓ Task saved: *{task['title']}*"]
    det = []
    if task["due"]: det.append(f"due {task['due'].strftime('%b %d')}")
    if task["priority"] != "normal": det.append(f"priority {task['priority']}")
    if task["projects"]: det.append("project "+", ".join(task["projects"]))
    if det: parts.append("("+", ".join(det)+")")
    parts.append(f" → `{dest.name}`")
    await update.message.reply_text("\n".join(parts), parse_mode="Markdown")

async def handle_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised."); return
    raw = update.message.text.strip()
    if not raw.startswith("@inbox"): return
    text = raw[len("@inbox"):].strip()
    if not text:
        await update.message.reply_text("`@inbox` needs something to capture. Example: `@inbox Idea for YouTube thumbnails`"); return
    folder = VAULT_ROOT / "00 - Inbox"
    _ensure_folder(folder)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    fname = f"{ts.replace(' ','_')}_capture.md"
    dest = folder / fname
    body = f"---\nsource: telegram\ntype: inbox-capture\ncreated: {ts}\n---\n\n{text}\n"
    dest.write_text(body, encoding="utf-8")
    await update.message.reply_text(f"✓ Saved to inbox → `{dest.relative_to(VAULT_ROOT)}`", parse_mode="Markdown")

async def handle_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised."); return
    raw = update.message.text.strip()
    if not raw.startswith("@note"): return
    text = raw[len("@note"):].strip()
    if not text:
        await update.message.reply_text("`@note` needs content. Example: `@note Obsidian is a markdown-based knowledge base`"); return
    folder = VAULT_ROOT / "01 - Notes"
    _ensure_folder(folder)
    slug = slugify(text.split()[0] if text.split() else "note")
    dest = folder / f"{slug}.md"
    cn = date.today().isoformat()
    body = f"""---\ncategories: [[Permanent Notes]]\ncreated: {cn}\n---\n\n# {text.splitlines()[0] if text.splitlines() else slug.title()}\n\n{text}\n"""
    if dest.exists():
        await update.message.reply_text(f"Note exists — not overwriting `{dest.relative_to(VAULT_ROOT)}`"); return
    dest.write_text(body, encoding="utf-8")
    await update.message.reply_text(f"✓ Note created → `{dest.relative_to(VAULT_ROOT)}`", parse_mode="Markdown")

async def handle_journal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised."); return
    raw = update.message.text.strip()
    if not raw.startswith("@journal"): return
    text = raw[len("@journal"):].strip()
    if not text:
        await update.message.reply_text("`@journal` needs an entry. Example: `@journal Meditated 20 min today`"); return
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
    await update.message.reply_text(f"✓ Journal updated → `{dest.relative_to(VAULT_ROOT)}`", parse_mode="Markdown")

async def handle_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = str(update.effective_user.id)
    if ALLOWED_IDS and uid not in ALLOWED_IDS:
        await update.message.reply_text("Not authorised."); return
    raw = update.message.text.strip()
    if not raw.startswith("@done"): return
    kw = raw[len("@done"):].strip()
    if not kw:
        await update.message.reply_text("`@done` needs a task keyword. Example: `@done Lovable CRM`"); return
    hits, done = [], []
    for src in sorted(TASKS_FOLDER.glob("*.md")):
        try: txt = src.read_text(encoding="utf-8")
        except OSError: continue
        if re.search(rf"status:\s*done\b", txt, re.I): continue
        title_m = re.search(r"^# (.+)$", txt, re.M)
        title = title_m.group(1) if title_m else src.stem
        if kw.lower() in title.lower():
            hits.append((src, title, txt))
    if not hits:
        await update.message.reply_text(f"No open task matching `_{kw}_` found. Run `@list` to see current tasks."); return
    if len(hits) > 1:
        names = "\n".join(f"  _{t}_" for _, t, _ in hits[:10])
        await update.message.reply_text(f"Multiple matches (showing first {len(hits[:10])}):\n{names}\n\nPlease be more specific or run `@done <exact title>`."); return
    src, orig, txt = hits[0]
    new = re.sub(r"(?m)^status:\s*.+$", "status: done", txt, count=1)
    if "status:" not in txt:
        new = f"---\nstatus: done\n---\n\n{new}"
    src.write_text(new, encoding="utf-8")
    await update.message.reply_text(f"✓ Marked *{orig}* as done → `{src.name}`", parse_mode="Markdown")
