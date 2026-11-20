# Output Format Specification

All converted knowledge-base files live under `<OUTPUT_DIR>/`.

## Directory Layout

```text
<OUTPUT_DIR>/
  MANIFEST.md              index of every document (date, type, status, summary, topics)
  GLOSSARY.md              acronyms, codenames, project/system names, key people
  TIMELINE.md              chronological view of milestones, decisions, results
  docs/
    <slug>.md              converted document (one file per document by default)
    <slug>/                only if a huge document was split for readability:
      index.md             frontmatter + overview + links to part-*.md
      part-01.md
  assets/
    <slug>/                clean extracted figures, diagrams, screenshots, charts
  .ingest/                 working directory managed by scripts (state, extracts, reports)
```

## YAML Frontmatter

Every `docs/<slug>.md` (or `docs/<slug>/index.md` when split) starts with YAML frontmatter. Keys are always English. Values (`summary`, `tags`, etc.) follow the corpus metadata language chosen in Stage 1 (`en` by default, or the shared corpus language if every document uses the same non-English language).

```yaml
---
source:
  - "2026-03-14_q1-review.pptx"
  - "2026-03-14_q1-review.pdf"
sha256: "<64-char sha256 from meta.json>"
date: "2026-03-14"            # YYYY-MM-DD, YYYY-MM, YYYY, or unknown
date_source: filename         # filename | metadata | content | path | mtime | none
date_confidence: high         # high | medium | low
period: "2026-Q1"             # optional: time span the content covers
type: slides                  # slides | report | document | notes | spreadsheet | data | figure | conversation | email | other
language: en                  # ISO 639-1 code of the document body (e.g. en, fr, de)
authors: ["Alice", "Bob"]     # optional
summary: "One-to-three sentence factual summary of the document."
tags: [q1-review, latency, architecture]
related: []                   # optional: slugs of related docs (filled in Context/Stage 3)
supersedes: []                # optional: slugs of older docs this replaces
superseded_by: []             # optional: filled by Stage 3 synthesis
uncertainty: []               # optional: short notes on gaps, low-confidence dates, illegible parts
---
```

Rules:
- Copy `source` and `sha256` verbatim from `.ingest/extract/<slug>/meta.json`. Never alter `sha256` — incremental re-runs depend on it.
- Keep the **body** in the document's original language (`language`). Only frontmatter values (`summary`, `tags`, `uncertainty`) and the synthesis files use the metadata language.
- If the content reveals a clearly better date than `meta.json` (for example, `meta.json` only had `mtime` or a Google export timestamp, while slide 1 says "Review — 14 March 2026"), use the content date and set `date_source: content` with appropriate `date_confidence` (`high` or `medium`).

## Anchors & Footnotes

- **Page / slide anchors:** preserve `<!-- p.N -->` before each page or slide in multi-page PDFs, presentations, and paired documents. This lets downstream readers cite exact pages (`p.12`).
- **Part anchors:** for `+folder/` multi-file documents, preserve `<!-- part: <filename> -->` before each part.
- **Footnotes:** do not discard real footnotes when removing running headers/footers. Re-anchor them with standard Markdown footnotes (`[^1]`).

## Figures, Charts, and Diagrams

When a page or document carries a meaningful visual (chart, plot, architecture diagram, technical drawing, screenshot, or informative photo):

1. Copy the cleanest available image (from `.ingest/extract/<slug>/figures/`, `media/`, or `pages/`) into `<OUTPUT_DIR>/assets/<slug>/` with a descriptive filename (e.g., `p04-latency-chart.png`, `slide03-arch.png`).
2. Link it in the Markdown body using a relative path:
   - Single-file doc (`docs/<slug>.md`): `![Latency p99 across regions](../assets/<slug>/p04-latency-chart.png)`
   - Split doc (`docs/<slug>/part-01.md`): `![...](../../assets/<slug>/p04-latency-chart.png)`
3. Directly underneath the image link, write a thorough text description so a downstream agent can search and cite every fact without opening the image:
   - **Charts / plots:** chart type, title, axis labels and units, legend/series, baseline, exact numbers/deltas (if read from `.pptx`/`.xlsx` XML, state them directly; if estimated from pixels, prefix with `~` and mark `(read from chart)`), trends, and takeaways.
   - **Diagrams / architecture:** component names, groupings, data/control flows, arrow directions and labels, protocols/formats, and key takeaways.
   - **Tables rendered as images:** transcribe into a Markdown table; mark any hard-to-read cell with `[uncertain: ...]` or `[illegible]`.
4. **Skip decorative visuals** (company logos, slide background motifs, decorative icons, divider lines). If a page was flagged `figure` only because of decorative elements, note `<!-- figure skipped: decorative logo/background -->` so validation knows it was checked.

## Faithfulness vs. Cross-Document Context

Keep faithful document transcription strictly separate from cross-document interpretation:

- **Body:** faithful only to this source document. Keep its numbers, claims, terminology, and gaps intact. Do **not** silently "correct" an old figure using a newer document, and do **not** invent missing text from memory or other files. You may expand an acronym in brackets once if helpful (e.g., `HBM [High Bandwidth Memory]`).
- **Uncertainty markers:** mark unreadable spans as `[illegible]`, approximate chart readings as `~42 (read from chart)`, and doubtful readings as `[uncertain: value]`.
- **`## Context` (at the end of the file):** record observations connecting this document to others you know about from the corpus overview or earlier converted docs (e.g., *"Continues the discussion in `2026-03-01-design-chat`"*, *"Throughput target updated here from 120 to 180 req/s compared to `2026-01-proposal`"*). Stage 3 uses this section to build `GLOSSARY.md`, `TIMELINE.md`, and `superseded_by` links.
