#!/bin/bash
set -e

# Define installation paths
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"

echo "### Updating System and Installing Core Dependencies ###"
sudo apt update
sudo apt install -y curl git build-essential ripgrep fd-find unzip tar xclip python3-venv python3-dev python3-setuptools python3-pynvim imagemagick sqlite3 libsqlite3-dev luarocks zip

# Create a symlink for fd if it doesn't exist (Ubuntu installs it as fdfind)
if ! command -v fd &>/dev/null; then
  echo "Linking fdfind to fd..."
  ln -s $(which fdfind) "$BIN_DIR/fd"
fi

echo "### Installing Node.js and NPM (Required for tree-sitter-cli and many LSPs) ###"
if ! command -v npm &>/dev/null; then
  # Using a robust install script for nvm/node is often safer, but here is a direct apt approach
  # or you can use the nodesource setup if you need a newer version.
  sudo apt install -y nodejs npm
fi

echo "### Installing tree-sitter-cli ###"
# We try to install via npm as it's the standard way for this tool
sudo npm install -g tree-sitter-cli neovim

echo "### Installing FZF ###"
if [ ! -d "$HOME/.fzf" ]; then
  git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
  ~/.fzf/install --all --no-bash --no-zsh --no-fish # Install binaries only
  # Symlink to bin if not automatically added
  ln -sf "$HOME/.fzf/bin/fzf" "$BIN_DIR/fzf"
else
  echo "FZF already installed."
fi

echo "### Installing Lazygit ###"
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf lazygit.tar.gz lazygit
mv lazygit "$BIN_DIR/"
rm lazygit.tar.gz config.yml 2>/dev/null || true
echo "Lazygit installed to $BIN_DIR/lazygit"

echo "### Installing Neovim (Latest Stable from GitHub) ###"
# Removing apt neovim if present
if dpkg -l | grep -q neovim; then
  echo "Removing apt neovim..."
  sudo apt remove -y neovim
fi

# Download AppImage
curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.appimage
chmod u+x nvim-linux-x86_64.appimage
mv nvim-linux-x86_64.appimage "$BIN_DIR/nvim"
echo "Neovim installed to $BIN_DIR/nvim"

echo "### Backing up and Removing Old Vim Configs ###"
# Backing up just in case
mv ~/.config/nvim ~/.config/nvim.bak.$(date +%s) 2>/dev/null || true
mv ~/.local/share/nvim ~/.local/share/nvim.bak.$(date +%s) 2>/dev/null || true
mv ~/.local/state/nvim ~/.local/state/nvim.bak.$(date +%s) 2>/dev/null || true
mv ~/.cache/nvim ~/.cache/nvim.bak.$(date +%s) 2>/dev/null || true

echo "### Bootstrapping LazyVim ###"
git clone https://github.com/LazyVim/starter ~/.config/nvim

echo "### Done! ###"
echo "Restart your shell or ensure $BIN_DIR is in your PATH."
echo "Run 'nvim' to start LazyVim and let it install plugins."
