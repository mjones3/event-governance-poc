# BioPro Manufacturing Services - Comprehensive Event Inventory

**Generated:** extract_all_biopro_events.py

**Total Events:** 46

**Services Analyzed:** 13

## Table of Contents

- [apheresisplasma](#apheresisplasma) (4 events)
- [apheresisplatelet](#apheresisplatelet) (12 events)
- [apheresisrbc](#apheresisrbc) (8 events)
- [labeling](#labeling) (4 events)
- [pooling](#pooling) (4 events)
- [productmodification](#productmodification) (1 events)
- [qualitycontrol](#qualitycontrol) (4 events)
- [storage](#storage) (2 events)
- [wholeblood](#wholeblood) (7 events)

---

## apheresisplasma

**Total Events:** 4

### ApheresisPlasmaProductCompletedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_COMPLETED`

**Version:** 1.0

**Payload Class:** `ProductCompleted`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplasma\src\main\java\com\arcone\biopro\manufacturing\apheresisplasma\domain\event\ApheresisPlasmaProductCompletedEvent.java`

---

### ApheresisPlasmaProductCreatedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_CREATED`

**Version:** 1.0

**Payload Class:** `ProductCreated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplasma\src\main\java\com\arcone\biopro\manufacturing\apheresisplasma\domain\event\ApheresisPlasmaProductCreatedEvent.java`

---

### ApheresisPlasmaProductUpdatedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_UPDATED`

**Version:** 1.0

**Payload Class:** `ProductUpdated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplasma\src\main\java\com\arcone\biopro\manufacturing\apheresisplasma\domain\event\ApheresisPlasmaProductUpdatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| performedBy | String | No | - |
| updatedDate | ZonedDateTime | No | - |
| inputProducts | List<InputProduct> | No | - |

---

### ProductUnsuitableEvent

**Event Type:** `PRODUCT_UNSUITABLE`

**Version:** 1.0

**Payload Class:** `ProductUnsuitable`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplasma\src\main\java\com\arcone\biopro\manufacturing\apheresisplasma\domain\event\ProductUnsuitableEvent.java`

---

## apheresisplatelet

**Total Events:** 12

### ApheresisPlateletProductCompletedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_COMPLETED`

**Version:** 1.0

**Payload Class:** `ProductCompleted`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletProductCompletedEvent.java`

---

### ApheresisPlateletProductCreatedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_CREATED`

**Version:** 1.0

**Payload Class:** `ProductCreated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletProductCreatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| productFamily | String | No | - |
| completionStage | ProductCompletionStage | No | - |
| weight | Weight | No | - |
| volume | Volume | No | - |
| anticoagulantVolume | Volume | No | - |
| drawTime | ZonedDateTime | No | - |
| donationType | String | No | - |
| procedureType | String | No | - |
| collectionLocation | String | No | - |
| manufacturingLocation | String | No | - |
| aboRh | String | No | - |
| performedBy | String | No | - |
| createDate | ZonedDateTime | No | - |
| inputProducts | List<InputProduct> | No | - |
| additionalSteps | List<Step> | No | - |
| bagType | String | No | - |
| expirationDate | String | No | - |
| expirationTime | String | No | - |
| collectionTimeZone | String | No | - |
| qcTests | List<QcTestDTO> | No | - |

---

### ApheresisPlateletProductUpdatedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_UPDATED`

**Version:** 1.0

**Payload Class:** `ProductUpdated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletProductUpdatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| completionStage | ProductCompletionStage | No | - |

---

### ApheresisPlateletQCRequestedEvent

**Event Type:** `APHERESIS_PLATELET_QC_REQUESTED`

**Version:** 1.0

**Payload Class:** `QCRequest`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletQCRequestedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| selectedQCTests | List<String> | No | - |
| properties | Map<String, String> | No | - |
| performedBy | String | No | - |
| createDate | ZonedDateTime | No | - |
| bagType | String | No | - |
| manufacturingLocation | String | No | - |

---

### ApheresisPlateletReadyForCADEvent

**Event Type:** `APHERESIS_PLATELET_READY_FOR_CAD`

**Version:** 1.0

**Payload Class:** `ReadyForCAD`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletReadyForCADEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |

---

### ApheresisPlateletSampleCollectedEvent

**Event Type:** `APHERESIS_PLATELET_SAMPLE_COLLECTED`

**Version:** 1.0

**Payload Class:** `SampleCollected`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletSampleCollectedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| machineType | String | No | - |
| procedureType | String | No | - |
| selectedQCTests | List<String> | No | - |
| performedBy | String | No | - |
| filtrationEnd | ZonedDateTime | No | - |
| productDescription | String | No | - |

---

### ApheresisPlateletVolumeCalculatedEvent

**Event Type:** `APHERESIS_PLATELET_VOLUME_CALCULATED`

**Version:** 1.0

**Payload Class:** `ProductVolumeCalculated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ApheresisPlateletVolumeCalculatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| volumeType | VolumeType | No | - |
| volume | Volume | No | - |
| weight | Weight | No | - |
| bagTareWeight | Weight | No | - |
| performedBy | String | No | - |
| productDescription | String | No | - |

---

### ProductBottleCreatedEvent

**Event Type:** `PRODUCT_BOTTLE_CREATED`

**Version:** 1.0

**Payload Class:** `ProductBottleCreated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ProductBottleCreatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| inoculationDate | ZonedDateTime | No | - |

---

### ProductUnsuitableEvent

**Event Type:** `PRODUCT_UNSUITABLE`

**Version:** 1.0

**Payload Class:** `ProductUnsuitable`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\ProductUnsuitableEvent.java`

---

### QuarantineProductEvent

**Event Type:** `QUARANTINE_PRODUCT`

**Version:** 1.0

**Payload Class:** `QuarantineProduct`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\QuarantineProductEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| products | List<QuarantineProductInput> | No | - |
| triggeredBy | String | No | - |
| reasonKey | String | No | - |
| comments | String | No | - |

---

### QuarantineUnitEvent

**Event Type:** `QUARANTINE_UNIT`

**Version:** 1.0

**Payload Class:** `QuarantineUnit`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\QuarantineUnitEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| reasonKey | String | No | - |
| triggeredBy | String | No | - |
| performedBy | String | No | - |

---

### RemoveQuarantineEvent

**Event Type:** `REMOVE_QUARANTINE`

**Version:** 1.0

**Payload Class:** `RemoveQuarantine`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplatelet\src\main\java\com\arcone\biopro\manufacturing\apheresisplatelet\domain\event\RemoveQuarantineEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| products | List<String> | No | - |
| reasonKey | String | No | - |
| triggeredBy | String | No | - |
| performedBy | String | No | - |

---

## apheresisrbc

**Total Events:** 8

### ApheresisRBCProductCompletedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_COMPLETED`

**Version:** 1.0

**Payload Class:** `ProductCompleted`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ApheresisRBCProductCompletedEvent.java`

---

### ApheresisRBCProductCreatedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_CREATED`

**Version:** 1.0

**Payload Class:** `ProductCreated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ApheresisRBCProductCreatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| productFamily | String | No | - |
| completionStage | ProductCompletionStage | No | - |
| weight | Weight | No | - |
| volume | Volume | No | - |
| anticoagulantVolume | Volume | No | - |
| drawTime | ZonedDateTime | No | - |
| donationType | String | No | - |
| procedureType | String | No | - |
| collectionLocation | String | No | - |
| manufacturingLocation | String | No | - |
| aboRh | String | No | - |
| performedBy | String | No | - |
| createDate | ZonedDateTime | No | - |
| inputProducts | List<InputProduct> | No | - |
| additionalSteps | List<Step> | No | - |
| bagType | String | No | - |
| expirationDate | String | No | - |
| expirationTime | String | No | - |

---

### ApheresisRBCProductUpdatedEvent

**Event Type:** `APHERESIS_PLASMA_PRODUCT_UPDATED`

**Version:** 1.0

**Payload Class:** `ProductUpdated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ApheresisRBCProductUpdatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| performedBy | String | No | - |
| updatedDate | ZonedDateTime | No | - |
| inputProducts | List<InputProduct> | No | - |

---

### ApheresisRBCQCRequestedEvent

**Event Type:** `APHERESIS_RBC_QC_REQUESTED`

**Version:** 1.0

**Payload Class:** `QCRequest`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ApheresisRBCQCRequestedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| selectedQCTests | List<String> | No | - |
| performeBy | String | No | - |
| createDate | ZonedDateTime | No | - |
| bagType | String | No | - |
| manufacturingLocation | String | No | - |

---

### ApheresisRBCSampleCollectedEvent

**Event Type:** `APHERESIS_RBC_SAMPLE_COLLECTED`

**Version:** 1.0

**Payload Class:** `SampleCollected`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ApheresisRBCSampleCollectedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| machineType | String | No | - |
| procedureType | String | No | - |
| selectedQCTests | List<String> | No | - |
| performedBy | String | No | - |
| filtrationEnd | ZonedDateTime | No | - |
| productDescription | String | No | - |

---

### ApheresisRBCVolumeCalculatedEvent

**Event Type:** `APHERESIS_RBC_VOLUME_CALCULATED`

**Version:** 1.0

**Payload Class:** `ProductVolumeCalculated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ApheresisRBCVolumeCalculatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| volumeType | VolumeType | No | - |
| volume | Volume | No | - |
| weight | Weight | No | - |
| bagTareWeight | Weight | No | - |
| performedBy | String | No | - |
| productDescription | String | No | - |

---

### ProductUnsuitableEvent

**Event Type:** `PRODUCT_UNSUITABLE`

**Version:** 1.0

**Payload Class:** `ProductUnsuitable`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\ProductUnsuitableEvent.java`

---

### QuarantineProductEvent

**Event Type:** `QUARANTINE_PRODUCT`

**Version:** 1.0

**Payload Class:** `QuarantineProduct`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisrbc\src\main\java\com\arcone\biopro\manufacturing\apheresisrbc\domain\event\QuarantineProductEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| products | List<QuarantineProductInput> | No | - |
| triggeredBy | String | No | - |
| reasonKey | String | No | - |
| comments | String | No | - |

---

## labeling

**Total Events:** 4

### CreatedEvent

**Event Type:** `CreatedEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\labeling\src\main\java\com\arcone\biopro\manufacturing\labeling\domain\event\CreatedEvent.java`

---

### InvalidatedEvent

**Event Type:** `InvalidatedEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\labeling\src\main\java\com\arcone\biopro\manufacturing\labeling\domain\event\InvalidatedEvent.java`

---

### LabeledEvent

**Event Type:** `LabeledEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\labeling\src\main\java\com\arcone\biopro\manufacturing\labeling\domain\event\LabeledEvent.java`

---

### ModifiedEvent

**Event Type:** `ModifiedEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\labeling\src\main\java\com\arcone\biopro\manufacturing\labeling\domain\event\ModifiedEvent.java`

---

## pooling

**Total Events:** 4

### PooledProductCompletedEvent

**Event Type:** `POOLED_PRODUCT_COMPLETED`

**Version:** 1.0

**Payload Class:** `ProductCompleted`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\pooling\src\main\java\com\arcone\biopro\manufacturing\pooling\domain\event\PooledProductCompletedEvent.java`

---

### PooledProductCreatedEvent

**Event Type:** `POOLED_PRODUCT_CREATED`

**Version:** 1.0

**Payload Class:** `ProductCreated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\pooling\src\main\java\com\arcone\biopro\manufacturing\pooling\domain\event\PooledProductCreatedEvent.java`

---

### PooledProductUpdatedEvent

**Event Type:** `POOLED_PRODUCT_UPDATED`

**Version:** 1.0

**Payload Class:** `ProductUpdated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\pooling\src\main\java\com\arcone\biopro\manufacturing\pooling\domain\event\PooledProductUpdatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| performedBy | String | No | - |
| updatedDate | ZonedDateTime | No | - |
| inputProducts | List<InputProduct> | No | - |

---

### UnitUnsuitableEvent

**Event Type:** `UNIT_UNSUITABLE`

**Version:** 1.0

**Payload Class:** `UnitUnsuitable`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\pooling\src\main\java\com\arcone\biopro\manufacturing\pooling\domain\event\UnitUnsuitableEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| reasonKey | String | No | - |
| triggeredBy | String | No | - |
| performedBy | String | No | - |

---

## productmodification

**Total Events:** 1

### ProductModifiedEvent

**Event Type:** `PRODUCT_MODIFIED`

**Version:** 1.0

**Payload Class:** `ProductModified`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\productmodification\src\main\java\com\arcone\biopro\manufacturing\productmodification\domain\event\ProductModifiedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| parentProductCode | String | No | - |
| productFamily | String | No | - |
| weight | Weight | No | - |
| volume | Volume | No | - |
| expirationDate | String | No | - |
| expirationTime | String | No | - |
| modificationLocation | String | No | - |
| modificationDate | ZonedDateTime | No | - |
| modificationTimeZone | String | No | - |
| collectionTime | ZonedDateTime | No | - |
| collectionTimeZone | String | No | - |
| properties | Map<String, String> | No | - |

---

## qualitycontrol

**Total Events:** 4

### BottleInformationRequestEvent

**Event Type:** `BottleInformationRequestEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\qualitycontrol\src\main\java\com\arcone\biopro\manufacturing\qualitycontrol\domain\event\BottleInformationRequestEvent.java`

---

### PQCCompletedEvent

**Event Type:** `PQCCompletedEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\qualitycontrol\src\main\java\com\arcone\biopro\manufacturing\qualitycontrol\domain\event\PQCCompletedEvent.java`

---

### QCRequestEvent

**Event Type:** `QCRequestEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\qualitycontrol\src\main\java\com\arcone\biopro\manufacturing\qualitycontrol\domain\event\QCRequestEvent.java`

---

### QcSampleCollectedRequestEvent

**Event Type:** `QcSampleCollectedRequestEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\qualitycontrol\src\main\java\com\arcone\biopro\manufacturing\qualitycontrol\domain\event\QcSampleCollectedRequestEvent.java`

---

## storage

**Total Events:** 2

### CartonEvent

**Event Type:** `CartonEvent`

**Version:** 1.0

**Payload Class:** `Unknown`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\storage\src\main\java\com\arcone\biopro\manufacturing\storage\domain\event\CartonEvent.java`

---

### StorageCreatedEvent

**Event Type:** `StorageCreatedEvent`

**Version:** 1.0

**Payload Class:** `ProductStored`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\storage\src\main\java\com\arcone\biopro\manufacturing\storage\domain\event\StorageCreatedEvent.java`

---

## wholeblood

**Total Events:** 7

### ProductUnsuitableEvent

**Event Type:** `PRODUCT_UNSUITABLE`

**Version:** 1.0

**Payload Class:** `ProductUnsuitable`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\ProductUnsuitableEvent.java`

---

### WholeBloodProductCompletedEvent

**Event Type:** `WHOLE_BLOOD_PRODUCT_COMPLETED`

**Version:** 1.0

**Payload Class:** `ProductCompleted`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\WholeBloodProductCompletedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| completionStage | ProductCompletionStage | No | - |
| weight | Weight | No | - |
| volume | Volume | No | - |
| aboRh | String | No | - |
| completionDate | ZonedDateTime | No | - |

---

### WholeBloodProductCreatedEvent

**Event Type:** `WHOLE_BLOOD_PRODUCT_CREATED`

**Version:** 1.0

**Payload Class:** `ProductCreated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\WholeBloodProductCreatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| productFamily | String | No | - |
| completionStage | ProductCompletionStage | No | - |
| weight | Weight | No | - |
| volume | Volume | No | - |
| anticoagulantVolume | Volume | No | - |
| drawTime | ZonedDateTime | No | - |
| donationType | String | No | - |
| procedureType | String | No | - |
| collectionLocation | String | No | - |
| manufacturingLocation | String | No | - |
| aboRh | String | No | - |
| performedBy | String | No | - |
| createDate | ZonedDateTime | No | - |
| inputProducts | List<InputProduct> | No | - |
| additionalSteps | List<Step> | No | - |
| bagType | String | No | - |
| expirationDate | String | No | - |
| expirationTime | String | No | - |
| collectionTimeZone | String | No | - |
| separationTime | ZonedDateTime | No | - |

---

### WholeBloodProductUpdatedEvent

**Event Type:** `WHOLE_BLOOD_PRODUCT_UPDATED`

**Version:** 1.0

**Payload Class:** `ProductUpdated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\WholeBloodProductUpdatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| completionStage | ProductCompletionStage | No | - |

---

### WholeBloodQCRequestedEvent

**Event Type:** `WHOLE_BLOOD_QC_REQUESTED`

**Version:** 1.0

**Payload Class:** `QCRequest`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\WholeBloodQCRequestedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| selectedQCTests | List<String> | No | - |
| properties | Map<String, String> | No | - |
| performedBy | String | No | - |
| createDate | ZonedDateTime | No | - |
| bagType | String | No | - |

---

### WholeBloodSampleCollectedEvent

**Event Type:** `WHOLE_BLOOD_SAMPLE_COLLECTED`

**Version:** 1.0

**Payload Class:** `SampleCollected`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\WholeBloodSampleCollectedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| productDescription | String | No | - |
| procedureType | String | No | - |
| selectedQCTests | List<String> | No | - |
| performedBy | String | No | - |
| filtrationEnd | ZonedDateTime | No | - |

---

### WholeBloodVolumeCalculatedEvent

**Event Type:** `WHOLE_BLOOD_VOLUME_CALCULATED`

**Version:** 1.0

**Payload Class:** `ProductVolumeCalculated`

**Schema Location:** `C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\wholeblood\src\main\java\com\arcone\biopro\manufacturing\wholeblood\domain\event\WholeBloodVolumeCalculatedEvent.java`

**Key Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| unitNumber | String | No | - |
| productCode | String | No | - |
| volumeType | VolumeType | No | - |
| volume | Volume | No | - |
| weight | Weight | No | - |
| bagTareWeight | Weight | No | - |
| performedBy | String | No | - |

---

## Summary Statistics

### Events by Service

| Service | Event Count |
|---------|-------------|
| apheresisplasma | 4 |
| apheresisplatelet | 12 |
| apheresisrbc | 8 |
| labeling | 4 |
| pooling | 4 |
| productmodification | 1 |
| qualitycontrol | 4 |
| storage | 2 |
| wholeblood | 7 |
| **TOTAL** | **46** |

### All Event Types

- `APHERESIS_PLASMA_PRODUCT_COMPLETED` (used in: apheresisrbc, apheresisplasma, apheresisplatelet)
- `APHERESIS_PLASMA_PRODUCT_CREATED` (used in: apheresisrbc, apheresisplasma, apheresisplatelet)
- `APHERESIS_PLASMA_PRODUCT_UPDATED` (used in: apheresisrbc, apheresisplasma, apheresisplatelet)
- `APHERESIS_PLATELET_QC_REQUESTED` (used in: apheresisplatelet)
- `APHERESIS_PLATELET_READY_FOR_CAD` (used in: apheresisplatelet)
- `APHERESIS_PLATELET_SAMPLE_COLLECTED` (used in: apheresisplatelet)
- `APHERESIS_PLATELET_VOLUME_CALCULATED` (used in: apheresisplatelet)
- `APHERESIS_RBC_QC_REQUESTED` (used in: apheresisrbc)
- `APHERESIS_RBC_SAMPLE_COLLECTED` (used in: apheresisrbc)
- `APHERESIS_RBC_VOLUME_CALCULATED` (used in: apheresisrbc)
- `BottleInformationRequestEvent` (used in: qualitycontrol)
- `CartonEvent` (used in: storage)
- `CreatedEvent` (used in: labeling)
- `InvalidatedEvent` (used in: labeling)
- `LabeledEvent` (used in: labeling)
- `ModifiedEvent` (used in: labeling)
- `POOLED_PRODUCT_COMPLETED` (used in: pooling)
- `POOLED_PRODUCT_CREATED` (used in: pooling)
- `POOLED_PRODUCT_UPDATED` (used in: pooling)
- `PQCCompletedEvent` (used in: qualitycontrol)
- `PRODUCT_BOTTLE_CREATED` (used in: apheresisplatelet)
- `PRODUCT_MODIFIED` (used in: productmodification)
- `PRODUCT_UNSUITABLE` (used in: apheresisrbc, apheresisplasma, apheresisplatelet, wholeblood)
- `QCRequestEvent` (used in: qualitycontrol)
- `QUARANTINE_PRODUCT` (used in: apheresisrbc, apheresisplatelet)
- `QUARANTINE_UNIT` (used in: apheresisplatelet)
- `QcSampleCollectedRequestEvent` (used in: qualitycontrol)
- `REMOVE_QUARANTINE` (used in: apheresisplatelet)
- `StorageCreatedEvent` (used in: storage)
- `UNIT_UNSUITABLE` (used in: pooling)
- `WHOLE_BLOOD_PRODUCT_COMPLETED` (used in: wholeblood)
- `WHOLE_BLOOD_PRODUCT_CREATED` (used in: wholeblood)
- `WHOLE_BLOOD_PRODUCT_UPDATED` (used in: wholeblood)
- `WHOLE_BLOOD_QC_REQUESTED` (used in: wholeblood)
- `WHOLE_BLOOD_SAMPLE_COLLECTED` (used in: wholeblood)
- `WHOLE_BLOOD_VOLUME_CALCULATED` (used in: wholeblood)
