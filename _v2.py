import importlib, importlib.util, logging, sys, time
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, "/Users/rajeshcsharma/.hermes")
spec = importlib.util.spec_from_file_location("bot", "/Users/rajeshcsharma/.hermes/telegram_task_bot.py")
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)

tests = [
    ("Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]",
     {"title": "Launch WhatsApp order automation", "due": "2026-09-20", "priority": "high",
      "projects": ["2026-Q3", "Ecommerce"], "contexts": [], "status": "open"}),
    ("Morning yoga due:tomorrow [[Daily Rituals]]:context",
     {"title": "Morning yoga", "due": "2026-09-14", "priority": "normal",
      "projects": [], "contexts": ["Daily Rituals"], "status": "open"}),
    ("Review GTM config due:next Monday priority:high [[2026-Q3]]",
     {"title": "Review GTM config", "due": "2026-09-14", "priority": "high",
      "projects": ["2026-Q3"], "contexts": [], "status": "open"}),
    ("Meditate 20 min [[Daily Rituals]]:context due:today",
     {"title": "Meditate 20 min", "due": "2026-09-13", "priority": "normal",
      "projects": [], "contexts": ["Daily Rituals"], "status": "open"}),
    ("Call Vicky Friday priority:high",
     {"title": "Call Vicky Friday", "due": None, "priority": "high",
      "projects": [], "contexts": [], "status": "open"}),
    ("Build cart logic in Lovable",
     {"title": "Build cart logic in Lovable", "due": None, "priority": "normal",
      "projects": [], "contexts": [], "status": "open"}),
]

ok = True
for text, expected in tests:
    r = bot.parse_task_text(text)
    due_str = r["due"].isoformat() if r["due"] else None
    got = {"title": r["title"], "due": due_str, "priority": r["priority"],
           "projects": r["projects"], "contexts": r["contexts"], "status": r["status"]}
    good = got == expected
    if not good:
        ok = False
    print(f"{'PASS' if good else 'FAIL'}: {text}")
    if not good:
        print(f"  expected: {expected}")
        print(f"  got:      {got}")
print("\nALL PASS" if ok else "\nSOME FAILED")
