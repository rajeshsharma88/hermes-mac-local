# Reading a subagent's live transcript

## Location

The delegation completion message names the full transcript path:
`/Users/rajeshcsharma/.hermes/cache/delegation/live/<delegation_id>/task-<N>.log`

`<delegation_id>` is the `deleg_XXXXXXXX` id from the async completion header
(e.g. `deleg_21f1aaf0`). One `task-<N>.log` per delegated task; fan-out
batches produce one file per subtask.

## Log shape

Pipe-delimited lines, timestamp first, then role, then payload:

```
07:38:30 tool     | -> web_search(Meta ads policy 2026 India health sup...)
07:38:31 result   | web_search ok 1.0s: { "success": true, "data": { ... }
07:38:31 result   | web_search ERROR 0.9s: { "success": false, "error": ... }
```

`-> tool_name(args)` is an invocation. The following line is the return,
and `ok Ns:` vs `ERROR Ns:` tells you which. Truncated payloads show
`(+NNNN chars)`.

## What to check

1. **List every invocation** — grep the log for `-> ` to enumerate calls.
2. **Pair each with its outcome** — count `ok` vs `ERROR` returns.
3. **Note tool mix** — `web_search` only vs. `web_extract` present.
   Absence of `web_extract` means all grounding is snippet-level.
4. **Verify a successful extract returned the page you asked for.** A
   `web_extract ok` can still have fetched the wrong URL — one call for
   `faq.whatsapp.com/933578044281252` returned the
   `developers.facebook.com/.../phone-numbers` page instead. Read the
   `"url"` inside the result before crediting a claim to that source.
   Checking `ok`/`ERROR` alone confirms success, not relevance.
5. **Read the error payloads.** Backend 403s (e.g. Firecrawl keyless),
   timeouts, and empty result sets each fail differently and each matters
   for what claim is left unsupported.

## Common backends and their failure modes

- `web_search` may route to Firecrawl keyless mode. Without
  `FIRECRAWL_API_KEY` it returns `403 Forbidden`. Set the key via
  `hermes tools` if search reliability matters — this is a setup fix, not a
  permanent limitation.
- A 403 on one query does not disable others in the same batch — remaining
  calls in the batch still complete. Check each return individually.

## Cross-checking with session history

`session_search` returns the delegation completion message (role `user`,
prefixed `[ASYNC DELEGATION BATCH COMPLETE`) including the summary and the
transcript path. Use `role_filter: "user,assistant,tool"` to also see
the original `delegate_task` call arguments — useful to compare what was
*asked for* against what came back. Scroll the session with `session_id`
plus `around_message_id` to widen the window.

## Reporting pattern

1. State outcome first: finished / still running / failed.
2. Quote the result verbatim if that's what was asked for.
3. List tool calls with each one's outcome, sourced from the log.
4. Flag which claims lack full-body grounding, separately from the quote.
5. Distinguish the child's self-reported gaps from your own assessment.
