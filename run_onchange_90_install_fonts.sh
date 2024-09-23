#!/bin/bash
############################
# FONTS
fonts_dir="${HOME}/.local/share/fonts"
if [ ! -d "${fonts_dir}" ]; then
    echo "mkdir -p $fonts_dir"
    mkdir -p "${fonts_dir}"
else
    echo "Found fonts dir $fonts_dir"
fi

# FIRA CODE
version=5.2
zip=Fira_Code_v${version}.zip
curl --fail --location --show-error https://github.com/tonsky/FiraCode/releases/download/${version}/${zip} --output ${zip}
unzip -o -q -d ${fonts_dir} ${zip}
rm ${zip}

# NERD FONTS
wget -q -O - https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest | grep 'zip"$' | awk -F'"' ' {print $4} ' | while read -r url; do
	echo "downloading: $url"
        wget -q -O font.zip "$url"
        unzip -o -q -d ${fonts_dir} font.zip
        rm font.zip
done

# install the fonts
fc-cache -f
