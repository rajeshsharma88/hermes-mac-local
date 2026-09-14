import importlib, importlib.util, sys, logging, os
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, "/Users/rajeshcsharma/.hermes")

# force re-read from disk (the source file), bypassing any cached .pyc
bot_path = "/Users/rajeshcsharma/.hermes/telegram_task_bot.py"
spec = importlib.util.spec_from_file_location("bot_fresh", bot_path)
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)

print("=== tokenizer (fresh from disk) ===")
for text in [
    "hello world",
    "[[2026-Q3]]",
    "due:Sep 20",
    "[[Daily Rituals]]:context",
    "priority:high",
    "Build cart logic in Lovable",
    "Morning yoga due:tomorrow [[Daily Rituals]]:context",
    "Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]",
    "Review GTM config due:next Monday priority:high [[2026-Q3]]",
    "Meditate 20 min [[Daily Rituals]]:context due:today",
    "Call Vicky Friday priority:high",
]:
    print(f"  {text!r}")
    print(f"    -> {list(bot._tokenize(text))}")

print("\n=== parser + file write ===")
for text in [
    "Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]",
    "Morning yoga due:tomorrow [[Daily Rituals]]:context",
    "Review GTM config due:next Monday priority:high [[2026-Q3]]",
    "Meditate 20 min [[Daily Rituals]]:context due:today",
    "Call Vicky Friday priority:high",
    "Build cart logic in Lovable",
]:
    r = bot.parse_task_text(text)
    print(f"\n{text}")
    print(f"  title={r['title']!r} due={r['due']} pri={r['priority']} "
          f"proj={r['projects']} ctx={r['contexts']}")
    if r["due"] or r["projects"] or r["contexts"]:
        p = bot.write_task_file(r)
        print(f"  FILE: {p.name}")
        print("   " + "\n   ".join(p.read_text().splitlines()[:16]))
print("\nDONE")
