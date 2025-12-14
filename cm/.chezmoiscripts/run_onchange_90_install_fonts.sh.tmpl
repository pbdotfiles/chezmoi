#!/bin/bash

set -euo pipefail

#################################################
# Download latest version of the JetBrainsMono fonts
#################################################

fonts_dir="${HOME}/.local/share/fonts"
if [ ! -d "${fonts_dir}" ]; then
  mkdir -p "${fonts_dir}"
fi

URL=$(curl -s "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest" |
  jq -r '.assets[] | select(.name == "JetBrainsMono.zip") | .browser_download_url')

if [ -z "$URL" ]; then
  echo "Error: Could not find JetBrainsMono.zip in the latest Nerd Fonts release."
  exit 1
fi

echo "Downloading latest JetBrainsMono version from: $URL"
wget -q -O font.zip "$URL"
unzip -o -q -d "${fonts_dir}" font.zip
rm font.zip

# Install the font
fc-cache -f
