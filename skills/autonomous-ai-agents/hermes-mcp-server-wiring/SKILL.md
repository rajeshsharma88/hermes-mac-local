---
name: hermes-mcp-server-wiring
description: "Use to wire a local stdio MCP server into Hermes."
version: 1.0.0
author: Atlas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, mcp, stdio, server-wiring, config]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [hermes-agent, hermes-plugin-enable-verify]
---

# Wiring Local Stdio MCP Servers into Hermes

Hermes ships a native MCP client, but its stdio recipe assumes an `npx`
package that lives wherever npm can find it. A server that is a local repo
with a working directory, an `.env`, or a build step needs a different shape,
and the stock recipe fails in ways that look like the server is broken.

**Scope boundary:** the bundled `hermes-agent` skill's
`references/native-mcp.md` covers transports, auth, and the general config
schema. It is out of date on the details below (`cwd`, stdout purity, env-file
loading, the restart story). Where they conflict, trust the code and this
skill: `tools/mcp_tool_transport.py` and `tools/mcp_tool_config.py`.

## Standing Rules

1. **Never put secrets in `config.yaml`.** Keep credentials in the server's
   own `.env` and load them at spawn time, so the value is never a config
   edit that shows up in diffs or backups.
2. **stdout is the protocol. Only JSON-RPC on stdout.** Anything else the
   server writes to stdout silently corrupts the stream; stderr is safe.
3. **Verify against Hermes's own env filter, not your shell.** A server that
   boots in your interactive shell can still die under the filtered env
   Hermes actually hands it. Probe with the filtered env before wiring.
4. **`hermes mcp test <name>` is the authoritative check.** In-turn `tool_search`
   is stale until the next session; do not use it to judge a fresh wiring.

## The Stdio Contract

Three hard facts from the source, all of which the common recipe violates:

- **The child inherits the agent's cwd, but `cwd` is configurable.**
  `tools/mcp_tool_transport.py` reads `config.get("cwd")` first, then falls
  back to the resolved session cwd, then `None`. Hermes also runs
  `_runtime_cwd.resolve_context_cwd()`, so an unconfigured server runs
  wherever the agent happens to be — which is almost never the server's repo.
- **stderr goes to `~/.hermes/logs/mcp-stderr.log`, not the stream.** Banners
  on stderr are harmless (and are where the MCP SDK writes most of its
  logging). Only stdout is fatal.
- **The env is stripped to a fixed allowlist.**
  `_SAFE_ENV_KEYS = {PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR}`
  plus `XDG_*`, plus any names registered by an external secret source, plus
  whatever you set under `env:`. Every API key in your shell is gone.

## Wrapper Pattern

For a local repo that needs a cwd and an `.env`, ship a small launcher and
point `command:` at it. This is the shape that survives the stripped env and
keeps secrets out of config:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "/path/to/server/repo"
exec node --env-file=.env dist/index.js --transport stdio "$@"
```

Then:

```bash
hermes config set mcp_servers.<name>.command /path/to/repo/start-stdio.sh
hermes config unset mcp_servers.<name>.args   # stale args from an old recipe
```

Use `hermes config set` / `unset`, never a hand edit — a stray indent in a
mapping section corrupts the live gateway config. After changing `command`,
always `unset` any stale `args` from the previous recipe; they still apply and
will break the new command's argument parsing.

`hermes mcp add --command X --args Y` cannot express `cwd`, which is why a
wrapper is the right answer for a repo-rooted server rather than an unfixable
limitation.

### Why not `command: npm`, `args: [run, start:stdio]`

Two separate failures, both independent:

- **No cwd** — `npm run` resolves the package relative to the inherited cwd,
  which is the agent's directory, so the package is not found and the
  connection closes on spawn.
- **Banner on stdout** — even from the right directory, npm prints its
  package-name and script-name lines to stdout before invoking the script.
  That interleaves with JSON-RPC and the client rejects the connection.

`exec node ...` (or `exec uvx ...`) skips the package-manager layer entirely
and keeps stdout clean.

### Env loading: `--env-file` must be a direct flag

Node rejects `--env-file` inside `NODE_OPTIONS` outright (`node: --env-file=
is not allowed in NODE_OPTIONS`), so the option has to be passed to `node`
straight. This applies to whatever runtime hosts the server:

| Runtime | Loads `.env` |
|---|---|
| Node | `node --env-file=.env dist/index.js` (Node ≥ 20.6) |
| Node + npm | `npm run start --env-file=.env -- --transport stdio` (npm ≥ 10.7) |
| Python | `python -c 'from dotenv import load_dotenv; ...'` or a wrapper that calls `load_dotenv()` before importing the entrypoint |
| Bun | `bun --env-file=.env ./index.ts` |
| pnpm | `pnpm --env-file=.env start:stdio` |

If the server does not ship a dotenv loader of its own, grep before assuming:
`grep -rn dotenv src/ package.json` then check whether `dotenv` is actually a
dependency. Many servers read only `process.env` and expect the env to be
injected by the wrapper or launcher — nothing loads `.env` by itself.

## Verify Before Wiring

Reproduce Hermes's filtered env and run a real handshake. This catches
missing-cwd, missing-secrets, and stdout-corruption bugs at once:

```javascript
// temp .mjs — probe with the allowlist Hermes actually hands over
import { spawn } from 'node:child_process';

