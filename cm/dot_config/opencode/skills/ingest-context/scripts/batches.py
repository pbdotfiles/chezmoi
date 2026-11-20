"""Stage 2 planner for ingest-context: group documents into subagent batches and waves.

Usage: bash run.sh batches.py --output DIR [--max-images 36] [--max-tokens 120000] [--all]

Reads <output>/.ingest/inventory.json and per-doc meta.json files, groups
related documents (parent/attachments, same folder, chronological proximity),
and proposes chronological waves plus handling strategies for large documents.
Writes <output>/.ingest/batches.json and prints a human-readable summary.
"""
import argparse
import sys
from pathlib import Path

from common import load_json, natural_key, save_json, work_dir


def doc_sort_key(d: dict):
    dt = d.get("date")
    val = dt["value"] if dt else "9999-99-99"
    # Undated or low-confidence dates (e.g. mtime or Office template dates) go after reliably dated docs
    low = 1 if (not dt or dt.get("confidence") == "low") else 0
    return (low, val, d.get("dir", ""), natural_key(d["slug"]))


def effective_images(d: dict, meta: dict | None) -> int:
    """Estimate how many full-resolution images a subagent actually needs to view."""
    est = d["est"]
    req = est["images_required"]
    sheets = est["sheets"]
    if d.get("slide_like") and sheets > 0 and req == 0:
        # Simple text-only slide deck: contact sheets suffice
        return sheets
    return req


def propose_large_doc_strategy(d: dict, meta: dict | None, max_images: int, max_tokens: int) -> list[str]:
    est = d["est"]
    pages = est["pages"]
    req = est["images_required"]
    sheets = est["sheets"]
    text_toks = est["text_tokens"]
    strategies = []

    if req <= max_images and text_toks <= max_tokens:
        if pages > max_images:
            strategies.append(
                f"vision-only on {req} flagged pages (of {pages} total) fits in one subagent"
            )
        return strategies

    if sheets > 0 and req > max_images:
        strategies.append(
            f"use {sheets} contact sheet(s) for overview and open full-size renders/crops only for key figures"
        )

    if meta and meta.get("pages"):
        crop_count = sum(len(p.get("figures", [])) for p in meta["pages"])
        if crop_count > 0 and crop_count < req:
            strategies.append(f"view {crop_count} figure crops instead of {req} full pages where text is clean")

    if req > max_images or text_toks > max_tokens:
        outline = (meta or {}).get("outline", [])
        parts = (meta or {}).get("parts", [])
        n_chunks = max(
            (req + max_images - 1) // max(max_images, 1),
            (text_toks + max_tokens - 1) // max(max_tokens, 1),
            2,
        )
        if outline:
            top = [o for o in outline if o.get("level", 1) <= 2][:12]
            labels = ", ".join(f"'{o['title']}' (p.{o['page']})" for o in top[:6])
            strategies.append(
                f"sequential handoff across ~{n_chunks} subagents appending to docs/{d['slug']}.md "
                f"along PDF outline boundaries ({labels})"
            )
        elif parts:
            strategies.append(
                f"sequential handoff across ~{n_chunks} subagents appending to docs/{d['slug']}.md "
                f"along part boundaries ({len(parts)} parts)"
            )
        else:
            strategies.append(
                f"sequential handoff across ~{n_chunks} subagents appending to docs/{d['slug']}.md "
                f"at natural section/page boundaries"
            )

    if text_toks > 140_000:
        strategies.append(
            f"very large text (~{text_toks:,} tokens): consider splitting output into "
            f"docs/{d['slug']}/index.md + part-N.md for readability"
        )
    return strategies


