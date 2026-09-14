import sys, signal, importlib, logging
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, "/Users/rajeshcsharma/.hermes")

def _alarm_exit(signum, frame):
    print("ALARM — hung at this point")
    sys.exit(2)

signal.signal(signal.SIGALRM, _alarm_exit)

print("step 1: import module")
import telegram_task_bot as bot
print("  ok, module imported")

print("step 2: reload")
importlib.reload(bot)
print("  ok, reloaded")

signal.alarm(8)
print("step 3: _tokenize one trivial string")
toks = list(bot._tokenize("hello world"))
print("  tokens:", toks)
signal.alarm(0)

signal.alarm(8)
print("step 4: _tokenize a [[link]] string")
toks = list(bot._tokenize("[[2026-Q3]]"))
print("  tokens:", toks)
signal.alarm(0)

signal.alarm(8)
print("step 5: _tokenize due:Sep 20")
toks = list(bot._tokenize("due:Sep 20"))
print("  tokens:", toks)
signal.alarm(0)

signal.alarm(8)
print("step 6: _tokenize [[Daily Rituals]]:context")
toks = list(bot._tokenize("[[Daily Rituals]]:context"))
print("  tokens:", toks)
signal.alarm(0)

print("DONE")
