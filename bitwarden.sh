#!bin/bash
# Setup bitwarden on this computer
curl -L "https://vault.bitwarden.com/download/?app=cli&platform=linux" > bw.zip
unzip bw.zip
chmod +x bw
sudo mv bw ~/bin/
rm bw.zip
~/bin/bw config server https://vault.bitwarden.eu
export BW_SESSION=$(bw login --raw)
