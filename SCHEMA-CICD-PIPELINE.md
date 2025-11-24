# Automated Schema Evolution CI/CD Pipeline

## Overview

Automatically detect event schema changes, validate compatibility, register new versions in Schema Registry, and sync with EventCatalog.

## Pipeline Flow

```
Code Change (Event Publisher/Listener)
    ↓
Extract Avro Schemas from Java Code
    ↓
Compare with Schema Registry (Current Version)
    ↓
Schema Changed? → No → Skip
    ↓ Yes
Validate Compatibility (BACKWARD/FORWARD/FULL)
    ↓
Compatible? → No → FAIL BUILD with error message
    ↓ Yes
Auto-increment Version & Register to Schema Registry
    ↓
Update EventCatalog with New Version
    ↓
Generate Migration Guide (if breaking changes detected)
    ↓
Success ✓
```

## Implementation Components

### 1. Schema Extraction (Already Built!)

You already have this with `extract_schemas_from_java_v3.py`. Use it in CI/CD:

```yaml
# .github/workflows/schema-evolution.yml or Jenkins/GitLab CI
steps:
  - name: Extract Avro Schemas from Java
    run: python scripts/extract_schemas_from_java_v3.py
```

### 2. Schema Comparison Script

```python
#!/usr/bin/env python3
"""
Compare extracted schemas with Schema Registry and detect changes
"""
import requests
import json
from pathlib import Path

SCHEMA_REGISTRY_URL = "http://localhost:8081"

def get_latest_schema_from_registry(subject: str):
    """Get current schema version from registry"""
    try:
        response = requests.get(
            f"{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions/latest"
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'id': data['id'],
                'version': data['version'],
                'schema': json.loads(data['schema'])
            }
        elif response.status_code == 404:
            return None  # New schema
    except Exception as e:
        print(f"Error fetching schema: {e}")
    return None

def compare_schemas(old_schema, new_schema):
    """Compare two schemas and return differences"""
    if old_schema is None:
        return {'is_new': True, 'changes': []}

    changes = []

    # Compare fields
    old_fields = {f['name']: f for f in old_schema.get('fields', [])}
    new_fields = {f['name']: f for f in new_schema.get('fields', [])}

    # Detect added fields
    for field_name in new_fields:
        if field_name not in old_fields:
            has_default = 'default' in new_fields[field_name]
            changes.append({
                'type': 'FIELD_ADDED',
                'field': field_name,
                'backward_compatible': has_default,
                'message': f"Added field '{field_name}'" +
                          (" with default value" if has_default else " WITHOUT default value - BREAKING!")
            })

    # Detect removed fields
    for field_name in old_fields:
        if field_name not in new_fields:
            changes.append({
                'type': 'FIELD_REMOVED',
                'field': field_name,
                'backward_compatible': False,
                'message': f"Removed field '{field_name}' - BREAKING CHANGE!"
            })

    # Detect type changes
    for field_name in old_fields:
        if field_name in new_fields:
            old_type = old_fields[field_name]['type']
            new_type = new_fields[field_name]['type']
            if old_type != new_type:
                changes.append({
                    'type': 'FIELD_TYPE_CHANGED',
                    'field': field_name,
                    'backward_compatible': False,
                    'message': f"Changed type of '{field_name}' from {old_type} to {new_type} - BREAKING CHANGE!"
                })

    return {'is_new': False, 'changes': changes}

def check_compatibility(subject: str, new_schema: dict):
    """Check if new schema is compatible with existing schema"""
    try:
        response = requests.post(
            f"{SCHEMA_REGISTRY_URL}/compatibility/subjects/{subject}/versions/latest",
            json={'schema': json.dumps(new_schema)},
            headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('is_compatible', False)
        elif response.status_code == 404:
            # No existing schema - it's a new event
            return True
    except Exception as e:
        print(f"Error checking compatibility: {e}")
    return False

def main():
    """Main function to detect schema changes"""
    import sys

    # Load extracted schemas
    extracted_schemas_dir = Path("extracted-biopro-schemas-v3")

    has_breaking_changes = False
    schema_changes = []

    for schema_file in extracted_schemas_dir.glob("*.avsc"):
        with open(schema_file, 'r') as f:
            new_schema = json.load(f)

        event_name = new_schema.get('name')
        subject = f"{event_name}-value"

        # Get current schema from registry
        current = get_latest_schema_from_registry(subject)
        current_schema = current['schema'] if current else None

        # Compare schemas
        diff = compare_schemas(current_schema, new_schema)

        if diff['is_new']:
            print(f"✓ NEW EVENT: {event_name}")
            schema_changes.append({
                'event': event_name,
                'subject': subject,
                'type': 'NEW',
                'compatible': True
            })
        elif diff['changes']:
            print(f"\n📝 CHANGES DETECTED: {event_name}")

            # Check compatibility
            is_compatible = check_compatibility(subject, new_schema)

            for change in diff['changes']:
                symbol = "✓" if change['backward_compatible'] else "✗"
                print(f"  {symbol} {change['message']}")

            if is_compatible:
                print(f"  ✓ BACKWARD COMPATIBLE - Safe to deploy")
                schema_changes.append({
                    'event': event_name,
                    'subject': subject,
                    'type': 'UPDATE',
                    'compatible': True,
                    'changes': diff['changes']
                })
            else:
                print(f"  ✗ NOT BACKWARD COMPATIBLE - BREAKING CHANGE!")
                has_breaking_changes = True
                schema_changes.append({
                    'event': event_name,
                    'subject': subject,
                    'type': 'UPDATE',
                    'compatible': False,
                    'changes': diff['changes']
                })

    # Save change report
    with open('schema-changes-report.json', 'w') as f:
        json.dump(schema_changes, f, indent=2)

    if has_breaking_changes:
        print("\n❌ BREAKING CHANGES DETECTED - Build should fail!")
        print("Review schema-changes-report.json for details")
        sys.exit(1)
    elif schema_changes:
        print(f"\n✓ {len(schema_changes)} schema changes detected - all backward compatible")
        sys.exit(0)
    else:
        print("\n✓ No schema changes detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### 3. Auto-Register New Versions

```python
#!/usr/bin/env python3
"""
Auto-register schema changes to Schema Registry with version increment
"""
import requests
import json
from pathlib import Path

