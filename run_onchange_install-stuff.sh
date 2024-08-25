#!/bin/bash
sudo apt install ripgrep cifs-utils samba remmina filelight syncthing micro gnome-tweaks borgbackup lm-sensors exiftool qbittorrent syncthing neovim htop stress s-tui nload flameshot nvtop liblzo2-dev

############################
# OBSIDIAN LATEST
URL=$(wget -q -O - https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | grep 'deb"$' | awk -F'"' ' {print $4}  ')
wget -q -O obsidian.deb "$URL"
sudo dpkg -i obsidian.deb
rm obsidian.deb

# Configure SSH access to minis
ssh-keygen -t rsa
ssh-copy-id -i /home/paul/.ssh/id_rsa paul@192.168.1.222

# DCONF for GNOME-TWEAK-TOOLS
dconf load / < my-cinnamon.dconf

#############################
# MOUNT POINTS
if [ ! -d /mnt/minis_share ]; then
	sudo mkdir /mnt/minis_share
	sudo chattr +i /mnt/minis_share
fi
if [ ! -d /mnt/ext4_data ]; then
	sudo mkdir /mnt/ext4_data
	sudo chattr +i /mnt/ext4_data
fi

rm -rf Downloads Documents Pictures
ln -s /mnt/ext4_data/Downloads ~/Downloads
ln -s /mnt/ext4_data/Documents ~/Documents
ln -s /mnt/ext4_data/Pictures ~/Pictures
ln -s /mnt/ext4_data/Torrents ~/Torrents


# FSTAB
read -s -p "Enter password for SAMBA share: " password
sudo tee /root/.smbcredentials >/dev/null <<EOF
username=paul
password=$password
EOF

temp_file="/tmp/fstab_temp"
sudo grep -v "bca615bc" /etc/fstab | grep -v "minis_share" > "$temp_file"
sudo mv "$temp_file" /etc/fstab


# Append this at the end of /etc/fstab : 
# use "fdisk -l" and "blkid" to get the UUID
sudo tee -a /etc/fstab >/dev/null <<EOF
UUID="bca615bc-2c63-4db8-8408-ddd48b27ab55" /mnt/ext4_data ext4 defaults 0 2
//192.168.1.222/share /mnt/minis_share cifs credentials=/root/.smbcredentials,uid=1000,gid=1000,dir_mode=0755,file_mode=0755,iocharset=utf8,noauto,x-systemd.automount,_netdev 0 0
EOF

sudo umount -a
sudo mount -a
sudo chown -R paul /mnt/ext4_data

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

############################
# FONTS
#fonts_dir="${HOME}/.local/share/fonts"
#if [ ! -d "${fonts_dir}" ]; then
    #echo "mkdir -p $fonts_dir"
    #mkdir -p "${fonts_dir}"
#else
    #echo "Found fonts dir $fonts_dir"
#fi

# FIRA CODE
#version=5.2
#zip=Fira_Code_v${version}.zip
#curl --fail --location --show-error https://github.com/tonsky/FiraCode/releases/download/${version}/${zip} --output ${zip}
#unzip -o -q -d ${fonts_dir} ${zip}
#rm ${zip}

# NERD FONTS
#wget -q -O - https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest | grep 'zip"$' | awk -F'"' ' {print $4} ' | while read -r url; do
	#echo "downloading: $url"
        #wget -q -O font.zip "$url"
        #unzip -o -q -d ${fonts_dir} font.zip
        #rm font.zip
#done

# install the fonts
#fc-cache -f
##############################
# PYCHARM 2024.2
wget -q -O pycharm.tar.gz https://download.jetbrains.com/python/pycharm-community-2024.2.tar.gz
tar -xzf pycharm.tar.gz -C ~/.local/share/applications
~/.local/share/applications/pycharm-community-2024.2/bin/pycharm
rm pycharm.tar.gz

sudo apt install --yes --install-recommends winehq-staging
