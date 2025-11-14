#!/bin/bash
# kcat wrapper script - automatically uses the kcat container
# Usage: ./kcat.sh [kcat options]
# Example: ./kcat.sh -L
#          ./kcat.sh -C -t biopro.orders.dlq -o beginning

docker exec biopro-kcat kcat -b redpanda:9092 "$@"
