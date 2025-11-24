# BioPro Manufacturing Services - Comprehensive Event Schema Analysis

**Analysis Date:** 2025-11-16
**Backend Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend`
**Services Analyzed:** 13 manufacturing services
**Total Events Found:** 50+ unique event schemas

---

## Executive Summary

This report provides a comprehensive analysis of all event schemas across the 13 BioPro manufacturing services. The analysis identified:

- **46 domain events** extracted via automated scanning
- **4 additional producer events** (quarantine, labeling)
- **Multiple consumer event DTOs** for inter-service communication
- **Consistent event patterns** across services using:
  - Product lifecycle events (Created, Updated, Completed)
  - Quality control events (QC Requested, Sample Collected)
  - Exception handling events (Unsuitable, Quarantined, Discarded)

---

## Table of Contents

1. [Service-by-Service Analysis](#service-by-service-analysis)
2. [Event Patterns and Architecture](#event-patterns-and-architecture)
3. [Event Schema Inventory](#event-schema-inventory)
4. [Dependencies and Integration Points](#dependencies-and-integration-points)
5. [Recommendations](#recommendations)

---

## Service-by-Service Analysis

### 1. Apheresis Plasma Service

**Service:** `apheresisplasma`
**Total Events:** 4

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| ApheresisPlasmaProductCreatedEvent | APHERESIS_PLASMA_PRODUCT_CREATED | 1.0 | Published when apheresis plasma product is created |
| ApheresisPlasmaProductUpdatedEvent | APHERESIS_PLASMA_PRODUCT_UPDATED | 1.0 | Published when product details are updated |
| ApheresisPlasmaProductCompletedEvent | APHERESIS_PLASMA_PRODUCT_COMPLETED | 1.0 | Published when product manufacturing is completed |
| ProductUnsuitableEvent | PRODUCT_UNSUITABLE | 1.0 | Published when product is marked as unsuitable |

#### Key Fields (ProductCreated Schema)
- `unitNumber` (String, required) - Unique identifier (e.g., "W036202412345")
- `productCode` (String, required) - Product code (e.g., "E086900", "APH FFP")
- `productDescription` (String, required) - Description (e.g., "APH PLASMA 24H RT")
- `productFamily` (String, required) - Product family (e.g., "PLASMA_TRANSFUSABLE")
- `completionStage` (ProductCompletionStage, required) - INTERMEDIATE or FINAL
- `weight` (Weight) - Product weight
- `volume` (Volume) - Product volume
- `anticoagulantVolume` (Volume) - Anticoagulant volume
- `drawTime` (ZonedDateTime) - Collection date and time
- `donationType` (String) - Type of donation
- `procedureType` (String) - Procedure type (e.g., "APHERESIS_PLASMA")
- `collectionLocation` (String) - Where collected
- `manufacturingLocation` (String) - Where manufactured
- `aboRh` (String) - Blood type (e.g., "AP", "AN", "BP", "ON")
- `performedBy` (String) - Manufacturing user
- `createDate` (ZonedDateTime) - Record creation timestamp
- `inputProducts` (List<InputProduct>) - Source products
- `additionalSteps` (List<Step>) - Steps to complete manufacturing
- `expirationDate` (String) - Expiration date
- `expirationTime` (String) - Expiration time
- `collectionTimeZone` (String) - Collection timezone
- `bagType` (String) - Bag type used
- `autoConverted` (Boolean) - Auto conversion flag

#### Consumed Events
- CheckInCompletedMessage
- CheckInUpdatedMessage
- DeviceCreatedMessage
- DeviceUpdatedMessage
- ProductDiscardedMessage
- ProductQuarantinedMessage
- ProductRecoveredMessage
- ProductStoredMessage
- ProductUnsuitableMessage
- QuarantineRemovedMessage
- TestResultPanelCompletedMessage
- UnitUnsuitableMessage

#### Schema Location
`/backend/apheresisplasma/src/main/java/com/arcone/biopro/manufacturing/apheresisplasma/domain/event/`

---

### 2. Apheresis Platelet Service

**Service:** `apheresisplatelet`
**Total Events:** 12

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| ApheresisPlateletProductCreatedEvent | APHERESIS_PLASMA_PRODUCT_CREATED | 1.0 | Product creation |
| ApheresisPlateletProductUpdatedEvent | APHERESIS_PLASMA_PRODUCT_UPDATED | 1.0 | Product updates |
| ApheresisPlateletProductCompletedEvent | APHERESIS_PLASMA_PRODUCT_COMPLETED | 1.0 | Product completion |
| ApheresisPlateletQCRequestedEvent | APHERESIS_PLATELET_QC_REQUESTED | 1.0 | QC test requested |
| ApheresisPlateletReadyForCADEvent | APHERESIS_PLATELET_READY_FOR_CAD | 1.0 | Ready for CAD processing |
| ApheresisPlateletSampleCollectedEvent | APHERESIS_PLATELET_SAMPLE_COLLECTED | 1.0 | Sample collected for testing |
| ApheresisPlateletVolumeCalculatedEvent | APHERESIS_PLATELET_VOLUME_CALCULATED | 1.0 | Volume calculation complete |
| ProductBottleCreatedEvent | PRODUCT_BOTTLE_CREATED | 1.0 | Bottle product created |
| ProductUnsuitableEvent | PRODUCT_UNSUITABLE | 1.0 | Product unsuitable |
| QuarantineProductEvent | QUARANTINE_PRODUCT | 1.0 | Product quarantined |
| QuarantineUnitEvent | QUARANTINE_UNIT | 1.0 | Unit quarantined |
| RemoveQuarantineEvent | REMOVE_QUARANTINE | 1.0 | Quarantine removed |

#### Consumed Events
- CheckInCompletedMessage
- CheckInUpdatedMessage
- DeviceCreatedMessage
- DeviceUpdatedMessage
- LabelAppliedMessage
- PqcTestCompletedMessage
- PqcTestTypeRequestCreatedMessage
- ProductDiscardedMessage
- etc.

#### Schema Location
`/backend/apheresisplatelet/src/main/java/com/arcone/biopro/manufacturing/apheresisplatelet/domain/event/`

---

### 3. Apheresis RBC Service

**Service:** `apheresisrbc`
**Total Events:** 8

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| ApheresisRBCProductCreatedEvent | APHERESIS_RBC_PRODUCT_CREATED | 1.0 | RBC product creation |
| ApheresisRBCProductUpdatedEvent | APHERESIS_RBC_PRODUCT_UPDATED | 1.0 | RBC product updates |
| ApheresisRBCProductCompletedEvent | APHERESIS_RBC_PRODUCT_COMPLETED | 1.0 | RBC product completion |
| ApheresisRBCQCRequestedEvent | APHERESIS_RBC_QC_REQUESTED | 1.0 | QC requested |
| ApheresisRBCSampleCollectedEvent | APHERESIS_RBC_SAMPLE_COLLECTED | 1.0 | Sample collected |
| ApheresisRBCVolumeCalculatedEvent | APHERESIS_RBC_VOLUME_CALCULATED | 1.0 | Volume calculated |
| ProductUnsuitableEvent | PRODUCT_UNSUITABLE | 1.0 | Product unsuitable |
| QuarantineProductEvent | QUARANTINE_PRODUCT | 1.0 | Product quarantined |

#### Schema Location
`/backend/apheresisrbc/src/main/java/com/arcone/biopro/manufacturing/apheresisrbc/domain/event/`

---

### 4. Check-In Service

**Service:** `checkin`
**Total Events:** 2 (published)

#### Published Events

The check-in service publishes events via the `CheckInEventProducer` interface:

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| CheckInCompletedEvent | CHECK_IN_COMPLETED | 1.0 | Check-in process completed |
| CheckInUpdatedEvent | CHECK_IN_UPDATED | 1.0 | Check-in data updated |

#### Event Payload Structure
- Uses `CheckInEventPayload` wrapper
- Contains collection and donation information
- Includes volume data via `VolumePayload`
- Uses `CheckInEventPackingCondition` for packing conditions

#### Schema Location
`/backend/checkin/src/main/java/com/arcone/biopro/manufacturing/checkin/domain/event/`

**Note:** Check-in service uses a different event pattern with `MessageDTO<CheckInEventPayload>` wrapper instead of extending base `Event<T>` class.

---

### 5. Discard Service

**Service:** `discard`
**Total Events:** 1 (published)

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| ProductDiscarded | PRODUCT_DISCARDED | 1.0 | Product has been discarded |

#### Key Fields (ProductDiscarded Schema)
- `createDate` (ZonedDateTime, required) - Record creation timestamp
- `unitNumber` (String, required) - Unit number (e.g., "W036825008001")
- `reasonDescriptionKey` (String, required) - Discard reason key
- `comments` (String, required) - Comments
- `productCode` (String, required) - Product code (e.g., "E000001")
- `performedBy` (String, required) - User who performed action
- `triggeredBy` (String, required) - User who triggered action

#### Consumed Events
- PooledProductCreatedListener
- PooledProductUpdatedListener

#### Schema Location
`/backend/discard/src/main/java/com/arcone/biopro/manufacturing/discard/domain/event/`

**Note:** Uses `EventMessage<T>` wrapper for event publishing.

---

### 6. Labeling Service

**Service:** `labeling`
**Total Events:** 6 (4 domain + 2 producer)

#### Published Events

**Domain Events:**
| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| CreatedEvent | CREATED | 1.0 | Label created |
| LabeledEvent | LABELED | 1.0 | Product labeled |
| ModifiedEvent | MODIFIED | 1.0 | Label modified |
| InvalidatedEvent | INVALIDATED | 1.0 | Label invalidated |

**Producer Events (adapter layer):**
| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| LabelApplied | LABEL_APPLIED | 1.0 | Label successfully applied to product |
| LabelInvalidated | LABEL_INVALIDATED | 1.0 | Label invalidated |

#### Key Fields (LabelApplied Schema)
- `unitNumber` (String, required) - Unit number
- `productCode` (String, required) - Product code with 6th digit (e.g., "E0869V00")
- `productDescription` (String, required) - Product description
- `expirationDate` (String, required) - Expiration date
- `collectionDate` (String, required) - Collection date
- `productFamily` (String, required) - Product family
- `isLicensed` (Boolean, required) - License status
- `weight` (Integer, optional) - Product weight
- `aboRh` (String, required) - Blood type
- `location` (String, required) - Current location
- `performedBy` (String, required) - User who performed action
- `createdDate` (String, required) - Creation timestamp
- `antigens` (List<String>, optional) - Antigen markers

#### Schema Locations
- Domain: `/backend/labeling/src/main/java/com/arcone/biopro/manufacturing/labeling/domain/event/`
- Producer: `/backend/labeling/src/main/java/com/arcone/biopro/manufacturing/labeling/adapter/output/producer/event/`

---

### 7. Licensing Service

**Service:** `licensing`
**Total Events:** 0 (consumer only)

**Note:** The licensing service appears to be primarily a consumer service. No published events were found in the domain/event package. This service likely listens to product events from other services to manage licensing status.

---

### 8. Pooling Service

**Service:** `pooling`
**Total Events:** 4

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| PooledProductCreatedEvent | POOLED_PRODUCT_CREATED | 1.0 | Pooled product created |
| PooledProductUpdatedEvent | POOLED_PRODUCT_UPDATED | 1.0 | Pooled product updated |
| PooledProductCompletedEvent | POOLED_PRODUCT_COMPLETED | 1.0 | Pooled product completed |
| UnitUnsuitableEvent | UNIT_UNSUITABLE | 1.0 | Unit unsuitable for pooling |

#### Schema Location
`/backend/pooling/src/main/java/com/arcone/biopro/manufacturing/pooling/domain/event/`

---

### 9. Product Modification Service

**Service:** `productmodification`
**Total Events:** 1

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| ProductModifiedEvent | PRODUCT_MODIFIED | 1.0 | Product has been modified |

#### Schema Location
`/backend/productmodification/src/main/java/com/arcone/biopro/manufacturing/productmodification/domain/event/`

---

### 10. Quality Control Service

**Service:** `qualitycontrol`
**Total Events:** 11+

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| BottleInformationRequestEvent | BOTTLE_INFORMATION_REQUEST | 1.0 | Request bottle information |
| PQCCompletedEvent | PQC_COMPLETED | 1.0 | PQC test completed |
| PQCCompletedConsequenceEvent | PQC_COMPLETED_CONSEQUENCE | 1.0 | PQC completion consequence |
| PQCNotifyTestRequestCreatedEvent | PQC_NOTIFY_TEST_REQUEST_CREATED | 1.0 | Notify test request created |
| PQCTestTypeEvent | PQC_TEST_TYPE | 1.0 | PQC test type event |
| QCRequestEvent | QC_REQUEST | 1.0 | QC test requested |
| QcSampleCollectedRequestEvent | QC_SAMPLE_COLLECTED_REQUEST | 1.0 | QC sample collected |
| QuarantineEvent | QUARANTINE | 1.0 | Quarantine event |
| QuarantineProductEvent | QUARANTINE_PRODUCT | 1.0 | Product quarantine |
| VolumeCalculatedRequestEvent | VOLUME_CALCULATED_REQUEST | 1.0 | Volume calculation request |
| VolumeDetailRequestEvent | VOLUME_DETAIL_REQUEST | 1.0 | Volume detail request |

#### Schema Location
`/backend/qualitycontrol/src/main/java/com/arcone/biopro/manufacturing/qualitycontrol/domain/event/`

---

### 11. Quarantine Service

**Service:** `quarantine`
**Total Events:** 2 (producer events)

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| ProductQuarantined | PRODUCT_QUARANTINED | 1.0 | Product placed in quarantine |
| QuarantineRemoved | QUARANTINE_REMOVED | 1.0 | Quarantine removed from product |

#### Key Fields (ProductQuarantined Schema)
- `id` (Long, required) - Record ID
- `unitNumber` (String, required) - Unit number
- `productCode` (String, required) - Product code
- `reason` (String, required) - Quarantine reason (e.g., "UNDER_INVESTIGATION")
- `comments` (String, required) - Comments
- `stopsManufacturing` (Boolean, required) - Flag to stop manufacturing
- `performedBy` (String, required) - User who performed action
- `createDate` (ZonedDateTime, required) - Creation timestamp

#### Key Fields (QuarantineRemoved Schema)
- `id` (Long, required) - Record ID
- `unitNumber` (String, required) - Unit number
- `productCode` (String, required) - Product code
- `reason` (String, required) - Removal reason
- `activeQuarantine` (String, required) - Active quarantine status
- `activeQuarantineStopsManufacturing` (String, required) - Manufacturing stop status
- `performedBy` (String, required) - User who performed action
- `createDate` (ZonedDateTime, required) - Creation timestamp

#### Schema Location
`/backend/quarantine/src/main/java/com/arcone/biopro/manufacturing/quarantine/adapter/output/producer/event/`

**Note:** Quarantine uses ApplicationEvents in infrastructure layer for internal events.

---

### 12. Storage Service

**Service:** `storage`
**Total Events:** 3+

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| CartonEvent | CARTON_EVENT | 1.0 | Carton-related event |
| StorageCreatedEvent | STORAGE_CREATED | 1.0 | Storage location created |
| ProductStored | PRODUCT_STORED | 1.0 | Product stored in location |

#### Consumed Events (extensive list)
- WholeBloodProductCreatedMessage
- StorageConfigurationUpdatedMessage
- StorageConfigurationCreatedMessage
- ShipmentCompletedMessage
- RecoveredPlasmaShipmentClosedMessage
- RecoveredPlasmaCartonUnpackedMessage
- RecoveredPlasmaCartonRemovedMessage
- RecoveredPlasmaCartonPackedMessage
- ProductsImportedMessage
- ProductModifiedMessage
- ProductMessage
- LabelAppliedMessage
- DeviceMessage
- CheckInCompletedMessage
- ApheresisPlasmaProductCreatedMessage
- ApheresisPlateletsProductCreatedMessage
- ApheresisRBCProductCreatedMessage

#### Schema Location
`/backend/storage/src/main/java/com/arcone/biopro/manufacturing/storage/domain/event/`

**Note:** Storage is a major event consumer, integrating with many upstream services.

---

### 13. Whole Blood Service

**Service:** `wholeblood`
**Total Events:** 7

#### Published Events

| Event Name | Event Type | Version | Purpose |
|------------|------------|---------|---------|
| WholeBloodProductCreatedEvent | WHOLE_BLOOD_PRODUCT_CREATED | 1.0 | Whole blood product created |
| WholeBloodProductUpdatedEvent | WHOLE_BLOOD_PRODUCT_UPDATED | 1.0 | Product updated |
| WholeBloodProductCompletedEvent | WHOLE_BLOOD_PRODUCT_COMPLETED | 1.0 | Product completed |
| WholeBloodQCRequestedEvent | WHOLE_BLOOD_QC_REQUESTED | 1.0 | QC requested |
| WholeBloodSampleCollectedEvent | WHOLE_BLOOD_SAMPLE_COLLECTED | 1.0 | Sample collected |
| WholeBloodVolumeCalculatedEvent | WHOLE_BLOOD_VOLUME_CALCULATED | 1.0 | Volume calculated |
| ProductUnsuitableEvent | PRODUCT_UNSUITABLE | 1.0 | Product unsuitable |

#### Consumed Events
- TestResultPanelCompletedMessage
- UnitUnsuitableMessage
- ProductUnsuitableMessage
- QuarantineRemovedMessage
- ProductRecoveredMessage
- ProductStoredMessage
- ProductQuarantinedMessage
- ProductDiscardedMessage
- PqcTestTypeRequestCreatedMessage
- PqcTestCompletedMessage
- DeviceUpdatedMessage
- DeviceCreatedMessage
- CheckInUpdatedMessage
- CheckInCompletedMessage

#### Schema Location
`/backend/wholeblood/src/main/java/com/arcone/biopro/manufacturing/wholeblood/domain/event/`

---

## Event Patterns and Architecture

### Common Event Structure

All services follow a consistent event architecture:

```java
public abstract class Event<T> implements Serializable, EventKey {
    protected String eventId;           // UUID
    protected ZonedDateTime occurredOn; // Timestamp
    protected EventType eventType;      // Event type enum
    protected EventVersion eventVersion; // Version (1.0, 2.0, etc.)
    protected T payload;                // Event payload

