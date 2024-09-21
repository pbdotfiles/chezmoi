#!/bin/bash
sudo apt install unattended-upgrades update-notifier-common wireguard

sudo perl -pi -e 's/^.*Unattended-Upgrade::Automatic-Reboot .*$/Unattended-Upgrade::Automatic-Reboot "true";/' /etc/apt/apt.conf.d/50unattended-upgrades
sudo perl -pi -e 's/^.*Unattended-Upgrade::Automatic-Reboot-Time .*$/Unattended-Upgrade::Automatic-Reboot-Time "23:00";/' /etc/apt/apt.conf.d/50unattended-upgrades

sudo systemctl enable wg-quick@wg0

