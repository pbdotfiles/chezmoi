#!/bin/bash

set -euo pipefail

# WINE STAGING, MINT 22
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources
sudo apt update
# The line below installs wine's latest staging version. It doesn't work with Trackmania.
sudo apt install --yes --install-recommends winehq-staging # FIXEDVERSION
# Instead we force install the latest version known to work with Trackmania:
# sudo apt install --install-recommends wine-staging-i386=9.17~noble-1 -y
# sudo apt install --install-recommends wine-staging-amd64=9.17~noble-1 -y
# sudo apt install --install-recommends wine-staging=9.17~noble-1 -y
# sudo apt install --install-recommends winehq-staging=9.17~noble-1 -y

sudo apt install winetricks -y
winetricks -q mono
winetricks -q dxvk
winetricks -q isolate_home
