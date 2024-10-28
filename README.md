# `chezmoi` dotfiles

System setup and dotfiles using [`chezmoi`](https://www.chezmoi.io/)

## Quick start

1. Install chezmoi: `sh -c "$(curl -fsLS get.chezmoi.io)"` in `~`
2. Clone the chezmoi repository: `~/bin/chezmoi init https://github.com/pbdotfiles/chezmoi.git`
3. Configure Bitwarden: `bash ~/.local/share/chezmoi/bitwarden.sh`
4. Run `~/bin/chezmoi apply`

## Manual installation steps
Wireguard configuration:
1. Download config_wireguard.conf
2. `scp ~/Downloads/config_wireguard.conf 192.168.xxx.xxx:/tmp/wg0.conf`
3. SSH into 192.168.xxx.xxx
4. `sudo mv /tmp/wg0.conf /etc/wireguard/wg0.conf`
5. `sudo chmod 600 /etc/wireguard/wg0.conf`

## Other dotfiles available on github
https://github.com/renemarc/dotfiles/tree/master

## dconf checklist:
`dconf dump /org/cinnamon/desktop/keybindings/ > keybindings.dconf`
`dconf dump /org/cinnamon/desktop/peripherals/keyboard/ > keyboard.dconf`

`dconf load /org/cinnamon/desktop/keybindings/ < keybindings.dconf`
`dconf load /org/cinnamon/desktop/peripherals/keyboard/ < keyboard.dconf`
