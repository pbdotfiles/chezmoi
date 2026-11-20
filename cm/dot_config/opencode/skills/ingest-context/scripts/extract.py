"""Stage 1 of ingest-context: inventory and mechanical extraction, no LLM.

Usage: bash run.sh extract.py --input DIR --output DIR [--force]

Groups the input into documents (Office + PDF pairs, `+` folders, email
attachments), extracts text, page images, figure crops and native data (chart
values, speaker notes, comments, formulas), and flags what text extraction
cannot capture. Everything goes under <output>/.ingest/:

  state.json            slug of each document, kept across runs
  inventory.json        every document: status, sources, date, flags, cost
  report.md             human-readable summary, warnings, flag meanings
  extract/<slug>/       text.md, meta.json, pages/, figures/, sheets/, media/,
                        data/, attachments/

A document whose converted file (docs/<slug>.md) records the same sha256 as
its sources is "unchanged" and is not extracted again unless --force.
The input directory is only read.
"""
import argparse
import csv
import difflib
import email
import email.utils
import hashlib
import io
import mailbox
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email import policy
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps

from common import (image_tokens, load_json, natural_key, output_files, frontmatter_sha,
                    save_json, slugify, work_dir, DOCS)

PDF_EXT = {".pdf"}
SLIDES_EXT = {".pptx"}
DOCX_EXT = {".docx"}
SHEET_EXT = {".xlsx", ".xlsm"}
LEGACY_EXT = {".ppt": "pptx", ".pps": "pptx", ".ppsx": "pptx", ".odp": "pptx",
              ".doc": "docx", ".odt": "docx", ".rtf": "docx", ".wpd": "docx",
              ".xls": "xlsx", ".ods": "xlsx"}
OFFICE_EXT = SLIDES_EXT | DOCX_EXT | SHEET_EXT | set(LEGACY_EXT)
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
TEXT_EXT = {".md", ".markdown", ".txt", ".text", ".rst", ".org", ".log", ".json", ".jsonl",
            ".yaml", ".yml", ".xml", ".tex", ".svg", ".vtt", ".srt", ".ini", ".toml"}
HTML_EXT = {".html", ".htm", ".mhtml"}
TABLE_EXT = {".csv", ".tsv"}
JUNK_NAMES = {"__MACOSX", "__pycache__", "Thumbs.db", "desktop.ini", ".DS_Store"}
JUNK_SUFFIXES = (".tmp", ".crdownload", ".part", ".partial")

RENDER_LONG_SIDE = 1500
CROP_LONG_SIDE = 1400
MAX_TEXT_CHARS = 400_000
MAX_TABLE_ROWS = 300
MAX_TABLE_COLS = 40

C_NS = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

FLAG_HELP = {
    "no_text_layer": "page has no text layer (scan, or text drawn as an image): read it from the page image",
    "garbled_text": "extracted text is partly garbage (font without a character map): trust the page image",
    "figure": "page holds a chart, diagram or picture: crops are in figures/",
    "full_page_image": "page is mostly one image (background, screenshot or scan)",
    "table": "a table was detected: the auto-extracted Markdown table may have merged or split cells",
    "annotations": "PDF comments or highlights, written in the text",
    "blank": "page looks empty",
    "hidden_slide": "slide is hidden in the presentation",
    "speaker_notes": "slide has speaker notes, written in the text",
    "slide_comments": "slide has review comments, written in the text",
    "chart_data": "chart values were read from the file itself: exact, prefer them to reading the image",
    "chart_no_cached_data": "chart found but the file holds no values for it: read it from the image",
    "smartart": "SmartArt diagram: its text is listed, but the links between boxes are only in the image",
    "diagram": "shapes and connectors form a diagram: the structure is only in the image",
    "picture": "picture covering a significant part of the slide",
    "media": "embedded audio or video: its content is lost",
    "ole_object": "embedded object (spreadsheet, drawing...): only its preview image may be readable",
    "rendered_with_libreoffice": "page images rendered by LibreOffice: fonts and layout may differ from the original",
    "converted_with_libreoffice": "legacy format converted with LibreOffice before extraction",
    "no_render": "no page images could be produced (no paired PDF and no LibreOffice)",
    "pair_mismatch": "the paired PDF does not have the same number of pages as the Office file",
    "comments": "document has review comments (shown as comment spans in the text)",
    "tracked_changes": "document has tracked changes (insertion/deletion spans in the text)",
    "headers_footers": "header and footer text, written at the end of the text",
    "unreadable_image": "an image could not be decoded (EMF/WMF/HEIC...): see the paired PDF or ask the user",
    "hidden_sheet": "workbook has hidden sheets (included and marked)",
    "hidden_rows_cols": "sheet has hidden rows or columns (included, listed)",
    "formulas": "sheet has formulas: cached values are shown, samples of formulas are listed",
    "formula_no_value": "formulas without a stored value (file saved by a script?): values are missing",
    "conditional_formatting": "colours carry meaning (conditional formatting) that text does not show",
    "truncated_table": "only the first rows/columns are in text.md; the full table is in data/",
    "cell_comments": "cells have comments, listed in the text",
    "pivot_table": "workbook has pivot tables (their cached values may be stale)",
    "quoted_history": "email body repeats earlier messages: keep each message once",
    "attachments": "document carries attachments, extracted as their own documents",
    "inline_images": "email has inline images, in media/",
    "tall_image": "very tall image cut into overlapping tiles in pages/",
    "truncated_text": "text was too long and was cut: see the source",
    "linked_images": "text references local images, copied to media/",
    "password_protected": "file is password-protected: nothing extracted",
    "unreadable": "file could not be opened",
    "unsupported_format": "format not handled by the script: read the source directly if possible",
    "needs_libreoffice": "legacy format needs LibreOffice (soffice), which is not installed",
}


# ----------------------------------------------------------------------------- scanning

@dataclass
class Unit:
    key: str                 # identity across runs
    name: str                # base for the slug and filename dates
    kind: str                # single | pair | group | attachment
    files: list              # [Path]
    rel: list                # source paths shown to the user
    dir_rel: str = ""        # folder relative to the input ("" = top level)
    parent: str | None = None
    group_root: Path | None = None


def is_junk(name: str) -> bool:
    return (name in JUNK_NAMES or name.startswith(".") or name.startswith("~$")
            or name.startswith(".~lock") or name.lower().endswith(JUNK_SUFFIXES))


def norm_stem(p: Path) -> str:
    return re.sub(r"\s*\(\d+\)$", "", p.stem.strip()).lower()


def scan(input_dir: Path, output_dir: Path):
    units, warnings = [], []
    out_resolved = output_dir.resolve()

    def rel(p: Path) -> str:
        return p.relative_to(input_dir).as_posix()

    def walk(d: Path):
        try:
            entries = sorted(d.iterdir(), key=lambda p: natural_key(p.name))
        except PermissionError:
            warnings.append(f"cannot read folder `{rel(d)}`")
            return
        files = [e for e in entries if e.is_file() and not is_junk(e.name)]
        dirs = [e for e in entries if e.is_dir() and not is_junk(e.name)
                and e.resolve() != out_resolved]
        dir_rel = "" if d == input_dir else rel(d)

        by_stem = {}
        for f in files:
            by_stem.setdefault((norm_stem(f)), []).append(f)
        for stem, stem_files in by_stem.items():
            office = [f for f in stem_files if f.suffix.lower() in OFFICE_EXT]
            pdfs = [f for f in stem_files if f.suffix.lower() in PDF_EXT]
            # Same key whether the Office file and the PDF are paired or alone, so that
            # adding or removing one of them keeps the document's slug.
            paged_key = f"{dir_rel + '/' if dir_rel else ''}{stem} [office/pdf]"
            paired = set()
            if office and pdfs:
                o, p = office[0], pdfs[0]
                paired = {o, p}
                units.append(Unit(paged_key, o.stem, "pair", [o, p], [rel(o), rel(p)], dir_rel))
            for f in stem_files:
                if f in paired:
                    continue
                key = rel(f)
                if not paired and f.suffix.lower() in OFFICE_EXT | PDF_EXT:
                    key, paired = paged_key, {None}
                units.append(Unit(key, f.stem, "single", [f], [rel(f)], dir_rel))

        if d != input_dir and len(files) >= 2 and not dirs \
                and all(f.suffix.lower() in IMAGE_EXT for f in files):
            warnings.append(
                f"folder `{rel(d)}` holds only {len(files)} images: if they form one document "
                f"(e.g. screenshots of one conversation), rename it `+{d.name}`")

        for sub in dirs:
            if sub.name.startswith("+"):
                parts = sorted((f for f in sub.rglob("*") if f.is_file()
                                and not any(is_junk(x) for x in f.relative_to(sub).parts)),
                               key=lambda f: natural_key(f.relative_to(sub).as_posix()))
                if not parts:
                    warnings.append(f"folder `{rel(sub)}` is empty")
                    continue
                units.append(Unit(rel(sub) + "/", sub.name[1:] or "group", "group", parts,
                                  [rel(f) for f in parts], dir_rel, group_root=sub))
            else:
                walk(sub)

    walk(input_dir)
    return units, warnings


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------- dates

