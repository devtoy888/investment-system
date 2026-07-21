---
name: pdf-batch-ingestion
description: "Batch ingest PDFs (single, ZIP, 100+ pages) into LLM Wiki: extract text, split by chapter, archive originals to R2, cross-link sections."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pdf, ingestion, wiki, document-processing, batch]
    category: research
    related_skills: [llm-wiki, ocr-and-documents]
---

# PDF Batch Ingestion into LLM Wiki

Workflow for processing local PDF files (including ZIP archives and 100+ page
documents) into an LLM Wiki. Designed to integrate with `llm-wiki` skill's
Core Operations → 1. Ingest.

## When This Skill Activates

Use when the user:
- Sends or provides PDF files they want ingested into their wiki
- Provides a ZIP archive containing multiple PDFs
- Asks about processing long documents (standards, regulations, theses)
- Wants to test the full PDF-to-wiki pipeline

## Prerequisites

- `llm-wiki` skill loaded (for wiki structure conventions)
- `ocr-and-documents` skill loaded (or pymupdf installed locally)
- Cloud storage (R2/S3) upload script available for archiving originals
- `unzip` available (for ZIP archives)

## Workflow

### 1. Receive files

| Input | Action |
|-------|--------|
| Single .pdf | Extract text, decide if chapter-splitting needed |
| .zip containing PDFs | `unzip` to temp dir, then process each PDF |
| Multiple separate .pdf | Process each, but batch the ingest for efficiency |

### 2. Extract text

Use `ocr-and-documents` skill for the extraction method:

```bash
# Text-based PDF (pymupdf, instant)
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

| PDF type | Tool | Speed |
|----------|------|-------|
| Text-based (most gov/standards docs) | pymupdf | Instant |
| Scanned / equations / complex layout | marker-pdf | ~1-14s/page |

### 3. Archive original

Always upload the original PDF to cloud storage before creating pages:

```bash
python3 wiki_upload.py document.pdf --key wiki-media/pdfs/YYYY-MM/document.pdf
# Returns URL like: https://cdn.example.com/wiki-media/pdfs/2026-07/document.pdf
```

This URL goes into each wiki page's `sources:` frontmatter as `r2_url:`.

### 4. Assess document size

| Size | Strategy |
|------|----------|
| <30 pages | Single wiki page |
| 30-100 pages | 2-4 section pages |
| 100+ pages | Chapter-aware split (step 5) |

### 5. Chapter splitting (100+ page PDFs)

For long documents, do NOT create a single massive page. Instead:

1. Extract the full text
2. Detect section boundaries (see detection table below)
3. Split at each boundary
4. Create one wiki page per section
5. Create an overview page linking all sections

**Section boundary detection:**

| Document type | Patterns to scan for |
|--------------|---------------------|
| Chinese standards (GB/T,等保) | `第N章`, `第N部分`, `## N.` |
| English papers | `## Introduction`, `## Related Work`, `Chapter N` |
| Legal/regulatory | `第N条`, `Article N`, roman numerals |
| General fallback | Page-number jumps, blank-page separators, TOC |

### 6. Page creation format

Each section page:

```markdown
---
title: Exact Section Title (From Document Name)
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept
tags: [tag1, tag2]
sources: [raw/papers/document-name.md]
r2_url: https://cdn.example.com/wiki-media/pdfs/YYYY-MM/original.pdf
---

# Exact Section Title

Extracted content...

See also: [[sibling-section-a]], [[sibling-section-b]]
```

Overview/index page for the document:

```markdown
---
title: Document Name — Overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: summary
tags: [tag1, tag2]
sources: [raw/papers/document-name.md]
r2_url: https://cdn.example.com/wiki-media/pdfs/YYYY-MM/original.pdf
---

# Document Name

[1-2 sentence summary of the document]

## Sections

- [[section-1]] — description
- [[section-2]] — description
...
```

### 7. Update navigation

- Add each section + overview page to `index.md` under the correct section
- The overview page is the primary entry; list sections as sub-bullets
- Append batch entry to `log.md`:
  `## [YYYY-MM-DD] ingest | Document Name (N sections)`
- Cross-check: every section page has ≥2 outbound [[wikilinks]]

## Pitfalls

- **Always archive the original PDF** before creating pages — text extraction
  may miss tables, diagrams, or formatting. The original is your source of truth.
- **Do NOT create 2000-line pages** from 100+ page PDFs. Split by chapter.
- **Check for embedded images** — pymupdf can extract them via
  `page.get_images()`. Upload relevant ones to R2 and embed in wiki pages.
- **Verify TOC structure** — some PDFs have a proper table of contents that's
  faster to parse than guessing section boundaries from headers.
- **Consistent frontmatter** — all pages from one batch share `created:` date
  and `r2_url:`. Set them together.
- **Use raw/ frontmatter** — save extracted text to `raw/papers/` with its own
  frontmatter (ingested date, sha256, r2_url). This is the source of truth for
  future re-ingests.
