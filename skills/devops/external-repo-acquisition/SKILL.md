---
name: external-repo-acquisition
description: Clone an LFS repo via tarball; copy skill dirs intact.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, lfs, clone, tarball, cp, skills, install, recovery]
    related_skills: [hermes-agent]
---

# External Repo Acquisition

Fetch a repo when a normal `git clone` cannot complete checkout, then place its contents
as intact directories. Use before bulk-copying external skill bundles into
`~/.hermes/skills/`.

## When to Use

- `git clone` prints `git-lfs filter-process: git-lfs: command not found` and ends in
  `Clone succeeded, but checkout failed`, or
- copying a tree of per-item directories into a managed install dir.

## Procedure

### 1. When checkout is blocked by LFS, fetch the tarball

`.gitattributes` declaring `filter=lfs` makes checkout invoke git-lfs, which is absent on many
hosts. Do not fight the filter — bypass git entirely:

```bash
curl -sL -o out.tgz https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/main
tar xzf out.tgz   # extracts to <repo>-<branch>/
```

The codeload archive holds plain blobs and needs no git-lfs, so LFS pointer stubs never appear.
`--filter=blob:none` makes this worse, not better: it forces lazy blob fetches that also fail.

If git-lfs is genuinely needed, install it rather than recording "git clone does not work":

```bash
brew install git-lfs && git lfs install
```

### 2. Copy as intact directories

`/bin/cp` is BSD on macOS. `cp -R <src>/` (trailing slash) copies the source's **contents**,
not the directory itself, so the target never contains the folder name.

```bash
cp -R src/subdir/ dest/    # WRONG on BSD: flattens subdir/* into dest/
cp -R src/subdir   dest/   # correct: creates dest/subdir
```

This is silent — rc is 0 and no error is printed. Verify every time:

```bash
test -d dest/subdir || echo 'FLATTENED: subdir was not created as a directory'
```

For a whole tree of items, use Python — no glob, no quoting ambiguity:

```python
import shutil, pathlib
for src in sorted(pathlib.Path('src').iterdir()):
    if src.is_dir():
        shutil.copytree(src, pathlib.Path('dest') / src.name)
```

### 3. Verify parity

File count and file-set equality against the source, plus one `SKILL.md` per installed dir
(adjust the per-item marker to the content type):

```python
import pathlib
SRC = pathlib.Path('src'); DST = pathlib.Path('dest')
for src in sorted(p for p in SRC.iterdir() if p.is_dir()):
    sf = {str(x.relative_to(src)) for x in src.rglob('*') if x.is_file()}
    df = {str(x.relative_to(DST / src.name)) for x in (DST / src.name).rglob('*') if x.is_file()}
    assert sf == df, f'{src.name}: {len(sf)} vs {len(df)} files'
```

### 4. After the bulk copy

Confirm the target's pre-existing managed content survived: nothing bundled or user-installed
should have changed, and no stray files should sit at the target root.

## Pitfalls

- **The check must assert the destination DIRECTORY exists, not the copy exit code.**
  `cp -R "$d" dest/` from a glob ends in a trailing slash and returns 0 while flattening every
  item, so a `[ -d "$DST/$name" ]` guard reports failure while the junk is already written.
  Assert the resulting structure, not the rc.
- **Quarantine before deleting.** On damage, `mv` the suspect entries to scratch first, then
  diff them against the quarantine. Never `rm` straight from a managed skills dir.
- **A changed mtime is not proof of overwriting.** Only an entry that is absent from the
  manifest (or an unbundled dir that exists at the target root) is actually lost data. Confirm
  provenance — that every junk entry also exists verbatim under a correctly installed item —
  before treating it as pure redundancy.
- **Unmanaged bulk copies are invisible to the toolchain.** Files placed into
  `~/.hermes/skills/` that never entered `.bundled_manifest` are not updated or repaired by
  `hermes update`, and `hermes skills list` may not show them. Prefer `hermes skills install`
  for anything the toolchain should manage; note manual provenance for the rest.
