#!/usr/bin/sudo /bin/bash

# Export the environment variables
set -a
source .env || exit 1
set +a
env | grep -E '^(TZ|POSTGRES|HOST|FOLDER|CREDSFILE|CONTAINER)' || exit 1

# Create the folder for the DB
if [ ! -d "${POSTGRES_DATA}" ]; then
  mkdir -p "${POSTGRES_DATA}" || exit 1
fi

# Check if the container exists
CONTAINER_EXISTS=$(sudo docker ps -a | grep "${CONTAINER_NAME}")
if [ -z "$CONTAINER_EXISTS" ]
then
    sudo docker start -ia "${CONTAINER_NAME}" || exit 1
else
  sudo docker run \
  -it \
  --name="${CONTAINER_NAME}" \
  -e TZ="${TZ}" \
  -e HOST_CONTAINERNAME="${CONTAINER_NAME}" \
  -e 'POSTGRES_PASSWORD'="${POSTGRES_PASSWORD}" \
  -e 'POSTGRES_USER'="${POSTGRES_USER}" \
  -e 'POSTGRES_DB'="${POSTGRES_DB}" \
  -p "${POSTGRES_PORT}":5432/tcp \
  -v "${POSTGRES_DATA}":/var/lib/postgresql/data:rw \
  "${POSTGRES_IMAGE}":"${POSTGRES_VERSION}" || exit 1
fi

# EOF
