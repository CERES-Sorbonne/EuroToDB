#!/usr/bin/sudo /bin/sh

# Export the environment variables
set -a
source .env || exit 1
set +a
env | grep -E '^(TZ|POSTGRES|HOST|FOLDER|CREDSFILE|CONTAINER)' || exit 1

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

# EOF
