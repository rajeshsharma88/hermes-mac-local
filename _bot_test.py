import importlib, logging, sys
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, "/Users/rajeshcsharma/.hermes")
import telegram_task_bot as bot
importlib.reload(bot)

print("=== tokenizer tokens ===")
for text in [
    "Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]",
    "Morning yoga due:tomorrow [[Daily Rituals]]:context",
    "Review GTM config due:next Monday priority:high [[2026-Q3]]",
    "Meditate 20 min [[Daily Rituals]]:context due:today",
]:
    print(f"\n{text}")
    print("  TOK:", list(bot._tokenize(text)))

print("\n=== parser results ===")
for text in [
    "Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]",
    "Morning yoga due:tomorrow [[Daily Rituals]]:context",
    "Review GTM config due:next Monday priority:high [[2026-Q3]]",
    "Meditate 20 min [[Daily Rituals]]:context due:today",
    "Call Vicky Friday priority:high",
]:
    r = bot.parse_task_text(text)
    print(f"\n{text}")
    print(f"  title={r['title']!r} due={r['due']} pri={r['priority']} "
          f"proj={r['projects']} ctx={r['contexts']}")
    if r["due"]:
        p = bot.write_task_file(r)
        print(f"  FILE: {p.name}")
        print("   " + "\n   ".join(p.read_text().splitlines()[:14]))
print("\nDONE")
