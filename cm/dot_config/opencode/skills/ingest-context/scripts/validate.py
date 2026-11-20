"""Validation for ingest-context output.

Usage: bash run.sh validate.py --output DIR [--docs-only] [--strict]

Checks:
  - every document in .ingest/inventory.json has a converted Markdown file
  - YAML frontmatter is valid, has required fields, and matches sha256
  - all relative image and file links in docs/**/*.md resolve on disk
  - page/part anchors and flagged visual documents are accounted for
  - synthesis files (MANIFEST.md, GLOSSARY.md, TIMELINE.md) exist and cover all docs
    (skipped when --docs-only is passed after Stage 2)
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

from common import (
    ASSETS,
    CONFIDENCES,
    DATE_SOURCES,
    DOCS,
    FIGURE_SKIPPED_RE,
    GENRES,
    IMAGE_LINK_RE,
    PAGE_ANCHOR_RE,
    PART_ANCHOR_RE,
    SYNTHESIS_FILES,
    load_json,
    output_files,
    split_frontmatter,
    work_dir,
)

REQUIRED_FM = ("source", "sha256", "date", "date_source", "date_confidence",
               "type", "language", "summary", "tags")
DATE_RE = re.compile(r"^(?:\d{4}(?:-\d{2}(?:-\d{2})?)?|unknown)$")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)")
PLACEHOLDER_RE = re.compile(r"<!--\s*TODO|\[TODO|\?\?\?")
VISUAL_FLAGS = {"figure", "no_text_layer", "garbled_text", "chart_no_cached_data",
                "smartart", "diagram", "tall_image", "image"}


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    fm_raw, body = split_frontmatter(text)
    if fm_raw is None:
        return None, text, "missing YAML frontmatter"
    try:
        data = yaml.safe_load(fm_raw)
    except yaml.YAMLError as e:
        return None, body, f"invalid YAML frontmatter: {e}"
    if not isinstance(data, dict):
        return None, body, "frontmatter must be a YAML mapping"
    return data, body, None


def resolve_local_link(md_file: Path, raw_target: str, out: Path) -> Path | None:
    target = unquote(raw_target.split("#", 1)[0].strip())
    if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    return (md_file.parent / target).resolve()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--docs-only", action="store_true",
                    help="skip checking MANIFEST.md, GLOSSARY.md, TIMELINE.md (use before Stage 3)")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors (non-zero exit code)")
    a = ap.parse_args()

    out = a.output.resolve()
    wd = work_dir(out)
    inv = load_json(wd / "inventory.json")
    if inv is None:
        sys.exit(f"inventory.json not found in {wd} — run extract.py first")

    errors: list[str] = []
    warnings: list[str] = []

    docs_inv = inv.get("documents", [])
    known_slugs = {d["slug"] for d in docs_inv}
    referenced_assets: set[Path] = set()

    # 1. Per-document coverage, frontmatter, anchors, flags
    for d in docs_inv:
        slug = d["slug"]
        files = output_files(out, slug)
        if not files:
            errors.append(f"[{slug}] missing output file (expected {DOCS}/{slug}.md or {DOCS}/{slug}/index.md)")
            continue

        main_file = files[0]
        rel_main = main_file.relative_to(out).as_posix()
        fm, _, fm_err = parse_frontmatter(main_file)
        if fm_err:
            errors.append(f"[{slug}] {rel_main}: {fm_err}")
            continue

        for k in REQUIRED_FM:
            if k not in fm or fm[k] in (None, ""):
                errors.append(f"[{slug}] {rel_main}: missing required frontmatter key `{k}`")

        if fm.get("sha256") != d["sha256"]:
            errors.append(f"[{slug}] {rel_main}: sha256 mismatch (stale or wrong source hash)")

        dtype = fm.get("type")
        if dtype and dtype not in GENRES:
            warnings.append(f"[{slug}] {rel_main}: unexpected type `{dtype}` (expected one of {GENRES})")

        ds = fm.get("date_source")
        if ds and ds not in DATE_SOURCES:
            errors.append(f"[{slug}] {rel_main}: invalid date_source `{ds}`")

        dc = fm.get("date_confidence")
        if dc and dc not in CONFIDENCES:
            errors.append(f"[{slug}] {rel_main}: invalid date_confidence `{dc}`")

        dt_val = str(fm.get("date", ""))
        if dt_val and not DATE_RE.match(dt_val):
            warnings.append(f"[{slug}] {rel_main}: non-standard date `{dt_val}` (use YYYY-MM-DD, YYYY-MM, YYYY, or unknown)")

        tags = fm.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append(f"[{slug}] {rel_main}: `tags` must be a list")

        for ref_key in ("related", "supersedes", "superseded_by"):
            refs = fm.get(ref_key)
            if not refs:
                continue
            if isinstance(refs, str):
                refs = [refs]
            if not isinstance(refs, list):
                errors.append(f"[{slug}] {rel_main}: `{ref_key}` must be a list or string")
                continue
            for r in refs:
                if r not in known_slugs:
                    warnings.append(f"[{slug}] {rel_main}: `{ref_key}` references unknown slug `{r}`")

        # Combine body across main_file and any split parts
        combined_text = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files)
        _, main_body = split_frontmatter(main_file.read_text(encoding="utf-8", errors="replace"))
        if len(files) == 1 and not main_body.strip():
            errors.append(f"[{slug}] {rel_main}: document body is empty")

        # Links and images across all files of this doc
        doc_images = []
        for f in files:
            rel_f = f.relative_to(out).as_posix()
            txt = f.read_text(encoding="utf-8", errors="replace")
            for m in IMAGE_LINK_RE.finditer(txt):
                raw_t = m.group(1)
                resolved = resolve_local_link(f, raw_t, out)
                if resolved is None:
                    continue
                if not resolved.exists():
                    errors.append(f"[{slug}] {rel_f}: broken image link `{raw_t}`")
                else:
                    referenced_assets.add(resolved)
                    doc_images.append(resolved)
            for m in MD_LINK_RE.finditer(txt):
                raw_t = m.group(1)
                resolved = resolve_local_link(f, raw_t, out)
                if resolved is not None and not resolved.exists():
                    errors.append(f"[{slug}] {rel_f}: broken link `{raw_t}`")
            if PLACEHOLDER_RE.search(txt):
                warnings.append(f"[{slug}] {rel_f}: contains unresolved TODO/??? marker")

        # Anchor checks
        meta = load_json(wd / d["extract_dir"] / "meta.json") or {}
        if d.get("anchors") == "pages" and d["est"]["pages"] > 1:
            if not PAGE_ANCHOR_RE.search(combined_text):
                warnings.append(f"[{slug}] missing `<!-- p.N -->` page anchors in multi-page document")
        if d.get("anchors") == "parts" and len(meta.get("parts", [])) > 1:
            if not PART_ANCHOR_RE.search(combined_text):
                warnings.append(f"[{slug}] missing `<!-- part: ... -->` anchors in multi-part `+` folder")

        # Visual flag check
        doc_flags = set(d.get("flags", {}).keys())
        unrecoverable = {"unreadable", "password_protected", "needs_libreoffice"}
        if (doc_flags & VISUAL_FLAGS) and not (doc_flags & unrecoverable):
            has_skip = bool(FIGURE_SKIPPED_RE.search(combined_text))
            has_illegible = "[illegible]" in combined_text
            if not doc_images and not has_skip and not has_illegible:
                warnings.append(
                    f"[{slug}] flagged {sorted(doc_flags & VISUAL_FLAGS)} but has no linked images in assets/"
                )

    # 2. Check for orphaned assets not referenced by any doc
    assets_dir = out / ASSETS
    if assets_dir.is_dir():
        for p in sorted(assets_dir.rglob("*")):
            if p.is_file() and p.resolve() not in referenced_assets:
                warnings.append(f"unreferenced asset: {p.relative_to(out).as_posix()}")

    # 3. Synthesis files
    if not a.docs_only:
        for name in SYNTHESIS_FILES:
            sp = out / name
            if not sp.is_file() or not sp.read_text(encoding="utf-8", errors="replace").strip():
                errors.append(f"missing or empty synthesis file: {name}")
        manifest = out / "MANIFEST.md"
        if manifest.is_file():
            mtxt = manifest.read_text(encoding="utf-8", errors="replace")
            for slug in sorted(known_slugs):
                if slug not in mtxt:
                    errors.append(f"MANIFEST.md does not mention document `{slug}`")

    # Report
    print(f"Validated {len(docs_inv)} document(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  ERROR: {e}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  WARN:  {w}")

    if errors or (a.strict and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
