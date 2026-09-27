---
name: subagent-verification
description: Verify a subagent's result against its transcript log.
---

Rules for reporting delegated work:

- **Verify against the live transcript before reporting.** A subagent's
  summary is a self-report. Its live log records actual tool calls; read it
  before you state what a subagent "did." Log path and reading patterns:
  see `references/transcript-log.md`.
- **`api_calls` counts the child's own turns, not tool calls.** A summary
  showing `api_calls: 2` may have made 3 web searches, or it may have made
  none. Only the transcript log settles which. Don't cite the header as
  evidence of tool use.
- **Treat "ran N searches" as N-attempted, not N-succeeded.** Failed calls
  (403, timeout, empty result) still show in the log. A subagent that
  reports "I searched for X, Y, Z" may have had the most decision-relevant
  of those fail — the failure is usually flagged by the child, but confirm
  it yourself before deciding the gap is minor. Partial retrieval is not
  the same as full coverage.
- **Check grounding depth, not just grounding presence.** Search results
  return snippets and titles; `web_extract` returns full page bodies. If a
  subagent made zero `web_extract` calls, every specific number or policy
  detail is snippet-only — unverified against the actual source. Say so
  plainly when reporting; don't let "cited" imply "confirmed."
- **Quote the subagent's result verbatim when the user asks for it.** Don't
  paraphrase findings back when the request is for the raw answer — the
  user wants to judge quality themselves. Add caveats separately, below the
  quote, not folded into it.
- **Separate self-reported caveats from findings you added.** A subagent
  flags its own gaps ("couldn't verify X"); your job is to independently
  confirm whether those gaps are real and material, not to echo them as if
  they were your own judgment.
- **Resolution test, not index listing.** When checking whether a skill or
  persona exists, `skill_view(name)` is the resolution test — it reads from
  disk and returns `success: true/false`. The `available_skills` index in
  your system prompt can be stale or incomplete relative to `~/.hermes/
  skills/` and must not be cited as evidence that a name fails. A name
  missing from the index still resolves if the file exists on disk.
