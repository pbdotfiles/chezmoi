#!/bin/bash
# MOUNT POINTS

sudo umount -a

if [ ! -d /mnt/minis_share ]; then
	sudo mkdir /mnt/minis_share
fi

sudo chattr -i /mnt/minis_share
sudo chown -R paul /mnt/minis_share
sudo chattr +i /mnt/minis_share

# CREDENTIALS
read -s -p "Enter password for minis SAMBA share: " password
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
//minis/share /mnt/minis_share cifs credentials=/root/.smbcredentials,uid=1000,gid=1000,dir_mode=0755,file_mode=0755,iocharset=utf8,noauto,x-systemd.automount,_netdev 0 0
EOF

sudo mount -a

