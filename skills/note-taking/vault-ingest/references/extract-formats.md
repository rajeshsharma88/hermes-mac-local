# Extracting Text from Source Formats

Recipes for pulling text out of the formats that show up in an ingest. Write output to the scratch dir and read it back; do not print full bodies into the session.

## PDF

`pypdf` handles text-layer PDFs. Report page count and character count so an empty or image-only extraction is obvious.

```python
from pypdf import PdfReader

r = PdfReader(path)
print("pages", len(r.pages))
txt = "\n".join((pg.extract_text() or "") for pg in r.pages)
print("chars", len(txt))
```

Zero or near-zero characters means the PDF is scanned images. Switch to OCR or a vision pass on rendered pages; do not report an empty extraction as content.

PDF extraction emits repeated running headers and page footers as lines (for example a document title and page number on every page). Leave them in when reading — they mark structure — but strip them when composing wiki pages.

## HTML

Stripping `<script>` and `<style>` first shrinks a page dramatically. Inline CSS in the head and JS payloads usually dominate a single-file export by several times the real prose.

```python
import re

t = open(path, encoding="utf-8", errors="replace").read()
t = re.sub(r"<script.*?</script>", "", t, flags=re.S | re.I)
t = re.sub(r"<style.*?</style>", "", t, flags=re.S | re.I)
txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()
```

Triage a bundle before reading whole bodies. Title, h1 and meta description say whether a file is worth the pass:

```python
ti = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S | re.I)
desc = re.search(r'<meta name="description" content="([^"]*)"', t)
```

Extracted prose loses its layout, so a heading outline and the document tail are often the fastest way to understand an export. Print both ends plus heading matches rather than the middle.

## DOCX and PPTX

Use the `word-analysis` and `ppt-analysis` skills for full extraction. For a quick prose read, `python-docx` paragraphs:

```python
import docx
d = docx.Document(path)
for p in d.paragraphs:
    if p.text.strip():
        print(p.text)
```

Tables need separate iteration — they are not in `paragraphs`.

## Archives

List before extracting. Never unzip into the vault directly.

```bash
unzip -l file.zip | tail -20
unzip -l file.zip | awk '{print $4}' | grep -iE 'key|token|secret|env|config'
```

Read a single member without extracting the archive:

```bash
unzip -p file.zip 'data/photos.mjs' | head -40
```

Check the data-bearing module itself, not just filenames — a neutral filename can wrap sensitive content. Report the archive's size, member count, and whether anything looked sensitive.

## Detecting duplicates

```bash
diff -q a.txt b.txt && echo IDENTICAL
diff a.txt b.txt          # show differences when they exist
```

For size-only triage across a folder:

```bash
wc -c file1 file2
```

Near-duplicates that differ only in formatting still deserve one canonical wiki page, not two.

## Binary files

Do not ingest. Note them in the log with size and skip. If a binary is load-bearing, copy it to `vault/sources/` and describe it on a wiki page instead of reading it.

## Practical note on extraction scripts

Write the extraction as a real file and run it. Embedding a shell heredoc inside a Python f-string fails to parse because the f-string literal breaks on the quote characters. Keep shell-out calls simple, or move multi-step logic into a script file.
