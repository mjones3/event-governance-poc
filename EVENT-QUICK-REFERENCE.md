# BioPro Manufacturing Events - Quick Reference Guide

## All Services Event Summary

| # | Service | Events Published | Key Events | Event Pattern |
|---|---------|-----------------|------------|---------------|
| 1 | apheresisplasma | 4 | ProductCreated, ProductUpdated, ProductCompleted, ProductUnsuitable | Standard Lifecycle |
| 2 | apheresisplatelet | 12 | + QCRequested, SampleCollected, VolumeCalculated, ReadyForCAD, QuarantineProduct, RemoveQuarantine, ProductBottleCreated | Extended Lifecycle + QC |
| 3 | apheresisrbc | 8 | + QCRequested, SampleCollected, VolumeCalculated, QuarantineProduct | Extended Lifecycle + QC |
| 4 | checkin | 2 | CheckInCompleted, CheckInUpdated | Entry Point |
| 5 | discard | 1 | ProductDiscarded | Terminal State |
| 6 | labeling | 6 | LabelApplied, LabelInvalidated, Created, Labeled, Modified, Invalidated | Label Lifecycle |
| 7 | licensing | 0 | (Consumer only) | Validation Service |
| 8 | pooling | 4 | PooledProductCreated, PooledProductUpdated, PooledProductCompleted, UnitUnsuitable | Pooling Lifecycle |
| 9 | productmodification | 1 | ProductModified | Modification |
| 10 | qualitycontrol | 11+ | PQCCompleted, QCRequest, QcSampleCollected, VolumeCalculated, BottleInformationRequest, QuarantineProduct, etc. | QC Orchestration |
| 11 | quarantine | 2 | ProductQuarantined, QuarantineRemoved | Quarantine Management |
| 12 | storage | 3 | ProductStored, StorageCreated, CartonEvent | Storage Management |
| 13 | wholeblood | 7 | ProductCreated, ProductUpdated, ProductCompleted, QCRequested, SampleCollected, VolumeCalculated, ProductUnsuitable | Full Lifecycle + QC |

**Total: 50+ published events across 13 services**

---

## Event Types by Category

### Product Lifecycle Events (23)

| Event Type | Used By | Purpose |
|------------|---------|---------|
| APHERESIS_PLASMA_PRODUCT_CREATED | apheresisplasma | Plasma product created |
| APHERESIS_PLASMA_PRODUCT_UPDATED | apheresisplasma | Plasma product updated |
| APHERESIS_PLASMA_PRODUCT_COMPLETED | apheresisplasma | Plasma product completed |
| APHERESIS_PLATELET_PRODUCT_CREATED | apheresisplatelet | Platelet product created |
| APHERESIS_PLATELET_PRODUCT_UPDATED | apheresisplatelet | Platelet product updated |
| APHERESIS_PLATELET_PRODUCT_COMPLETED | apheresisplatelet | Platelet product completed |
| APHERESIS_RBC_PRODUCT_CREATED | apheresisrbc | RBC product created |
| APHERESIS_RBC_PRODUCT_UPDATED | apheresisrbc | RBC product updated |
| APHERESIS_RBC_PRODUCT_COMPLETED | apheresisrbc | RBC product completed |
| WHOLE_BLOOD_PRODUCT_CREATED | wholeblood | Whole blood product created |
| WHOLE_BLOOD_PRODUCT_UPDATED | wholeblood | Whole blood product updated |
| WHOLE_BLOOD_PRODUCT_COMPLETED | wholeblood | Whole blood product completed |
| POOLED_PRODUCT_CREATED | pooling | Pooled product created |
| POOLED_PRODUCT_UPDATED | pooling | Pooled product updated |
| POOLED_PRODUCT_COMPLETED | pooling | Pooled product completed |
| PRODUCT_BOTTLE_CREATED | apheresisplatelet | Bottle created |
| CHECK_IN_COMPLETED | checkin | Check-in completed |
| CHECK_IN_UPDATED | checkin | Check-in updated |
| CREATED | labeling | Label created |
| LABELED | labeling | Product labeled |
| MODIFIED | labeling | Label modified |
| PRODUCT_MODIFIED | productmodification | Product modified |
| STORAGE_CREATED | storage | Storage created |

### Quality Control Events (11)

