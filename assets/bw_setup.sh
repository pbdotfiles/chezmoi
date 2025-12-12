#!/bin/bash
set -euo pipefail

# Check we have the "unzip" prerequisite
if ! command -v unzip &>/dev/null; then
  sudo apt install -y unzip
fi

# Setup bitwarden on this computer
curl -L "https://vault.bitwarden.com/download/?app=cli&platform=linux" >bw.zip
unzip bw.zip
chmod +x bw
mkdir -p ~/bin
mv bw ~/bin/
rm bw.zip
~/bin/bw config server https://vault.bitwarden.eu
export PATH="$HOME/bin:$PATH"
source ~/.local/share/chezmoi/assets/bw_login.sh
