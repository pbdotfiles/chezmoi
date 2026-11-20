# Document Type Recipes

`extract.py` detects the technical file format (PDF, pptx, docx, xlsx, image, email, text). You decide the **semantic `type`** from the content and choose the structure that preserves the most signal.

## 1. `slides` (Google Slides, PowerPoint, slide-like PDFs)

- Go **slide by slide** using `<!-- p.N -->` and `### Slide N: <title>` (mark hidden slides as `(hidden)`).
- Keep bullet hierarchy and exact phrasing where technical.
- Include **Speaker notes** cleanly under each slide (`**Speaker notes:** ...`) — they often hold the real rationale that is missing from the slides themselves.
- Include **Slide comments** if present.
- **Charts:** prefer the exact series tables extracted from `.pptx` XML (`chart_data`) over pixel estimates; still check the slide render to verify units, annotations, callout boxes, or trendlines drawn on top. If `chart_no_cached_data`, read values from the image and mark `~value (read from chart)`.
- **Diagrams / SmartArt:** `extract.py` flags `smartart` / `diagram` when shapes and connectors carry meaning. Copy the slide render to `assets/<slug>/` and describe the topology, arrows, and boxes in text.
- **Simple text slides:** when `sheets/` has contact sheets and a slide has no visual flags, reading the contact sheet (or verifying extracted text against it) saves image budget.

## 2. `report` / `document` (PDF reports, papers, Google Docs, `.docx`)

- Preserve the document's **heading hierarchy** (`#`, `##`, `###`) and **page anchors** (`<!-- p.N -->`).
- Clean up PDF extraction artefacts: broken line wraps inside paragraphs, hyphenated line-end words, repeated running headers/footers, and standalone page numbers.
- Re-anchor real **footnotes** (`[^1]`) rather than leaving them mid-paragraph.
- **Tables:** `extract.py` runs `find_tables()` and puts both raw text and an auto-detected Markdown table in `text.md`. Verify tables against the page render when `table` is flagged, especially for merged cells, multi-page tables, or misread columns, and keep only the single clean Markdown table.
- **Equations:** if `garbled_text` or math symbols got mangled in text extraction, read the page render and transcribe equations into clean LaTeX (`$...$` / `$$...$$`).
- **Tracked changes & comments (`.docx`):** pandoc outputs `.insertion`, `.deletion`, and `.comment-start` spans. Resolve clean prose by keeping accepted/current text (or showing meaningful proposed alternatives + who commented in a brief note or blockquote) so the disagreement/rationale is preserved without leaving raw pandoc bracket soup.
- **Scanned pages (`no_text_layer`):** transcribe faithfully from the page image; do not invent unclear numbers (`[illegible]` / `[uncertain: ...]`).

## 3. `notes` (meeting notes, scratchpads, unstructured Markdown/text)

- Lightly clean formatting while keeping dates, attendees, decisions, action items, owners, and open questions clearly structured.
- Keep raw technical snippets, commands, metrics, or quotes verbatim.

## 4. `spreadsheet` / `data` (`.xlsx`, `.csv`, `.tsv`)

- Summarize what the workbook/file contains (purpose, tabs, time range, key metrics/takeaways).
- Keep clean Markdown tables for small/medium sheets. For large sheets (`truncated_table`), summarize structure, columns, key aggregates/extremes, and point to the raw CSV in `.ingest/extract/<slug>/data/` or the original source rather than bloating the Markdown with thousands of rows.
- Preserve **hidden sheets**, **hidden rows/columns** (explicitly marked), **formula insights** (what drives key cells, especially if `formula_no_value` is flagged), **cell comments**, and **embedded chart data** (`xl/charts/`).
- If `conditional_formatting` is flagged and a paired PDF/screenshot exists, inspect it to capture what colour coding signifies (e.g., red = SLA breach).

## 5. `figure` (standalone image, plot, architecture diagram, whiteboard photo)

- Copy the image to `assets/<slug>/`, link it, and write a comprehensive structured text description covering every label, axis, number, connection, legend, and takeaway.
- Include brief metadata on provenance/context if apparent from the image or filename.

## 6. `conversation` / `email` (`.eml`, `.mbox`, exported chats, `+folder` screenshot sets)

Start with a **distilled header section** followed by a **cleaned transcript**:

1. **Top distillation:**
   - Participants & roles (when known)
   - Time span covered
   - **Key decisions**, **action items** (owner + due date if given), **open questions**, and **technical facts/numbers stated**, each attributed (`[Alice, 14:22]`).
2. **Cleaned transcript:**
   - Keep full chronological messages with attribution (`**Alice** (2026-03-12 14:22): ...`) so nuance is not lost.
   - **Quoted email history (`quoted_history`):** deduplicate repeated reply chains so each message appears once in chronological order.
   - **Overlapping screenshots / tall-image tiles (`+folder/` or `tall_image`):** stitch messages across screenshots/tiles in chronological order, **deduplicating messages repeated in the overlap**. Note which source screenshot/tile (`<!-- part: screen-01.png -->`) each segment came from.
   - Note inline images or attachments (attachments are also converted as their own linked documents).

## 7. `other` (anything that doesn't fit above)

- Choose the clearest Markdown structure for the material, explain any format limitations in `uncertainty`, and stay faithful to what could be read.