def filename_dates(name: str):
    """Dates written in a file or folder name: [(value, confidence)]."""
    found = []
    pats = [
        (r"(?<!\d)((?:19|20)\d{2})[-_. ](\d{2})[-_. ](\d{2})(?!\d)", "ymd", "high"),
        (r"(?<!\d)((?:19|20)\d{2})(\d{2})(\d{2})(?!\d)", "ymd", "high"),
        (r"(?<!\d)(\d{2})[-_.](\d{2})[-_.]((?:19|20)\d{2})(?!\d)", "dmy", "medium"),
        (r"(?<!\d)((?:19|20)\d{2})[-_.](\d{2})(?![-_.]?\d)", "ym", "medium"),
    ]
    for pat, order, conf in pats:
        for m in re.finditer(pat, name):
            g = m.groups()
            try:
                if order == "ymd":
                    found.append((datetime(int(g[0]), int(g[1]), int(g[2])).strftime("%Y-%m-%d"), conf))
                elif order == "dmy":
                    found.append((datetime(int(g[2]), int(g[1]), int(g[0])).strftime("%Y-%m-%d"), conf))
                elif 1 <= int(g[1]) <= 12:
                    found.append((f"{g[0]}-{g[1]}", conf))
            except ValueError:
                pass
        if found:
            return found
    return found


def iso(d) -> str | None:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    return str(d)[:10]


def parse_pdf_date(s):
    m = re.match(r"D:(\d{4})(\d{2})?(\d{2})?", s or "")
    if not m:
        return None
    y, mo, d = m.group(1), m.group(2) or "01", m.group(3) or "01"
    try:
        return datetime(int(y), int(mo), int(d)).strftime("%Y-%m-%d")
    except ValueError:
        return None


DATE_RANK = {("filename", "high"): 0, ("metadata", "high"): 1, ("filename", "medium"): 2,
             ("metadata", "medium"): 3, ("path", "low"): 4, ("metadata", "low"): 5,
             ("mtime", "low"): 6}


# ----------------------------------------------------------------------------- document

class Doc:
    def __init__(self, unit: Unit, xdir: Path, input_dir: Path):
        self.unit, self.x, self.input_dir = unit, xdir, input_dir
        self.lines: list[str] = []
        self.tail: list[str] = []
        self.pages: list[dict] = []
        self.images: list[dict] = []
        self.sheets: list[str] = []
        self.flags: dict[str, list] = {}
        self.dates: list[dict] = []
        self.links: set[str] = set()
        self.outline: list[dict] = []
        self.children: list[dict] = []
        self.authors: set[str] = set()
        self.formats: list[str] = []
        self.anchors = "none"
        self.slide_like = False

    def w(self, s: str = ""):
        self.lines.append(s)

    def flag(self, name: str, detail=None):
        lst = self.flags.setdefault(name, [])
        if detail is not None and detail not in lst and len(lst) < 200:
            lst.append(detail)

    def date(self, value, source, confidence, note):
        if value:
            self.dates.append({"value": value, "source": source, "confidence": confidence,
                               "note": note})

    def path(self, sub: str, name: str) -> Path:
        p = self.x / sub / name
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def relx(self, p: Path) -> str:
        return p.relative_to(self.x).as_posix()

    def add_attachment(self, name: str, data: bytes):
        safe = re.sub(r"[^\w.\- ]+", "_", Path(name).name).strip() or "attachment"
        dest = self.path("attachments", safe)
        k = 2
        while dest.exists():
            dest = dest.with_name(f"{Path(safe).stem}-{k}{Path(safe).suffix}")
            k += 1
        dest.write_bytes(data)
        self.children.append({"name": dest.name, "path": self.relx(dest)})
        self.flag("attachments", dest.name)
        return dest

    def add_image(self, p: Path, where: str, vision: str):
        try:
            with Image.open(p) as im:
                w, h = im.size
        except Exception:
            self.flag("unreadable_image", p.name)
            return
        if vision == "required" and (w < 120 or h < 120):
            vision = "useful"
        self.images.append({"path": self.relx(p), "where": where, "vision": vision, "w": w, "h": h})


def prefix_for(part):
    return f"{slugify(part, 40)}-" if part else ""


def save_render(pix_or_img, dest: Path) -> tuple[int, int]:
    if isinstance(pix_or_img, pymupdf.Pixmap):
        pix_or_img.save(dest)
        return pix_or_img.width, pix_or_img.height
    pix_or_img.save(dest)
    return pix_or_img.size


