---
name: hermes-plugin-enable-verify
description: "Use to enable a Hermes plugin and prove it actually serves."
version: 1.0.0
author: Atlas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, plugins, enablement, verification, dashboard, desktop, gateway]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [hermes-agent]
---

# Enabling and Verifying Hermes Plugins

`hermes plugins enable <id>` only writes a config line. It registers intent;
the plugin serves nothing until two conditions are met that neither the config
file nor the CLI output tells you:

1. the **gateway process** has been restarted since the config changed, and
2. a **surface is actually reachable** that speaks the runtime the plugin ships
   for.

Most "plugin not appearing" / "widgets show no data" reports are condition 1 or
2, not a broken install. Diagnose in that order.

**Scope boundary:** the bundled `hermes-agent` skill's `references/desktop-plugins.md`
already covers the plugin SDK, manifest layout, the `desktop-plugins/` vs
`plugins/<id>/desktop/` split, and Settings → Plugins. This skill covers only
what that reference omits: the restart requirement, the gateway-port confusion,
and surface-to-backend topology.

## Standing Rules

1. **Enablement is registration, not activation.** Never report a plugin as
   "working" or "visible" from a successful `hermes plugins enable` alone.
2. **Verify in both directions — loaded AND serving.** Status says it's
   enabled; a live probe of the plugin's API route says it's actually mounted.
   Neither alone is sufficient.
3. **Restart the gateway before concluding anything about the live process.**
   Plugins load at gateway boot, not hot. A gateway older than the enable
   change has the old process state regardless of config.
4. **Only verify against a backend that is reachable.** A plugin enabled on
   backend A does not serve a browser pointed at backend B. Confirm the
   browser's target before reading "offline" widgets.
5. **Never claim a desktop plugin loads into a browser surface.** The PWA and
   the Electron app are different runtimes. See "Surface map" below.

## Procedure

### 1. Enable

```bash
hermes plugins enable <id>        # CLI
# or: Settings → Plugins → toggle (app UI, live)
```

Output ends with "Takes effect on next session." That is the CLI telling you
the live process is stale — honor it. The config lands at
`config.yaml` `plugins.enabled:`.

### 2. Restart the gateway

```bash
hermes gateway restart
```

Then confirm the process is new:

```bash
ps aux | grep "gateway run" | grep -v grep   # PID + start time
lsof -iTCP -sTCP:LISTEN -p <pid>             # what it actually listens on
```

A restarted gateway drops whatever was mid-flight: messaging platform
connections and webhook routes reconnect within seconds, but jobs firing during
the gap can miss. Tell the user.

### 3. Verify it is serving

