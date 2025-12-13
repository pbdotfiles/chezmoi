#!/bin/bash

set -euo pipefail

sudo apt update

PACKAGES=(
  7zip
  bat
  borgbackup
  btop
  build-essential
  cifs-utils
  curl
  exiftool
  fd-find
  fuse3
  git
  htop
  imagemagick
  jq
  libfuse-dev
  liblzo2-dev
  libsqlite3-dev
  lm-sensors
  luarocks
  nload
  openssh-server
  pkg-config
  poppler-utils
  python3-dev
  python3-pynvim
  python3-setuptools
  python3-venv
  ripgrep
  s-tui
  sqlite3
  sshfs
  sshpass
  stress
  syncthing
  tmux
  tree
  unzip
  wget
  xclip
  zip
)

echo "Installing common APT packages..."
sudo apt install -y "${PACKAGES[@]}"
