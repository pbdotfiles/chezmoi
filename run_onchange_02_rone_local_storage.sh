#!/bin/bash
sudo umount -a

###############################################
#                HD-IDLE
###############################################
URL=$(wget -q -O - https://api.github.com/repos/adelolmo/hd-idle/releases/latest | grep 'amd64\.deb"$' | awk -F'"' ' {print $4}  ')
wget -q -O hd-idle.deb "$URL"
sudo dpkg -i hd-idle.deb
rm hd-idle.deb


sudo perl -pi -e 's/^.*START_HD_IDLE=.*$/START_HD_IDLE=true/' /etc/default/hd-idle
sudo perl -pi -e 's/^.*HD_IDLE_OPTS=.*$/HD_IDLE_OPTS="-i 600 -l /var/log/hd-idle.log"/' /etc/default/hd-idle

sudo systemctl start hd-idle
sudo systemctl enable hd-idle

###############################################

if [ ! -d /mnt/wdd ]; then
	sudo mkdir /mnt/wdd
fi

sudo chattr -i /mnt/wdd
sudo chown -R paul /mnt/wdd
sudo chattr +i /mnt/wdd

# FSTAB
temp_file="/tmp/fstab_temp"
grep -v "0cfde01b" /etc/fstab > "$temp_file"
sudo mv "$temp_file" /etc/fstab

# Append this at the end of /etc/fstab :
# use "fdisk -l" and "blkid" to get the UUID
sudo tee -a /etc/fstab >/dev/null <<EOF
UUID="0cfde01b-f95e-4c53-842b-42674ddd3b25" /mnt/wdd ext4 defaults 0 2
EOF

sudo mount -a
