# Story: EventCatalog Platform Upgrade and Enhancement

**Story Points**: 3
**Priority**: Low
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: Event Documentation

---

## User Story

**As a** BioPro developer
**I want** EventCatalog upgraded to latest version with customized event detail pages
**So that** I can view complete schema information, sample payloads, and download schemas without manual coordination

---

## Description

Upgrade EventCatalog platform from current version to latest stable release and customize event detail pages to display complete Avro schema fields extracted from Schema Registry, generate realistic sample event payloads, and provide schema downloads. Additional enhancements include improved visualization, BioPro branding, and performance optimization for large event catalogs.

### Background
EventCatalog evolves rapidly with new features that improve:
- Event discovery and search capabilities
- Service dependency visualization
- Schema version management
- Performance with large catalogs
- UI customization options

Current POC work has demonstrated the need for better event detail pages that:
- Display **all** schema fields with types, descriptions, and required status
- Generate **realistic sample payloads** based on Avro schemas
- Provide **schema downloads** without cluttering the page with full schema JSON
- Automatically extract field information from Schema Registry

Upgrading and customizing ensures developers have self-service access to accurate, current schema information.

---

## Acceptance Criteria

**AC1: Version Upgrade**
- GIVEN EventCatalog currently on older version
- WHEN upgrade to latest stable version is performed
- THEN EventCatalog successfully starts on new version
- AND all existing event pages display correctly
- AND all service pages display correctly
- AND no regression in core functionality
- AND new version number visible in UI footer

**AC2: Enhanced Search and Discovery**
- GIVEN upgraded EventCatalog with improved search
- WHEN developer searches for events
- THEN search includes:
  - Full-text search across event descriptions
  - Field-level search within schemas
  - Fuzzy matching for typos
  - Search result relevance ranking
  - Search filters (by domain, service, event type)
- AND search results display quickly (< 500ms)
- AND search highlights matching terms

**AC3: Improved Visualization**
- GIVEN upgraded EventCatalog with enhanced NodeGraph
- WHEN viewing service dependency visualization
- THEN visualization includes:
  - Interactive zoom and pan
  - Clickable nodes linking to service/event pages
  - Event flow direction indicators
  - Filterable views (by domain, event type)
  - Export to PNG/SVG
- AND visualization loads smoothly with 30+ services
- AND layout algorithm prevents overlapping nodes

**AC4: Schema Version Management**
- GIVEN events with multiple schema versions
- WHEN viewing event in EventCatalog
- THEN version history is displayed
- AND each version shows what changed
- AND developer can view any previous version
- AND backward compatibility status is indicated
- AND version timeline is visualized

**AC5: UI Customization and Branding**
- GIVEN BioPro branding requirements
- WHEN EventCatalog is customized
- THEN UI reflects BioPro brand:
  - BioPro logo in header
  - BioPro color scheme (primary, secondary)
  - Custom navigation links
  - BioPro favicon
  - Custom footer with links
- AND branding is consistent across all pages

**AC6: Event Detail Page Customization**
- GIVEN event registered in Schema Registry
- WHEN viewing event detail page in EventCatalog
- THEN page displays:
  - Complete schema fields table with name, type, required status, and description
  - Generated sample event payload in JSON format
  - Download link for Avro schema file (.avsc)
  - Schema version and ID
  - Producer and consumer services
- AND schema fields are automatically extracted from Schema Registry
- AND sample payload contains realistic data (UUIDs, timestamps, enums)
- AND full Avro schema JSON is NOT displayed inline (only available for download)

**AC7: Automated Event Page Generation**
- GIVEN script to update event pages from Schema Registry
- WHEN script is executed
- THEN all 80+ event pages are updated with:
  - Complete field information from Avro schemas
  - Generated sample payloads
  - Schema download links
- AND script handles complex types (arrays, maps, records, enums)
- AND script handles logical types (UUID, timestamp-millis)
- AND script completes in reasonable time (< 5 minutes)

**AC8: Performance Optimization**
- GIVEN EventCatalog with 80+ events and 30+ services
- WHEN navigating catalog
- THEN performance meets targets:
  - Homepage loads in < 2 seconds
  - Event page loads in < 1 second
  - Search results in < 500ms
  - Build time < 5 minutes
  - Hot reload during development < 3 seconds
- AND performance is measured and tracked

---

## Technical Details

### Current vs. Target Version
- **Current**: EventCatalog v1.x (or current POC version)
- **Target**: EventCatalog v2.x (latest stable)
- **Migration**: Review breaking changes and migration guide

### Upgrade Process
```bash
# Backup current configuration
cp -r eventcatalog eventcatalog-backup

# Update package.json
cd eventcatalog
npm install @eventcatalog/core@latest

# Update dependencies
npm install

# Update configuration file
# Review migration guide for breaking changes

# Test build
npm run build

# Test development mode
npm run dev
```

