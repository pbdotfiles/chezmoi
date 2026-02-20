#!/bin/bash

# $HOME/bin is probably already on the path, re-add it just in case
export PATH="$HOME/bin:$PATH"

# Check the Bitwarden status
# We use grep so we don't depend on 'jq' being installed
if bw status | grep -q '"status":"unauthenticated"'; then
  echo "🔑 Logging into Bitwarden..."
  export BW_SESSION=$(bw login --raw)
else
  echo "🔓 Unlocking Bitwarden..."
  export BW_SESSION=$(bw unlock --raw)
fi

# Optional: Verify it worked
if [ -n "$BW_SESSION" ]; then
  echo "✅ Bitwarden session exported successfully."
else
  echo "❌ Failed to retrieve session key."
fi
