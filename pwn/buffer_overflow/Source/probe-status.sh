#!/bin/bash

# Default values for optional parameters
HOSTNAME="127.0.0.1"
PORT=1337
FLAG=""
CONTAINER_NAME=buffer_overflow$PORT

set -e

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --hostname)
            HOSTNAME="$2"; shift 2;;
        --port)
            PORT="$2"; shift 2;;
        --help)
            echo "Usage: ./run.sh --hostname HOSTNAME --port PORT --flag FLAG"
            echo "  --hostname   Hostname to bind the service (default: localhost)"
            echo "  --port       Port to expose the service (default: 1337)"
            exit 0;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./probe-status.sh --hostname HOSTNAME --port PORT"
            exit 1;;
    esac
done

nc -z $HOSTNAME $PORT
if [ $? -eq 0 ]
then
    echo "[OK] port $HOSTNAME - $PORT is open!"
else
    echo "[FAIL] port $HOSTNAME - $PORT is closed!"
    exit 1;
fi

docker inspect $CONTAINER_NAME > /dev/null
if [ $? -eq 0 ]
then
    echo "[OK] port container is running!"
    exit 0;
else
    echo "[FAIL ]container not found!"
    exit 1;
fi
