#!/bin/bash
# Interactive Kafka Monitoring UI using kcat
# Provides a menu-driven interface for monitoring Kafka

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KCAT="$SCRIPT_DIR/kcat.sh"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function show_menu() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}           Kafka Monitoring Dashboard (kcat)${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}[1]${NC} View Broker Status"
    echo -e "${GREEN}[2]${NC} List All Topics"
    echo -e "${GREEN}[3]${NC} View DLQ Messages (last 10)"
    echo -e "${GREEN}[4]${NC} Monitor DLQ in Real-Time"
    echo -e "${GREEN}[5]${NC} Consume from Specific Topic"
    echo -e "${GREEN}[6]${NC} Show Full Cluster Metadata"
    echo -e "${GREEN}[7]${NC} Produce Test Message to DLQ"
    echo -e "${GREEN}[8]${NC} Check Service Health"
    echo -e "${GREEN}[9]${NC} View Container Logs"
    echo -e "${GREEN}[0]${NC} Exit"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -n "Select option: "
}

function show_brokers() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Kafka Broker Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    $KCAT -L | grep -E "broker|Metadata"
    echo ""
    read -p "Press Enter to continue..."
}

function list_topics() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Kafka Topics${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    $KCAT -L | grep 'topic "' | sed 's/  topic /  /'
    echo ""
    read -p "Press Enter to continue..."
}

function view_dlq() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Dead Letter Queue - Last 10 Messages${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    $KCAT -C -t biopro.orders.dlq -o -10 -e -f 'Offset: %o | Time: %T\nKey: %k\nValue: %s\n---\n' 2>/dev/null || echo "No messages found"
    echo ""
    read -p "Press Enter to continue..."
}

function monitor_dlq() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Monitoring DLQ in Real-Time (Ctrl+C to stop)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    $KCAT -C -t biopro.orders.dlq -o end -f 'Time: %T | Offset: %o\nKey: %k\nValue: %s\n════════════════════════════════════════════════════════════\n'
    echo ""
    read -p "Press Enter to continue..."
}

function consume_topic() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Consume from Topic${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Available topics:"
    $KCAT -L | grep 'topic "' | sed 's/.*topic "\([^"]*\)".*/  - \1/'
    echo ""
    read -p "Enter topic name: " topic
    if [ -z "$topic" ]; then
        echo "No topic specified"
        read -p "Press Enter to continue..."
        return
    fi
    echo ""
    echo "How many messages? (Enter for all from beginning)"
    read -p "Count (-10 for last 10, or blank for all): " count

    if [ -z "$count" ]; then
        $KCAT -C -t "$topic" -o beginning -f 'Offset: %o | Time: %T\nKey: %k\nValue: %s\n---\n'
    else
        $KCAT -C -t "$topic" -o "$count" -e -f 'Offset: %o | Time: %T\nKey: %k\nValue: %s\n---\n'
    fi
    echo ""
    read -p "Press Enter to continue..."
}

function show_metadata() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Full Cluster Metadata${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    $KCAT -L
    echo ""
    read -p "Press Enter to continue..."
}

function produce_message() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Produce Test Message to DLQ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Enter message (JSON format recommended):"
    read -p "> " message
    if [ -z "$message" ]; then
        echo "No message entered"
        read -p "Press Enter to continue..."
        return
    fi
    echo "$message" | $KCAT -P -t biopro.orders.dlq
    echo ""
    echo -e "${GREEN}✓ Message sent successfully${NC}"
    echo ""
    read -p "Press Enter to continue..."
}

function check_health() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Service Health Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "biopro|NAMES"
    echo ""
    read -p "Press Enter to continue..."
}

function view_logs() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   View Container Logs${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Available services:"
    docker ps --format "  {{.Names}}" | grep biopro
    echo ""
    read -p "Enter service name: " service
    if [ -z "$service" ]; then
        echo "No service specified"
        read -p "Press Enter to continue..."
        return
    fi
    echo ""
    echo "Showing last 50 lines (Ctrl+C to stop):"
    echo ""
    docker logs --tail 50 -f "$service"
    echo ""
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read -r choice

    case $choice in
        1)
            show_brokers
            ;;
        2)
            list_topics
            ;;
        3)
            view_dlq
            ;;
        4)
            monitor_dlq
            ;;
        5)
            consume_topic
            ;;
        6)
            show_metadata
            ;;
        7)
            produce_message
            ;;
        8)
            check_health
            ;;
        9)
            view_logs
            ;;
        0)
            echo ""
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            sleep 1
            ;;
    esac
done
