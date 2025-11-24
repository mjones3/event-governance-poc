# Story: CI/CD Schema Validation Pipeline

**Story Points**: 5
**Priority**: High
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: CI/CD Automation

---

## User Story

**As a** BioPro developer
**I want** schema compatibility automatically validated in pull requests
**So that** breaking schema changes are caught before merge and production deployment is prevented

---

## Description

Implement automated CI/CD pipeline that extracts schemas from code changes, compares with Schema Registry, validates backward compatibility, and blocks merges if breaking changes are detected. Pipeline should provide clear feedback to developers about schema changes and their compatibility impact.

### Background
Currently, schema changes can be merged without compatibility validation, leading to:
- Breaking changes deployed to production
- Consumer failures due to incompatible schemas
- Manual coordination required for schema changes
- Production incidents from schema mismatches
- No systematic review of schema evolution

This pipeline automates schema validation as part of standard development workflow.

---

## Acceptance Criteria

**AC1: Automatic Schema Extraction on PR**
- GIVEN a pull request modifying Java event classes
- WHEN PR is created or updated
- THEN CI/CD pipeline automatically extracts Avro schemas from changed Java code
- AND extraction happens in PR build job
- AND extracted schemas are available for comparison

**AC2: Schema Comparison with Registry**
- GIVEN extracted schemas from PR code
- WHEN pipeline runs schema comparison
- THEN each schema is compared against current version in Schema Registry
- AND differences are identified (added fields, removed fields, type changes)
- AND comparison results show what changed

**AC3: Backward Compatibility Validation**
- GIVEN schema differences detected
- WHEN compatibility is checked
- THEN Schema Registry compatibility endpoint is called
- AND backward compatibility is validated according to configured mode
- AND validation result is clear: COMPATIBLE or BREAKING

**AC4: Build Failure on Breaking Changes**
- GIVEN a schema change that is not backward compatible
- WHEN PR build runs
- THEN build FAILS with clear error message
- AND error message lists specific breaking changes:
  - "Removed field 'trackingId' - BREAKING"
  - "Changed type of 'shippedDate' from string to long - BREAKING"
- AND PR cannot be merged until issue is resolved

**AC5: PR Comment with Schema Change Summary**
- GIVEN schema changes detected (compatible or breaking)
- WHEN PR build completes
- THEN automated comment is posted to PR with summary:
  - List of events with schema changes
  - Type of changes (added field, etc.)
  - Compatibility status for each event
  - Action required (if breaking)
- AND comment is updated if PR is modified

**AC6: Automatic Registration on Merge (Compatible Changes Only)**
- GIVEN backward-compatible schema changes
- WHEN PR is merged to main branch
- THEN pipeline automatically registers new schema versions to Schema Registry
- AND schema IDs are returned and logged
- AND EventCatalog is triggered to update documentation

---

## Technical Details

### GitHub Actions Workflow
```yaml
name: Schema Compatibility Check

on:
  pull_request:
    paths:
      - '**/domain/event/**/*.java'

jobs:
  schema-validation:
    runs-on: ubuntu-latest

    services:
      schema-registry:
        image: confluentinc/cp-schema-registry:latest
        ports:
          - 8081:8081

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Extract Schemas from Java Code
        run: |
          python scripts/extract_schemas_from_java_v3.py \
            --source-dir ./src/main/java \
            --output-dir ./extracted-schemas

      - name: Compare with Schema Registry
        id: compare
        run: |
          python scripts/compare_schemas.py \
            --extracted-dir ./extracted-schemas \
            --registry-url http://localhost:8081 \
            --output schema-changes.json

      - name: Validate Compatibility
        id: validate
        run: |
          python scripts/validate_compatibility.py \
            --changes schema-changes.json \
            --registry-url http://localhost:8081

      - name: Comment on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const changes = JSON.parse(fs.readFileSync('schema-changes.json', 'utf8'));
            // Generate comment content...
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: commentBody
            });

      - name: Fail if Breaking Changes
        if: steps.validate.outcome == 'failure'
        run: |
          echo "❌ BREAKING SCHEMA CHANGES DETECTED"
          cat schema-changes.json
          exit 1
```

### Schema Comparison Script
```python
#!/usr/bin/env python3
"""
Compare extracted schemas with Schema Registry
"""
import requests
import json
from pathlib import Path

def compare_schemas(extracted_dir, registry_url):
    changes = []

    for schema_file in Path(extracted_dir).glob("*.avsc"):
        with open(schema_file) as f:
            new_schema = json.load(f)

        # Get current schema from registry
        subject = f"{new_schema['name']}-value"
        current = get_latest_schema(registry_url, subject)

        if current is None:
            changes.append({
                'event': new_schema['name'],
                'type': 'NEW',
                'compatible': True
            })
        else:
            # Compare schemas
            diff = compare_field_changes(current, new_schema)
            if diff:
                changes.append({
                    'event': new_schema['name'],
                    'type': 'MODIFIED',
                    'changes': diff,
                    'compatible': check_compatibility(registry_url, subject, new_schema)
                })

    return changes
```

