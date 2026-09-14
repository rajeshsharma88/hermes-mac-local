import importlib, importlib.util, logging, sys
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, "/Users/rajeshcsharma/.hermes")
spec = importlib.util.spec_from_file_location("bot", "/Users/rajeshcsharma/.hermes/telegram_task_bot.py")
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)

# instrument parse_task_text to print a trace for one input
original = bot.parse_task_text
def traced(text):
    print(f"\n=== TRACE: {text!r}")
    import copy
    state = {"calls": []}
    n = len(text)
    i = 0
    def _mark(label):
        state["calls"].append((label, i, text[i:] if i < n else ""))
    # We'll just call the real function but also a hand-rolled mini trace of the
    # title-collection + key:value decision for "due:Sep 20 priority:high".
    # Simpler: print what the tokenizer (if any) would do and what _parse_key_value
    # sees when called at i for key 'due'.
    return original(text)

if False:
    r = traced("Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]]")
    print("result:", r)

# direct probe: hand-run the title collection + key detection for "due:Sep 20"
text = "due:Sep 20"
n = len(text)
print(f"\nmanual parse of {text!r}:")
i = 0
def is_letter(c): return c.isalpha()
def is_word(c): return c.isalnum() or c in "-."
while i < n:
    while i < n and text[i].isspace():
        i += 1
    if i >= n: break
    ch = text[i]
    if ch == "[":
        print(f"  i={i} '[' -> structured link, stop title")
        break
    if is_letter(ch):
        k = i
        while k < n and is_letter(text[k]):
            k += 1
        print(f"  i={i} letter-run={text[i:k]!r}  text[k]={text[k]!r if k<n else None}")
        if k < n and text[k] == ":":
            print(f"    -> key:value detected, title ends here")
            # we WOULD set i = k+1 and call _parse_key_value()
            i_keyval = k + 1
            print(f"    _parse_key_value would receive i={i_keyval}, text[i:]={text[i_keyval:]!r}")
            # simulate _parse_key_value
            ks = i_keyval
            # key_start is ch..k-1 but note: _parse_key_value starts from current i
            # which is k+1... so it would re-read from ':' onward!
            print(f"    BUG: _parse_key_value starts at i={i_keyval} which is AFTER the colon; "
                  f"it will read key starting at text[{i_keyval}]={text[i_keyval]!r}")
            break
        else:
            print(f"    -> plain word, absorb")
            while i < n and is_word(text[i]) and text[i] != "[":
                i += 1
            print(f"    absorbed {text[:i]!r}, i now {i}")
            continue
    break

print("\nNOW probe the actual _parse_key_value as called from the real parser for due:Sep 20:")
import importlib, importlib.util, logging, sys as _sys
logging.basicConfig(level=logging.WARNING)
_sys.path.insert(0, "/Users/rajeshcsharma/.hermes")
spec = importlib.util.spec_from_file_location("bot2", "/Users/rajeshcsharma/.hermes/telegram_task_bot.py")
bot2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot2)
# monkeypatch _parse_key_value to print
_pkv = bot2.parse_task_text.__globals__["_parse_key_value"]
orig_pkv = bot2.parse_task_text.__globals__["_parse_key_value"]
print("cannot monkeypatch inner func easily; checking source instead")
PYEOF