def make_sheets(doc: Doc, items: list[tuple[str, Path]], per_sheet: int = 6, cols: int = 3,
                thumb_w: int = 600):
    """Contact sheets: several pages per image, labelled, for a cheap overview."""
    if len(items) < 2:
        return
    try:
        font = ImageFont.load_default(size=22)
    except TypeError:
        font = ImageFont.load_default()
    for s in range(0, len(items), per_sheet):
        chunk = items[s:s + per_sheet]
        thumbs = []
        for label, p in chunk:
            with Image.open(p) as im:
                im = im.convert("RGB")
                im.thumbnail((thumb_w, thumb_w * 2))
                thumbs.append((label, im.copy()))
        th = max(t.size[1] for _, t in thumbs)
        rows = (len(thumbs) + cols - 1) // cols
        ncols = min(cols, len(thumbs))
        sheet = Image.new("RGB", (ncols * (thumb_w + 10) + 10, rows * (th + 40) + 10), "white")
        draw = ImageDraw.Draw(sheet)
        for i, (label, t) in enumerate(thumbs):
            x = 10 + (i % cols) * (thumb_w + 10)
            y = 10 + (i // cols) * (th + 40)
            draw.text((x, y), label, fill="black", font=font)
            sheet.paste(t, (x, y + 30))
            draw.rectangle([x - 1, y + 29, x + t.size[0], y + 30 + t.size[1]], outline="gray")
        dest = doc.path("sheets", f"sheet-{s // per_sheet + 1:02d}.png")
        sheet.save(dest)
        doc.sheets.append(doc.relx(dest))


def md_cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        v = format(v, ".10g")
    elif isinstance(v, datetime):
        v = v.isoformat(sep=" ").removesuffix(" 00:00:00")
    return str(v).replace("|", "\\|").replace("\r", "").replace("\n", "<br>").strip()


def md_table(rows: list[list], header: bool = True) -> str:
    rows = [[md_cell(c) for c in r] for r in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    if not header:
        rows.insert(0, [f"col{i + 1}" for i in range(n)])
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def xml_paragraph_text(data: bytes) -> str:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return ""
    paras = []
    for el in root.iter():
        if el.tag.endswith("}p"):
            t = "".join(x.text or "" for x in el.iter() if x.tag.endswith("}t"))
            if t.strip():
                paras.append(t.strip())
    return "\n".join(paras)


# ----------------------------------------------------------------------------- charts

def _cache_values(el):
    if el is None:
        return []
    for cache in el.iter():
        tag = cache.tag.replace(C_NS, "")
        if tag in ("strCache", "numCache", "strLit", "numLit"):
            pts = []
            for pt in cache.findall(C_NS + "pt"):
                v = pt.find(C_NS + "v")
                pts.append((int(pt.get("idx", "0")), v.text if v is not None else ""))
            return [v for _, v in sorted(pts)]
        if tag == "multiLvlStrCache":
            lvls = cache.findall(C_NS + "lvl")
            if lvls:
                pts = []
                for pt in lvls[0].findall(C_NS + "pt"):
                    v = pt.find(C_NS + "v")
                    pts.append((int(pt.get("idx", "0")), v.text if v is not None else ""))
                return [v for _, v in sorted(pts)]
    direct = el.find(C_NS + "v")
    return [direct.text] if direct is not None and direct.text else []


def chart_xml_to_md(data: bytes):
    """Chart title, axis titles and the cached series values. Returns (markdown, has_values)."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return "**Chart** (could not be parsed)", False
    chart = root.find(C_NS + "chart")
    if chart is None:
        return "**Chart** (empty)", False

    def title_of(el):
        t = el.find(C_NS + "title") if el is not None else None
        return " ".join((x.text or "") for x in t.iter(A_NS + "t")).strip() if t is not None else ""

    title = title_of(chart)
    plot_area = chart.find(C_NS + "plotArea")
    out = [f"**Chart{': ' + title if title else ''}** (values read from the file)"]
    has_values = False
    if plot_area is None:
        return out[0], False
    axes = []
    for ax in plot_area:
        tag = ax.tag.replace(C_NS, "")
        if tag in ("valAx", "catAx", "dateAx", "serAx"):
            t = title_of(ax)
            pos = ax.find(C_NS + "axPos")
            if t:
                axes.append(f"{tag[:-2]} axis ({pos.get('val') if pos is not None else '?'}): {t}")
    if axes:
        out.append("Axis titles: " + "; ".join(axes))
    for plot in plot_area:
        ptype = plot.tag.replace(C_NS, "")
        if not ptype.endswith("Chart"):
            continue
        series = []
        for ser in plot.findall(C_NS + "ser"):
            name = " ".join(_cache_values(ser.find(C_NS + "tx"))) or "series"
            cats = _cache_values(ser.find(C_NS + "cat")) or _cache_values(ser.find(C_NS + "xVal"))
            vals = _cache_values(ser.find(C_NS + "val")) or _cache_values(ser.find(C_NS + "yVal"))
            ref = ser.find(f".//{C_NS}val/{C_NS}numRef/{C_NS}f")
            series.append((name, cats, vals, ref.text if ref is not None else None))
            has_values = has_values or bool(vals)
        out.append(f"Type: {ptype}, {len(series)} series")
        if not series:
            continue
        cats0 = series[0][1]
        if all(s[1] == cats0 for s in series) and any(s[2] for s in series):
            n = max(len(cats0), max(len(s[2]) for s in series))
            rows = [["Category"] + [s[0] for s in series]]
            for i in range(min(n, MAX_TABLE_ROWS)):
                rows.append([cats0[i] if i < len(cats0) else i + 1]
                            + [s[2][i] if i < len(s[2]) else "" for s in series])
            out.append(md_table(rows))
        else:
            for name, cats, vals, _ in series:
                rows = [["x / category", name]]
                for i in range(min(max(len(cats), len(vals)), MAX_TABLE_ROWS)):
                    rows.append([cats[i] if i < len(cats) else i + 1, vals[i] if i < len(vals) else ""])
                out.append(md_table(rows))
        refs = [f"{s[0]}: `{s[3]}`" for s in series if s[3]]
        if refs:
            out.append("Data references: " + "; ".join(refs))
    return "\n\n".join(out), has_values


# ----------------------------------------------------------------------------- PDF

def garbled_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    bad = sum(1 for c in chars if c == "\ufffd" or 0xE000 <= ord(c) <= 0xF8FF
              or unicodedata.category(c) in ("Cc", "Co", "Cs"))
    return bad / len(chars)


def merge_rects(rects, gap=8):
    rects = [pymupdf.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        out = []
        while rects:
            r = rects.pop()
            grown = pymupdf.Rect(r.x0 - gap, r.y0 - gap, r.x1 + gap, r.y1 + gap)
            i = 0
            while i < len(rects):
                if grown.intersects(rects[i]):
                    r |= rects.pop(i)
                    grown = pymupdf.Rect(r.x0 - gap, r.y0 - gap, r.x1 + gap, r.y1 + gap)
                    changed = True
                else:
                    i += 1
            out.append(r)
        rects = out
    return rects


def pdf_page_figures(page, tables):
    area = page.rect.width * page.rect.height
    try:
        drawing_rects = list(page.cluster_drawings())
    except Exception:
        drawing_rects = []
    table_rects = [pymupdf.Rect(t.bbox) for t in tables]

    def in_table(r):
        return any((r & t).get_area() > 0.7 * max(r.get_area(), 1) for t in table_rects)

    drawing_rects = [r for r in drawing_rects if not in_table(r)
                     and not (r.width < 20 or r.height < 20)]
    image_rects = []
    try:
        for info in page.get_image_info():
            r = pymupdf.Rect(info["bbox"]) & page.rect
            if r.get_area() > 0.01 * area:
                image_rects.append(r)
    except Exception:
        pass
    merged = merge_rects(drawing_rects + image_rects)
    figures = [r & page.rect for r in merged
               if r.width >= 40 and r.height >= 40 and r.get_area() > 0.03 * area]
    full = [r for r in figures if r.get_area() > 0.85 * area]
    figures = [r for r in figures if r.get_area() <= 0.85 * area]
    figures.sort(key=lambda r: (round(r.y0 / 20), r.x0))
    return figures[:6], bool(full), bool(drawing_rects or image_rects)


def render_page(page, dest: Path, long_side=RENDER_LONG_SIDE, clip=None):
    r = clip or page.rect
    zoom = long_side / max(r.width, r.height)
    if clip is not None:
        zoom = min(5.0, max(1.5, zoom))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
    return save_render(pix, dest)


def extract_pdf(doc: Doc, path: Path, part=None, with_text=True, render_all=None, renders_only=False):
    """PDF pages: text, tables, annotations, figure crops, renders. Returns page count or None.

    with_text=False: the text comes from a paired Office file; the PDF only gives
    page images, page flags and a page map. renders_only: page images, nothing else.
    """
    try:
        pdf = pymupdf.open(path)
    except Exception as e:
        doc.flag("unreadable", f"{path.name}: {e}")
        doc.w(f"[could not open {path.name}: {e}]")
        return None
    if pdf.needs_pass and not pdf.authenticate(""):
        doc.flag("password_protected", path.name)
        doc.w(f"[{path.name} is password-protected]")
        return None
    pre = prefix_for(part)
    if renders_only:
        renders = []
        for i, page in enumerate(pdf, 1):
            dest = doc.path("pages", f"{pre}p{i:03d}.png")
            render_page(page, dest)
            renders.append(dest)
        return renders

    doc.formats.append("pdf")
    meta = pdf.metadata or {}
    producer = f"{meta.get('producer') or ''} {meta.get('creator') or ''}".strip()
    conf = "low" if re.search(r"google|skia|chrom", producer, re.I) else "medium"
    doc.date(parse_pdf_date(meta.get("creationDate")), "metadata", conf,
             f"PDF creation date ({producer or 'unknown producer'})")
    if meta.get("author"):
        doc.authors.add(meta["author"].strip())

    toc = pdf.get_toc(simple=True)
    if toc:
        doc.outline += [{"level": lvl, "title": t, "page": p, "part": part} for lvl, t, p in toc]
        if with_text:
            doc.w("**Outline (PDF bookmarks):**")
            doc.w()
            for lvl, t, p in toc[:300]:
                doc.w(f"{'  ' * (lvl - 1)}- {t} (p.{p})")
            doc.w()

    landscape = sum(1 for p in pdf if p.rect.width > p.rect.height)
    slide_like = pdf.page_count >= 3 and landscape >= 0.8 * pdf.page_count
    doc.slide_like = doc.slide_like or slide_like
    if render_all is None:
        render_all = slide_like
    if part is None and with_text:
        doc.anchors = "pages"

    page_map = []
    sheet_items = []
    for i, page in enumerate(pdf, 1):
        text = page.get_text("text")
        chars = len(text.strip())
        flags = []
        try:
            tables = page.find_tables().tables
        except Exception:
            tables = []
        figures, full_image, has_visuals = pdf_page_figures(page, tables)
        g = garbled_ratio(text)
        if chars < 20 and (has_visuals or full_image):
            flags.append("no_text_layer")
        elif chars < 20:
            flags.append("blank")
        if g > 0.15:
            flags.append("garbled_text")
        if figures:
            flags.append("figure")
        if full_image and chars >= 20:
            flags.append("full_page_image")
        if tables:
            flags.append("table")
        annots = []
        try:
            for a in page.annots() or []:
                atype = a.type[1]
                if atype in ("Link", "Widget", "Popup"):
                    continue
                info = a.info or {}
                content = (info.get("content") or "").strip()
                author = (info.get("title") or "").strip()
                quoted = ""
                if atype in ("Highlight", "Underline", "StrikeOut", "Squiggly"):
                    quoted = page.get_textbox(a.rect).strip()
                if atype == "FileAttachment":
                    try:
                        doc.add_attachment(a.file_info.get("filename") or "annotation-file", a.get_file())
                    except Exception:
                        pass
                if content or quoted:
                    annots.append(f"> [PDF annotation: {atype}{' by ' + author if author else ''}] "
                                  + (f"“{quoted}” " if quoted else "") + (f"— {content}" if content else ""))
        except Exception:
            pass
        if annots:
            flags.append("annotations")
        for link in page.get_links():
            if link.get("uri"):
                doc.links.add(link["uri"])

        required = bool({"no_text_layer", "garbled_text", "figure"} & set(flags))
        useful = bool({"table", "full_page_image", "annotations"} & set(flags)) or (chars < 200 and has_visuals)
        vision = "required" if required else "useful" if useful else "no"
        entry = {"part": part, "n": i, "chars": chars, "vision": vision, "flags": flags,
                 "render": None, "figures": []}
        if render_all or vision != "no":
            dest = doc.path("pages", f"{pre}p{i:03d}.png")
            entry["w"], entry["h"] = render_page(page, dest)
            entry["render"] = doc.relx(dest)
            sheet_items.append((f"p.{i}", dest))
        for k, r in enumerate(figures, 1):
            clip = pymupdf.Rect(r.x0 - 6, r.y0 - 6, r.x1 + 6, r.y1 + 6) & page.rect
            dest = doc.path("figures", f"{pre}p{i:03d}-f{k}.png")
            fw, fh = render_page(page, dest, CROP_LONG_SIDE, clip)
            entry["figures"].append({"path": doc.relx(dest), "w": fw, "h": fh,
                                     "bbox": [round(v, 1) for v in clip]})
        for f in flags:
            doc.flag(f, f"{part + ' ' if part else ''}p.{i}")
        doc.pages.append(entry)

        if with_text:
            doc.w(f"<!-- p.{i} -->")
            if "no_text_layer" in flags:
                doc.w(f"[no text layer: read the page image {entry['render']}]")
            elif text.strip():
                doc.w(text.rstrip())
            for t in tables:
                try:
                    tmd = t.to_markdown().strip()
                except Exception:
                    tmd = ""
                if tmd:
                    doc.w()
                    doc.w(f"<!-- table auto-detected on p.{i}; its text also appears above -->")
                    doc.w(tmd)
            if annots:
                doc.w()
                doc.lines += annots
            doc.w()
        else:
            first = re.sub(r"\s+", " ", text.strip())[:90]
            page_map.append(f"- p.{i}: {first or '[no text]'}")

    if not with_text and page_map:
        doc.tail.append("## Page map of the paired PDF")
        doc.tail.append("")
        doc.tail.append("First words of each page, to place `<!-- p.N -->` anchors in the "
                        "converted text when the layout makes it possible.")
        doc.tail.append("")
        doc.tail += page_map
        doc.tail.append("")
    if slide_like and len(sheet_items) == pdf.page_count:
        make_sheets(doc, sheet_items)

    try:
        for k in range(pdf.embfile_count()):
            info = pdf.embfile_info(k)
            doc.add_attachment(info.get("filename") or info.get("name") or f"embedded-{k}",
                               pdf.embfile_get(k))
    except Exception:
        pass
    return pdf.page_count


# ----------------------------------------------------------------------------- LibreOffice

def soffice_convert(doc: Doc, path: Path, fmt: str):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return None
    outdir = doc.x / "converted"
    outdir.mkdir(parents=True, exist_ok=True)
    profile = (doc.x.parent.parent / "lo-profile").resolve()
    try:
        subprocess.run([exe, f"-env:UserInstallation={profile.as_uri()}", "--headless",
                        "--convert-to", fmt, "--outdir", str(outdir), str(path)],
                       capture_output=True, timeout=300, check=False)
    except subprocess.TimeoutExpired:
        return None
    result = outdir / f"{path.stem}.{fmt.split(':')[0]}"
    return result if result.exists() else None


# ----------------------------------------------------------------------------- PPTX

def extract_pptx(doc: Doc, path: Path, part=None, pdf_path=None):
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE as T

    try:
        prs = Presentation(str(path))
    except Exception as e:
        doc.flag("unreadable", f"{path.name}: {e}")
        doc.w(f"[could not open {path.name}: {e}]")
        return
    doc.formats.append("pptx")
    doc.slide_like = True
    if part is None:
        doc.anchors = "pages"
    cp = prs.core_properties
    doc.date(iso(cp.created), "metadata", "low", "pptx creation date")
    if cp.author:
        doc.authors.add(cp.author)
    pre = prefix_for(part)
    slide_area = (prs.slide_width or 1) * (prs.slide_height or 1)
    slides = list(prs.slides)
    hidden = [s._element.get("show") in ("0", "false") for s in slides]

    render_pdf, rendered_by_lo = pdf_path, False
    if render_pdf is None:
        render_pdf = soffice_convert(doc, path, "pdf")
        rendered_by_lo = render_pdf is not None
    renders = extract_pdf(doc, render_pdf, part, renders_only=True) if render_pdf else None
    mapping = {}
    if renders:
        visible = [i for i, h in enumerate(hidden) if not h]
        if len(renders) == len(slides):
            mapping = {i: renders[i] for i in range(len(slides))}
        elif len(renders) == len(visible):
            mapping = {i: renders[k] for k, i in enumerate(visible)}
        else:
            doc.flag("pair_mismatch", f"{len(slides)} slides, {len(renders)} PDF pages")
    if rendered_by_lo:
        doc.flag("rendered_with_libreoffice", path.name)
    if not renders:
        doc.flag("no_render", path.name)

    def safe_type(shp):
        try:
            return shp.shape_type
        except Exception:
            return None

    sheet_items = []
    for idx, slide in enumerate(slides, 1):
        stats = Counter()
        body = []
        flags = []

        def walk(shapes, depth=0):
            for shp in sorted(shapes, key=lambda s: ((s.top or 0) // 50000, s.left or 0)):
                st = safe_type(shp)
                xml = shp._element.xml if hasattr(shp._element, "xml") else ""
                if st == T.GROUP:
                    stats["groups"] += 1
                    walk(shp.shapes, depth + 1)
                    continue
                if getattr(shp, "has_chart", False) and shp.has_chart:
                    md, has_values = chart_xml_to_md(shp.chart.part.blob)
                    body.append(md)
                    stats["charts" if has_values else "charts_empty"] += 1
                    continue
                if getattr(shp, "has_table", False) and shp.has_table:
                    rows = [[c.text for c in r.cells] for r in shp.table.rows]
                    body.append(md_table(rows))
                    stats["tables"] += 1
                    continue
                if "drawingml/2006/diagram" in xml:
                    stats["smartart"] += 1
                    continue
                if st in (T.MEDIA, T.WEB_VIDEO) or "<p:videoFile" in xml or "<a:videoFile" in xml:
                    stats["media"] += 1
                if st in (T.EMBEDDED_OLE_OBJECT, T.LINKED_OLE_OBJECT):
                    stats["ole"] += 1
                if shp.__class__.__name__ == "Connector" or st == T.LINE:
                    stats["connectors"] += 1
                    continue
                image = None
                try:
                    image = shp.image if st in (T.PICTURE, T.PLACEHOLDER, T.LINKED_PICTURE) else None
                except Exception:
                    image = None
                if image is not None:
                    ratio = (shp.width or 0) * (shp.height or 0) / slide_area
                    stats["pictures_big" if ratio > 0.04 else "pictures_small"] += 1
                    if ratio > 0.04:
                        dest = doc.path("media", f"{pre}s{idx:03d}-{stats['pictures_big']}.{image.ext}")
                        dest.write_bytes(image.blob)
                        body.append(f"[picture: media/{dest.name}]")
                if getattr(shp, "has_text_frame", False) and shp.has_text_frame:
                    if shp == slide.shapes.title:
                        continue
                    paras = [(p.level, "".join(r.text for r in p.runs).replace("\x0b", " ").strip())
                             for p in shp.text_frame.paragraphs]
                    for p in shp.text_frame.paragraphs:
                        for r in p.runs:
                            try:
                                if r.hyperlink and r.hyperlink.address:
                                    doc.links.add(r.hyperlink.address)
                            except Exception:
                                pass
                    paras = [(lvl, t) for lvl, t in paras if t]
                    if not paras:
                        if st in (T.AUTO_SHAPE, T.FREEFORM):
                            stats["shapes"] += 1
                        continue
                    stats["text_shapes"] += 1
                    if len(paras) == 1:
                        body.append(paras[0][1])
                    else:
                        body.append("\n".join(f"{'  ' * lvl}- {t}" for lvl, t in paras))
                elif st in (T.AUTO_SHAPE, T.FREEFORM):
                    stats["shapes"] += 1

        walk(slide.shapes)

        smartart_text, comments = [], []
        for rel in slide.part.rels.values():
            rt = rel.reltype.lower()
            try:
                if rt.endswith("/diagramdata"):
                    smartart_text.append(xml_paragraph_text(rel.target_part.blob))
                elif "comment" in rt and "author" not in rt:
                    comments.append(xml_paragraph_text(rel.target_part.blob))
            except Exception:
                pass
        notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes = slide.notes_slide.notes_text_frame.text.strip()

        if hidden[idx - 1]:
            flags.append("hidden_slide")
        if notes:
            flags.append("speaker_notes")
        if any(comments):
            flags.append("slide_comments")
        if stats["charts"]:
            flags.append("chart_data")
        if stats["charts_empty"]:
            flags.append("chart_no_cached_data")
        if stats["smartart"]:
            flags.append("smartart")
        if stats["connectors"] >= 2 or stats["shapes"] >= 4:
            flags.append("diagram")
        if stats["pictures_big"]:
            flags.append("picture")
        if stats["media"]:
            flags.append("media")
        if stats["ole"]:
            flags.append("ole_object")
        if stats["tables"]:
            flags.append("table")
        visual = {"chart_no_cached_data", "smartart", "diagram", "picture", "ole_object"}
        no_text = not body and not (slide.shapes.title is not None and slide.shapes.title.has_text_frame
                                    and slide.shapes.title.text_frame.text.strip())
        if visual & set(flags) or (no_text and renders):
            vision = "required"
        elif {"chart_data", "table", "media"} & set(flags) or stats["groups"] or stats["pictures_small"]:
            vision = "useful"
        else:
            vision = "no"
        entry = {"part": part, "n": idx, "chars": sum(len(b) for b in body), "vision": vision,
                 "flags": flags, "render": None, "figures": []}
        if idx - 1 in mapping:
            entry["render"] = doc.relx(mapping[idx - 1])
            with Image.open(mapping[idx - 1]) as im:
                entry["w"], entry["h"] = im.size
            sheet_items.append((f"slide {idx}", mapping[idx - 1]))
        for f in flags:
            doc.flag(f, f"{part + ' ' if part else ''}slide {idx}")
        doc.pages.append(entry)

        title = ""
        if slide.shapes.title is not None and slide.shapes.title.has_text_frame:
            title = slide.shapes.title.text_frame.text.replace("\x0b", " ").strip()
        doc.w(f"<!-- p.{idx} -->")
        doc.w(f"### Slide {idx}{' (hidden)' if hidden[idx - 1] else ''}{': ' + title if title else ''}")
        doc.w()
        for b in body:
            doc.w(b)
            doc.w()
        for t in smartart_text:
            if t:
                doc.w("SmartArt text (box order may not match the diagram):")
                doc.w(t)
                doc.w()
        if notes:
            doc.w("**Speaker notes:**")
            doc.w()
            doc.w(notes)
            doc.w()
        for c in comments:
            if c:
                doc.w("**Slide comments:**")
                doc.w(c)
                doc.w()
    if sheet_items:
        make_sheets(doc, sheet_items)


# ----------------------------------------------------------------------------- DOCX

def extract_docx(doc: Doc, path: Path, part=None, pdf_path=None):
    doc.formats.append("docx")
    media_dir = f"media/{slugify(part, 40)}" if part else "media"
    try:
        r = subprocess.run(["pandoc", "-f", "docx", "-t", "markdown", "--wrap=none",
                            "--track-changes=all", f"--extract-media={media_dir}", str(path.resolve())],
                           cwd=doc.x, capture_output=True, text=True, timeout=600)
        text = r.stdout
        if r.returncode != 0:
            doc.flag("unreadable", f"{path.name}: pandoc failed: {r.stderr.strip()[:200]}")
    except Exception as e:
        text = ""
        doc.flag("unreadable", f"{path.name}: {e}")
    if ".comment-start" in text:
        doc.flag("comments", f"{text.count('.comment-start')} comments")
    if ".insertion" in text or ".deletion" in text:
        doc.flag("tracked_changes",
                 f"{text.count('.insertion')} insertions, {text.count('.deletion')} deletions")

    for ref in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text):
        p = doc.x / ref
        if p.suffix.lower() in (".emf", ".wmf") and p.exists():
            conv = soffice_convert(doc, p, "png")
            if conv:
                newp = p.with_suffix(".png")
                shutil.move(conv, newp)
                text = text.replace(ref, Path(ref).with_suffix(".png").as_posix())
                p = newp
        if p.exists():
            doc.add_image(p, f"inline image ({part or path.name})", "required")

    doc.w(text.strip())
    doc.w()

    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            hf = sorted(n for n in names if re.match(r"word/(header|footer)\d*\.xml$", n))
            texts = []
            for n in hf:
                t = xml_paragraph_text(z.read(n))
                if t and t not in texts:
                    texts.append(t)
            if texts:
                doc.flag("headers_footers", path.name)
                doc.tail.append(f"## Headers and footers ({path.name})")
                doc.tail.append("")
                doc.tail += [f"- {t}" for t in texts]
                doc.tail.append("")
            charts = sorted((n for n in names if re.match(r"word/charts/chart\d+\.xml$", n)),
                            key=natural_key)
            if charts:
                doc.tail.append(f"## Charts embedded in {path.name} (data from the file; "
                                "their position in the text is not known)")
                doc.tail.append("")
                for n in charts:
                    md, has_values = chart_xml_to_md(z.read(n))
                    doc.flag("chart_data" if has_values else "chart_no_cached_data", n)
                    doc.tail += [md, ""]
            for n in names:
                if n.startswith("word/embeddings/"):
                    ext = Path(n).suffix.lower()
                    if ext in OFFICE_EXT | PDF_EXT:
                        doc.add_attachment(Path(n).name, z.read(n))
                    else:
                        doc.flag("ole_object", Path(n).name)
            if "docProps/core.xml" in names:
                core = z.read("docProps/core.xml").decode("utf-8", "replace")
                m = re.search(r"<dcterms:created[^>]*>([^<]+)<", core)
                if m:
                    doc.date(m.group(1)[:10], "metadata", "low", "docx creation date")
                m = re.search(r"<dc:creator>([^<]+)<", core)
                if m:
                    doc.authors.add(m.group(1).strip())
    except zipfile.BadZipFile:
        doc.flag("unreadable", f"{path.name}: not a valid docx")

    if pdf_path is not None:
        n = extract_pdf(doc, pdf_path, part, with_text=False, render_all=False)
        if n and part is None:
            doc.anchors = "optional-pages"


# ----------------------------------------------------------------------------- spreadsheets

def extract_xlsx(doc: Doc, path: Path, part=None, pdf_path=None):
    import openpyxl

    doc.formats.append("xlsx")
    pre = prefix_for(part)
    try:
        big = path.stat().st_size > 30_000_000
        wb_v = openpyxl.load_workbook(path, data_only=True, read_only=big)
        wb_f = openpyxl.load_workbook(path, data_only=False, read_only=big)
    except Exception as e:
        doc.flag("unreadable", f"{path.name}: {e}")
        doc.w(f"[could not open {path.name}: {e}]")
        return
    try:
        doc.date(iso(wb_v.properties.created), "metadata", "low", "xlsx creation date")
        if wb_v.properties.creator:
            doc.authors.add(wb_v.properties.creator)
    except Exception:
        pass
    for ws in wb_v.worksheets:
        wf = wb_f[ws.title]
        state = getattr(ws, "sheet_state", "visible")
        if state != "visible":
            doc.flag("hidden_sheet", ws.title)
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        while rows and not any(v not in (None, "") for v in rows[-1]):
            rows.pop()
        ncols = 0
        for r in rows:
            for j in range(len(r) - 1, -1, -1):
                if r[j] not in (None, ""):
                    ncols = max(ncols, j + 1)
                    break
        rows = [r[:ncols] for r in rows]
        doc.w(f"## Sheet: {ws.title}{' (' + state + ')' if state != 'visible' else ''}")
        doc.w()
        doc.w(f"{len(rows)} rows × {ncols} columns used.")
        if not rows:
            doc.w("[empty sheet]")
            doc.w()
            continue
        csv_path = doc.path("data", f"{pre}{slugify(ws.title, 40)}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([[md_cell(c).replace("<br>", "\n") for c in r] for r in rows])
        shown = [r[:MAX_TABLE_COLS] for r in rows[:MAX_TABLE_ROWS]]
        if len(rows) > MAX_TABLE_ROWS or ncols > MAX_TABLE_COLS:
            doc.flag("truncated_table", ws.title)
            doc.w(f"Showing the first {len(shown)} rows and {min(ncols, MAX_TABLE_COLS)} columns; "
                  f"full sheet: {doc.relx(csv_path)}")
        doc.w()
        doc.w(md_table(shown, header=False))
        doc.w()
        if not big:
            hidden_rows = [i for i, d in ws.row_dimensions.items() if d.hidden]
            hidden_cols = [k for k, d in ws.column_dimensions.items() if d.hidden]
            if hidden_rows or hidden_cols:
                doc.flag("hidden_rows_cols", ws.title)
                doc.w(f"Hidden rows: {hidden_rows[:50] or 'none'}; hidden columns: {hidden_cols[:50] or 'none'}")
            merged = [str(r) for r in ws.merged_cells.ranges]
            if merged:
                doc.w(f"Merged cells: {', '.join(merged[:40])}")
            try:
                if len(list(ws.conditional_formatting)):
                    doc.flag("conditional_formatting", ws.title)
            except Exception:
                pass
        formulas, missing = [], 0
        cell_comments = []
        for row in wf.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    v = ws[c.coordinate].value
                    if v is None:
                        missing += 1
                    if len(formulas) < 15:
                        formulas.append(f"- {c.coordinate}: `{c.value}` → {md_cell(v) or '(no stored value)'}")
                    elif not big:
                        formulas.append(None)
                if not big and getattr(c, "comment", None):
                    cell_comments.append(f"- {c.coordinate}: {c.comment.text.strip()}")
        n_formulas = len(formulas)
        if n_formulas:
            doc.flag("formulas", ws.title)
            doc.w(f"Formulas: {n_formulas} cells. Samples:")
            doc.lines += [f for f in formulas if f]
        if missing:
            doc.flag("formula_no_value", f"{ws.title}: {missing} cells")
        if cell_comments:
            doc.flag("cell_comments", ws.title)
            doc.w("Cell comments:")
            doc.lines += cell_comments[:100]
        doc.w()

    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            charts = sorted((n for n in names if re.match(r"xl/charts/chart\d+\.xml$", n)), key=natural_key)
            if charts:
                doc.w("## Charts (data from the file; the sheet they sit on is not recorded)")
                doc.w()
                for n in charts:
                    md, has_values = chart_xml_to_md(z.read(n))
                    doc.flag("chart_data" if has_values else "chart_no_cached_data", n)
                    doc.w(md)
                    doc.w()
            if any(n.startswith("xl/pivotTables/") for n in names):
                doc.flag("pivot_table", path.name)
    except zipfile.BadZipFile:
        pass
    if pdf_path is not None:
        extract_pdf(doc, pdf_path, part, with_text=False, render_all=True)


def extract_csv(doc: Doc, path: Path, part=None):
    doc.formats.append("csv")
    text = read_text(path)
    try:
        dialect = csv.Sniffer().sniff(text[:5000], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    doc.w(f"{len(rows)} rows.")
    if len(rows) > MAX_TABLE_ROWS:
        doc.flag("truncated_table", path.name)
        doc.w(f"Showing the first {MAX_TABLE_ROWS} rows; full file: the source.")
    doc.w()
    doc.w(md_table([r[:MAX_TABLE_COLS] for r in rows[:MAX_TABLE_ROWS]]))
    doc.w()


# ----------------------------------------------------------------------------- images, text, mail

def extract_image(doc: Doc, path: Path, part=None):
    doc.formats.append("image")
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)
    except Exception:
        doc.flag("unreadable_image", path.name)
        doc.w(f"[image {path.name} could not be decoded: ask the user for a PNG or JPEG]")
        return
    try:
        exif = im.getexif()
        raw = exif.get_ifd(0x8769).get(36867) or exif.get(306)
        if raw:
            doc.date(raw[:10].replace(":", "-"), "metadata", "high", "photo EXIF date")
    except Exception:
        pass
    pre = prefix_for(part)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    jpg = path.suffix.lower() in (".jpg", ".jpeg")
    ext = ".jpg" if jpg else ".png"
    w, h = im.size
    tiles = []
    if h > 2.0 * w:
        doc.flag("tall_image", path.name)
        tile_h = int(w * 1.3)
        step = int(tile_h * 0.85)
        y = 0
        while True:
            box = (0, y, w, min(y + tile_h, h))
            tiles.append(im.crop(box))
            if y + tile_h >= h:
                break
            y += step
    else:
        tiles.append(im)
    for k, t in enumerate(tiles, 1):
        t = t.copy()
        t.thumbnail((2000 if len(tiles) == 1 else 1200, 2000))
        name = f"{pre}image{ext}" if len(tiles) == 1 else f"{pre}tile-{k:02d}{ext}"
        dest = doc.path("pages", name)
        t.save(dest, quality=90) if jpg else t.save(dest)
        doc.pages.append({"part": part, "n": k, "chars": 0, "vision": "required",
                          "flags": ["image"] + (["tile"] if len(tiles) > 1 else []),
                          "render": doc.relx(dest), "w": t.size[0], "h": t.size[1], "figures": []})
    doc.w(f"[image: {w}×{h} px, {len(tiles)} {'tiles' if len(tiles) > 1 else 'file'} in pages/ — "
          "content only readable by vision]")
    doc.w()


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def extract_text(doc: Doc, path: Path, part=None):
    doc.formats.append(path.suffix.lower().lstrip(".") or "text")
    text = read_text(path)
    if len(text) > MAX_TEXT_CHARS:
        doc.flag("truncated_text", path.name)
        text = text[:MAX_TEXT_CHARS] + "\n\n[... truncated by extract.py ...]"
    for ref in set(re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text)):
        src = (path.parent / ref)
        if not ref.startswith(("http:", "https:", "data:")) and src.is_file():
            dest = doc.path("media", f"{prefix_for(part)}{src.name}")
            shutil.copy2(src, dest)
            doc.flag("linked_images", src.name)
            doc.add_image(dest, f"linked from {path.name}", "required")
            text = text.replace(f"]({ref})", f"]({doc.relx(dest)})")
    if path.suffix.lower() == ".svg":
        doc.flag("unsupported_format", f"{path.name}: SVG kept as XML; its labels are in <text> elements")
    doc.w(text.rstrip())
    doc.w()


def html_to_md(html: str) -> str:
    try:
        r = subprocess.run(["pandoc", "-f", "html", "-t", "markdown", "--wrap=none"],
                           input=html, capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            return r.stdout
    except Exception:
        pass
    return re.sub(r"<[^>]+>", " ", html)


def extract_html(doc: Doc, path: Path, part=None):
    doc.formats.append("html")
    doc.w(html_to_md(read_text(path)).strip())
    doc.w()


def write_message(doc: Doc, msg, part=None, number=None):
    hdr = []
    for h in ("From", "To", "Cc", "Date", "Subject"):
        if msg[h]:
            hdr.append(f"**{h}:** {msg[h]}")
    try:
        dt = email.utils.parsedate_to_datetime(msg["Date"]) if msg["Date"] else None
    except (TypeError, ValueError):
        dt = None
    if dt:
        doc.date(dt.strftime("%Y-%m-%d"), "metadata", "high", "email Date header")
    if number is not None:
        doc.w(f"<!-- message {number} -->")
    doc.w(f"### {'Message ' + str(number) + ': ' if number else ''}{msg['Subject'] or '(no subject)'}")
    doc.w()
    doc.lines += [h + "  " for h in hdr]
    doc.w()
    body = msg.get_body(preferencelist=("plain", "html"))
    content = ""
    if body is not None:
        try:
            content = body.get_content()
        except Exception:
            content = body.get_payload(decode=True).decode("utf-8", "replace")
        if body.get_content_type() == "text/html":
            content = html_to_md(content)
    if re.search(r"^>|^-{2,} ?Original Message|^(On|Le) .{5,80}(wrote|a écrit) ?:|^(From|De) ?: ",
                 content, re.M | re.I):
        doc.flag("quoted_history", msg["Subject"] or "message")
    doc.w(content.strip())
    doc.w()
    for att in msg.iter_attachments():
        name = att.get_filename()
        ctype = att.get_content_type()
        if ctype == "message/rfc822":
            inner = att.get_payload()[0] if isinstance(att.get_payload(), list) else att.get_payload()
            doc.add_attachment((name or "forwarded") + ".eml", inner.as_bytes())
            doc.w(f"[attached email: {name or 'forwarded message'}]")
            continue
        data = att.get_payload(decode=True) or b""
        if ctype.startswith("image/") and (att["Content-ID"] or not name):
            dest = doc.path("media", f"{prefix_for(part)}{slugify(name or 'inline', 40)}"
                            f".{ctype.split('/')[1].replace('jpeg', 'jpg')}")
            dest.write_bytes(data)
            doc.flag("inline_images", dest.name)
            doc.add_image(dest, "inline image of the email", "useful")
            continue
        dest = doc.add_attachment(name or f"attachment.{ctype.split('/')[-1]}", data)
        doc.w(f"[attachment: {dest.name}]")
    doc.w()


def extract_eml(doc: Doc, path: Path, part=None):
    doc.formats.append("eml")
    msg = email.message_from_bytes(path.read_bytes(), policy=policy.default)
    write_message(doc, msg, part)


def extract_mbox(doc: Doc, path: Path, part=None):
    doc.formats.append("mbox")
    for k, m in enumerate(mailbox.mbox(str(path)), 1):
        msg = email.message_from_bytes(m.as_bytes(), policy=policy.default)
        write_message(doc, msg, part, number=k)


def extract_file(doc: Doc, path: Path, part=None, pdf_pair=None):
    ext = path.suffix.lower()
    try:
        if ext in PDF_EXT:
            extract_pdf(doc, path, part)
        elif ext in SLIDES_EXT:
            extract_pptx(doc, path, part, pdf_pair)
        elif ext in DOCX_EXT:
            extract_docx(doc, path, part, pdf_pair)
        elif ext in SHEET_EXT:
            extract_xlsx(doc, path, part, pdf_pair)
        elif ext in LEGACY_EXT:
            conv = soffice_convert(doc, path, LEGACY_EXT[ext])
            if conv is None:
                doc.flag("needs_libreoffice", path.name)
                doc.w(f"[{path.name}: legacy format, LibreOffice conversion failed or unavailable]")
                if pdf_pair is not None:
                    extract_pdf(doc, pdf_pair, part)
            else:
                doc.flag("converted_with_libreoffice", path.name)
                extract_file(doc, conv, part, pdf_pair)
        elif ext in IMAGE_EXT:
            extract_image(doc, path, part)
        elif ext in TABLE_EXT:
            extract_csv(doc, path, part)
        elif ext in HTML_EXT:
            extract_html(doc, path, part)
        elif ext == ".eml":
            extract_eml(doc, path, part)
        elif ext == ".mbox":
            extract_mbox(doc, path, part)
        elif ext in TEXT_EXT:
            extract_text(doc, path, part)
        else:
            head = path.read_bytes()[:4096]
            if b"\x00" not in head and head:
                doc.flag("unsupported_format", f"{path.name}: read as plain text")
                extract_text(doc, path, part)
            else:
                hint = " (save the email as .eml or PDF)" if ext == ".msg" else ""
                doc.flag("unsupported_format", f"{path.name}{hint}")
                doc.w(f"[{path.name}: format not supported by extract.py{hint}]")
    except Exception as e:
        doc.flag("unreadable", f"{path.name}: {type(e).__name__}: {e}")
        doc.w(f"[extraction of {path.name} failed: {type(e).__name__}: {e}]")


# ----------------------------------------------------------------------------- units

def extract_unit(unit: Unit, xdir: Path, input_dir: Path, sha: str, slug: str, sources: list) -> dict:
    if xdir.exists():
        shutil.rmtree(xdir)
    xdir.mkdir(parents=True)
    doc = Doc(unit, xdir, input_dir)

    if unit.kind == "group":
        doc.anchors = "parts"
        for f in unit.files:
            name = f.relative_to(unit.group_root).as_posix()
            doc.w(f"<!-- part: {name} -->")
            doc.w(f"## Part: {name}")
            doc.w()
            extract_file(doc, f, part=name)
            for value, conf in filename_dates(f.stem):
                doc.date(value, "filename", conf, f"part file name {name}")
    elif unit.kind == "pair":
        extract_file(doc, unit.files[0], pdf_pair=unit.files[1])
    else:
        extract_file(doc, unit.files[0])

    for value, conf in filename_dates(unit.name):
        doc.date(value, "filename", conf, f"name `{unit.name}`")
    for comp in Path(unit.dir_rel).parts:
        if re.fullmatch(r"(19|20)\d{2}", comp):
            doc.date(comp, "path", "low", f"folder `{comp}`")
    if unit.kind != "attachment":
        mtime = min(f.stat().st_mtime for f in unit.files)
        doc.date(datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%d"), "mtime", "low",
                 "file modification time (often the copy or download date)")

    best = None
    if doc.dates:
        best = min(doc.dates, key=lambda d: (DATE_RANK.get((d["source"], d["confidence"]), 9),
                                             d["value"]))
    text = "\n".join(doc.lines).rstrip() + "\n"
    if doc.links:
        doc.tail += ["## Links found in the document", ""] + [f"- {u}" for u in sorted(doc.links)[:200]] + [""]
    if doc.tail:
        text += "\n" + "\n".join(doc.tail).rstrip() + "\n"
    (xdir / "text.md").write_text(text, encoding="utf-8")

    renders_required = [p for p in doc.pages if p["vision"] == "required"]
    img_tokens = sum(image_tokens(p.get("w", 1500), p.get("h", 1100)) for p in renders_required)
    img_tokens += sum(image_tokens(i["w"], i["h"]) for i in doc.images if i["vision"] == "required")
    sample = re.sub(r"<!--.*?-->|[#*>|\[\]]", " ", text)
    sample = re.sub(r"\s+", " ", sample).strip()[:400]
    meta = {
        "key": unit.key, "slug": slug, "kind": unit.kind, "sources": sources, "sha256": sha,
        "formats": sorted(set(doc.formats)), "dir": unit.dir_rel, "parent": unit.parent,
        "anchors": doc.anchors, "slide_like": doc.slide_like,
        "parts": [f.relative_to(unit.group_root).as_posix() for f in unit.files] if unit.kind == "group" else [],
        "date": best, "date_candidates": doc.dates, "authors": sorted(doc.authors),
        "pages": doc.pages, "images": doc.images, "sheets": doc.sheets, "outline": doc.outline,
        "flags": doc.flags, "children": doc.children, "sample": sample,
        "est": {
            "text_chars": len(text),
            "text_tokens": int(len(text) / 3.5),
            "pages": len(doc.pages),
            "images_required": len(renders_required) + sum(1 for i in doc.images if i["vision"] == "required"),
            "images_useful": sum(1 for p in doc.pages if p["vision"] == "useful")
            + sum(1 for i in doc.images if i["vision"] == "useful"),
            "image_tokens_required": img_tokens,
            "sheets": len(doc.sheets),
        },
    }
    save_json(xdir / "meta.json", meta)
    return meta


# ----------------------------------------------------------------------------- corpus

TERM_STOP = {"PDF", "THE", "AND", "OK", "PM", "AM", "II", "III", "IV", "VI", "VII", "TBD", "FYI",
             "NB", "PS", "RE", "TR", "FW", "CC", "BCC", "URL", "HTTP", "HTTPS", "WWW", "COM", "ID",
             "NA", "N/A", "TODO", "QA", "PNG", "JPG", "CSV", "XLSX", "DOCX", "PPTX", "UTC", "LE",
             "LA", "LES", "DE", "DU", "DES", "ET", "EN", "UN", "UNE", "DANS", "POUR", "SUR"}


def corpus_terms(docs: list[dict], xroot: Path, limit=80):
    doc_freq, total = Counter(), Counter()
    for d in docs:
        p = xroot / d["slug"] / "text.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"<!--.*?-->|\]\([^)]*\)|https?://\S+", " ", text)
        found = re.findall(r"\b[A-Z][A-Z0-9]{1,9}s?\b|\b[A-Z][a-z]+[A-Z][A-Za-z0-9]*\b", text)
        found = [t for t in found if t not in TERM_STOP and not t.isdigit()]
        total.update(found)
        doc_freq.update(set(found))
    terms = [t for t in total if doc_freq[t] >= 2 or total[t] >= 5]
    terms.sort(key=lambda t: (-doc_freq[t], -total[t], t))
    return [{"term": t, "docs": doc_freq[t], "count": total[t]} for t in terms[:limit]]


def near_pairs(docs: list[dict], xroot: Path):
    """Unpaired Office file and PDF in the same folder that look like the same document."""
    warnings = []
    by_dir = {}
    for d in docs:
        if d["kind"] in ("single",) and d["formats"] and (set(d["formats"]) & {"pptx", "docx", "pdf"}):
            by_dir.setdefault(d["dir"], []).append(d)
    for items in by_dir.values():
        office = [d for d in items if "pdf" not in d["formats"]]
        pdfs = [d for d in items if "pdf" in d["formats"]]
        for o in office:
            for p in pdfs:
                same_pages = o["est"]["pages"] and o["est"]["pages"] == p["est"]["pages"]
                ratio = difflib.SequenceMatcher(None, o["sample"][:300].lower(),
                                                p["sample"][:300].lower()).ratio()
                if ratio > 0.6 or (same_pages and ratio > 0.3):
                    warnings.append(f"`{o['sources'][0]}` and `{p['sources'][0]}` look like the same "
                                    "document: give them the same base name to pair them")
    return warnings


def write_report(path: Path, inv: dict):
    docs = inv["documents"]
    count = Counter(d["status"] for d in docs)
    lines = [f"# Extraction report ({inv['generated']})", "",
             f"Input: `{inv['input']}`  ", f"Output: `{inv['output']}`", "",
             f"Documents: {len(docs)} (new {count['new']}, changed {count['changed']}, "
             f"unchanged {count['unchanged']})", ""]
    attention = inv["warnings"] + [f"source removed: `{r['key']}` (output `{r['output']}` still exists)"
                                   for r in inv["removed"]]
    attention += [f"output without a source: `{o}`" for o in inv["orphans"]]
    if attention:
        lines += ["## Needs attention", ""] + [f"- {w}" for w in attention] + [""]
    undated = [d["slug"] for d in docs if not d["date"] or d["date"]["source"] == "mtime"]
    if undated:
        lines += ["## Undated (only the file modification time, or nothing)", "",
                  ", ".join(f"`{s}`" for s in undated), ""]
    lines += ["## Documents", "",
              "| slug | status | sources | date (source, confidence) | pages | vision req./useful | ~tokens | flags |",
              "|---|---|---|---|---|---|---|---|"]
    for d in docs:
        dt = d["date"]
        dtxt = f"{dt['value']} ({dt['source']}, {dt['confidence']})" if dt else "unknown"
        est = d["est"]
        tokens = est["text_tokens"] + est["image_tokens_required"]
        lines.append(f"| {d['slug']} | {d['status']} | {'<br>'.join(d['sources'])} | {dtxt} | "
                     f"{est['pages']} | {est['images_required']}/{est['images_useful']} | {tokens:,} | "
                     f"{', '.join(sorted(d['flags']))} |")
    lines += ["", "## Flags", ""]
    used = sorted({f for d in docs for f in d["flags"]})
    lines += [f"- `{f}`: {FLAG_HELP.get(f, '')}" for f in used]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--force", action="store_true", help="extract again even unchanged documents")
    a = ap.parse_args()

    input_dir, out = a.input.resolve(), a.output.resolve()
    if not input_dir.is_dir():
        sys.exit(f"input folder not found: {input_dir}")
    if out == input_dir or input_dir.is_relative_to(out):
        sys.exit("the output folder must not be the input folder or contain it")
    wd = work_dir(out)
    xroot = wd / "extract"
    xroot.mkdir(parents=True, exist_ok=True)
    state = load_json(wd / "state.json", {"version": 1, "slugs": {}})
    slugs: dict = state.setdefault("slugs", {})

    units, warnings = scan(input_dir, out)
    queue = deque(sorted(units, key=lambda u: natural_key(u.key)))
    docs, seen_keys, by_sha = [], set(), {}

    def slug_for(u: Unit) -> str:
        if u.key in slugs:
            return slugs[u.key]
        used = set(slugs.values())
        base = slugify(u.name)
        if u.parent:
            base = f"{slugs[u.parent]}--{slugify(u.name, 40)}"
        cand = base
        if cand in used and u.dir_rel:
            cand = slugify(f"{Path(u.dir_rel).name}-{u.name}")
        k = 2
        while cand in used:
            cand = f"{base}-{k}"
            k += 1
        slugs[u.key] = cand
        return cand

    total = len(queue)
    done = 0
    while queue:
        u = queue.popleft()
        done += 1
        seen_keys.add(u.key)
        slug = slug_for(u)
        hashes = []
        for f in u.files:
            name = f.name if u.kind == "attachment" else f.relative_to(input_dir).as_posix()
            fh = sha256_file(f)
            hashes.append(f"{name}:{fh}")
            if u.kind != "attachment":
                by_sha.setdefault(fh, []).append(name)
        sha = hashlib.sha256("\n".join(sorted(hashes)).encode()).hexdigest()
        xdir = xroot / slug
        meta = load_json(xdir / "meta.json")
        if a.force or meta is None or meta.get("sha256") != sha:
            print(f"[{done}/{total}] extracting {slug} ...", file=sys.stderr, flush=True)
            meta = extract_unit(u, xdir, input_dir, sha, slug, u.rel)
        outs = output_files(out, slug)
        if not outs:
            status = "new"
        else:
            status = "unchanged" if frontmatter_sha(outs[0]) == sha else "changed"
        for c in meta.get("children", []):
            child = Unit(f"{u.key}::{c['name']}", Path(c["name"]).stem, "attachment",
                         [xdir / c["path"]], [f"{u.rel[0]} ▸ {c['name']}"], u.dir_rel, parent=u.key)
            queue.append(child)
            total += 1
        docs.append({
            "slug": slug, "key": u.key, "kind": u.kind, "status": status, "sources": u.rel,
            "sha256": sha, "dir": u.dir_rel, "parent": u.parent,
            "children": [f"{u.key}::{c['name']}" for c in meta.get("children", [])],
            "formats": meta["formats"], "anchors": meta["anchors"], "slide_like": meta["slide_like"],
            "date": meta["date"], "flags": {k: len(v) or 1 for k, v in meta["flags"].items()},
            "est": meta["est"], "sample": meta["sample"][:200], "extract_dir": f"extract/{slug}",
        })

    key_to_slug = {d["key"]: d["slug"] for d in docs}
    for d in docs:
        d["children"] = [key_to_slug[k] for k in d["children"] if k in key_to_slug]
        d["parent"] = key_to_slug.get(d["parent"]) if d["parent"] else None

    removed = []
    for key, slug in list(slugs.items()):
        if key in seen_keys:
            continue
        outs = output_files(out, slug)
        if outs:
            removed.append({"key": key, "slug": slug, "output": outs[0].relative_to(out).as_posix()})
        else:
            del slugs[key]
            shutil.rmtree(xroot / slug, ignore_errors=True)
    current = {d["slug"] for d in docs} | {r["slug"] for r in removed}
    orphans = []
    if (out / DOCS).is_dir():
        for p in sorted((out / DOCS).iterdir()):
            s = p.stem if p.suffix == ".md" else p.name
            if s not in current:
                orphans.append(p.relative_to(out).as_posix())

    for fh, names in by_sha.items():
        if len(names) > 1:
            warnings.append("identical files: " + ", ".join(f"`{n}`" for n in names))
    warnings += near_pairs(docs, xroot)

    inv = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "input": str(input_dir), "output": str(out),
        "documents": docs, "warnings": warnings, "removed": removed, "orphans": orphans,
        "terms": corpus_terms(docs, xroot),
    }
    save_json(wd / "state.json", state)
    save_json(wd / "inventory.json", inv)
    write_report(wd / "report.md", inv)
    count = Counter(d["status"] for d in docs)
    print(f"{len(docs)} documents: {count['new']} new, {count['changed']} changed, "
          f"{count['unchanged']} unchanged; {len(warnings)} warnings, {len(removed)} removed, "
          f"{len(orphans)} orphan outputs.\nReport: {wd / 'report.md'}")


if __name__ == "__main__":
    main()
