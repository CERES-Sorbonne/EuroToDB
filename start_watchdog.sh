#!/usr/bin/sudo /bin/bash

# Export the environment variables
set -a
source .env || exit 1
set +a
env | grep -E '^(TZ|POSTGRES|HOST|FOLDER|CREDSFILE|CONTAINER)' || exit 1

source venv/bin/activate || exit 1
python ElChienDeGarde.py "$CREDS_FILE" "$FOLDER_TO_WATCH" || exit 1

# EOF
