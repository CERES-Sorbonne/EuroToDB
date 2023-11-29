#!/usr/bin/sudo /bin/bash

# Export the environment variables
set -a
source .env || exit 1
set +a
env | grep -E '^(TZ|POSTGRES|HOST|FOLDER|CREDSFILE|CONTAINER)' || exit 1


cd "$ROOT_FOLDER" || exit 1

git pull origin master --quiet || exit 1

source "$ROOT_FOLDER"/venv/bin/activate || exit 1

DB_IS_RUNNING=1
WATCHDOG_IS_RUNNING=$(screen -ls | grep EuroWatchdog)

# Check if the container is running
if [ "$(sudo docker inspect -f '{{.State.Running}}' "${HOST_CONTAINERNAME}")" = "true" ]; then
  echo "Container ${HOST_CONTAINERNAME} is running."
else
  echo "Container ${HOST_CONTAINERNAME} is not running."
  DB_IS_RUNNING=0
fi

# Check if the container is healthy
if [ "$(sudo docker inspect -f '{{.State.Health.Status}}' "${HOST_CONTAINERNAME}")" = "healthy" ]; then
  echo "Container ${HOST_CONTAINERNAME} is healthy."
else
  echo "Container ${HOST_CONTAINERNAME} is not healthy."
  DB_IS_RUNNING=0
fi

if [ -z "$DB_IS_RUNNING" ]
then
    echo "EuroDB service currently not running, starting..."
    screen -S EuroDB -dm bash -c "$ROOT_FOLDER/start_DB.sh"
else
    echo "EuroDB already running, restarting..."
    screen -S EuroDB -X quit
    screen -S EuroDB -dm bash -c "$ROOT_FOLDER/start_DB.sh"
fi

# Wait for the DB to start
sleep 10

if [ -z "$WATCHDOG_IS_RUNNING" ]
then
    echo "EuroWatchdog service currently not running, starting..."
    screen -S EuroWatchdog -dm bash -c "$ROOT_FOLDER/start_watchdog.sh"
else
    echo "EuroWatchdog already running, restarting..."
    screen -S EuroWatchdog -X quit
    screen -S EuroWatchdog -dm bash -c "$ROOT_FOLDER/start_watchdog.sh"
fi

cd - || exit 1
# EOF
