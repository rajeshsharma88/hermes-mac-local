import sys

def _tokenize(text):
    """Yield tokens from `text`. Three token shapes, all consuming their chars:
    - [[...]] blocks (optionally followed by :role, folded into ONE token)
    - key:value pairs where key is [a-z]+ and ':' appears before the next space
      or '[' (e.g. "due:Sep 20", "priority:high") — value absorbs one trailing
      bare word if it completes a date phrase
    - plain words otherwise (no ':' and no '[' in the span)

    Each iteration MUST advance `i` past the yielded token; otherwise the loop
    is infinite."""
    i, n = 0, len(text)
    while i < n:
        # skip whitespace between tokens
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break

        # ---- [[...]] block (with optional :role) ----
        if text[i] == "[":
            end = text.find("]]", i)
            if end == -1:
                yield text[i:]
                break
            j = end + 2                       # end of "]]"
            # fold a following :role into the same token
            if j < n and text[j] == ":":
                j += 1
                while j < n and not text[j].isspace():
                    j += 1
            yield text[i:j]
            i = j
            continue

        # ---- key:value pair: a run of letters, then ':', then value ----
        if text[i].isalpha():
            key_end = i
            while key_end < n and text[key_end].isalpha():
                key_end += 1
            if key_end < n and text[key_end] == ":":
                val_start = key_end + 1
                j = val_start
                # absorb the first value word (no spaces)
                while j < n and not text[j].isspace():
                    j += 1
                # absorb one more bare word if it looks like the rest of a date
                # phrase and the char after it is a space then a [[, another key:,
                # or EOF (don't greedily swallow a third token)
                sp = j
                while sp < n and text[sp].isspace():
                    sp += 1
                if sp < n and text[sp] != "[" and (not text[sp].isalpha() or sp + 1 >= n or not text[sp + 1].isalpha()):
                    # next non-space char isn't a letter, or is a single letter
                    # followed by non-letter -> we're done after one value word
                    pass
                else:
                    # peek at the next bare word; absorb it if it looks like a
                    # continuation (e.g. "20" in "Sep 20", "Monday" in "next Monday")
                    second = sp
                    while second < n and not text[second].isspace() and text[second] != "[":
                        second += 1
                    if second > sp:
                        j = second
                yield text[i:j]
                i = j
                continue
            # not a key:value (no ':' right after the letters) — fall through to
            # plain-word branch; advance i so we don't re-scan the same letters
            i = key_end
            continue

        # ---- plain word (no ':' and no '[' in the span) ----
        start = i
        while i < n and not text[i].isspace() and text[i] != "[" and text[i] != ":":
            i += 1
        if i > start:
            yield text[start:i]
            continue
        # nothing consumed (i landed on ':' or '[' with no preceding word) —
        # advance past the delimiter so the loop makes progress
        i += 1

tests = [
    ("hello world", ["hello", "world"]),
    ("[[2026-Q3]]", ["[[2026-Q3]]"]),
    ("due:Sep 20", ["due:Sep 20"]),
    ("[[Daily Rituals]]:context", ["[[Daily Rituals]]:context"]),
    ("priority:high", ["priority:high"]),
    ("Build cart logic in Lovable", ["Build", "cart", "logic", "in", "Lovable"]),
    ("Morning yoga due:tomorrow [[Daily Rituals]]:context",
     ["Morning", "yoga", "due:tomorrow", "[[Daily Rituals]]:context"]),
    ("Launch WhatsApp order automation due:Sep 20 priority:high [[2026-Q3]] [[Ecommerce]]",
     ["Launch", "WhatsApp", "order", "automation", "due:Sep 20", "priority:high", "[[2026-Q3]]", "[[Ecommerce]]"]),
    ("Review GTM config due:next Monday priority:high [[2026-Q3]]",
     ["Review", "GTM", "config", "due:next Monday", "priority:high", "[[2026-Q3]]"]),
]

ok = True
for text, expected in tests:
    got = list(_tokenize(text))
    status = "PASS" if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"{status}: {text!r}")
    if got != expected:
        print(f"  expected: {expected}")
        print(f"  got:      {got}")

print("\nALL PASS" if ok else "\nSOME FAILED — check above")
