#!/bin/bash
# Default values for optional parameters
HOSTNAME="127.0.0.1"
PORT=1337
FLAG=""

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --port)
            PORT="$2"; shift 2;;
        --help)
            echo "Usage: ./desroy.sh --port PORT"
            echo "  --port       Port the service is exposed at (default: 1337)"
            exit 0;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./desroy.sh --port PORT"
            exit 1;;
    esac
done

# Build and run the Docker container
export HOSTNAME=$HOSTNAME
export PORT=$PORT
export FLAG=$FLAG

docker kill buffer_overflow$PORT
docker remove buffer_overflow$PORT
# Exit with the status code of the previous command
exit $?
