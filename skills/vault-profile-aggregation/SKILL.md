---
name: vault-profile-aggregation
description: Build a personal profile from a vault when none exists yet.
version: 1.0.0
author: Hermes Agent (autonomous curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, vault, profile, bio, personal-knowledge-base, note-synthesis]
    related_skills: [obsidian]
---

# Vault Profile Aggregation

Use this skill when the user asks to create or update a personal profile, bio, or "about me" note sourced from their vault (Obsidian or any markdown-based personal knowledge base), and either no such note exists or the existing one is stale, thin, or scattered across several notes.

This skill covers the REASONING and SYNTHESIS, not the file mechanics. The file mechanics (read, search, write, patch, wikilinks) are handled by the `obsidian` skill for Obsidian vaults, or by ordinary file tools for any other markdown vault. This skill tells you WHAT to gather, in what order, what to synthesize, and what conventions to respect.

## Trigger

- User says: "update my profile," "refresh my bio," "write a profile about me," "create an about-me note," "update my personal profile," or a close variant.
- The vault has no obvious dedicated profile note, OR an existing profile note is stale/incomplete.

## When NOT to use this skill

- The user points at a SPECIFIC existing profile note and says "update this." Use ordinary file tools / the `obsidian` skill to read and patch that note directly — no aggregation needed.
- The user asks for a profile OUTSIDE a vault context (e.g. a LinkedIn bio, a speaker bio for a conference) with no vault to source from. This skill is about vault-sourced synthesis.
- The request is for someone else's profile (e.g. "write a bio for my client"). The vault aggregation pattern assumes the vault belongs to the person being profiled.

## Source priority — gather in this order

Stop gathering when the picture is clear enough to write; the full list is the ceiling, not the minimum.

1. **Vault root system file.** The vault's root guide (commonly `CLAUDE.md`, `README.md`, or a vault-guide file at the vault root). Highest signal-to-noise: usually carries the user's stated identity, email, the vault's purpose, and any working agreement. Read this first.
2. **Folder-level guide files.** Major folders often have their own guide file (e.g. `01 - Notes/CLAUDE.md`, `02 - Categories/CLAUDE.md`, `05 - Periodic Notes/CLAUDE.md`, `06 - Tasks/CLAUDE.md`, `00 - Inbox/CLAUDE.md`). Read the ones relevant to the user's stated focus. These encode the conventions you must follow when writing the profile.
3. **Active quarterly / periodic goals.** The current quarterly note (e.g. `05 - Periodic Notes/Quarterly/YYYY-QN.md`) is the best single source for "what am I building toward right now."
4. **A recent daily note with real content.** The most recent daily note that has actual entries (not an empty template) shows working rituals, current priorities, habits, and what the day looks like. Useful for the "how I work" section.
5. **Reading list / book notes.** Scan the notes folder for book notes. Books read, rated, and annotated are strong signal of intellectual terrain, values, and the lenses the user applies. A book table with the user's own one-line reasons is a good profile section.
6. **Category and subject container notes.** Reading the taxonomy hub notes tells you the classification system the user operates inside — useful context for framing, not for the profile's own content.
7. **Inbox and tasks — light touch only.** Glance for current-project signal; do NOT populate the profile from transit-zone files (inbox) or individual operational tasks. The inbox is a "process later" zone; tasks are operations, not identity.

## What to synthesize (typical sections)

A useful vault-sourced profile note usually carries these sections. Not all are required — include what the sources actually support.

- **The short version.** 1–3 sentences: name, email if it appears in the vault, what the user does, what they're building. The elevator pitch.
- **What I do now.** Current projects, business, content, parallel tracks. Source: quarterly goals + recent daily notes + root system file.
- **How I think about [the domain].** The user's stated principles, framings, and values. Source: book annotations, daily-note reflections, any explicit principles/philosophy notes. Use the user's own phrases where they appear verbatim in notes — these are already their voice.
- **What I'm reading / have read.** A table of books with author and a one-line reason drawn from the user's own summary or annotation. Do NOT invent reasons.
- **Interests and lenses.** The subjects/tags the user repeatedly returns to. Source: `subjects:` properties across notes, or the vault's stated subject list.
- **Working style.** How the user operates. Source: daily rituals, task conventions, periodic-note structure, root system file working agreement.
- **Current quarterly focus.** A short list pulled from the active quarterly note. Date-stamp the quarter.
- **Connected notes.** Wikilinks back to the key source notes so the profile is a hub, not a dead end.
- **Updates log.** A short chronological list at the bottom: when the profile was created, when revised, and what changed.

