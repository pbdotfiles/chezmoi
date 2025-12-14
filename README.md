# `chezmoi` dotfiles

System setup and dotfiles using [`chezmoi`](https://www.chezmoi.io/)

## First installation

1. Install chezmoi: `sh -c "$(curl -fsLS get.chezmoi.io)"` in `~`
2. Clone the chezmoi repository: `~/bin/chezmoi init https://github.com/pbdotfiles/chezmoi.git`
3. Setup Bitwarden: `source ~/.local/share/chezmoi/assets/bw_setup.sh`
4. Run `~/bin/chezmoi apply`

sh -c "$(curl -fsLS get.chezmoi.io)"
~/bin/chezmoi init https://github.com/pbdotfiles/chezmoi.git
source ~/.local/share/chezmoi/assets/bw_setup.sh
~/bin/chezmoi apply

## Updating the configuration:

1. Log in Bitwarden: `source ~/.local/share/chezmoi/assets/bw_login.sh`
2. Run `~/bin/chezmoi apply`

## Manual installation steps
Wireguard configuration:
1. Download config_wireguard.conf
2. `scp ~/Downloads/config_wireguard.conf 192.168.xxx.xxx:/tmp/wg0.conf`
3. SSH into 192.168.xxx.xxx
4. `sudo mv /tmp/wg0.conf /etc/wireguard/wg0.conf`
5. `sudo chmod 600 /etc/wireguard/wg0.conf`

