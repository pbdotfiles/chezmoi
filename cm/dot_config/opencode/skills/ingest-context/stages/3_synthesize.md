# Stage 3: Corpus Synthesis (Subagent Instructions)

You are running Stage 3 of `ingest-context` in a fresh session with **no images**. Your job is to turn the individually converted documents in `<OUTPUT_DIR>/docs/` into a coherent, navigable knowledge base.

## Inputs

- `<SKILL>/references/format.md`
- `<OUTPUT_DIR>/.ingest/inventory.json`
- `<OUTPUT_DIR>/.ingest/overview.md`
- Every converted file under `<OUTPUT_DIR>/docs/` (read **text only** — start with frontmatter, summaries, and `## Context` sections; read bodies selectively when resolving contradictions, terminology, or supersession).

**Language rule:** write `MANIFEST.md`, `GLOSSARY.md`, and `TIMELINE.md` in the `metadata_language` specified in `.ingest/overview.md` (`en` by default, or the shared non-English corpus language).

## Deliverables

### 1. `<OUTPUT_DIR>/MANIFEST.md`
An index of **every** document in `docs/` (every slug from `inventory.json` must appear):
- Corpus overview (total docs, date span, languages, key unresolved gaps/warnings from `.ingest/report.md`).
- Table or structured list of all documents ordered chronologically (undated last), with:
  - Link to `docs/<slug>.md` (or `docs/<slug>/index.md`)
  - Date (`date`, plus `period` if set, and low-confidence marker if applicable)
  - Type (`type`) and language (`language`)
  - Supersession status (e.g., `superseded by <slug>`)
  - Concise summary & key topics/tags
- Note any removed sources or unreadable/incomplete files reported in `inventory.json` so downstream readers know what is missing.

### 2. `<OUTPUT_DIR>/GLOSSARY.md`
A deduplicated reference of:
- Acronyms and abbreviations (with expansion and which documents define/use them)
- Project codenames, internal systems, components, and metrics
- Key people/teams and roles (only what is explicitly stated in the corpus)
- Any conflicting definitions or naming shifts across time (cite the slugs)

### 3. `<OUTPUT_DIR>/TIMELINE.md`
A chronological synthesis across the corpus:
- Ordered milestones, major decisions, experiment/benchmark results, releases, incidents, and deliverables, each citing `[slug, p.N]` or `[slug]`.
- Explicit note of **supersessions and reversals** (e.g., *"2026-02-10: Target changed from X to Y [slug-b], superseding [slug-a]"*).
- Separate section at the bottom for **Undated or ambiguous-date items**.

### 4. Back-fill Cross-References in `docs/` Frontmatter
When the corpus clearly shows that document B supersedes document A (or updates a specific result in A), update **only the YAML frontmatter** (`superseded_by`, `supersedes`, `related`) of the affected `docs/<slug>.md` (or `docs/<slug>/index.md`) files:
- Never alter `sha256`, `source`, or the document body of `docs/<slug>.md`.
- Only add `superseded_by` / `supersedes` when supported by explicit evidence in the documents; otherwise use `related`.

## Final Report

Report:
1. Counts: total documents indexed in `MANIFEST.md`, glossary entries, timeline events.
2. Frontmatter cross-links updated (`superseded_by` / `supersedes` / `related`).
3. Key contradictions, unresolved gaps, or missing-date items surfaced during synthesis.
