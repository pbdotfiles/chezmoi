# Stage 2: Per-Document Conversion (Subagent Instructions)

You are converting one batch of extracted documents into clean, searchable Markdown files under `<OUTPUT_DIR>/docs/`.

## Read First (Before Opening Any Images)

1. `<SKILL>/references/format.md` (exact output structure, frontmatter, figure blocks, anchors, faithfulness rules).
2. `<SKILL>/references/types.md` (recipes per semantic document type).
3. `<OUTPUT_DIR>/.ingest/overview.md` (corpus context, metadata language, candidate acronyms/terms).
4. If earlier waves have already written files in `<OUTPUT_DIR>/docs/`, you may skim relevant earlier `.md` files (text only!) when you need to understand a project codename, acronym, or reference. Never open images from other documents.

## Image & Session Discipline (Critical)

- **Write each document file to `<OUTPUT_DIR>/docs/<slug>.md` as soon as you finish it**, before moving to the next document in your batch. OpenCode drops older images from context — anything not written to disk is lost.
- **Never reopen an image you already saw.**
- **Only view images that add information:**
  - Read `<OUTPUT_DIR>/.ingest/extract/<slug>/meta.json` and `text.md` first.
  - Pages with `vision: "no"` and clean text do **not** need to be opened.
  - Prefer `figures/` crops over full `pages/` renders when the surrounding text extracted cleanly.
  - For simple slide decks, open `sheets/sheet-*.png` contact sheets for overview rather than opening every slide individually.
  - Open full `pages/` renders whenever `no_text_layer`, `garbled_text`, `chart_no_cached_data`, `smartart`, `diagram`, `full_page_image`, `table` (if messy), or `tall_image` is flagged, or when visual layout is essential.
- Stay comfortably within your image budget (target ≤ 40 images per session; requests fail beyond 64). If you approach ~35 images and still have documents left, stop cleanly after finishing the current file and list the remaining slugs in your final report so the orchestrator can continue in a fresh session.

## Converting Each Document

For each assigned `<slug>` (and optional page/part range if doing a sequential handoff on a large document):

1. Inspect `.ingest/extract/<slug>/meta.json` and `.ingest/extract/<slug>/text.md`.
2. Decide the semantic `type` (`slides`, `report`, `document`, `notes`, `spreadsheet`, `data`, `figure`, `conversation`, `email`, `other`) and `language`.
3. Open only the needed images from `.ingest/extract/<slug>/` (`pages/`, `figures/`, `media/`, `sheets/`).
4. Copy meaningful, non-decorative visuals you want in the knowledge base to `<OUTPUT_DIR>/assets/<slug>/` with clean descriptive filenames (using `cp` in shell). Link them from `docs/<slug>.md` and write a full, searchable text description directly underneath each image link (values, axes, deltas, labels, component flows, takeaways).
5. Preserve `<!-- p.N -->` / `<!-- part: ... -->` anchors and re-anchor real footnotes (`[^1]`).
6. Keep the document body **strictly faithful** to this source document:
   - Never alter numbers, claims, or terminology using knowledge from other documents.
   - Mark unreadable text as `[illegible]`, pixel-estimated chart values as `~val (read from chart)`, and doubtful readings as `[uncertain: ...]`.
   - Record cross-document connections you notice in `## Context` at the end of the file (and `related:` / `supersedes:` in frontmatter), clearly separated from the document body.
7. Write `<OUTPUT_DIR>/docs/<slug>.md` (with `sha256` and `source` copied verbatim from `meta.json`).

### Sequential Handoff Mode (for a Very Large Document)

If the orchestrator assigned you a **page/chapter slice** of a large document:
- **Part 1:** write frontmatter + content for your assigned range, plus a `<!-- handoff: ... -->` comment at the bottom noting where you stopped and any key terms/open threads.
- **Part N (continuation):** first read the existing `<OUTPUT_DIR>/docs/<slug>.md` (text only) to see the handoff note and style, then append your assigned slice cleanly to the same file (or write `docs/<slug>/part-NN.md` and update `docs/<slug>/index.md` if the orchestrator specified split-file mode). Update `uncertainty` in frontmatter if needed, and remove temporary `<!-- handoff: ... -->` comments once the final slice completes.

## Final Report

Return a concise report listing:
1. Documents converted (`slug`, `type`, `date`, output file path(s)).
2. Assets copied to `assets/<slug>/` (and any pages/figures intentionally skipped as decorative).
3. Number of images opened in this session.
4. Any uncertainties, unrecoverable losses (e.g., `formula_no_value`, `media`, `unreadable_image`), or remaining documents if you stopped early.
