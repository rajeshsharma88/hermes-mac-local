import re, sys

def _tokenize(text):
    """Yield tokens from `text`. Three token shapes, all consuming their chars:
    - [[...]] blocks (optionally followed by :role, folded into ONE token)
    - key:value pairs where key is [a-z]+ and ':' appears before the next space
      or '[' (e.g. "due:Sep 20", "priority:high") — value absorbs one trailing
      bare word if it completes a date phrase (a numeric word, or a word that
      itself isn't a key: or [[)
    - plain words otherwise (no ':' and no '[' in the span)

    Each iteration MUST advance `i` past the yielded token; otherwise the loop
    is infinite."""
    i, n = 0, len(text)
    is_letter = lambda c: c.isalpha()
    is_digit = lambda c: c.isdigit()
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

        # ---- key:value pair: a run of [a-z] letters, then ':', then value ----
        if is_letter(text[i]):
            key_start = i
            while i < n and is_letter(text[i]):
                i += 1
            if i < n and text[i] == ":":
                # this is a key:value — consume the colon
                i += 1
                val_start = i
                # absorb the first value word (no spaces)
                while i < n and not text[i].isspace() and text[i] != "[":
                    i += 1
                # optionally absorb one more bare word if it completes a date
                # phrase. Look at the next non-space char; if it's a bare word
                # that does NOT start a new key: or [[, absorb it.
                sp = i
                while sp < n and text[sp].isspace():
                    sp += 1
                if sp < n and (is_letter(text[sp]) or is_digit(text[sp])) and text[sp] != "[":
                    # peek: is the next bare word itself a key: (letter-run then ':')?
                    k = sp
                    while k < n and is_letter(text[k]):
                        k += 1
                    if k < n and text[k] == ":":
                        # it's a new key:value — stop after the first value word
                        pass
                    else:
                        # absorb the second word (e.g. "20" in "Sep 20",
                        # "Monday" in "next Monday")
                        second_start = sp
                        while i < n and not text[i].isspace() and text[i] != "[":
                            i += 1
                yield text[key_start:i]
                continue
            # not a key:value — `i` is already at key_end (first non-letter);
            # fall through to the plain-word branch below

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
    ("Meditate 20 min [[Daily Rituals]]:context due:today",
     ["Meditate", "20", "min", "[[Daily Rituals]]:context", "due:today"]),
    ("Call Vicky Friday priority:high",
     ["Call", "Vicky", "Friday", "priority:high"]),
    ("@task Launch WhatsApp due:Sep 20 [[Proj]]",
     ["@task", "Launch", "WhatsApp", "due:Sep 20", "[[Proj]]"]),
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
