#!/bin/bash
# MOUNT POINTS
if [ ! -d /mnt/minis_share ]; then
	sudo mkdir /mnt/minis_share
	sudo chattr +i /mnt/minis_share
fi

# CREDENTIALS
read -s -p "Enter password for SAMBA share: " password
sudo tee /root/.smbcredentials >/dev/null <<EOF
username=paul
password=$password
EOF

# FSTAB
temp_file="/tmp/fstab_temp"
grep -v "minis_share" /etc/fstab > "$temp_file"
sudo mv "$temp_file" /etc/fstab

# Append this at the end of /etc/fstab :
# use "fdisk -l" and "blkid" to get the UUID
sudo tee -a /etc/fstab >/dev/null <<EOF
//192.168.1.222/share /mnt/minis_share cifs credentials=/root/.smbcredentials,uid=1000,gid=1000,dir_mode=0755,file_mode=0755,iocharset=utf8,noauto,x-systemd.automount,_netdev 0 0
EOF

sudo umount -a
sudo mount -a

# Configure SSH access to minis
ssh-keygen -t rsa
ssh-copy-id -i /home/paul/.ssh/id_rsa paul@192.168.1.222
