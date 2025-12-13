#!/bin/bash

set -euo pipefail

sudo apt update
sudo apt upgrade -y

sudo apt install cifs-utils borgbackup lm-sensors exiftool syncthing htop btop stress s-tui nload liblzo2-dev git tmux openssh-server tree fuse3 libfuse-dev pkg-config sshfs bat jq sshpass curl git build-essential ripgrep fd-find unzip xclip python3-venv python3-dev python3-setuptools python3-pynvim imagemagick sqlite3 libsqlite3-dev luarocks zip wget 7zip poppler-utils -y
