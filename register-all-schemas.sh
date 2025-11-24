#!/bin/bash

###############################################################################
# BioPro Schema Registry - Bulk Schema Registration
#
# This script registers all Avro schemas to Confluent Schema Registry
# After registration, SpringWolf can document them automatically
###############################################################################

set -e

# Configuration
SCHEMA_REGISTRY_URL="${SCHEMA_REGISTRY_URL:-http://localhost:8081}"
SCHEMAS_DIR="./schemas/avro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   BioPro Schema Registry - Bulk Registration Tool     ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${YELLOW}Schema Registry URL:${NC} $SCHEMA_REGISTRY_URL"
echo -e "${YELLOW}Schemas Directory:${NC} $SCHEMAS_DIR"
echo ""

# Check if Schema Registry is accessible
echo -e "${BLUE}[1/3] Checking Schema Registry connectivity...${NC}"
if ! curl -sf "$SCHEMA_REGISTRY_URL/subjects" > /dev/null 2>&1; then
    echo -e "${RED}✗ ERROR: Cannot connect to Schema Registry at $SCHEMA_REGISTRY_URL${NC}"
    echo -e "${YELLOW}  Make sure Schema Registry is running:${NC}"
    echo -e "${YELLOW}    docker-compose ps schema-registry${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Schema Registry${NC}"
echo ""

# Check if schemas directory exists
echo -e "${BLUE}[2/3] Checking schemas directory...${NC}"
if [ ! -d "$SCHEMAS_DIR" ]; then
    echo -e "${RED}✗ ERROR: Schemas directory not found: $SCHEMAS_DIR${NC}"
    exit 1
fi

# Count schema files
schema_count=$(find "$SCHEMAS_DIR" -name "*.avsc" | wc -l)
if [ "$schema_count" -eq 0 ]; then
    echo -e "${RED}✗ ERROR: No .avsc files found in $SCHEMAS_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found $schema_count schema file(s)${NC}"
echo ""

# Register each schema
echo -e "${BLUE}[3/3] Registering schemas...${NC}"
echo ""

registered=0
failed=0

for schema_file in "$SCHEMAS_DIR"/*.avsc; do
    schema_name=$(basename "$schema_file" .avsc)
    subject="${schema_name}-value"

    echo -e "${YELLOW}→ Registering: ${NC}$schema_name"
    echo -e "  File: $schema_file"
    echo -e "  Subject: $subject"

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
echo -e "${GREEN}Registration complete!${NC}"
echo -e "  ${GREEN}✓ Successfully registered: $registered${NC}"
if [ "$failed" -gt 0 ]; then
    echo -e "  ${RED}✗ Failed: $failed${NC}"
fi
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Verify registration
echo -e "${BLUE}Verifying registered subjects:${NC}"
curl -s "$SCHEMA_REGISTRY_URL/subjects" | jq -r '.[]' | grep -E "(ApheresisPlasmaProductCreated|CollectionReceived|OrderCreated)" || echo "No BioPro subjects found"
echo ""

# Show next steps
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Verify schemas: ${BLUE}curl $SCHEMA_REGISTRY_URL/subjects${NC}"
echo -e "  2. Add SpringWolf to your services"
echo -e "  3. Access AsyncAPI docs: ${BLUE}http://localhost:8082/springwolf/docs${NC}"
echo -e "  4. Sync to EventCatalog: ${BLUE}npm run generate${NC}"
echo ""

exit 0
