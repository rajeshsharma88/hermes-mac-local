#!/usr/bin/env python3
"""Telegram bot — @task/@inbox/@note/@journal/@done/@list/@search/
@remind/@today/@weather/@news/@help → Obsidian vault files.
General chat → OpenRouter LLM. Long polling, no webhook."""
from __future__ import annotations
import os, re, sys, logging, httpx
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
            if not line or line.startswith("#") or "=" not in line: continue
            k, _, v = line.partition("="); env[k.strip()] = v.strip()
    except OSError as e: logger.exception("read %s", ENV_PATH)
    return env
_env = _load_env()
BOT_TOKEN = _env.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_USERS = _env.get("TELEGRAM_ALLOWED_USERS", "").strip()
LLM_BASE_URL = _env.get("LLM_BASE_URL", "https://openrouter.ai/api/v1").strip()
LLM_MODEL = _env.get("LLM_MODEL", "deepseek/deepseek-v4.1-flash").strip()
LLM_API_KEY = _env.get("LLM_API_KEY", "").strip()
ALLOWED_IDS = set(t.strip() for t in ALLOWED_USERS.split(",") if t.strip()) if ALLOWED_USERS else set()
if not BOT_TOKEN:
    logging.error("No TELEGRAM_BOT_TOKEN in %s", ENV_PATH); sys.exit(1)
VAULT_ROOT = Path("/Users/rajeshcsharma/Documents/Obisidian/Rajesh Sharma OS")
TASKS_FOLDER = VAULT_ROOT / "06 - Tasks"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("telegram_task_bot")

# ---- date parsing ----
_WEEKDAYS = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,"friday":4,"saturday":5,"sunday":6}
_DATE_FORMATS = ["%Y-%m-%d","%b %d","%b %d, %Y","%d %b %Y"]
_STATUS_KEYWORDS = {"done":"done","completed":"done","open":"open","in-progress":"in-progress","inprogress":"in-progress","ip":"in-progress","high":"high","normal":"normal","low":"low"}
_RAW_DATE_PHRASES = ["by tomorrow","due tomorrow","by next week","next week","in a week","in 1 week","in 2 weeks","in 3 weeks"]
def _next_weekday(twd, after=True):
    today = date.today()
    da = (twd - today.weekday()) % 7
    if da == 0 and after: da = 7
    return today + timedelta(days=da)
def _parse_date(s):
    s = s.strip().lower()
    if s.isdigit():
        d = int(s); now = datetime.now()
        try: return date(now.year, now.month, d)
        except ValueError: return None
    for fmt in _DATE_FORMATS:
        try: return datetime.strptime(s, fmt).date()
        except ValueError: continue
    if s in _WEEKDAYS: return _next_weekday(_WEEKDAYS[s], False)
    if s.startswith("next ") and s[5:] in _WEEKDAYS: return _next_weekday(_WEEKDAYS[s[5:]], True)
    if s.startswith("by ") and s[3:] in _WEEKDAYS: return _next_weekday(_WEEKDAYS[s[3:]], False)
    m = re.match(r"^in\s+(\d+)\s+days?$", s)
    if m: return date.today() + timedelta(days=int(m.group(1)))
    m = re.match(r"^in\s+(\d+)\s+weeks?$", s)
    if m: return date.today() + timedelta(weeks=int(m.group(1)))
    if s in ("today","tonight"): return date.today()
    if s == "tomorrow": return date.today() + timedelta(days=1)
    if s == "yesterday": return date.today() - timedelta(days=1)
    return None
def _first_weekday_in_text(text, prefer_after=True):
    low = text.lower()
    for nm, num in _WEEKDAYS.items():
        if re.search(rf"\b{nm}\b", low): return _next_weekday(num, prefer_after)
    return None

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
