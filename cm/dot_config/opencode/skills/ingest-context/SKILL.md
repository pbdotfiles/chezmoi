---
name: ingest-context
description: Convert a mixed folder of raw documents (PDFs, slides, Word docs, spreadsheets, images, conversation dumps/screenshots, emails) into a clean, searchable Markdown knowledge base with extracted figures and cross-document synthesis. Load on explicit request.
compatibility: opencode
metadata:
  opencode/autoinvoke: false
---

# Ingest Context: Orchestrator

You are the orchestrator. Your goal is to transform everything in `INPUT_DIR` into a clean, faithful, searchable Markdown knowledge base in `OUTPUT_DIR` so downstream readers or agents can work solely from `OUTPUT_DIR` without touching the raw files.

**Never modify, rename, or delete anything inside `INPUT_DIR`.** Never install packages yourself.

## Defaults & Conventions

- **`INPUT_DIR`:** `raw_context/` (unless overridden by the user)
- **`OUTPUT_DIR`:** `parsed_context/` (unless overridden by the user)
- **Multi-file documents (`+` prefix):** any subfolder whose name starts with `+` (e.g., `+2026-03-12_design-chat/` containing 4 conversation screenshots) is treated as **one document** by `extract.py`. All other subfolders are purely organisational.
- **Paired exports:** an Office file and a PDF with the same base name in the same folder (e.g., `q1-review.pptx` + `q1-review.pdf`, with or without a date in the name) are paired into one document (text/notes/chart XML from Office, exact page renders from PDF).

Paths below marked `<SKILL>` refer to the directory containing this `SKILL.md`; always pass **absolute paths** to subagents.

## Pipeline

| Stage | Who | Purpose |
|---|---|---|
| 0. Setup | You | Confirm `INPUT_DIR`/`OUTPUT_DIR`, vision model (if custom), check tools |
| 1. Extract | `extract.py` + You | Inventory, pairing, mechanical extraction, loss report, triage warnings, choose metadata language (`stages/1_extract.md`) |
| 2. Convert | Subagents | Plan batches (`batches.py`), run 1 representative doc per type, then chronological parallel waves (`stages/2_convert.md`) |
| 3. Synthesize | 1 subagent (no images) | Build `MANIFEST.md`, `GLOSSARY.md`, `TIMELINE.md`, back-fill `superseded_by` (`stages/3_synthesize.md`) |
| 4. Validate & Report | `validate.py` + You | Verify coverage, frontmatter, links, anchors; fix gaps; report summary to user |

---

## Stage 0: Setup

1. Determine `INPUT_DIR` and `OUTPUT_DIR` from the user's request (or defaults `raw_context/` and `parsed_context/`). Verify `INPUT_DIR` exists.
2. Check the environment without installing anything:
   - Verify `bash "<SKILL>/scripts/run.sh" extract.py --help >/dev/null` works (uses `pixi exec` with Python, PyMuPDF, python-pptx, openpyxl, pillow, pandoc, pyyaml). If `pixi` cannot download packages (e.g. offline/sandboxed) or fails, tell the user and stop.
   - Check `command -v soffice || command -v libreoffice` (optional: only needed when rendering standalone `.pptx` without a paired PDF, or converting legacy `.doc`/`.ppt`/`.xls`).
3. If the user named a specific vision model for Stage 2 conversion, resolve its `providerID/modelID` with the model lookup tool; otherwise use the same model as you (omit `model`). If anything is ambiguous (directories, model choice, re-run behaviour), ask in one concise `question` call.

---

## Stage 1: Mechanical Extraction & Triage

Follow `<SKILL>/stages/1_extract.md`:
1. Run `bash "<SKILL>/scripts/run.sh" extract.py --input "<INPUT_DIR>" --output "<OUTPUT_DIR>"`.
2. Read `<OUTPUT_DIR>/.ingest/report.md` and `<OUTPUT_DIR>/.ingest/inventory.json` (never read full `text.md` files).
3. Surface any warnings (unmarked image-only folders, near-pairs, undated/low-confidence files, removed sources from earlier runs) to the user in one batch and wait if they decide to rename/clean up inputs; re-run `extract.py` once if inputs changed.
4. Determine `metadata_language` (`en` by default, or the shared corpus language if every document shares the same non-English language; ask the user if a re-run introduces a language conflict). Save it in `<OUTPUT_DIR>/.ingest/state.json`.
5. Write `<OUTPUT_DIR>/.ingest/overview.md` (metadata language, document list, top candidate terms).

If `extract.py` reports **0 new and 0 changed** documents (and no removed/unlinked docs need updating), skip Stage 2 and ask whether to refresh Stage 3 synthesis or exit.

---

## Stage 2: Batch Planning & Per-Document Conversion

1. Run `batches.py` to generate a proposed plan:
   ```bash
   bash "<SKILL>/scripts/run.sh" batches.py --output "<OUTPUT_DIR>"
   ```
