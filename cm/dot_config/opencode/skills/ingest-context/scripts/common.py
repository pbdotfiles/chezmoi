"""Helpers shared by the ingest-context scripts."""
import json
import re
import unicodedata
from pathlib import Path

WORK = ".ingest"
DOCS = "docs"
ASSETS = "assets"
SYNTHESIS_FILES = ("MANIFEST.md", "GLOSSARY.md", "TIMELINE.md")

GENRES = ("slides", "report", "document", "notes", "spreadsheet", "data", "figure",
          "conversation", "email", "other")
DATE_SOURCES = ("filename", "metadata", "content", "path", "mtime", "none")
CONFIDENCES = ("high", "medium", "low")

PAGE_ANCHOR_RE = re.compile(r"<!--\s*p\.(\d+)\s*-->")
PART_ANCHOR_RE = re.compile(r"<!--\s*part:\s*(.+?)\s*-->")
FIGURE_SKIPPED_RE = re.compile(r"<!--\s*figure skipped:")
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")


def work_dir(out: Path) -> Path:
    return out / WORK


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")


def slugify(text: str, maxlen: int = 80) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:maxlen].strip("-") or "doc"


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def image_tokens(w: int, h: int) -> int:
    """Rough vision cost of one image, after the usual downscale to 1568 px."""
    scale = min(1.0, 1568 / max(w, h, 1))
    return min(1600, int(w * scale * h * scale / 750) + 1)


def output_files(out: Path, slug: str) -> list[Path]:
    """The Markdown file(s) of a document: docs/<slug>.md, or docs/<slug>/*.md when split."""
    single = out / DOCS / f"{slug}.md"
    if single.exists():
        return [single]
    folder = out / DOCS / slug
    if folder.is_dir():
        files = sorted(folder.glob("*.md"), key=lambda p: natural_key(p.name))
        index = folder / "index.md"
        if index in files:
            files.remove(index)
            files.insert(0, index)
        return files
    return []


def split_frontmatter(text: str):
    """Returns (frontmatter text or None, body)."""
    if not text.startswith("---"):
        return None, text
    m = re.match(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def frontmatter_sha(path: Path):
    """The sha256 recorded in a converted file, read without YAML."""
    try:
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    except OSError:
        return None
    if fm is None:
        return None
    m = re.search(r"^sha256:\s*[\"']?([0-9a-f]{64})", fm, re.M)
    return m.group(1) if m else None
