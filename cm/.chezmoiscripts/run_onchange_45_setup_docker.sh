#!/bin/bash
set -euo pipefail

echo "🐳 Starting Docker installation..."

# 1. Clean up old versions (if any)
echo "Removing conflicting packages..."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y $pkg || true
done

# 2. Update and install prerequisites
echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# 3. Add Docker's official GPG key
echo "Adding Docker GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 4. Set up the repository
# Note: Handles Linux Mint by using UBUNTU_CODENAME if available, otherwise falls back to standard lsb_release
echo "Setting up Docker repository..."
if [ -f /etc/os-release ]; then
  . /etc/os-release
  VERSION_CODENAME=${UBUNTU_CODENAME:-$VERSION_CODENAME}
fi

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $VERSION_CODENAME stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

# 5. Install Docker packages
echo "Installing Docker Engine and Compose..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. Post-installation steps (Rootless mode)
echo "Configuring user permissions..."
# Create docker group if it doesn't exist
sudo groupadd docker || true
# Add current user to the docker group
sudo usermod -aG docker "$USER"

# 7. Enable and start service
echo "Enabling Docker service..."
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo systemctl start docker

echo "✅ Docker installation complete!"
echo "Reboot, then test it with: docker run hello-world"
