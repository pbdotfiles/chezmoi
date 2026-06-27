#!/bin/bash

# 1. Define paths
TLDR_ZIP_URL="https://tldr.sh/assets/tldr.zip"
TLDR_LOCAL_DIR="$HOME/.local/share/tldr"

# Locate a working CA cert (try common locations for corporate proxy certs)
WORKING_CERT=""
for candidate in \
    /etc/ssl/certs/*Root_CA.pem \
    /etc/ssl/ca-bundle.pem \
    /usr/local/share/ca-certificates/*.crt ; do
    # skip if glob didn't expand
    [ -f "$candidate" ] || continue
    WORKING_CERT="$candidate"
    break
done

echo "Using curl to manually download tldr pages..."

# 2. Create the target directory
mkdir -p "$TLDR_LOCAL_DIR"

# 3. Download the zip file
CURL_ARGS=(-L)
[ -n "$WORKING_CERT" ] && CURL_ARGS+=(--cacert "$WORKING_CERT")
if curl "${CURL_ARGS[@]}" "$TLDR_ZIP_URL" -o "$TLDR_LOCAL_DIR/tldr.zip"; then
  echo "✅ Download successful."

  # 4. Unzip the contents
  echo "Extracting pages..."
  unzip -o "$TLDR_LOCAL_DIR/tldr.zip" -d "$TLDR_LOCAL_DIR"

  # 5. Cleanup the zip
  rm "$TLDR_LOCAL_DIR/tldr.zip"

  echo "✨ Done! You can now use 'tldr <command>' normally."
else
  echo "❌ Manual download failed."
fi
