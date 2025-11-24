#!/bin/bash

###############################################################################
# BioPro Schema Registry - EventCatalog Schema Registration
#
# This script registers all Avro schemas from EventCatalog to Schema Registry
###############################################################################

set -e

# Configuration
SCHEMA_REGISTRY_URL="${SCHEMA_REGISTRY_URL:-http://localhost:8081}"
EVENTCATALOG_DIR="./eventcatalog/events"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   BioPro EventCatalog Schema Registration Tool        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Schema Registry URL:${NC} $SCHEMA_REGISTRY_URL"
echo -e "${YELLOW}EventCatalog Events:${NC} $EVENTCATALOG_DIR"
echo ""

# Check if Schema Registry is accessible
echo -e "${BLUE}[1/3] Checking Schema Registry connectivity...${NC}"
if ! curl -sf "$SCHEMA_REGISTRY_URL/subjects" > /dev/null 2>&1; then
    echo -e "${RED}✗ ERROR: Cannot connect to Schema Registry at $SCHEMA_REGISTRY_URL${NC}"
    echo -e "${YELLOW}  Make sure Schema Registry is running:${NC}"
    echo -e "${YELLOW}    docker-compose up -d schema-registry${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Schema Registry${NC}"
echo ""

# Check if eventcatalog directory exists
echo -e "${BLUE}[2/3] Checking EventCatalog directory...${NC}"
if [ ! -d "$EVENTCATALOG_DIR" ]; then
    echo -e "${RED}✗ ERROR: EventCatalog directory not found: $EVENTCATALOG_DIR${NC}"
    exit 1
fi

# Count schema files
schema_count=$(find "$EVENTCATALOG_DIR" -name "*.avsc" | wc -l)
if [ "$schema_count" -eq 0 ]; then
    echo -e "${RED}✗ ERROR: No .avsc files found in $EVENTCATALOG_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found $schema_count schema file(s)${NC}"
echo ""

# Register each schema
echo -e "${BLUE}[3/3] Registering schemas...${NC}"
echo ""

registered=0
failed=0
skipped=0

find "$EVENTCATALOG_DIR" -name "*.avsc" | while read schema_file; do
    # Extract event name and schema name from path
    event_dir=$(dirname "$schema_file")
    event_name=$(basename "$event_dir")
    schema_name=$(basename "$schema_file" .avsc)

    # Skip payload-only schemas (they're embedded in the main schema)
    if [[ "$schema_name" == *"Payload" ]]; then
        echo -e "${YELLOW}⊘ Skipping payload schema:${NC} $schema_name (embedded in main schema)"
        ((skipped++))
        echo ""
        continue
    fi

    subject="${schema_name}"

    echo -e "${YELLOW}→ Registering: ${NC}$schema_name"
    echo -e "  Event: $event_name"
    echo -e "  File: $schema_file"
    echo -e "  Subject: $subject"

    # Validate JSON first
    if ! jq empty "$schema_file" 2>/dev/null; then
        echo -e "${RED}  ✗ Invalid JSON in schema file${NC}"
        ((failed++))
        echo ""
        continue
    fi

    # Read and escape the schema content for JSON
    schema_content=$(cat "$schema_file" | jq -c . | jq -R .)

    # Create the registration payload
    payload="{\"schema\": $schema_content}"

    # Register the schema
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/vnd.schemaregistry.v1+json" \
        --data "$payload" \
        "$SCHEMA_REGISTRY_URL/subjects/$subject/versions")

    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        schema_id=$(echo "$response_body" | jq -r '.id')
        echo -e "${GREEN}  ✓ Registered successfully${NC}"
        echo -e "    Schema ID: $schema_id"
        echo -e "    HTTP Status: $http_code"
        ((registered++))
    else
        echo -e "${RED}  ✗ Registration failed${NC}"
        echo -e "    HTTP Status: $http_code"
        echo -e "    Response: $response_body"
        ((failed++))
    fi

    echo ""
done

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Registration Summary:${NC}"
echo -e "  ${GREEN}✓ Successfully registered: $registered${NC}"
echo -e "  ${YELLOW}⊘ Skipped (embedded): $skipped${NC}"
if [ "$failed" -gt 0 ]; then
    echo -e "  ${RED}✗ Failed: $failed${NC}"
fi
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Show registered subjects
echo -e "${BLUE}Registered Subjects in Schema Registry:${NC}"
curl -s "$SCHEMA_REGISTRY_URL/subjects" | jq -r '.[]' | head -20
echo ""
echo -e "${YELLOW}(Showing first 20 subjects)${NC}"
echo ""

# Show next steps
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. View all schemas: ${BLUE}http://localhost:8000${NC} (Schema Registry UI)"
echo -e "  2. View subjects API: ${BLUE}curl $SCHEMA_REGISTRY_URL/subjects${NC}"
echo -e "  3. EventCatalog: ${BLUE}http://localhost:3002${NC}"
echo ""

exit 0
