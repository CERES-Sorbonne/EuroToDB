#!/bin/bash

# Export the environment variables
set -a
source .env_e2d || exit 1
set +a
env | grep -E '^(TZ|POSTGRES|HOST|FOLDER|CREDSFILE|CONTAINER)' || exit 1

source venv/bin/activate || exit 1
python ElChienDeGarde.py "$CREDSFILE" "$FOLDER_TO_WATCH" "$FOLDER_TO_STASH" || exit 1

# EOF
