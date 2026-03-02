#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# Exit immediately if attempting to use an unset variable.
# Treat pipe errors as command errors.
set -euo pipefail

# --- Documentation ---
#
# Description:
# This script securely exports a Bitwarden vault, sets appropriate permissions
# on the export, and archives it into a password-protected 7z file using AES-256.
# It uses a temporary file for the export, which is securely deleted afterwards.
#
# WARNING: This version prompts for the archive password within the script and
#          passes it to 7z via the command line ('-p"$PASSWORD"'). This method
#          is considered insecure as the password may be visible in the system's
#          process list. Use with caution and preferably on a trusted machine.
#          The alternative is to remove the script's password prompt loop and
#          use '7z a -p ...' (without the password) to trigger 7z's own secure
#          interactive prompt (which also asks for confirmation).
#
# Usage:
#   ./script_name.sh [output_filename.7z]
#
# Arguments:
#   [output_filename.7z] (Optional):
#     If provided, this will be the name of the created 7z archive.
#     If omitted, a default filename including the current date and time
#     will be used (e.g., bitwarden_export_YYYYMMDD_HHMMSS.7z).
#
# Requirements:
#   - bash
#   - Bitwarden CLI (bw)
#   - 7zip (7z command, requires p7zip-full or similar package)
#   - coreutils (for mktemp)
#
# --- Configuration ---
# Default filename pattern for the output 7z archive
DEFAULT_FILENAME="bitwarden_export_$(date +%Y%m%d_%H%M%S).7z"
# Use first argument ($1) as filename if provided, otherwise use the default.
OUTPUT_FILENAME="${1:-$DEFAULT_FILENAME}"

# --- Temporary File Setup ---
# Create a secure temporary file path using mktemp. Exit if it fails.
TEMP_JSON_FILE=$(mktemp --suffix=_bw_export.json) || { echo "Error: Failed to create temporary file path." >&2; exit 1; }
echo "Using temporary file: $TEMP_JSON_FILE" # Info message

# --- Cleanup Function ---
# Registered with 'trap' to run on script exit/interrupt.
cleanup() {
  local exit_status=$?
  echo "Cleaning up..."
  unset BW_PASSWORD BW_SESSION ARCHIVE_PASSWORD ARCHIVE_PASSWORD_CONFIRM # Include archive pw vars
  if [ -v TEMP_JSON_FILE ] && [ -f "$TEMP_JSON_FILE" ]; then
      echo "Removing temporary file: $TEMP_JSON_FILE"
      rm -f "$TEMP_JSON_FILE"
  elif [ -v TEMP_JSON_FILE ]; then
      # echo "Temporary file path $TEMP_JSON_FILE was allocated but file not found (or already removed)." # Less verbose cleanup
      rm -f "$TEMP_JSON_FILE" # Attempt removal just in case
  fi
  if command -v bw &> /dev/null && [ -n "${BW_SESSION-}" ]; then
     echo "Attempting to lock Bitwarden vault..."
     bw lock &> /dev/null || true
  fi
  echo "Cleanup finished."
  # exit $exit_status # Optional: preserve original exit status
}
trap cleanup EXIT INT TERM

# --- Check Prerequisites ---
if ! command -v bw &> /dev/null; then echo "Error: bw not found. Please install: https://bitwarden.com/help/cli/" >&2; exit 1; fi
if ! command -v 7z &> /dev/null; then echo "Error: 7z not found. Please install (e.g., sudo apt install p7zip-full)." >&2; exit 1; fi
if ! command -v mktemp &> /dev/null; then echo "Error: mktemp not found (should be part of coreutils)." >&2; exit 1; fi

# --- Get Bitwarden Master Password ---
read -s -p "Enter Bitwarden Master Password: " BW_PASSWORD
echo
if [ -z "$BW_PASSWORD" ]; then echo "Error: No Bitwarden password entered." >&2; exit 1; fi

# --- Unlock Vault and Get Session Key ---
echo "Attempting to unlock Bitwarden vault..."
export BW_SESSION=$(bw unlock --raw <<< "$BW_PASSWORD")
unlock_status=$?
unset BW_PASSWORD # Unset immediately
if [ $unlock_status -ne 0 ] || [ -z "$BW_SESSION" ]; then
    echo "Error: Failed to unlock Bitwarden vault." >&2
    unset BW_SESSION
    exit 1
fi
echo "Vault unlocked successfully."

# --- Sync Vault ---
echo "Syncing Bitwarden vault..."
if ! bw sync --quiet; then echo "Error: Failed to sync Bitwarden vault." >&2; exit 1; fi
echo "Vault synced successfully."

# --- Get 7z Archive Password (Script-level confirmation) ---
# WARNING: See script documentation regarding the insecurity of passing this password via -p.
while true; do
    read -s -p "Enter password for the 7z archive (AES-256): " ARCHIVE_PASSWORD
    echo
    if [ -z "$ARCHIVE_PASSWORD" ]; then
        echo "Error: Archive password cannot be empty." >&2
        continue
    fi
    read -s -p "Confirm password for the 7z archive: " ARCHIVE_PASSWORD_CONFIRM
    echo
    if [ "$ARCHIVE_PASSWORD" == "$ARCHIVE_PASSWORD_CONFIRM" ]; then
        unset ARCHIVE_PASSWORD_CONFIRM
        break
    else
        echo "Error: Passwords do not match. Please try again." >&2
        unset ARCHIVE_PASSWORD ARCHIVE_PASSWORD_CONFIRM
    fi
done
echo "Password confirmed by script."


# --- Export Vault to Temporary File ---
echo "Exporting vault to temporary file: $TEMP_JSON_FILE"
export BW_SESSION
if ! bw export --output "$TEMP_JSON_FILE" --format json --quiet; then
    echo "Error: Failed to export vault to temporary file." >&2
    exit 1
fi
if [ ! -s "$TEMP_JSON_FILE" ]; then
    echo "Error: Export created an empty temporary file." >&2
    exit 1
fi
echo "Vault exported successfully to temporary file."

# --- Set Permissions on Temporary File ---
echo "Setting secure permissions (600) on temporary file..."
chmod 600 "$TEMP_JSON_FILE"

# --- Create Encrypted 7z Archive from File ---
echo "Creating encrypted 7z archive: $OUTPUT_FILENAME"
# WARNING: Using '-p"$ARCHIVE_PASSWORD"' is INSECURE. See documentation block above.
if 7z a -p"$ARCHIVE_PASSWORD" -mhe=on "$OUTPUT_FILENAME" "$TEMP_JSON_FILE"; then
    unset ARCHIVE_PASSWORD # Unset password variable immediately after use
    echo "Successfully created encrypted 7z archive: $OUTPUT_FILENAME"
    echo "Permissions of the file inside the archive should be owner read/write (-rw-------)."
    echo "The temporary unencrypted file $TEMP_JSON_FILE will now be deleted."
else
    unset ARCHIVE_PASSWORD &> /dev/null || true # Also unset password variable on failure
    echo "Error: Failed to create 7z archive from temporary file." >&2
    exit 1
fi

# --- Cleanup ---
# The temporary file ($TEMP_JSON_FILE) will be removed automatically by the trap.
exit 0
