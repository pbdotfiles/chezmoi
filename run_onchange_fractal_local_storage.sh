#!/bin/bash

{{- if eq .chezmoi.hostname "fractal22" }}

if [ ! -d /mnt/ext4_data ]; then
	sudo mkdir /mnt/ext4_data
fi

# FSTAB
temp_file="/tmp/fstab_temp"
grep -v "bca615bc" /etc/fstab > "$temp_file"
sudo mv "$temp_file" /etc/fstab

# Append this at the end of /etc/fstab :
# use "fdisk -l" and "blkid" to get the UUID
sudo tee -a /etc/fstab >/dev/null <<EOF
UUID="bca615bc-2c63-4db8-8408-ddd48b27ab55" /mnt/ext4_data ext4 defaults 0 2
EOF

sudo umount -a
sudo mount -a
sudo chown -R paul /mnt/ext4_data
sudo chattr +i /mnt/ext4_data

rmdir ~/Downloads ~/Documents ~/Pictures
ln -s /mnt/ext4_data/Downloads ~/Downloads
ln -s /mnt/ext4_data/Documents ~/Documents
ln -s /mnt/ext4_data/Pictures ~/Pictures
ln -s /mnt/ext4_data/Torrents ~/Torrents

{{- end }}
