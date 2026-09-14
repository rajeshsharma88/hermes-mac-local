
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
