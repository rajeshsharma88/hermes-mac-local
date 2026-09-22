---
name: hermes-model-providers
description: "Use when a model is missing from picker or adding custom."
version: 1.0.0
---

# Hermes Model Providers & Custom Models

How to diagnose why a model is missing from Hermes' model picker and how to register
third-party OpenAI-compatible endpoints (SenseNova, Zhipu/GLM, Kimi, custom base_urls) as
first-class selectable models.

## Why a model doesn't show in `/model` / `hermes model`

The picker lists models only from the **active provider's catalog**, cached in
`~/.hermes/provider_models_cache.json` and `~/.hermes/models_dev_cache.json`. Check the
active `model.provider` in config.yaml first, then confirm the model ID is actually in that
provider's cached list.

- A model you expect but don't find is almost always because it belongs to a **different
  provider than the active one** — not a display bug.
- **Third-party OpenAI-compatible endpoints (own base_url + own API key) are never in any
  catalog** — not OpenRouter's, not anyone else's. OpenRouter does not route them. This is
expected, not an error: they must be registered as a custom alias.

## Registering a custom (non-catalog) model

Do NOT hand-edit `config.yaml` — build the alias with `hermes config set`, which accepts
dotted keys:

```bash
hermes config set model.aliases.<name>.model <model-id>
hermes config set model.aliases.<name>.provider custom
hermes config set model.aliases.<name>.base_url https://<endpoint>/v1
hermes config set model.aliases.<name>.key_env <UPPER_API_KEY_ENV_VAR>
```

Then select it with `/model <name>` (session) or `/model <name> --global` (persist as
default). Verify it landed:

```bash
python3 -c "import yaml;c=yaml.safe_load(open('~/.hermes/config.yaml'));print(yaml.safe_dump(c['model'],sort_keys=False))"
```

## Pitfalls

- **The API key is the user's job, never yours.** The alias's `key_env` var (e.g.
  `SENSENOVA_API_KEY`) must exist in `~/.hermes/.env` or every call 401s. Never accept a key
  in chat; put the alias in place first, then have the user add the key to `.env` themselves
  and confirm which base URL (.com vs .cn / regional) their account uses before wiring it.
- **Probe the custom base_url for provider-specific request strictness.** Some gateways
  (SenseNova 6.x) reject any request field outside their documented params table — notably
  `response_format`, `thinking`, and schema-level extras — returning vague errors instead of
  pointing at the culprit. Keep such providers on plain `chat_completions` and strip exotic
  request params. Some also need an explicit vendor param (SenseNova wants `watermark=false`).
- **Keep `/v1` in the base_url** — dropping it breaks the OpenAI-compatible path.

## Reading picker error strings

- **"{label} didn't answer after {N} attempts"** is a **health-probe failure**, not a crash.
  When a model/provider option is selected, Hermes sends a one-line test request and retries
  N times (default 3); no response after all retries = no working credential/auth behind that
  route. Diagnosis: check that provider's auth/key, not the core.
- **Anthropic "Claude Subscription" OAuth/DirectSDK options are a known trap** — Claude Pro
  subscribers cannot use the subscription OAuth path ("Pro looks like it should work; it
doesn't") and Claude-subscription auth is not a supported Hermes provider route. If a user
wants Claude in Hermes, point them at a real `ANTHROPIC_API_KEY` (pay-per-token) instead.