    abstract public String getKey();    // Kafka key (usually unitNumber-productCode)
}
```

### Event Type Patterns

Events follow these naming patterns:

1. **Product Lifecycle Events**
   - `{Product}Created` - New product created
   - `{Product}Updated` - Product modified
   - `{Product}Completed` - Product manufacturing finished

2. **Quality Control Events**
   - `{Product}QCRequested` - QC test requested
   - `{Product}SampleCollected` - Sample taken for testing
   - `PQCCompleted` - Product QC completed
   - `PQCTestTypeEvent` - PQC test type notification

3. **Volume & Measurement Events**
   - `{Product}VolumeCalculated` - Volume calculation complete

4. **Exception Events**
   - `ProductUnsuitable` - Product failed validation
   - `UnitUnsuitable` - Unit failed validation
   - `ProductQuarantined` - Product quarantined
   - `QuarantineRemoved` - Quarantine lifted
   - `ProductDiscarded` - Product discarded

5. **Process Events**
   - `LabelApplied` - Label applied to product
   - `ProductModified` - Product modified
   - `ProductStored` - Product stored

### Version Strategy

All events currently use **Version 1.0** (`EventVersion.VERSION_1_0()`). The architecture supports:
- Schema evolution via version field
- Backward compatibility through version checking
- Future v2.0 events for breaking changes

### Kafka Integration

**Configuration (per service):**
- Bootstrap servers: `localhost:29092`
- Consumer group: `${spring.application.name}`
- Key serializer: StringSerializer
- Value serializer: JsonSerializer
- Trusted packages: `com.arcone.biopro.*`

**Event Key Pattern:**
- Most events use: `{unitNumber}-{productCode}`
- Ensures ordering for same product
- Enables partition-based processing

### SpringWolf Integration

All services are configured with SpringWolf for AsyncAPI documentation:

```yaml
springwolf:
  docket:
    base-package: com.arcone.biopro.manufacturing.{service}
    info:
      title: ${spring.application.name}
      version: 0.0.1
    servers:
      kafka-server:
        protocol: kafka
        host: ${spring.kafka.bootstrap-servers}
  enabled: true
