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
