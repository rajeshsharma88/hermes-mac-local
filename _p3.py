
# ---- task parsing ----
def parse_task_text(text):
    rem = text.strip()
    if not rem: return {"title":"","due":None,"priority":"normal","projects":[],"contexts":[],"status":"open"}
    due=None; priority="normal"; projects=[]; contexts=[]; status="open"
    parts = re.split(r"\s+", rem, maxsplit=1)
    title = parts[0] if parts else ""
    rest = parts[1] if len(parts)>1 else ""
    for tok in re.split(r"\s+", rest):
        if not tok: continue
        m = re.match(r"^\[\[(.+?)\]\]\s*(?::\s*(.+))?$", tok)
        if m:
            label, kind = m.group(1), (m.group(2) or "").strip()
            if kind=="context": contexts.append(label)
            else: projects.append(label)
            continue
        m = re.match(r"^([a-z]+):(.+)$", tok)
        if not m: continue
        key, val = m.group(1), m.group(2).strip()
        if key=="due":
            due = _parse_date(val) or _first_weekday_in_text(val, True)
        elif key=="priority": priority = _STATUS_KEYWORDS.get(val,"normal")
        elif key=="status": status = _STATUS_KEYWORDS.get(val,"open")
    return {"title":title,"due":due,"priority":priority,"projects":projects,"contexts":contexts,"status":status}

# ---- file helpers ----
def slugify(title):
    s = re.sub(r'[^\w\s-]','',title.lower()); s = re.sub(r'[\s_]+','-',s).strip('-')
    return s[:50] or "untitled"
def _today_day(): return date.today().strftime("%a")[:2]
def _ensure_folder(p): p.mkdir(parents=True, exist_ok=True)
def today_daily_path():
    d = date.today(); folder = VAULT_ROOT/"05 - Periodic Notes"/"Daily"
    pat = re.compile(rf"^{d.isoformat()}\(.*\)\.md$", re.I)
    if folder.exists():
        for c in folder.iterdir():
            if c.is_file() and pat.match(c.name): return c
    return folder / f"{d.isoformat()}({_today_day()}).md"
def write_task_file(task):
    _ensure_folder(TASKS_FOLDER)
    slug = slugify(task["title"]); dest = TASKS_FOLDER / f"{slug}.md"
    links = " ".join(f"[[{p}]]" for p in task["projects"])
    due_line = f"  due: {task['due'].isoformat()}" if task['due'] else ""
    ctx_line = ("  contexts: "+", ".join(f"[[{c}]]" for c in task['contexts'])) if task['contexts'] else ""
    body = f"""---
tags:
  - task
title: {task['title']}
status: {task['status']}
priority: {task['priority']}
due: {task['due'].isoformat() if task['due'] else ''}
projects: {links}
contexts: {', '.join(task['contexts'])}
---

# {task['title']}
#{[f'  HAPPENED [[{p}]]' for p in task['projects']]}
{due_line}
{ctx_line}
"""
    dest.write_text(body, encoding="utf-8"); return dest
def md_title(path):
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "): return line[2:].strip()
    except OSError: pass
    return path.stem
