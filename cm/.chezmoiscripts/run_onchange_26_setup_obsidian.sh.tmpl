#!/bin/bash

set -euo pipefail

if ! command -v obsidian &>/dev/null; then
  echo "Begin installing obsidian."
  API_URL="https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest"
  OBSIDIAN_URL=$(curl -s "$API_URL" | jq -r '.assets[] | select(.name | test("amd64.deb$")) | .browser_download_url')
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