const SAFE = new Set(["PATH","HOME","USER","LANG","LC_ALL","TERM","SHELL","TMPDIR"]);
const safeEnv = Object.fromEntries(
  Object.entries(process.env).filter(([k]) =>
    SAFE.has(k) || SAFE.has(k.toUpperCase()) || k.startsWith("XDG_")));

const child = spawn("/path/to/repo/start-stdio.sh", [],
  { env: safeEnv, stdio: ["pipe","pipe","pipe"] });
let out = "";
child.stdout.on("data", d => out += d);
child.stdin.write(JSON.stringify({
  jsonrpc: "2.0", id: 1, method: "initialize",
  params: { protocolVersion: "2025-03-26", capabilities: {},
            clientInfo: { name: "probe", version: "1.0" } },
}) + "\n");

setTimeout(() => {
  const nonJson = out.trim().split("\n").filter(l => {
    try { JSON.parse(l); return false; } catch { return l.length > 0; }
  });
  console.log("clean stdout:", nonJson.length === 0);
  console.log("non-json lines:", JSON.stringify(nonJson));
  const init = out.split("\n").map(l => { try { return JSON.parse(l); } catch { return null; } })
    .find(o => o?.result?.serverInfo);
  console.log("server:", JSON.stringify(init?.result?.serverInfo));
  child.kill("SIGTERM");
  process.exit(0);
}, 8000);
```

Non-JSON lines in stdout mean the stream is corrupt — fix the launcher before
wiring. A successful `server:` line under the filtered env means the server
boots with nothing your shell provides.

A stdio server exits when stdin closes, so a bare `npm run start:stdio`
in a background terminal returns immediately — that is correct behaviour, not
a crash. Drive it through a pipe as above.

## Confirm Wiring

```bash
hermes mcp test <name>    # → ✓ Connected, ✓ Tools discovered: N
hermes mcp list           # shows transport + status
```

`hermes mcp test` spawns the server the same way the agent does, so it is the
only check that exercises the real path.

Tool count can differ between a raw `tools/list` probe and what the agent
registers (a small style drift — transport metadata and internal tools get
filtered). Do not treat a small count mismatch as failure; use it to check
the delta, not to fail the wiring.

## Reload Semantics

- **In-conversation MCP reload does happen.** Hermes detects the config
  change and reconnects within the session; the live conversation gains the
  tools and announces the new count. A full restart is not required.
- **The dashboard process picks the server up as a child** parented to its
  own PID. That is normal, not a leaked process — kill it with the dashboard,
  not separately.
- **Plugins do not share this behaviour.** Plugin tools are deferred to the
  next session even after the gateway reloads, so "I restarted, where are
  my tools?" after a plugin install is expected. See
  `hermes-plugin-enable-verify` for that path.

## Tool Naming

Registered names follow `mcp__<server>__<tool>` — double underscores, server
name lowercased with dashes kept, and the tool's own name preserved (underscores
stayed underscores, not converted). The bundled reference documents
`mcp_{server}_{tool}` with single underscores and says hyphens become
underscores; that is not what registration produces. Use `tool_search` with the
server name to read the actual names rather than assuming.

## Pitfalls

- **Do not leave stale `args` from a previous recipe.** `hermes config set`
  on `command` does not clear `args`; the old ones still concatenate and break
  the new command's parser.
- **Do not rely on `NODE_OPTIONS` for `.env`.** Node refuses it; only a
  direct runtime flag or a code-level `load_dotenv()` works.
- **Do not trust a shell-level smoke test.** Your shell has every API key
  set, so the server boots there while Hermes's stripped env kills it. Always
  probe with the allowlist above.
- **Do not use in-turn `tool_search` to judge a fresh wiring.** It is
  stale until the next session's deferred reload lands. `hermes mcp test`
  is current.
- **Do not paste the server's `env:` block into `config.yaml` to fix a
  "missing secret" error.** That writes credentials into a file that gets
  diffed, backed up, and versioned. Wrap the loader instead.
- **Do not wire an HTTP-transport server with a `command`.** A server config
  must have exactly one of `command` (stdio) or `url` (HTTP); both is a
  schema error, and neither produces a working connection.
- **Do not chase the wrapper's child process.** After wiring, the server
  runs as a child of whichever Hermes process discovered it (dashboard,
  gateway, or CLI). Managing it means managing the parent.
