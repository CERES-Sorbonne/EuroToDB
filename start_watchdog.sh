#!/usr/bin/sudo /bin/bash

# Export the environment variables
set -a
source .env || exit 1
set +a
env | grep -E '^(TZ|POSTGRES|HOST|FOLDER|CREDSFILE|CONTAINER)' || exit 1


# Check if the container is running
if [ "$(sudo docker inspect -f '{{.State.Running}}' "${HOST_CONTAINERNAME}")" = "true" ]; then
  echo "Container ${HOST_CONTAINERNAME} is running."
else
  echo "Container ${HOST_CONTAINERNAME} is not running."
  exit 1
fi

# Check if the container is healthy
if [ "$(sudo docker inspect -f '{{.State.Health.Status}}' "${HOST_CONTAINERNAME}")" = "healthy" ]; then
  echo "Container ${HOST_CONTAINERNAME} is healthy."
else
  echo "Container ${HOST_CONTAINERNAME} is not healthy."
  exit 1
fi

source venv/bin/activate || exit 1
python ElChienDeGarde.py "$CREDS_FILE" "$FOLDER_TO_WATCH" || exit 1

# EOF