| Event Type | Used By | Purpose |
|------------|---------|---------|
| APHERESIS_PLATELET_QC_REQUESTED | apheresisplatelet | Platelet QC requested |
| APHERESIS_RBC_QC_REQUESTED | apheresisrbc | RBC QC requested |
| WHOLE_BLOOD_QC_REQUESTED | wholeblood | Whole blood QC requested |
| APHERESIS_PLATELET_SAMPLE_COLLECTED | apheresisplatelet | Sample collected |
| APHERESIS_RBC_SAMPLE_COLLECTED | apheresisrbc | Sample collected |
| WHOLE_BLOOD_SAMPLE_COLLECTED | wholeblood | Sample collected |
| PQC_COMPLETED | qualitycontrol | PQC test completed |
| PQC_COMPLETED_CONSEQUENCE | qualitycontrol | PQC consequence processed |
| PQC_NOTIFY_TEST_REQUEST_CREATED | qualitycontrol | Test request notified |
| QC_REQUEST | qualitycontrol | QC requested |
| QC_SAMPLE_COLLECTED_REQUEST | qualitycontrol | Sample collection requested |

### Volume & Measurement Events (4)

| Event Type | Used By | Purpose |
|------------|---------|---------|
| APHERESIS_PLATELET_VOLUME_CALCULATED | apheresisplatelet | Volume calculated |
| APHERESIS_RBC_VOLUME_CALCULATED | apheresisrbc | Volume calculated |
| WHOLE_BLOOD_VOLUME_CALCULATED | wholeblood | Volume calculated |
| VOLUME_CALCULATED_REQUEST | qualitycontrol | Volume calculation requested |

### Exception Events (9)

| Event Type | Used By | Purpose |
|------------|---------|---------|
| PRODUCT_UNSUITABLE | plasma/rbc/wholeblood | Product failed validation |
| UNIT_UNSUITABLE | pooling | Unit failed validation |
| PRODUCT_QUARANTINED | quarantine | Product quarantined |
| QUARANTINE_REMOVED | quarantine | Quarantine lifted |
| QUARANTINE_PRODUCT | platelet/rbc/qc | Quarantine request |
| QUARANTINE_UNIT | apheresisplatelet | Unit quarantine |
| REMOVE_QUARANTINE | apheresisplatelet | Remove quarantine |
| PRODUCT_DISCARDED | discard | Product discarded |
| QUARANTINE | qualitycontrol | Quarantine event |

### Labeling Events (6)

| Event Type | Used By | Purpose |
|------------|---------|---------|
| LABEL_APPLIED | labeling | Label applied |
| LABEL_INVALIDATED | labeling | Label invalidated |
| CREATED | labeling | Label created |
| LABELED | labeling | Product labeled |
| MODIFIED | labeling | Label modified |
| INVALIDATED | labeling | Label invalidated |

### Other Events (3)

| Event Type | Used By | Purpose |
|------------|---------|---------|
| APHERESIS_PLATELET_READY_FOR_CAD | apheresisplatelet | Ready for CAD processing |
| BOTTLE_INFORMATION_REQUEST | qualitycontrol | Request bottle info |
| CARTON_EVENT | storage | Carton operation |
| PRODUCT_STORED | storage | Product stored |
| PQC_TEST_TYPE | qualitycontrol | PQC test type |
| VOLUME_DETAIL_REQUEST | qualitycontrol | Volume detail request |

---

## Common Event Payload Fields

### Base Event Fields (All Events)
```
eventId: String (UUID)
occurredOn: ZonedDateTime
eventType: EventType (enum)
eventVersion: EventVersion (1.0)
payload: T (typed payload)
```

### Common Product Fields
```
unitNumber: String (required) - e.g., "W036202412345"
productCode: String (required) - e.g., "E086900"
productDescription: String - e.g., "APH PLASMA 24H RT"
productFamily: String - e.g., "PLASMA_TRANSFUSABLE"
aboRh: String - e.g., "AP", "ON", "BP"
performedBy: String - Manufacturing user
createDate: ZonedDateTime - Record creation time
```

### Volume/Weight Fields
```
volume: Volume { amount: Double, unit: String }
weight: Weight { amount: Double, unit: String }
anticoagulantVolume: Volume
```

### Manufacturing Fields
```
completionStage: ProductCompletionStage (INTERMEDIATE | FINAL)
drawTime: ZonedDateTime - Collection time
donationType: String
procedureType: String - e.g., "APHERESIS_PLASMA"
collectionLocation: String
manufacturingLocation: String
inputProducts: List<InputProduct>
additionalSteps: List<Step>
```

