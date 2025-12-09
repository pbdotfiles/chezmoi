#!/bin/bash

set -euo pipefail

echo "Configuring hd-idle."

HDIDLE_URL=$(wget -q -O - https://api.github.com/repos/adelolmo/hd-idle/releases/latest | grep 'amd64\.deb"$' | awk -F'"' ' {print $4}  ')

if [ -z "$HDIDLE_URL" ]; then
  echo "Error: Failed to fetch hd-idle URL."
  exit 1
fi

wget -q -O hd-idle.deb "$HDIDLE_URL"
sudo dpkg -i hd-idle.deb
rm hd-idle.deb

sudo perl -pi -e 's/^.*START_HD_IDLE=.*$/START_HD_IDLE=true/' /etc/default/hd-idle
sudo perl -pi -e 's/^.*HD_IDLE_OPTS=.*$/HD_IDLE_OPTS="-i 600 -l /var/log/hd-idle.log"/' /etc/default/hd-idle

sudo systemctl start hd-idle
sudo systemctl enable hd-idle

echo "Finished configuring hd-idle."
