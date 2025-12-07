#!/bin/bash
#################################################
# Download latest version of the FiraCode fonts
#################################################

fonts_dir="${HOME}/.local/share/fonts"
if [ ! -d "${fonts_dir}" ]; then
  mkdir -p "${fonts_dir}"
fi

URL=$(wget -q -O - https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest | grep 'browser_download_url.*FiraCode.zip' | awk -F'"' '{print $4}')

if [ -z "$URL" ]; then
  echo "Error: Could not find FiraCode.zip in the latest Nerd Fonts release."
  exit 1
fi

echo "Downloading latest FiraCode version from: $URL"
wget -q -O font.zip "$URL"
unzip -o -q -d "${fonts_dir}" font.zip
rm font.zip

# Install the font
fc-cache -f