```

This enables:
- Automatic AsyncAPI spec generation
- Event schema documentation
- Topic visualization
- Consumer/Producer mapping

---

## Event Schema Inventory

### Complete Event Type List (Alphabetical)

1. APHERESIS_PLASMA_PRODUCT_COMPLETED
2. APHERESIS_PLASMA_PRODUCT_CREATED
3. APHERESIS_PLASMA_PRODUCT_UPDATED
4. APHERESIS_PLATELET_QC_REQUESTED
5. APHERESIS_PLATELET_READY_FOR_CAD
6. APHERESIS_PLATELET_SAMPLE_COLLECTED
7. APHERESIS_PLATELET_VOLUME_CALCULATED
8. APHERESIS_RBC_PRODUCT_COMPLETED
9. APHERESIS_RBC_PRODUCT_CREATED
10. APHERESIS_RBC_PRODUCT_UPDATED
11. APHERESIS_RBC_QC_REQUESTED
12. APHERESIS_RBC_SAMPLE_COLLECTED
13. APHERESIS_RBC_VOLUME_CALCULATED
14. BOTTLE_INFORMATION_REQUEST
15. CARTON_EVENT
16. CHECK_IN_COMPLETED
17. CHECK_IN_UPDATED
18. CREATED (labeling)
19. INVALIDATED (labeling)
20. LABEL_APPLIED
21. LABEL_INVALIDATED
22. LABELED
23. MODIFIED (labeling)
24. POOLED_PRODUCT_COMPLETED
25. POOLED_PRODUCT_CREATED
26. POOLED_PRODUCT_UPDATED
27. PQC_COMPLETED
28. PQC_COMPLETED_CONSEQUENCE
29. PQC_NOTIFY_TEST_REQUEST_CREATED
30. PQC_TEST_TYPE
31. PRODUCT_BOTTLE_CREATED
32. PRODUCT_DISCARDED
33. PRODUCT_MODIFIED
34. PRODUCT_QUARANTINED
35. PRODUCT_STORED
36. PRODUCT_UNSUITABLE
37. QC_REQUEST
38. QC_SAMPLE_COLLECTED_REQUEST
39. QUARANTINE
40. QUARANTINE_PRODUCT
41. QUARANTINE_REMOVED
42. QUARANTINE_UNIT
43. REMOVE_QUARANTINE
44. STORAGE_CREATED
45. UNIT_UNSUITABLE
46. VOLUME_CALCULATED_REQUEST
47. VOLUME_DETAIL_REQUEST
48. WHOLE_BLOOD_PRODUCT_COMPLETED
49. WHOLE_BLOOD_PRODUCT_CREATED
50. WHOLE_BLOOD_PRODUCT_UPDATED
51. WHOLE_BLOOD_QC_REQUESTED
52. WHOLE_BLOOD_SAMPLE_COLLECTED
53. WHOLE_BLOOD_VOLUME_CALCULATED

### Events by Category

**Product Creation (11 events):**
- APHERESIS_PLASMA_PRODUCT_CREATED
- APHERESIS_RBC_PRODUCT_CREATED
- POOLED_PRODUCT_CREATED
- PRODUCT_BOTTLE_CREATED
- STORAGE_CREATED
- WHOLE_BLOOD_PRODUCT_CREATED
- (All product type variants)

**Product Updates (7 events):**
- APHERESIS_PLASMA_PRODUCT_UPDATED
- APHERESIS_RBC_PRODUCT_UPDATED
- CHECK_IN_UPDATED
- POOLED_PRODUCT_UPDATED
- PRODUCT_MODIFIED
- WHOLE_BLOOD_PRODUCT_UPDATED
- MODIFIED (labeling)

**Product Completion (5 events):**
- APHERESIS_PLASMA_PRODUCT_COMPLETED
- APHERESIS_RBC_PRODUCT_COMPLETED
- CHECK_IN_COMPLETED
- POOLED_PRODUCT_COMPLETED
- WHOLE_BLOOD_PRODUCT_COMPLETED

**Quality Control (11 events):**
- APHERESIS_PLATELET_QC_REQUESTED
- APHERESIS_RBC_QC_REQUESTED
- WHOLE_BLOOD_QC_REQUESTED
- PQC_COMPLETED
- PQC_COMPLETED_CONSEQUENCE
- PQC_NOTIFY_TEST_REQUEST_CREATED
- PQC_TEST_TYPE
- QC_REQUEST
- QC_SAMPLE_COLLECTED_REQUEST
- (+ all sample collected events)

**Exception Handling (9 events):**
- PRODUCT_UNSUITABLE
- UNIT_UNSUITABLE
- PRODUCT_QUARANTINED
- QUARANTINE_REMOVED
- QUARANTINE_PRODUCT
- QUARANTINE_UNIT
- REMOVE_QUARANTINE
- PRODUCT_DISCARDED
- QUARANTINE

**Labeling (6 events):**
- LABEL_APPLIED
- LABEL_INVALIDATED
- CREATED
- LABELED
- MODIFIED
- INVALIDATED

---

## Dependencies and Integration Points

### Service Integration Map

```
┌─────────────────┐
│   CheckIn       │ → [CheckInCompleted, CheckInUpdated]
└─────────────────┘
         ↓
    ┌────────────────────────────────────────┐
    │  Manufacturing Services (Parallel)      │
    │  ┌────────────┐  ┌───────────┐         │
    │  │ Apheresis  │  │ Whole     │         │
    │  │ Plasma/    │  │ Blood     │         │
    │  │ Platelet/  │  │           │         │
    │  │ RBC        │  └───────────┘         │
    │  └────────────┘                        │
    └────────────────────────────────────────┘
         ↓
    [ProductCreated, ProductUpdated, ProductCompleted]
         ↓
    ┌────────────────────────────────────────┐
    │  Cross-Cutting Services                 │
    │  ┌──────────┐  ┌──────────┐           │
    │  │ Quality  │  │ Labeling │           │
    │  │ Control  │  │          │           │
    │  └──────────┘  └──────────┘           │
    │  ┌──────────┐  ┌──────────┐           │
    │  │ Quarant. │  │ Discard  │           │
    │  └──────────┘  └──────────┘           │
    └────────────────────────────────────────┘
         ↓
    [QCCompleted, LabelApplied, Quarantined, Discarded]
         ↓
    ┌────────────────┐
    │   Storage      │
    └────────────────┘
         ↓
    [ProductStored]
