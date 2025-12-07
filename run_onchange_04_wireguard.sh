#!/bin/bash

set -euo pipefail

sudo apt install wireguard -y
sudo systemctl enable wg-quick@wg0
