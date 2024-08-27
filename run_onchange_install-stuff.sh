#!/bin/bash
sudo apt install ripgrep cifs-utils samba remmina filelight syncthing micro gnome-tweaks borgbackup lm-sensors exiftool qbittorrent syncthing neovim htop stress s-tui nload flameshot liblzo2-dev git winetricks tmux openssh-server

############################
# OBSIDIAN LATEST
URL=$(wget -q -O - https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | grep 'deb"$' | awk -F'"' ' {print $4}  ')
wget -q -O obsidian.deb "$URL"
sudo dpkg -i obsidian.deb
rm obsidian.deb

#############################
# DCONF for GNOME-TWEAK-TOOLS
dconf load /org/cinnamon/desktop/keybindings/ < keybindings.dconf
dconf load /org/cinnamon/desktop/peripherals/keyboard/ < keyboard.dconf

#############################
# MINIFORGE LATEST
wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
chmod u+x ./Miniforge3.sh
./Miniforge3.sh -b
~/miniforge3/condabin/conda init
rm Miniforge3.sh

# DISCORD LATEST
#wget -q -O discord.deb https://discord.com/api/download?platform=linux&format=deb
#sudo dpkg -i discord.deb
#rm discord.deb

# WINE STAGING, MINT 22
sudo dpkg --add-architecture i386 
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources
sudo apt update
sudo apt install --yes --install-recommends winehq-staging

##############################
# PYCHARM 2024.2
wget -q -O pycharm.tar.gz https://download.jetbrains.com/python/pycharm-community-2024.2.tar.gz
tar -xzf pycharm.tar.gz -C ~/.local/share/applications
~/.local/share/applications/pycharm-community-2024.2/bin/pycharm
rm pycharm.tar.gz

##############################
# Update everything
sudo apt update
sudo apt upgrade
