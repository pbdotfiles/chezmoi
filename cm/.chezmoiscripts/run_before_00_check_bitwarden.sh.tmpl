#!/bin/bash

# 1. Check if 'bw' is even installed
if ! command -v bw &>/dev/null; then
  echo "❌ ERROR: Bitwarden CLI ('bw') is not installed or not in your PATH."
  echo "   Please run your bootstrap script first."
  exit 1
fi

# 2. Check if the session variable is set
# chezmoi's built-in template function relies on the BW_SESSION environment variable.
if [ -z "${BW_SESSION:-}" ]; then
  echo "❌ ERROR: You are not logged into Bitwarden."
  echo "   'chezmoi' needs the BW_SESSION variable to decrypt your secrets."
  echo ""
  echo "   Please run this command in your terminal:"
  echo "   export BW_SESSION=\$(bw unlock --raw)"
  echo ""
  exit 1
fi

# Check if the session is actually valid/unlocked
if ! bw status | grep -q '"status":"unlocked"'; then
  echo "❌ ERROR: Bitwarden is locked."
  echo "   Please run: export BW_SESSION=\$(bw unlock --raw)"
  exit 1
fi

echo "✅ Bitwarden is unlocked. Proceeding..."
