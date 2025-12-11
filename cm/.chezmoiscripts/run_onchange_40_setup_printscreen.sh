#!/bin/bash

set -eui pipefail

# 1. Define the Schema and the Path separately
SCHEMA="org.cinnamon.desktop.keybindings.custom-keybinding"
PATH_ID="/org/cinnamon/desktop/keybindings/custom-keybindings/custom0/"

# 2. Register the custom keybinding in the main list
# We set the list to contain only our 'custom0' slot
gsettings set org.cinnamon.desktop.keybindings custom-list \
  "['custom0']"

# 3. Configure the Flameshot details using the 'Schema:Path' syntax
gsettings set "${SCHEMA}:${PATH_ID}" name "Flameshot"
gsettings set "${SCHEMA}:${PATH_ID}" command "flameshot gui --clipboard --path /home/paul/Pictures"
gsettings set "${SCHEMA}:${PATH_ID}" binding "['Print']"

# 4. Unbind the default screenshot action so it doesn't conflict
gsettings set org.cinnamon.desktop.keybindings.media-keys area-screenshot "[]"
gsettings set org.cinnamon.desktop.keybindings.media-keys screenshot "[]"