### Enhanced Configuration
```javascript
// eventcatalog.config.js
module.exports = {
  title: 'BioPro Event Catalog',
  tagline: 'Event-Driven Architecture Documentation',
  organizationName: 'BioPro Blood Management System',
  homepageLink: 'https://biopro.example.com',

  // Enhanced branding
  logo: {
    alt: 'BioPro Logo',
    src: '/img/biopro-logo.svg',
    href: 'https://biopro.example.com',
  },

  // Custom theme
  themeConfig: {
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
    },
    colors: {
      primary: '#0066CC',      // BioPro blue
      secondary: '#00A86B',    // BioPro green
      accent: '#FF6B35',       // BioPro orange
    },
    navbar: {
      links: [
        { label: 'Events', to: '/events' },
        { label: 'Services', to: '/services' },
        { label: 'Domains', to: '/domains' },
        { label: 'Schema Registry', href: 'http://schema-registry:8081' },
        { label: 'Wiki', href: 'https://wiki.biopro.com' },
      ],
    },
    footer: {
      copyright: `Copyright © ${new Date().getFullYear()} BioPro Corporation`,
      links: [
        { label: 'Documentation', href: 'https://wiki.biopro.com' },
        { label: 'Support', href: 'https://support.biopro.com' },
        { label: 'FDA Compliance', href: 'https://wiki.biopro.com/fda' },
      ],
    },
  },

  // Enhanced search
  search: {
    enabled: true,
    fuzzySearch: true,
    searchFields: ['name', 'summary', 'description', 'fields'],
    maxResults: 20,
  },

  // Visualization enhancements
  visualization: {
    nodeGraph: {
      layout: 'force-directed',
      interactive: true,
      exportFormats: ['png', 'svg'],
    },
  },

  // Performance optimizations
  build: {
    parallel: true,
    cache: true,
    minify: true,
  },
};
```

### Event Detail Page Customization Script
```python
#!/usr/bin/env python3
"""
Update EventCatalog event pages with complete schema information
"""
import requests
import json
from pathlib import Path

def update_event_pages(registry_url: str, events_dir: Path):
    """
    Fetch schemas from Schema Registry and update all event MDX files
    """
    # Get all subjects from Schema Registry
    response = requests.get(f"{registry_url}/subjects")
    subjects = response.json()

    for subject in subjects:
        if not subject.endswith('-value'):
            continue

        # Get latest schema
        schema_response = requests.get(
            f"{registry_url}/subjects/{subject}/versions/latest"
        )
        schema_data = schema_response.json()
        schema = json.loads(schema_data['schema'])

        # Extract fields
        fields = extract_fields_from_schema(schema)

        # Generate sample event
        sample = generate_sample_event(fields)

        # Create fields table
        fields_table = create_fields_table(fields)

        # Update MDX file
        event_name = schema['name']
        mdx_file = events_dir / event_name / 'index.mdx'

        if mdx_file.exists():
            update_mdx_file(mdx_file, fields_table, sample, event_name)

def extract_fields_from_schema(schema: dict) -> list:
    """Extract complete field information from Avro schema"""
    fields = []

    for field in schema.get('fields', []):
        field_type = get_field_type(field['type'])
        is_required = not is_optional_field(field['type'])

        fields.append({
            'name': field['name'],
            'type': field_type,
            'required': is_required,
            'description': field.get('doc', ''),
            'default': field.get('default')
        })

    return fields

def generate_sample_event(fields: list) -> dict:
    """Generate realistic sample event from schema fields"""
    sample = {}

    for field in fields:
        if 'id' in field['name'].lower() and field['type'] == 'string':
            sample[field['name']] = str(uuid.uuid4())
        elif field['type'] == 'timestamp-millis':
            sample[field['name']] = datetime.now().isoformat()
        elif field['type'].startswith('enum'):
            # Extract first enum value
            sample[field['name']] = 'SAMPLE_VALUE'
        else:
            sample[field['name']] = get_sample_value(field['type'])

    return sample

def create_fields_table(fields: list) -> str:
    """Create markdown table for schema fields"""
    table = "| Field | Type | Required | Description |\n"
    table += "|-------|------|----------|-------------|\n"

    for field in fields:
        required = "Yes" if field['required'] else "No"
        description = field['description'] or "Field description"
        table += f"| `{field['name']}` | `{field['type']}` | {required} | {description} |\n"

    return table

def update_mdx_file(mdx_file: Path, fields_table: str, sample: dict, event_name: str):
    """Update MDX file with new content"""
    # Read existing content
    with open(mdx_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build new sections
    new_content = f"""
## Event Schema Fields

{fields_table}

## Sample Event

```json
{json.dumps(sample, indent=2)}
```

## Download Schema

- [Download Avro Schema](./{event_name}.avsc)
"""

    # Replace or append sections
    # (Implementation would handle existing sections)

    with open(mdx_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
```

