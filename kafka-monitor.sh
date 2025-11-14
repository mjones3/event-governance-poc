#!/bin/bash
# Kafka Monitoring Helper Script
# Common kcat commands for monitoring your Kafka cluster

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KCAT="$SCRIPT_DIR/kcat.sh"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function show_help() {
    echo -e "${BLUE}=== Kafka Monitoring Commands ===${NC}"
    echo ""
    echo "Usage: ./kafka-monitor.sh [command]"
    echo ""
    echo "Commands:"
    echo "  brokers          - Show broker information"
    echo "  topics           - List all topics"
    echo "  dlq              - Show DLQ messages"
    echo "  dlq-tail         - Monitor DLQ in real-time"
    echo "  consume <topic>  - Consume from a specific topic"
    echo "  metadata         - Show full cluster metadata"
    echo "  help             - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./kafka-monitor.sh brokers"
    echo "  ./kafka-monitor.sh topics"
    echo "  ./kafka-monitor.sh consume biopro.orders.dlq"
}

function show_brokers() {
    echo -e "${GREEN}=== Kafka Brokers ===${NC}"
    $KCAT -L | grep -E "broker|Metadata"
}

function list_topics() {
    echo -e "${GREEN}=== Kafka Topics ===${NC}"
    $KCAT -L | grep 'topic "' | sed 's/  topic //'
}

function show_dlq() {
    echo -e "${GREEN}=== DLQ Messages (last 10) ===${NC}"
    $KCAT -C -t biopro.orders.dlq -o -10 -f 'Offset %o | Time: %T | Key: %k\nValue: %s\n---\n'
}

function tail_dlq() {
    echo -e "${GREEN}=== Monitoring DLQ (Ctrl+C to stop) ===${NC}"
    $KCAT -C -t biopro.orders.dlq -o end -f 'Time: %T | Offset: %o\nKey: %k\nValue: %s\n========================================\n'
}

function consume_topic() {
    local topic=$1
    if [ -z "$topic" ]; then
        echo -e "${YELLOW}Error: Please specify a topic name${NC}"
        echo "Usage: ./kafka-monitor.sh consume <topic-name>"
        exit 1
    fi
    echo -e "${GREEN}=== Consuming from $topic ===${NC}"
    $KCAT -C -t "$topic" -o beginning -f 'Offset %o | Time: %T\nKey: %k\nValue: %s\n---\n'
}

function show_metadata() {
    echo -e "${GREEN}=== Full Cluster Metadata ===${NC}"
    $KCAT -L
}

# Main command handler
case "${1:-help}" in
    brokers)
        show_brokers
        ;;
    topics)
        list_topics
        ;;
    dlq)
        show_dlq
        ;;
    dlq-tail)
        tail_dlq
        ;;
    consume)
        consume_topic "$2"
        ;;
    metadata)
        show_metadata
        ;;
    help|*)
        show_help
        ;;
esac