## Vault conventions to respect

These are general vault-convention rules; an Obsidian vault using the `obsidian` skill adds the specific mechanics below.

- **Every note carries YAML frontmatter.** At minimum `categories:`; often also `subjects:`, `type:`, `status:`, `created:`. Follow the vault's own property set, not a different one.
- **Filing a note = adding the right category wikilink.** The profile must have at least one `categories:` wikilink. For a profile/hub note with no dedicated profile category, `[[Permanent Notes]]` is the usual home — unless the vault already has a `[[Profile]]` / `[[About]]` / equivalent category.
- **File location is a vault convention.** File the profile where the vault stores its notes (commonly a flat `Notes/` folder). Do not invent a new top-level folder.
- **Wikilinks, not filesystem paths.** Internal links use the vault's link syntax (e.g. `[[Note Name]]` for Obsidian). Reference notes by their display title, not by absolute path.
- **Strip foreign schemas.** If a source note carries a non-vault YAML schema (clipper output, Notion export, course-note template, etc.), do not propagate that schema into the profile. Rewrite using the vault's own property set. The inbox's own guide file usually states this rule explicitly.
- **Template-author attribution is a vault fact, not a profile detail.** If the vault originated from a template (e.g. "Sovereign Creator OS Lite"), the template author's bio, contacts, and links are NOT the user's. The root guide may mention template provenance as a factual note about the vault — keep it as a vault-fact, separate from the user's profile.
- **Archive by status, not by moving folders.** If the vault's convention is `status: archived` rather than moving to an Archive folder, follow that.

## Pitfalls

- **Gathering from one note only.** A profile built from a single recent book note or a single daily note is thin and may be wrong in the direction that matters. Gather from at least the root system file + the active quarterly goals + the reading list before writing. The root system file is the anchor — if it says who the user is in two lines, start there.
- **Treating the template author as the user.** The vault's root guide may reference the template author by name and link. That is provenance metadata about the vault, not the user. Do not put the template author's email, social handles, or bio into the user's profile.
- **Inventing quotes or reasons.** If a section reads better with a quote, use a phrase that appears verbatim in the user's own notes. Do not fabricate. For the reading list, the "why it landed" line must come from the user's own annotation or summary — if the note has no such line, omit the reason rather than invent one.
- **Promising live sync.** A vault-file-based profile is a markdown note on disk. It does NOT hook into Obsidian plugins (Spaced Repetition, TaskNotes, Bases queries, Periodic Notes), the Obsidian API, or any live-sync mechanism. Say plainly what it is and is not.
- **Writing too much on first pass.** A synthesized profile is a first draft. Keep it factual, sourced, and reviewable. Tell the user what sources you used and invite correction before treating it as canonical.
- **Leaving the root system file out of sync.** If the vault's root guide has an "About Me" or personal-summary block, add a one-line pointer to the new profile note so the root file does not drift from the canonical profile. If that edit is gated (approval, tool-timeout, protected file), surface it to the user rather than retrying silently or skipping it.

## After writing the profile

1. **Wire it into the category hub.** If filed under `[[Permanent Notes]]` (or the vault's equivalent), it will auto-populate in that category's container note via the Bases query (Obsidian) or equivalent mechanism. Verify by reading the container note — the query is the mechanism, not a manual link you add.
2. **Point the root system file at the profile, if it has a personal-summary block.** A one-line pointer keeps the root file from drifting. Patch with stable context from the existing block.
3. **Log the change if the vault keeps a session log.** Follow the vault's own logging convention (e.g. `log.md` at the vault root, newest-first, with what changed and why).
4. **Offer the user a review pass.** State what sources you used; invite corrections.

## If a profile note already exists

- Read it first. Compare its content to the vault's current state (quarterly goals, reading list, current projects).
- Update in place with `patch`, section by section, preserving stable structure. Refresh only the sections that have drifted.
- If the existing note is so thin or stale that a rewrite is clearer than patching, rewrite it in place (same path) and keep the same `categories:` / `type:` so the category hub stays coherent.