### Example Event Detail Page Structure
```markdown
---
id: OrderCreatedEvent
name: Order Created
version: 1.0.0
summary: Published when a new order is created in the system
producers:
  - orders-service
consumers:
  - collections-service
  - inventory-service
---

# Order Created Event

Published when a new blood product order is created and submitted to the system.

## Event Schema Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `orderId` | `string` (UUID) | Yes | Unique identifier for the order |
| `orderNumber` | `string` | Yes | Human-readable order number |
| `customerCode` | `string` | Yes | Customer/hospital identifier |
| `productCode` | `string` | Yes | Blood product type code |
| `quantity` | `int` | Yes | Quantity ordered |
| `priority` | `enum (ROUTINE, URGENT, EMERGENCY)` | Yes | Order priority level |
| `orderDate` | `timestamp-millis` | Yes | Timestamp when order was created |
| `deliveryDate` | `timestamp-millis` | No | Requested delivery date |
| `notes` | `string` | No | Additional order notes |

## Sample Event

```json
{
  "orderId": "550e8400-e29b-41d4-a716-446655440000",
  "orderNumber": "ORD-2024-001234",
  "customerCode": "HOSP-1001",
  "productCode": "PLATELET_APHERESIS",
  "quantity": 2,
  "priority": "ROUTINE",
  "orderDate": "2024-11-17T15:30:00Z",
  "deliveryDate": "2024-11-18T08:00:00Z",
  "notes": "Handle with care"
}
```

## Download Schema

- [Download Avro Schema](./OrderCreatedEvent.avsc)

<NodeGraph />
```

### Custom Styling
```css
/* custom.css */
:root {
  --biopro-blue: #0066CC;
  --biopro-green: #00A86B;
  --biopro-orange: #FF6B35;
}

.navbar {
  background-color: var(--biopro-blue);
}

.event-card {
  border-left: 4px solid var(--biopro-green);
}

.service-card {
  border-left: 4px solid var(--biopro-orange);
}

/* Improve search results highlighting */
.search-result mark {
  background-color: var(--biopro-orange);
  color: white;
  padding: 2px 4px;
  border-radius: 2px;
}

/* Schema fields table styling */
.event-schema-fields table {
  width: 100%;
  border-collapse: collapse;
}

.event-schema-fields th {
  background-color: var(--biopro-blue);
  color: white;
  padding: 12px;
  text-align: left;
}

.event-schema-fields td {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

/* Sample event code block styling */
.sample-event pre {
  background-color: #f5f5f5;
  border-left: 4px solid var(--biopro-green);
  padding: 16px;
  border-radius: 4px;
}
```

---

## Implementation Tasks

### 1. Pre-Upgrade Assessment (1 hour)
- [ ] Review EventCatalog changelog for breaking changes
- [ ] Document current version and features in use
- [ ] List custom modifications that may need updating
- [ ] Backup current eventcatalog directory
- [ ] Review migration guide

### 2. Perform Version Upgrade (2 hours)
- [ ] Update package.json dependencies
- [ ] Run npm install
- [ ] Update configuration file for new version
- [ ] Fix breaking changes identified in migration guide
- [ ] Test build process
- [ ] Test development mode
- [ ] Verify all existing pages render correctly

### 3. Configure Enhanced Search (2 hours)
- [ ] Enable fuzzy search in configuration
- [ ] Configure search fields (events, services, fields)
- [ ] Test search across event descriptions
- [ ] Test field-level search
- [ ] Optimize search indexing
- [ ] Test search performance

### 4. Enhance Visualization (2 hours)
- [ ] Configure NodeGraph layout algorithm
- [ ] Enable interactive features (zoom, pan)
- [ ] Add export functionality
- [ ] Test with full service graph (30+ services)
- [ ] Optimize rendering performance
- [ ] Add filtering options

### 5. Implement Schema Versioning UI (3 hours)
- [ ] Configure schema version display
- [ ] Add version comparison view
- [ ] Create version timeline component
- [ ] Test with events having multiple versions
- [ ] Document how to view version history

### 6. Apply BioPro Branding (2 hours)
- [ ] Add BioPro logo and favicon
- [ ] Configure color scheme
- [ ] Customize navigation links
- [ ] Update footer with BioPro links
- [ ] Apply custom CSS
- [ ] Test branding across all pages

### 7. Performance Optimization (2 hours)
- [ ] Enable build caching
- [ ] Configure parallel builds
- [ ] Enable code minification
- [ ] Test build performance
- [ ] Measure page load times
- [ ] Optimize images and assets

