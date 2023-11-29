#!/bin/bash

export "$(grep -v '^#' .env | xargs -d '\n')" || exit 1

cd "$ROOT_FOLDER" || exit 1

git pull origin master --quiet || exit 1

source "$ROOT_FOLDER"/venv/bin/activate || exit 1

DB_IS_RUNNING=$(screen -ls | grep EuroDB)
WATCHDOG_IS_RUNNING=$(screen -ls | grep EuroWatchdog)

if [ -z "$DB_IS_RUNNING" ]
then
    echo "EuroDB service currently not running, starting..."
    screen -S EuroDB -dm bash -c "$ROOT_FOLDER/start_DB.sh"
else
    echo "EuroDB already running, restarting..."
    screen -S EuroDB -X quit
    screen -S EuroDB -dm bash -c "$ROOT_FOLDER/start_DB.sh"
fi

if [ -z "$WATCHDOG_IS_RUNNING" ]
then
    echo "EuroWatchdog service currently not running, starting..."
    screen -S EuroWatchdog -dm bash -c "$ROOT_FOLDER/start_watchdog.sh"
else
    echo "EuroWatchdog already running, restarting..."
    screen -S EuroWatchdog -X quit
    screen -S EuroWatchdog -dm bash -c "$ROOT_FOLDER/start_watchdog.sh"
fi

cd -
# EOF