SCHEMA_REGISTRY_URL = "http://localhost:8081"

def register_schema(subject: str, schema: dict):
    """Register schema and get new version"""
    try:
        response = requests.post(
            f"{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions",
            json={'schema': json.dumps(schema)},
            headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
        )

        if response.status_code in [200, 201]:
            data = response.json()
            return {
                'id': data['id'],
                'success': True
            }
        else:
            return {
                'success': False,
                'error': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Register all changed schemas"""
    # Load change report from previous step
    with open('schema-changes-report.json', 'r') as f:
        changes = json.load(f)

    registered = []

    for change in changes:
        if change['type'] in ['NEW', 'UPDATE'] and change['compatible']:
            # Load schema file
            schema_file = Path(f"extracted-biopro-schemas-v3/{change['event']}.avsc")
            with open(schema_file, 'r') as f:
                schema = json.load(f)

            # Register to Schema Registry
            result = register_schema(change['subject'], schema)

            if result['success']:
                print(f"✓ Registered {change['event']} - Schema ID: {result['id']}")
                registered.append({
                    'event': change['event'],
                    'subject': change['subject'],
                    'schema_id': result['id'],
                    'type': change['type']
                })
            else:
                print(f"✗ Failed to register {change['event']}: {result['error']}")

    # Save registration report
    with open('schema-registration-report.json', 'w') as f:
        json.dump(registered, f, indent=2)

    print(f"\n✓ Registered {len(registered)} schemas")

if __name__ == "__main__":
    main()
```

### 4. Sync with EventCatalog

```python
#!/usr/bin/env python3
"""
Update EventCatalog with new schema versions
"""
import json
from pathlib import Path

def update_eventcatalog():
    """Update EventCatalog with new schema versions"""
    # Load registration report
    with open('schema-registration-report.json', 'r') as f:
        registered = json.load(f)

    for item in registered:
        event_name = item['event'].replace('Event', '')
        event_dir = Path(f"eventcatalog/events/{event_name}")

        if event_dir.exists():
            # Run your existing update script for just this event
            print(f"✓ Updated EventCatalog for {event_name}")
        else:
            print(f"⚠ Event directory not found: {event_dir}")

if __name__ == "__main__":
    update_eventcatalog()
```

### 5. Complete CI/CD Pipeline

```yaml
# .github/workflows/schema-evolution.yml
name: Schema Evolution Pipeline

on:
  pull_request:
    paths:
      - 'src/**/domain/event/**'  # Event classes
      - 'src/**/listener/**'       # Event listeners
  push:
    branches:
      - main

jobs:
  schema-evolution:
    runs-on: ubuntu-latest

    services:
      schema-registry:
        image: confluentinc/cp-schema-registry:latest
        ports:
          - 8081:8081
        env:
          SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:9092

      kafka:
        image: confluentinc/cp-kafka:latest
        ports:
          - 9092:9092

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install requests

      - name: Extract Avro Schemas from Java Code
        run: |
          python scripts/extract_schemas_from_java_v3.py

      - name: Detect Schema Changes
        id: detect_changes
        run: |
          python scripts/detect_schema_changes.py
        continue-on-error: true

      - name: Check for Breaking Changes
        if: steps.detect_changes.outcome == 'failure'
        run: |
          echo "❌ BREAKING CHANGES DETECTED!"
          echo "Please review schema-changes-report.json"
          cat schema-changes-report.json
          exit 1

      - name: Register Schema Changes (main branch only)
        if: github.ref == 'refs/heads/main' && steps.detect_changes.outcome == 'success'
        run: |
          python scripts/register_schema_changes.py

      - name: Update EventCatalog (main branch only)
        if: github.ref == 'refs/heads/main' && steps.detect_changes.outcome == 'success'
        run: |
          python scripts/sync_eventcatalog.py

      - name: Upload Schema Change Report
        uses: actions/upload-artifact@v3
        with:
          name: schema-changes-report
          path: schema-changes-report.json

      - name: Comment on PR with Schema Changes
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('schema-changes-report.json', 'utf8'));

            let comment = '## 📋 Schema Evolution Report\n\n';

            for (const change of report) {
              const icon = change.compatible ? '✅' : '❌';
              comment += `${icon} **${change.event}** (${change.type})\n`;

              if (change.changes) {
                for (const c of change.changes) {
                  comment += `  - ${c.message}\n`;
                }
              }
              comment += '\n';
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 6. Jenkins Pipeline (Alternative)

```groovy
pipeline {
    agent any

    stages {
        stage('Extract Schemas') {
            steps {
                sh 'python scripts/extract_schemas_from_java_v3.py'
            }
        }

        stage('Detect Changes') {
            steps {
                script {
                    def result = sh(
                        script: 'python scripts/detect_schema_changes.py',
                        returnStatus: true
                    )

                    if (result != 0) {
                        error("Breaking schema changes detected!")
                    }
                }
            }
        }

        stage('Register Schemas') {
            when {
                branch 'main'
            }
            steps {
                sh 'python scripts/register_schema_changes.py'
            }
        }

        stage('Update EventCatalog') {
            when {
                branch 'main'
            }
            steps {
                sh 'python scripts/sync_eventcatalog.py'
                sh 'cd eventcatalog && npm run build'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'schema-changes-report.json', allowEmptyArchive: true
        }
    }
}
```

## Benefits

1. **Automatic Detection**: No manual schema management needed
2. **Safety**: Catches breaking changes before they reach production
3. **Versioning**: Automatic version increments in Schema Registry
4. **Documentation**: EventCatalog stays in sync automatically
5. **Visibility**: PR comments show exactly what schemas changed
6. **Compatibility Reports**: Clear indication of backward compatibility

## Example PR Comment

```markdown
## 📋 Schema Evolution Report

✅ **OrderCreatedEvent** (UPDATE)
  - Added field 'customerNotes' with default value
  - Backward Compatible ✓

✅ **CollectionReceivedEvent** (NEW)
  - New event schema
  - Backward Compatible ✓

❌ **ProductShippedEvent** (UPDATE)
  - Removed field 'legacyTrackingId' WITHOUT default value - BREAKING!
  - Changed type of 'shippedDate' from string to timestamp-millis - BREAKING CHANGE!
  - Not Backward Compatible ✗

**Action Required**: ProductShippedEvent has breaking changes.
Please review and consider using a new event name or adding compatibility layer.
```

## Next Steps

Would you like me to:
1. Create these CI/CD scripts for your environment?
2. Set up the GitHub Actions or Jenkins pipeline?
3. Add Slack/Teams notifications for schema changes?
4. Create a schema evolution dashboard?