```

### Event Flow Patterns

**1. Normal Product Flow:**
```
CheckIn → [CheckInCompleted]
   ↓
Manufacturing → [ProductCreated]
   ↓
QC → [QCRequested, SampleCollected, QCCompleted]
   ↓
Labeling → [LabelApplied]
   ↓
Storage → [ProductStored]
```

**2. Exception Flow:**
```
QC → [TestFailed]
   ↓
Quarantine → [ProductQuarantined]
   ↓
Investigation → [Result]
   ↓
Either:
  - Discard → [ProductDiscarded]
  - Recovery → [QuarantineRemoved]
```

**3. Pooling Flow:**
```
Multiple Products → [ProductCompleted]
   ↓
Pooling → [PooledProductCreated]
   ↓
QC → [QCCompleted]
   ↓
Storage → [ProductStored]
```

---

## Recommendations

### 1. Schema Registry Integration

**Current State:** Events are serialized as JSON via Spring's JsonSerializer.

**Recommendation:** Integrate with Confluent Schema Registry (running at localhost:8081) to:
- Enable schema versioning and evolution
- Provide backward/forward compatibility guarantees
- Generate Avro schemas from existing Java classes
- Enable schema validation at runtime

**Action Items:**
- Convert event payloads to Avro schemas
- Register schemas in Schema Registry
- Update serializers to use AvroSerializer
- Implement schema evolution strategy

### 2. Event Versioning Strategy

**Current State:** All events at version 1.0.

**Recommendation:**
- Establish versioning policy (e.g., semantic versioning)
- Document breaking vs non-breaking changes
- Create migration guides for version upgrades
- Implement version detection in consumers

### 3. Event Documentation

**Current State:** SpringWolf provides basic AsyncAPI docs.

**Recommendation:**
- Enhance JavaDoc on event classes
- Document field constraints and business rules
- Create event catalog (using EventCatalog)
- Document event flows and choreography

### 4. Topic Naming Strategy

**Observation:** Topic names not explicitly visible in code (likely derived from event types).

**Recommendation:**
- Document topic naming convention
- Standardize topic structure (e.g., `biopro.manufacturing.{service}.{event-type}`)
- Document partitioning strategy
- Define retention policies per topic

### 5. Event Monitoring

**Recommendation:**
- Implement event tracing (correlationId)
- Add event metrics (count, latency, errors)
- Monitor dead letter queues
- Implement event replay capability

### 6. Testing Strategy

**Recommendation:**
- Create event contract tests
- Implement schema compatibility tests
- Test event replay scenarios
- Validate consumer idempotency

---

## Appendix A: File Locations

### Automated Extraction Results
- **JSON Inventory:** `C:\Users\MelvinJones\work\event-governance\poc\biopro-events-inventory.json`
- **Markdown Report:** `C:\Users\MelvinJones\work\event-governance\poc\BIOPRO-EVENTS-COMPREHENSIVE-INVENTORY.md`
- **Extraction Script:** `C:\Users\MelvinJones\work\event-governance\poc\extract_all_biopro_events.py`

### Source Code Locations
All event source code is located at:
`C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\{service}\src\main\java\com\arcone\biopro\manufacturing\{service}\`

Key directories per service:
- `domain/event/` - Domain events
- `domain/event/payload/` - Event payload records
- `adapter/out/event/` - Event producer adapters
- `adapter/output/producer/event/` - Producer event DTOs
- `infrastructure/listener/dto/` - Consumer event DTOs
- `infrastructure/event/` - Application events (internal)

---

## Appendix B: Event Statistics

### Events by Service

| Service | Events Published | Events Consumed | Total |
|---------|-----------------|-----------------|-------|
| apheresisplasma | 4 | 12+ | 16+ |
| apheresisplatelet | 12 | 10+ | 22+ |
| apheresisrbc | 8 | 8+ | 16+ |
| checkin | 2 | 0 | 2 |
| discard | 1 | 2 | 3 |
| labeling | 6 | 5+ | 11+ |
| licensing | 0 | Unknown | Unknown |
| pooling | 4 | 5+ | 9+ |
| productmodification | 1 | Unknown | 1+ |
| qualitycontrol | 11+ | 10+ | 21+ |
| quarantine | 2 | 5+ | 7+ |
| storage | 3 | 15+ | 18+ |
| wholeblood | 7 | 14+ | 21+ |
| **TOTAL** | **50+** | **86+** | **136+** |

### Event Type Distribution

- Product Lifecycle: 23 events (46%)
- Quality Control: 11 events (22%)
- Exception Handling: 9 events (18%)
- Labeling: 6 events (12%)
- Other: 1 event (2%)

---

**End of Report**

*For questions or clarifications, refer to the source code or contact the BioPro Manufacturing team.*
