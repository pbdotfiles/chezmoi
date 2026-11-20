# Stage 1: Mechanical Extraction & Triage (Orchestrator)

Stage 1 uses `extract.py` (no LLM) to inspect `<INPUT_DIR>`, group files into documents, extract raw text + native data + page images + figure crops, and produce a loss report.

## Steps

1. Run `extract.py`:
   ```bash
   bash <SKILL>/scripts/run.sh extract.py --input "<INPUT_DIR>" --output "<OUTPUT_DIR>"
   ```
   (Pass `--force` only if the user explicitly asks to re-extract unchanged documents.)

2. Read `<OUTPUT_DIR>/.ingest/report.md` and `<OUTPUT_DIR>/.ingest/inventory.json`. Do **not** read the full `text.md` files yourself — keep your own context light.

3. **Check warnings and ambiguities** from `report.md` and ask the user in one concise batch (using `question` when choices are closed):
   - **Unmarked image folders:** folders holding only images that lack a `+` prefix (confirm if the user wants to rename them `+<folder>/` before continuing, or treat each image separately).
   - **Near-pairs:** unpaired Office + PDF files that look like the same document (confirm if the user wants to rename one to match the base name).
   - **Undated / low-confidence dates:** mention documents that only have `mtime` or no date if they matter for ordering, in case the user wants to date-prefix filenames.
   - **Removed / orphan files:** on re-runs, list sources removed since the last run whose `docs/<slug>.md` still exists; ask whether to delete them or keep them.
   - **Missing tools:** if `needs_libreoffice` appears and `soffice` is missing, inform the user (never install anything yourself).

   If the user renames any files or `+` folders, re-run `extract.py` once after they confirm.

4. **Decide the metadata language:**
   - Look at the `sample` fields in `inventory.json` (plus any previously recorded `metadata_language` in `<OUTPUT_DIR>/.ingest/state.json`).
   - **Default:** `en` (English).
   - **Exception:** if **all** documents in the corpus clearly share the same non-English language (e.g., all French), use that language for frontmatter values (`summary`, `tags`, `uncertainty`) and synthesis files (`MANIFEST.md`, `GLOSSARY.md`, `TIMELINE.md`). Body text always stays in each document's own language.
   - **Re-run conflict:** if `state.json` already recorded a non-English `metadata_language` (e.g., `fr`) and new documents are in a different language (e.g., `en`), **ask the user** whether to switch metadata/manifest to English or keep the existing language.
   - Record the chosen `metadata_language` in `<OUTPUT_DIR>/.ingest/state.json` (or pass it explicitly in Stage 2 and Stage 3 prompts).

5. **Write `<OUTPUT_DIR>/.ingest/overview.md`** (a short corpus overview from `inventory.json`, under ~100 lines):
   - Metadata language chosen
   - Brief list of documents (`slug`, date, format, folder)
   - Candidate recurring acronyms/terms from `inventory.json["terms"]` (top ~40)

   Every Stage 2 subagent will read `overview.md` so even isolated batches have corpus awareness.
