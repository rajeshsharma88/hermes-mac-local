import importlib, importlib.util, logging, sys, time
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, "/Users/rajeshcsharma/.hermes")

t0 = time.time()
spec = importlib.util.spec_from_file_location("bot", "/Users/rajeshcsharma/.hermes/telegram_task_bot.py")
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)
print(f"loaded in {time.time() - t0:.2f}s")

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
    ("yoga [[Daily Rituals]]:context due:today",
     {"title": "yoga", "due": "2026-09-13", "priority": "normal",
      "projects": [], "contexts": ["Daily Rituals"], "status": "open"}),
]

fail = False
for text, expected in tests:
    r = bot.parse_task_text(text)
    due_str = r["due"].isoformat() if r["due"] else None
    got = {"title": r["title"], "due": due_str, "priority": r["priority"],
           "projects": r["projects"], "contexts": r["contexts"], "status": r["status"]}
    ok = got == expected
    if not ok:
        fail = True
    print(f"{'PASS' if ok else 'FAIL'}: {text}")
    if not ok:
        print(f"  expected: {expected}")
        print(f"  got:      {got}")

if fail:
    print("\nSOME FAILED")
else:
    print("\nALL PASS")

# file write check (only if all pass)
if not fail:
    r = bot.parse_task_text("Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]")
    p = bot.write_task_file(r)
    print(f"\nfile write test: {p.name}")
    print(p.read_text())
