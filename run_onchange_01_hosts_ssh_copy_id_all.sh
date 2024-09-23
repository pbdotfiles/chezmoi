#!/bin/bash

ssh-keygen -t rsa

echo "=========================== SSH_COPY_ID_ALL =============="

# Define the hosts to be added
hosts=(
  "192.168.1.201 fractal22"
  "192.168.1.202 morefine"
  "192.168.27.72 rone"
  "192.168.1.223 ronenu"
  "192.168.1.222 minis"
)

for host in "${hosts[@]}"; do
	if ! grep -q "^${host}\$" /etc/hosts; then
		echo "$host" | sudo tee -a /etc/hosts >/dev/null
	fi
done
echo "Filled hosts file successfully"

# Ask the user if they want to perform ssh-copy-id on all hosts
read -p "Do you want to perform ssh-copy-id on all hosts? (yes/no): " response
if [[ "$response" =~ ^[Yy][Ee][Ss]$ ]]; then
	for entry in "${hosts[@]}"; do
		ip=$(echo "$entry" | awk '{print $1a'})
		hostname=$(echo "$entry" | awk '{print $2}')

		echo "Copying SSH key to $hostname ($ip)"
		ssh-copy-id -i ~/.ssh/id_rsa.pub -o StrictHostKeyChecking=no "$hostname"
	done
	echo "SSH keys copied successfully"
else
  echo "Skipping ssh-copy-id"
fi
