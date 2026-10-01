---
name: vault-ingest
description: Use when ingesting raw material into the Obsidian vault.
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Notes, Markdown, Vault, Ingest]
    related_skills: [obsidian, pdf-analysis, word-analysis]
---

# Vault Ingest

Process a body of raw source material — a folder, PDF bundle, HTML export, or archive — into the vault's wiki layer. This is the `/ingest` command. Governed by the repo's Vault Protocol: three layers, sources immutable, one topic per page, wikilinks between pages, index and log maintained on every ingest.

Companion to the `obsidian` skill, which covers the low-level file operations. This skill is the ingest workflow itself.

## Layers

1. **Raw sources** — `vault/sources/`. Immutable. Copied in, never edited or deleted.
2. **The wiki** — everything else in `vault/`. Owned and maintained by the agent: create, update, cross-reference, keep consistent.
3. **The schema** — the repo's CLAUDE.md plus `soul.md`. Defines structure.

Wiki page locations:

| Content | Path |
|---|---|
| Something about the user | `vault/me/` |
| A person | `vault/people/{name}.md` |
| Business info, competitor moves | `vault/business/` |
| Project status | `vault/projects/{name}/status.md` (Tier 1), dense data in subfolders (Tier 2) |
| Decisions or preferences | `vault/me/preferences.md` or `vault/me/goals.md` |
| A meeting or call | `vault/meetings/` |
| Research or analysis | `vault/research/` |

Tier 1 status pages carry YAML frontmatter: `tags`, `date_created`, `date_updated`, `sources`, and `status` where applicable.

## Procedure

### 1. Survey before reading

List the folder first, then extract by type. Do not read everything into context at once — large HTML and PDF bodies will flood the turn.

```bash
find <folder> -maxdepth 4 -not -path '*/.DS_Store'
du -sh <folder>/*
```

Group files by format, note sizes, and flag archives and binaries. Extraction recipes per format are in `references/extract-formats.md`.

### 2. Extract text from each format

PDF, HTML, DOCX and archive contents each need a different path. Write extraction to files under the scratch dir and read the output back rather than printing full bodies into the session.

For triage of a large HTML bundle, extract `<title>`, `<h1>`, and `<meta name="description">` first. That decides whether the file is worth a full pass before spending context on it.

### 3. Deduplicate before ingesting

```bash
diff -q a.txt b.txt && echo IDENTICAL
```

Drop byte-identical duplicates and never ingest both. Browser and download artefacts routinely produce `name (1).ext` copies of the same file.

### 4. Check archives for secrets before including them

Archives are the highest-risk ingest input. List contents and scan filenames for credential patterns before copying anything into the vault:

```bash
unzip -l file.zip | awk '{print $4}' | grep -iE 'key|token|secret|env|config'
```

Then inspect any data-bearing module rather than trusting filenames alone. Skip the archive if it holds credentials, and say so.

### 5. Judge whether content is about the user

Do not ingest template, example, or worked-example content into `vault/me/` profile pages. A persona brief or onboarding sample describing a third party is *material about that person or a template for a task*, not a fact about the owner. When in doubt, create a `vault/people/` page for the person it actually describes and link it from the relevant research page.

### 6. Copy sources to the read-only layer

Copy the whole set into `vault/sources/<descriptive-name>/`, preserving relative structure. Keep originals on disk untouched. Rename colliding filenames on the way in (e.g. two `index.html` files from different contexts) so nothing overwrites silently.

### 7. Create and update wiki pages

One page per topic, with YAML frontmatter:

```yaml
---
tags: [...]
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
sources: [<relative source paths>]
---
```

Use `[[wiki links]]` to every related page, including the sources' own wiki counterparts. Link new pages to existing project and business pages rather than leaving them orphaned — a source about infrastructure the owner runs belongs on that project's status page.

Record licence or redistribution constraints found in the material on the page that carries it. A constraint only discoverable in the raw source is useless.

### 8. Update index and log

- `vault/index.md` — one line per new or changed page under the right section. Read it first; sections are commented.
- `vault/log.md` — append-only, format `## [YYYY-MM-DD HH:MM] command | description`. Record what was ingested, how many pages touched, source count and size, duplicates dropped, and any secret check performed.

### 9. Post-run ingestion (mandatory)

Before reporting results: create a `vault/people/` page for every new person found, a `vault/business/` page for every new company, and update `vault/projects/` for any status change.

### 10. Report and do not commit

Summarise new pages, updated pages, what was dropped, what was verified, and any judgement call taken on the owner's behalf instead of asking. Flag judgement calls explicitly — they are reviewable decisions.

Do not `git commit`. Report that changes are uncommitted and that an archive inflates the commit, then let the owner decide.

## Pitfalls

- **Never modify `vault/sources/`.** Read only. Corrections to source facts go in wiki pages, with the source path cited.
- **Byte-identical duplicates waste pages and contradict each other later.** Check with `diff -q` before ingesting.
- **A persona or onboarding template describes someone else.** Verifying whether the subject is the owner is a reading step, not an assumption.
- **Archives can carry credentials.** Check filenames and inspect data modules before copying an archive into the vault.
- **Colliding filenames overwrite silently when copied.** Rename on the way into `vault/sources/`.
- **Large binaries bloat git history.** Report size and ask rather than committing, and note whether the repo has LFS available.
- **A source containing a licence constraint must surface that constraint on the wiki page.** Discoverable only in the raw file, it is not a real constraint.
- **Write HTML and PDF extraction to a scratch file and read it back.** Printing full extracted bodies into the session floods the turn and the content is recoverable later from the file.
- **Heredocs nested inside f-strings break.** Write the extraction script with `write_file` and run it, rather than embedding shell in a Python f-string.

## Reference

- `references/extract-formats.md` — extraction recipes for PDF, HTML, DOCX, archives, plus dedup and secret-check commands
