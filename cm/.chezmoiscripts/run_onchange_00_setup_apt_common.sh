#!/bin/bash

set -euo pipefail

sudo apt update
sudo apt upgrade -y

sudo apt install ripgrep cifs-utils samba borgbackup lm-sensors exiftool syncthing htop btop stress s-tui nload liblzo2-dev git tmux openssh-server tree fuse3 libfuse-dev pkg-config sshfs bat -y
