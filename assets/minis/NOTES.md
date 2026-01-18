# 1. Permanent Driver Blacklist
echo "blacklist amd_sfh" | sudo tee /etc/modprobe.d/blacklist-amd-sfh.conf

# 2. Apply C-State limits and Driver overrides in GRUB
# (This adds the necessary parameters to your existing GRUB_CMDLINE_LINUX_DEFAULT)
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/&amd_sfh.enable_sfh=0 intel_idle.max_cstate=0 processor.max_cstate=1 /' /etc/default/grub

# 3. Commit changes to the bootloader and system image
sudo update-grub && sudo update-initramfs -u && sudo reboot

# 4. Post-reboot verification (Driver should be gone, max_cstate should be 0)
lsmod | grep amd_sfh
cat /sys/module/intel_idle/parameters/max_cstate
