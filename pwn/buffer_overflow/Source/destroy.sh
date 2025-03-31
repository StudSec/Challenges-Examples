#!/bin/bash
# Default values for optional parameter
TEAM_UUID=""

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --team)
            TEAM_UUID="$2"; shift 2;;
        --help)
            echo "Usage: ./desroy.sh --team TEAM_UUID"
            echo "  --team       Unique identifier for per-team instance (optional)"
            exit 0;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./desroy.sh --team TEAM_UUID"
            exit 1;;
    esac
done

if [ -n "$TEAM_UUID" ]; then
  docker compose -p "buffer_overflow_$TEAM_UUID" down
else
  docker compose down
fi

# Exit with the status code of the previous command
exit $?