def build_clusters(docs: list[dict]) -> list[list[dict]]:
    """Group parent documents with their attachment children; keep others as 1-doc clusters."""
    by_slug = {d["slug"]: d for d in docs}
    assigned = set()
    clusters = []

    for d in docs:
        if d["slug"] in assigned or d.get("parent"):
            continue
        group = [d]
        assigned.add(d["slug"])
        for cs in d.get("children", []):
            if cs in by_slug and cs not in assigned:
                group.append(by_slug[cs])
                assigned.add(cs)
        clusters.append(group)

    # Orphan children (whose parent was unchanged and skipped)
    for d in docs:
        if d["slug"] not in assigned:
            clusters.append([d])
            assigned.add(d["slug"])
    return clusters


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--max-images", type=int, default=36,
                    help="target max required images per subagent (default: 36, headroom under 40)")
    ap.add_argument("--max-tokens", type=int, default=120_000,
                    help="target max input tokens (text + required images) per batch (default: 120000)")
    ap.add_argument("--all", action="store_true", help="include unchanged documents too")
    a = ap.parse_args()

    out = a.output.resolve()
    wd = work_dir(out)
    inv = load_json(wd / "inventory.json")
    if inv is None:
        sys.exit(f"inventory.json not found in {wd} — run extract.py first")

    docs = [d for d in inv["documents"] if a.all or d["status"] in ("new", "changed")]
    if not docs:
        plan = {"generated": inv["generated"], "max_images": a.max_images,
                "max_tokens": a.max_tokens, "waves": [], "summary": "Nothing to convert."}
        save_json(wd / "batches.json", plan)
        print("All documents are unchanged; 0 batches needed.")
        return

    meta_by_slug = {}
    for d in docs:
        meta_by_slug[d["slug"]] = load_json(wd / d["extract_dir"] / "meta.json")

    docs_sorted = sorted(docs, key=doc_sort_key)
    clusters = build_clusters(docs_sorted)

    # Order clusters by (reliability, month, folder) so reliable older documents run first
    # and undated / low-confidence documents go in the final wave.
    def cluster_sort_key(cl):
        d0 = cl[0]
        dt = d0.get("date")
        is_low = 1 if (not dt or dt.get("confidence") == "low") else 0
        ym = dt["value"][:7] if (dt and not is_low) else "9999-99"
        return (is_low, ym, d0.get("dir", ""), doc_sort_key(d0))

    clusters.sort(key=cluster_sort_key)

    batches = []
    cur = {"docs": [], "tokens": 0, "images": 0, "dir": None, "oversized": False, "notes": []}

    def flush():
        nonlocal cur
        if cur["docs"]:
            batches.append(cur)
        cur = {"docs": [], "tokens": 0, "images": 0, "dir": None, "oversized": False, "notes": []}

    for cl in clusters:
        cl_tokens = sum(d["est"]["text_tokens"] + d["est"]["image_tokens_required"] for d in cl)
        cl_images = sum(effective_images(d, meta_by_slug[d["slug"]]) for d in cl)
        cl_dir = cl[0].get("dir", "")
        notes = []
        for d in cl:
            notes.extend(
                f"{d['slug']}: {s}"
                for s in propose_large_doc_strategy(d, meta_by_slug[d["slug"]], a.max_images, a.max_tokens)
            )
        is_oversized = cl_images > a.max_images or cl_tokens > a.max_tokens

        if is_oversized:
            flush()
            batches.append({
                "docs": cl,
                "tokens": cl_tokens,
                "images": cl_images,
                "dir": cl_dir,
                "oversized": True,
                "notes": notes,
            })
            continue

        would_exceed = (cur["images"] + cl_images > a.max_images) or (cur["tokens"] + cl_tokens > a.max_tokens)
        dir_changed = bool(cur["docs"] and cur["dir"] != cl_dir and cur["images"] >= a.max_images // 2)
        if cur["docs"] and (would_exceed or dir_changed):
            flush()

        cur["docs"].extend(cl)
        cur["tokens"] += cl_tokens
        cur["images"] += cl_images
        if cur["dir"] is None:
            cur["dir"] = cl_dir
        cur["notes"].extend(notes)

    flush()

    # Assign chronological waves:
    # Wave 1: first batch (if dated) or earliest dated batches from distinct folders;
    # Wait: simple & safe rule: group consecutive batches sharing the same YYYY-MM (or undated)
    # into parallel waves, EXCEPT oversized/sequential docs get their own wave or remain clearly tagged.
    waves = []
    cur_wave = None
    for idx, b in enumerate(batches, 1):
        dates = [d["date"]["value"][:7] for d in b["docs"]
                 if d.get("date") and d["date"].get("confidence") != "low"]
        bucket = min(dates) if dates else "undated-or-low"
        b_id = f"batch-{idx:02d}"
        entry = {
            "id": b_id,
            "bucket": bucket,
            "oversized": b["oversized"],
            "est_tokens": b["tokens"],
            "est_images": b["images"],
            "notes": b["notes"],
            "documents": [
                {
                    "slug": d["slug"],
                    "status": d["status"],
                    "dir": d.get("dir", ""),
                    "date": d["date"]["value"] if d.get("date") else "unknown",
                    "date_source": d["date"]["source"] if d.get("date") else "none",
                    "formats": d["formats"],
                    "pages": d["est"]["pages"],
                    "images_required": d["est"]["images_required"],
                    "images_useful": d["est"]["images_useful"],
                    "sheets": d["est"]["sheets"],
                    "text_tokens": d["est"]["text_tokens"],
                    "flags": sorted(d["flags"].keys()),
                }
                for d in b["docs"]
            ],
        }
        if cur_wave is None or cur_wave["bucket"] != bucket or len(cur_wave["batches"]) >= 4:
            cur_wave = {"wave": len(waves) + 1, "bucket": bucket, "batches": []}
            waves.append(cur_wave)
        cur_wave["batches"].append(entry)

    plan = {
        "generated": inv["generated"],
        "max_images": a.max_images,
        "max_tokens": a.max_tokens,
        "total_docs": len(docs),
        "total_batches": len(batches),
        "waves": waves,
    }
    save_json(wd / "batches.json", plan)

    print(f"Batch plan: {len(docs)} doc(s) -> {len(batches)} batch(es) across {len(waves)} wave(s)")
    print(f"Saved: {wd / 'batches.json'}\n")
    for w in waves:
        print(f"Wave {w['wave']} ({w['bucket']}):")
        for b in w["batches"]:
            slugs = ", ".join(d["slug"] for d in b["documents"])
            tag = " [OVERSIZED - ORCHESTRATOR REVIEW]" if b["oversized"] else ""
            print(f"  - {b['id']}: {len(b['documents'])} doc(s), ~{b['est_images']} req img, "
                  f"~{b['est_tokens']:,} tok{tag} -> {slugs}")
            for n in b["notes"]:
                print(f"      * {n}")


if __name__ == "__main__":
    main()