### Quality Fields
```
qcTests: List<QcTestDTO>
expirationDate: String
expirationTime: String
bagType: String
```

---

## Event Key Strategy

Most events use compound key:
```
Key Format: "{unitNumber}-{productCode}"
Example: "W036202412345-E086900"
```

**Purpose:** Ensures ordering for same product, enables partition-based processing

---

## Service Integration Patterns

### Producer Services (Publish Events)
- apheresisplasma
- apheresisplatelet
- apheresisrbc
- checkin
- discard
- labeling
- pooling
- productmodification
- qualitycontrol
- quarantine
- storage
- wholeblood

### Consumer Services (Listen to Events)
- All services consume events from other services
- Storage is the largest consumer (15+ event types)
- Licensing is consumer-only (no published events)

### Integration Flow
```
CheckIn → Manufacturing → QC → Labeling → Storage
              ↓
         Quarantine (on exception)
              ↓
         Discard (terminal)
```

---

## Technology Details

### Kafka Configuration
- **Broker:** localhost:29092
- **Serialization:** JSON (JsonSerializer)
- **Consumer Group:** Service name (e.g., "apheresis-plasma")
- **Key Serializer:** StringSerializer
- **Auto Offset Reset:** earliest

### Schema Registry
- **URL:** localhost:8081
- **Status:** Available but not yet integrated
- **Opportunity:** Convert to Avro for better compatibility

### AsyncAPI Documentation
- **Tool:** SpringWolf
- **URL:** http://localhost:8080/{service}/asyncapi (when service running)
- **Spec:** AsyncAPI 2.0

---

## Quick Commands

### View SpringWolf AsyncAPI (when service running)
```bash
# Apheresis Plasma
curl http://localhost:8080/asyncapi/docs

# Other services (adjust port per service)
```

### Extract Events (using provided script)
```bash
cd /c/Users/MelvinJones/work/event-governance/poc
python extract_all_biopro_events.py
```

### Find Events by Pattern
```bash
cd /c/Users/MelvinJones/work/biopro/biopro-manufacturing/backend

# Find all ProductCreated events
find . -name "*ProductCreated*.java" -type f

# Find all event producers
find . -name "*Producer.java" -path "*/infrastructure/*"

# Find all listeners
find . -name "*Listener.java"
```

---

## File Locations Reference

### Event Source Code
```
backend/{service}/src/main/java/com/arcone/biopro/manufacturing/{service}/
  ├── domain/event/           # Domain events
  │   ├── *Event.java         # Event classes
  │   └── payload/            # Event payloads
  ├── adapter/out/event/      # Event adapters
  ├── adapter/output/producer/event/  # Producer events
  └── infrastructure/listener/dto/    # Consumer DTOs
```

### Analysis Output
```
C:\Users\MelvinJones\work\event-governance\poc\
  ├── BIOPRO-MANUFACTURING-EVENTS-FINAL-REPORT.md  # Main report
  ├── BIOPRO-EVENTS-COMPREHENSIVE-INVENTORY.md      # Auto-generated
  ├── biopro-events-inventory.json                  # JSON format
  ├── extract_all_biopro_events.py                  # Extraction script
  ├── ANALYSIS-SUMMARY.md                           # Quick summary
  └── EVENT-QUICK-REFERENCE.md                      # This file
```

---

## Event Versions

### Current State
- All events: **Version 1.0**
- Version field: `EventVersion.VERSION_1_0()`
- No v2.0 events exist yet

### Version Strategy
- Field exists for future evolution
- Breaking changes require new version
- Consumers can check version for compatibility
- Schema Registry can enforce compatibility rules

---

## Contact & Resources

### Documentation
- **Main Report:** `BIOPRO-MANUFACTURING-EVENTS-FINAL-REPORT.md`
- **JSON Data:** `biopro-events-inventory.json`
- **Source Code:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend`

### Tools
- **Extraction Script:** `extract_all_biopro_events.py`
- **SpringWolf:** Embedded in each service
- **Schema Registry UI:** http://localhost:8081 (when running)

---

**Last Updated:** 2025-11-16
**Total Services:** 13
**Total Events:** 50+
**Analysis Status:** Complete