2. **Review the proposed batches and exercise judgement for large documents (>40 pages):**
   The ~40-image cap is a safety guideline (OpenCode drops old images and fails above 64), counting images the subagent actually views — **not** total pages. Prefer options in this order:
   1. View **only pages flagged `vision: "required"`** (clean text-only pages need no image).
   2. Use **`figures/` crops** instead of full pages, and **`sheets/` contact sheets** for simple slide decks.
   3. Keep a whole document in **one dedicated subagent** even if it slightly exceeds typical batch size, as long as viewed images stay ≤ 40.
   4. For genuinely huge visual documents, run **sequential subagents appending to the same `docs/<slug>.md`** at natural boundaries (PDF outline chapters, `+folder` parts, section breaks) with a `<!-- handoff: ... -->` note. Never run two subagents in parallel on the same output file.
   5. Only split the output file into `docs/<slug>/index.md` + `part-NN.md` when the resulting Markdown itself would be too large to read comfortably.
   Record any manual batch adjustments in `<OUTPUT_DIR>/.ingest/state.json` so re-runs reuse the same choice.
3. **Pilot check:** launch one subagent for a single representative document (or small pilot batch covering the main formats present), inspect the resulting `docs/<slug>.md` and `assets/<slug>/` to confirm frontmatter, anchors, and figure descriptions meet `<SKILL>/references/format.md`.
4. **Convert in chronological waves:** within each wave, launch the wave's batches in parallel using the `general` subagent (`model` only if the user chose a custom vision model). Wait for the wave to finish before starting the next wave so later waves can read earlier `docs/<slug>.md` files (text only) for context.
5. Keep track of every subagent `sessionID` so you can resume a session for fixes or if it stopped early near the image cap.
6. Run `validate.py --docs-only`:
   ```bash
   bash "<SKILL>/scripts/run.sh" validate.py --output "<OUTPUT_DIR>" --docs-only
   ```
   Resume the relevant subagent `sessionID` to fix any errors before Stage 3.

### Subagent Prompt Template (Stage 2)

```text
You are executing Stage 2 of the ingest-context skill.
Read first:
- <SKILL>/stages/2_convert.md
- <SKILL>/references/format.md
- <SKILL>/references/types.md
- <OUTPUT_DIR>/.ingest/overview.md

Output directory: <OUTPUT_DIR>
Metadata language (for frontmatter values): <metadata_language>
Assigned documents (process oldest first, writing each docs/<slug>.md before moving to the next):
- <slug> (extract dir: <OUTPUT_DIR>/.ingest/extract/<slug>, notes/strategy: <...>)

Rules reminder:
- Never modify <INPUT_DIR>.
- Write each document to <OUTPUT_DIR>/docs/<slug>.md as soon as you finish it.
- Never reopen an image you already viewed; stay <= 40 images total in this session.
- Keep the document body strictly faithful to the source; put cross-document links in ## Context.
Return the final report requested in stages/2_convert.md.
```

---

## Stage 3: Corpus Synthesis

Launch **one** `general` subagent in a fresh session (default model, **no images**) with `<SKILL>/stages/3_synthesize.md`:

```text
You are executing Stage 3 of the ingest-context skill (no images).
Read first:
- <SKILL>/stages/3_synthesize.md
- <SKILL>/references/format.md
- <OUTPUT_DIR>/.ingest/overview.md
- <OUTPUT_DIR>/.ingest/inventory.json

Output directory: <OUTPUT_DIR>
Metadata/synthesis language: <metadata_language>

Read all docs/*.md (and docs/*/index.md) text-only, write MANIFEST.md, GLOSSARY.md, and TIMELINE.md under <OUTPUT_DIR>/, and back-fill superseded_by / supersedes / related in document frontmatter where clearly evidenced.
Return the final report requested in stages/3_synthesize.md.
```

---

## Stage 4: Final Validation & User Report

1. Run full validation:
   ```bash
   bash "<SKILL>/scripts/run.sh" validate.py --output "<OUTPUT_DIR>"
   ```
   If any error or critical warning appears, resume the responsible Stage 2 or Stage 3 subagent `sessionID` to fix it, then re-run `validate.py`.
2. Present a clear final report to the user covering:
   - Total documents processed (`new`, `changed`, `unchanged`) and outputs created (`MANIFEST.md`, `GLOSSARY.md`, `TIMELINE.md`, `docs/`, `assets/`).
   - Any unrecoverable or partial losses flagged by `extract.py` (e.g. `formula_no_value`, `media`, `ole_object`, `password_protected`, `unreadable_image`, `rendered_with_libreoffice`).
   - Any documents with `date: unknown` or `date_source: mtime` / low confidence, plus any `[illegible]` spans.
   - Any removed sources or orphan outputs left for the user to decide on.