---

## Implementation Tasks

### 1. Create Schema Extraction Script for CI (2 hours)
- [ ] Adapt existing extraction tool for CI environment
- [ ] Add command-line arguments for source/output directories
- [ ] Handle errors gracefully with clear messages
- [ ] Test in CI environment

### 2. Implement Schema Comparison Logic (3 hours)
- [ ] Create script to fetch current schemas from registry
- [ ] Implement field-by-field comparison
- [ ] Detect added/removed/modified fields
- [ ] Detect type changes
- [ ] Generate change summary in JSON format

### 3. Implement Compatibility Validation (2 hours)
- [ ] Call Schema Registry compatibility endpoint
- [ ] Parse compatibility response
- [ ] Determine if changes are backward compatible
- [ ] Generate clear error messages for breaking changes

### 4. Set Up GitHub Actions Workflow (3 hours)
- [ ] Create workflow YAML file
- [ ] Configure triggers (PR on event class changes)
- [ ] Add schema extraction step
- [ ] Add comparison step
- [ ] Add compatibility validation step
- [ ] Add PR comment step
- [ ] Test workflow end-to-end

### 5. Implement PR Comment Generation (2 hours)
- [ ] Format schema changes for readability
- [ ] Use markdown tables for changes
- [ ] Add emojis for visual clarity (✅ ❌)
- [ ] Include action items if breaking changes
- [ ] Test comment formatting

### 6. Implement Auto-Registration on Merge (2 hours)
- [ ] Create separate workflow for main branch
- [ ] Register compatible schemas to registry
- [ ] Log schema IDs
- [ ] Trigger EventCatalog update
- [ ] Handle registration failures

---

## Testing Strategy

### Unit Tests
- Schema comparison logic
- Compatibility determination
- Change summary generation

### Integration Tests
- Full pipeline run with sample schema changes
- Compatible change scenario
- Breaking change scenario
- New event scenario
- PR comment generation

### Test Scenarios
1. **No Schema Changes**: PR with non-event code changes
2. **New Event**: PR adding new event class
3. **Compatible Change**: PR adding optional field with default
4. **Breaking Change**: PR removing field or changing type
5. **Multiple Events**: PR changing multiple events

---

## Definition of Done

- [ ] CI/CD pipeline running on every PR touching event classes
- [ ] Schema extraction working in CI environment
- [ ] Schema comparison correctly identifying changes
- [ ] Compatibility validation calling Schema Registry API
- [ ] Breaking changes failing the build with clear error
- [ ] Compatible changes passing the build
- [ ] PR comments showing schema change summary
- [ ] Auto-registration working on merge to main
- [ ] At least 3 test PRs validated (new, compatible, breaking)
- [ ] Documentation complete (how to handle schema changes)

---

## Documentation Deliverables

- Developer guide: How to make schema changes
- CI/CD pipeline documentation
- Troubleshooting guide for common issues
- Schema evolution best practices
- Example PR comments for each scenario

---

## Sample PR Comment

```markdown
## 📋 Schema Changes Detected

### ✅ OrderCreatedEvent (Compatible)
- Added field `customerNotes` with default value
- **Backward Compatible**: ✅ Safe to merge

### ❌ ProductShippedEvent (Breaking Changes)
- Removed field `trackingId` without default
- Changed type of `shippedDate` from `string` to `timestamp-millis`
- **Backward Compatible**: ❌ NOT SAFE

**Action Required**: ProductShippedEvent has breaking changes.
Please either:
1. Add default value for removed fields
2. Create new event (ProductShippedV2Event)
3. Coordinate breaking change with all consumers

---
📚 [Schema Evolution Guide](https://wiki.biopro.com/schema-evolution)
```

---

## Risk & Mitigation

**Risk**: False positives blocking valid changes
- **Mitigation**: Clear documentation on how to override if needed
- **Mitigation**: Manual approval process for exceptional cases

**Risk**: CI/CD pipeline failures blocking all PRs
- **Mitigation**: Pipeline should fail fast with clear errors
- **Mitigation**: Monitoring and alerts on pipeline health

**Risk**: Developers circumvent validation
- **Mitigation**: Require pipeline success for merge (branch protection)
- **Mitigation**: Code review process catches attempts to bypass

---

**Labels**: ci-cd, schema-validation, automation, github-actions, proof-of-concept
**Created By**: Melvin Jones
