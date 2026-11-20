#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: bash run.sh <script.py> [args...]" >&2
  exit 2
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/$1"
shift

if [ ! -f "$SCRIPT" ]; then
  echo "Script not found: $SCRIPT" >&2
  exit 2
fi

exec pixi exec \
  --spec 'python>=3.11' \
  --spec pymupdf \
  --spec python-pptx \
  --spec openpyxl \
  --spec pillow \
  --spec pandoc \
  --spec pyyaml \
  -- python "$SCRIPT" "$@"
