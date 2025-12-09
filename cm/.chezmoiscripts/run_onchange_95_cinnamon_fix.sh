#!/bin/bash

set -euo pipefail

sudo apt update
sudo apt upgrade -y
# Weird cinnamon install fix ?
sudo apt install nemo cinnamon -y
