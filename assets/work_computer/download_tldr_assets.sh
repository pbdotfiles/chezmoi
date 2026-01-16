#!/bin/bash

# 1. Define paths
TLDR_ZIP_URL="https://tldr.sh/assets/tldr.zip"
TLDR_LOCAL_DIR="$HOME/.local/share/tldr"
WORKING_CERT="/usr/local/share/ca-certificates/ZscalerRootCA.crt"

echo "Using curl to manually download tldr pages..."

# 2. Create the target directory
mkdir -p "$TLDR_LOCAL_DIR"

# 3. Download the zip file
if curl -L --cacert "$WORKING_CERT" "$TLDR_ZIP_URL" -o "$TLDR_LOCAL_DIR/tldr.zip"; then
  echo "✅ Download successful."

  # 4. Unzip the contents
  echo "Extracting pages..."
  unzip -o "$TLDR_LOCAL_DIR/tldr.zip" -d "$TLDR_LOCAL_DIR"

  # 5. Cleanup the zip
  rm "$TLDR_LOCAL_DIR/tldr.zip"

  echo "✨ Done! You can now use 'tldr <command>' normally."
else
  echo "❌ Manual download failed. Please check if $WORKING_CERT is the correct path."
fi
