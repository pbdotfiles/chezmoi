#!/bin/bash

set -euo pipefail

if ! command -v obsidian &>/dev/null; then
  echo "Begin installing obsidian."
  OBSIDIAN_URL=$(wget -q -O - https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | grep 'deb"$' | awk -F'"' ' {print $4}  ')
  if [ -z "$OBSIDIAN_URL" ]; then
    echo "Failed to fetch Obsidian URL"
    exit 1
  fi
  wget -q -O obsidian.deb "$OBSIDIAN_URL"
  sudo dpkg -i obsidian.deb
  rm obsidian.deb
  echo "Finished installing obsidian."
else
  echo "Obsidian is already installed."
fi
