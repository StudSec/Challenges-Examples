#!/bin/bash

# Default values for optional parameters
HOSTNAME="127.0.0.1"
PORT=1337
FLAG=""
TEAM_UUID=""

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --hostname)
            HOSTNAME="$2"; shift 2;;
        --port)
            PORT="$2"; shift 2;;
        --flag)
            FLAG="$2"; shift 2;;
        --team)
            TEAM_UUID="$2"; shift 2;;
        --help)
            echo "Usage: ./run.sh --hostname HOSTNAME --port PORT --flag FLAG --team TEAM_UUID"
            echo "  --hostname   Hostname to bind the service (default: localhost)"
            echo "  --port       Port to expose the service (default: 1337)"
            echo "  --flag       Flag to set in the container (required)"
            echo ""
            exit 0;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./run.sh --hostname HOSTNAME --port PORT --flag FLAG"
            exit 1;;
    esac
done

# Check if required arguments are provided
if [ -z "$FLAG" ]; then
    echo "Error: --flag argument is required."
    echo "Usage: ./run.sh --hostname HOSTNAME --port PORT --flag FLAG"
    exit 1
fi

# Build and run the Docker container
export HOSTNAME=$HOSTNAME
export PORT=$PORT
export FLAG=$FLAG

if [ -n "$TEAM_UUID" ]; then
  docker compose -p "buffer_overflow_$TEAM_UUID" up --build -d
else
  docker compose up --build -d
fi

echo "Challenge running on $HOSTNAME:$PORT with $FLAG"