### 8. Customize Event Detail Pages (4 hours)
- [ ] Create script to fetch schemas from Schema Registry
- [ ] Implement Avro schema field extraction
- [ ] Implement sample event generation with realistic data
- [ ] Create markdown table formatting for schema fields
- [ ] Update all 80+ event MDX files with:
  - Complete schema fields table
  - Generated sample payloads
  - Schema download links
- [ ] Test event pages display correctly
- [ ] Verify sample events are realistic and valid

### 9. Testing and Validation (2 hours)
- [ ] Test all event pages render correctly
- [ ] Verify schema fields tables are complete
- [ ] Verify sample events display properly
- [ ] Test schema download links work
- [ ] Test all service pages render correctly
- [ ] Test search functionality
- [ ] Test NodeGraph visualization
- [ ] Test on different browsers
- [ ] Test responsive design (mobile, tablet)
- [ ] Performance testing with full catalog

---

## Testing Strategy

### Regression Testing
- Verify all 80+ event pages render correctly
- Verify all 30+ service pages render correctly
- Verify domain pages display
- Verify search returns expected results
- Verify NodeGraph visualization loads

### New Features Testing
- Test enhanced search with various queries
- Test fuzzy search with typos
- Test field-level search
- Test interactive NodeGraph (zoom, pan, click)
- Test schema version history display

### Performance Testing
- Measure homepage load time
- Measure search response time
- Measure build time
- Test with simulated slow network
- Profile JavaScript performance

### Browser Compatibility Testing
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Android)

---

## Definition of Done

- [ ] EventCatalog upgraded to latest stable version
- [ ] All existing pages render correctly on new version
- [ ] **Event detail pages customized with complete schema information**
- [ ] **All 80+ events show complete schema fields table**
- [ ] **Sample events generated and displayed for all events**
- [ ] **Schema download links working for all events**
- [ ] Enhanced search configured and working
- [ ] Improved visualization configured and tested
- [ ] Schema versioning UI functional (if multiple versions exist)
- [ ] BioPro branding applied across all pages
- [ ] Performance optimizations implemented
- [ ] Performance metrics meet targets
- [ ] Tested on multiple browsers
- [ ] Migration documented (what was upgraded, what changed)
- [ ] **Event page customization script documented and reusable**
- [ ] User guide updated for new features

---

## Documentation Deliverables

- Upgrade migration guide (what changed)
- **Event detail page customization guide**
- **Script usage documentation (update_event_pages.py)**
- **Schema fields extraction reference**
- **Sample event generation guide**
- New features user guide
- Enhanced search usage examples
- NodeGraph visualization guide
- Schema version management guide
- Performance optimization documentation

---

## Migration Checklist

### Before Upgrade
- [ ] Backup eventcatalog directory
- [ ] Document current version
- [ ] Screenshot current UI for comparison
- [ ] Export current configuration

### During Upgrade
- [ ] Update dependencies
- [ ] Migrate configuration file
- [ ] Fix breaking changes
- [ ] Test core functionality

### After Upgrade
- [ ] Verify all pages render
- [ ] Test new features
- [ ] Apply branding
- [ ] Performance testing
- [ ] Update documentation

---

## Rollback Plan

If upgrade fails or introduces critical issues:
```bash
# Stop current instance
docker-compose stop eventcatalog

# Restore backup
rm -rf eventcatalog
cp -r eventcatalog-backup eventcatalog

# Restart with previous version
docker-compose up -d eventcatalog
```

---

## Risk & Mitigation

**Risk**: Breaking changes require significant rework
- **Mitigation**: Review migration guide before upgrade
- **Mitigation**: Test in isolated environment first
- **Mitigation**: Keep backup for rollback

**Risk**: Custom modifications break on new version
- **Mitigation**: Document all customizations before upgrade
- **Mitigation**: Test each customization after upgrade
- **Mitigation**: Refactor customizations if needed

**Risk**: Performance degrades on new version
- **Mitigation**: Benchmark before and after upgrade
- **Mitigation**: Enable performance optimizations in config
- **Mitigation**: Report performance issues to EventCatalog team

**Risk**: New features conflict with existing workflow
- **Mitigation**: Make new features opt-in where possible
- **Mitigation**: Train team on new features before rollout
- **Mitigation**: Document how to use (or disable) new features

---

## Future Enhancements (Post-Upgrade)

- API documentation integration
- Event analytics and usage tracking
- Real-time event monitoring dashboard
- GraphQL API for programmatic access
- Slack/Teams integration for notifications
- SSO authentication for access control

---

**Labels**: eventcatalog, upgrade, ui-enhancement, performance, proof-of-concept
**Created By**: Melvin Jones
