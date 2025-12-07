#!/bin/bash

set -euo pipefail

ssh-keygen -t rsa

echo "=========================== SSH_COPY_ID_ALL =============="

# Define the hosts to be added
hosts=(
  "fractal"
  "morefine"
  "rone"
  "ronenu"
  "minis"
  "ser"
)

# Ask the user if they want to perform ssh-copy-id on all hosts
read -p "Do you want to perform ssh-copy-id on all hosts? (yes/no): " response
if [[ "$response" =~ ^[Yy][Ee][Ss]$ ]]; then
  for entry in "${hosts[@]}"; do
    hostname=$(echo "$entry" | awk '{print $1}')
    # Skip if the hostname is the same as the current machine
    if [ "$hostname" = $(hostname) ]; then
      echo "Skipping $hostname (current machine)"
    else
      echo "Copying SSH key to $hostname"
      ssh-copy-id -i ~/.ssh/id_rsa.pub -o StrictHostKeyChecking=no -o ConnectTimeout=2 "$hostname"
    fi
  done
  echo "SSH keys copied successfully"
else
  echo "Skipping ssh-copy-id"
fi
