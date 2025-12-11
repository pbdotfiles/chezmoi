#!/bin/bash

BW_CMD="$HOME/bin/bw"

# Check the Bitwarden status
# We use grep so we don't depend on 'jq' being installed
if $BW_CMD status | grep -q '"status":"unauthenticated"'; then
  echo "🔑 Logging into Bitwarden..."
  export BW_SESSION=$($BW_CMD login --raw)
else
  echo "🔓 Unlocking Bitwarden..."
  export BW_SESSION=$($BW_CMD unlock --raw)
fi

# Optional: Verify it worked
if [ -n "$BW_SESSION" ]; then
  echo "✅ Bitwarden session exported successfully."
else
  echo "❌ Failed to retrieve session key."
fi