A plugin with a Python API backend exposes routes under
`/api/plugins/<id>/...`. Probe one:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:<dashboard-port>/api/plugins/<id>/<a-route>
```

**Expected codes:** `200` (routed and served), `404` (not mounted — gateway
needs restart, or you probed the wrong port), `000` (nothing listening, or
host unreachable — connectivity, not plugin state).

### 4. Confirm the user's surface exists

Enablement is per-backend. The browser must reach the backend that carries the
plugin. Resolve which one first — see "Find the browser's backend" below.

### 5. Report honestly

State exactly which of the four steps passed, and name what you could not
verify. "Enabled and gateway restarted; the tab is not verified live because no
dashboard is listening locally" is a complete answer. "Enabled ✓" is not.

## Surface map

Three surfaces, three different requirements. Mixing them is the dominant
failure mode.

| Surface | Command | What serves plugins | Requires |
|---|---|---|---|
| **Web dashboard** | `hermes dashboard [--port N]` | Gateway HTTP process | `dashboard/dist` + `plugins.enabled`, served on a real HTTP port |
| **Native Desktop** | `hermes desktop` | Electron `desktop-plugins` runtime | Local Electron build + `scripts/install-desktop.mjs` run |
| **TUI widgets** | `hermes --tui` | `~/.hermes/tui-widgets/` | Separate registry, separate from both above |

**Web dashboard ≠ webhook port.** A listener on the webhook port is not the
dashboard. A `404` from probing it at `/api/plugins/...` proves nothing about
the plugin — that port never carried those routes. Find the real dashboard port
before probing.

**Chrome Web App shortcut ≠ Electron app.** A
`~/Applications/Chrome Apps.localized/<Name>.app` containing only an
`app_mode_loader` binary is a browser shortcut, not the native desktop app. It
has no `desktop-plugins` runtime, so no `desktop/plugin.js` can load into it —
even when correctly installed. Detect:

```bash
ls ~/Applications/Chrome\ Apps.localized/<Name>.app/Contents/MacOS/
#  app_mode_loader only        → PWA shortcut, not native
#  Electron                     → real app
```

Confirm the Electron build actually exists (an unbuilt source tree will not
launch):

```bash
ls ~/.hermes/hermes-agent/apps/desktop/{node_modules,dist,build} 2>&1
# all three absent → never built; `hermes desktop` must build on first run
```

## Third-party plugins

A unified plugin splits across machines: the desktop half runs on the client
computer, but **all widget data comes from the backend the client connects to**.
Enabling locally does nothing when the client is remote. Install + enable on the
remote backend first; its README names the repair command (typically
`hermes plugins install <id> --force --enable` then backend reconnect).

Before enabling, flag the trust surface: the desktop half is often 100+ KB of
minified JS that executes inside the user's Electron app. The Python half is
usually small and only persists layout plus proxies host APIs — worth reading
the desktop bundle before enabling.

Third-party plugins are verified against the Hermes version current when
released. If a widget reports `no data` while the plugin loads cleanly, suspect
upstream API drift first — not an install failure.

## Verification ladder

Run in order; stop and report at the first failure. Later steps are
uninformative without the earlier ones.

```bash
# 1. Is the backend listening at all?
curl -s -o /dev/null -w "HTTP %{http_code} (%{time_total}s)\n" --max-time 10 <backend>/api/version
#    000 = unreachable → connectivity problem. Everything below is unanswerable.

# 2. Is the plugin route mounted?
curl -s -o /dev/null -w "%{http_code}\n" <backend>/api/plugins/<id>/<route>
#    404 = gateway needs restart, or wrong port

# 3. Is the plugin's UI asset resolvable?
#    Web: the dashboard entry the manifest declares, e.g. dashboard/dist/index.js
#    Desktop: the linked desktop-plugins/<id>/plugin.js
```

Only after steps 1–3 pass is "the tab/widget is live" a defensible claim.

## Find the browser's backend

Don't ask the user if it's recoverable:

1. **URL bar** — the window's address bar shows the host directly.
2. **Gateway log history** — search for the URL the user has pasted into chat;
   it frequently appears in message bodies.
   ```bash
   grep -iE "lives on|http://[0-9]+\.[0-9]+" ~/.hermes/logs/gateway.log | tail -5
   ```
3. **Local listener check** — if the expected local port has no listener, a local
   backend isn't running and the browser must be remote.
   ```bash
   lsof -iTCP:8000 -sTCP:LISTEN   # nothing → no local dashboard
   ```
4. **Probe it** — a remote backend that times out on `/`, `/api/version`, and
   `/api/health` three times each is down or network-blocked, and no plugin
   state change fixes that. Surface it as an infra issue rather than a plugin
   one.

## Pitfalls

- **Don't trust `hermes plugins list` status as liveness.** "enabled" is a
  config read, not a process probe. Status reflects the file, not the runtime.
- **Don't probe the webhook port for dashboard routes.** Different listeners,
different route tables. A `404` there is not evidence the plugin failed to
  load.
- **Don't assume `install` enabled it.** `hermes plugins install` may leave a
  plugin disabled, and it never touches the desktop runtime. Install and enable
  are separate, and desktop needs a third step.
- **Don't hand-edit `config.yaml` to enable a plugin.** Use `hermes plugins
  enable` — a stray indent can corrupt the file and break the live gateway.
- **Don't install a desktop plugin half into a browser surface.** The Electron
  runtime is the only thing that loads `desktop/plugin.js`. A PWA shortcut will
  never render it, and no config change will make it.
- **Don't diagnose widget data failures before checking backend reachability.**
  "Widgets say offline" with an unreachable backend is a connectivity problem,
  not a plugin bug. Fix the backend first.
- **Don't promise live delivery or visibility you haven't probed.** "The Home
  tab will appear on refresh" is a claim about a UI you cannot render here.
  State what you verified and what you couldn't reach.
