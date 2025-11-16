#!/bin/bash
#
# Register Avro Schemas to Confluent Schema Registry
# Usage: ./register-schemas.sh <schema-directory> <schema-registry-url>
#
# Example:
#   ./register-schemas.sh schemas http://localhost:8081
#

set -e  # Exit on error

SCHEMA_DIR=${1:-schemas}
SCHEMA_REGISTRY_URL=${2:-http://localhost:8081}

echo "========================================="
echo "Schema Registry Auto-Registration"
echo "========================================="
echo "Schema Directory: ${SCHEMA_DIR}"
echo "Schema Registry: ${SCHEMA_REGISTRY_URL}"
echo ""

# Counter for registered schemas
REGISTERED_COUNT=0
FAILED_COUNT=0

# Find all .avsc files in the schema directory
for schema_file in $(find "${SCHEMA_DIR}" -name "*.avsc" -type f); do
    echo "Processing: ${schema_file}"

    # Extract event name from filename (remove .avsc extension)
    filename=$(basename "${schema_file}")
    event_name="${filename%.avsc}"

    # Determine subject name based on directory structure
    # Example: schemas/testresults/TestResultReceived.avsc → testresults.TestResultReceived-value
    relative_path=$(dirname "${schema_file}" | sed "s|^${SCHEMA_DIR}/||")

    if [ "${relative_path}" == "." ] || [ -z "${relative_path}" ]; then
        # Schema in root of schemas/ directory
        subject="${event_name}-value"
    else
        # Schema in subdirectory
        subject="${relative_path}.${event_name}-value"
    fi

    echo "  → Subject: ${subject}"

    # Read schema content and escape for JSON
    schema_content=$(cat "${schema_file}" | jq -c .)

    # Build request payload
    request_payload=$(jq -n \
        --arg schema "$schema_content" \
        '{schema: $schema}')

    # Register schema with Schema Registry
    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/vnd.schemaregistry.v1+json" \
        --data "${request_payload}" \
        "${SCHEMA_REGISTRY_URL}/subjects/${subject}/versions")

    # Extract HTTP status code (last line)
    http_code=$(echo "${response}" | tail -n1)
    response_body=$(echo "${response}" | sed '$d')

    if [ "${http_code}" -eq 200 ] || [ "${http_code}" -eq 201 ]; then
        schema_id=$(echo "${response_body}" | jq -r '.id')
        echo "  ✓ Registered successfully (ID: ${schema_id})"
        ((REGISTERED_COUNT++))

        # Log to file for CI/CD artifacts
        echo "SCHEMA_${event_name}_ID=${schema_id}" >> schema-registration.env
        echo "[$(date)] ${subject} → ID ${schema_id}" >> schema-registration.log
    else
        echo "  ✗ Failed to register (HTTP ${http_code})"
        echo "  Response: ${response_body}"
        ((FAILED_COUNT++))

        # Log failure
        echo "[$(date)] FAILED: ${subject} → ${response_body}" >> schema-registration.log
    fi

    echo ""
done

echo "========================================="
echo "Summary"
echo "========================================="
echo "Registered: ${REGISTERED_COUNT}"
echo "Failed:     ${FAILED_COUNT}"

if [ ${FAILED_COUNT} -gt 0 ]; then
    echo ""
    echo "⚠️  Some schemas failed to register. Check schema-registration.log for details."
    exit 1
else
    echo ""
    echo "✓ All schemas registered successfully!"
    exit 0
fi
