#!/bin/bash

# Unmount all filesystems
sudo umount -a

# Create /mnt/ext4_data directory if it doesn't exist
if [ ! -d /mnt/ext4_data ]; then
    sudo mkdir /mnt/ext4_data
fi

# Remove immutable attribute if set
sudo chattr -i /mnt/ext4_data

# Change ownership to user 'paul'
sudo chown -R paul /mnt/ext4_data

# Set immutable attribute
sudo chattr +i /mnt/ext4_data

# Remove existing fstab entry for the specified UUID
temp_file="/tmp/fstab_temp"
grep -v "bca615bc" /etc/fstab > "$temp_file"
sudo mv "$temp_file" /etc/fstab

# Append the new fstab entry if it doesn't already exist (it shouldn't).
# use "fdisk -l" and "blkid" to get the UUID
sudo tee -a /etc/fstab >/dev/null <<EOF
UUID="bca615bc-2c63-4db8-8408-ddd48b27ab55" /mnt/ext4_data ext4 defaults 0 2
EOF

# Mount all filesystems
sudo mount -a

# Remove existing directories and create symbolic links if they don't already exist
for dir in Downloads Documents Pictures Torrents; do
    if [ -L ~/"$dir" ]; then
	rm ~/"$dir"
    fi
    if [ -d ~/"$dir" ]; then
        rmdir ~/"$dir"
    fi
    ln -s /mnt/ext4_data/"$dir" ~/"$dir"
done

