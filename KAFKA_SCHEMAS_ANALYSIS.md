# BioPro Kafka Message Schemas - Complete Analysis

## Collections Service Events

### CollectionReceivedEvent
- Package: com.arcone.biopro.interfaces.collections.adapter.output.producer.received
- Type: Java Record
- unitNumber: String (Required)
- status: String (Required)
- bagType: String (Required)
- drawTime: ZonedDateTime (Required)
- withdrawalTime: ZonedDateTime (Required)
- donationType: DonationType (ALLOGENEIC, AUTOLOGOUS)
- procedureType: String (Required)
- collectionLocation: String (Required)
- aboRh: String (Required)
- machineSerialNumber: String (Optional)
- machineType: String (Optional)
- donationProperties: Map<String,String> (Optional)
- drawProperties: Map<String,String> (Optional)
- volumes: List<Volume> (Required)
  - Volume: type (VolumeType), amount (Integer), excludeInCalculation (boolean)
  - VolumeType: PLASMA, RBC, PLASMA_ANTICOAGULANT, PLATELET, PAS, etc. (12 values)

### CollectionUpdatedEvent
- Package: com.arcone.biopro.interfaces.collections.adapter.output.producer.updated
- Structure: IDENTICAL to CollectionReceivedEvent

### AcceptedNewDonationEvent / AcceptedUpdatedDonationEvent
- Package: com.arcone.biopro.interfaces.collections.domain.event
- Type: Java Records
- Fields: source (CollectionAggregate)

---

## Orders Service Events

### DomainEvent Interface
- Methods: getEventId(), getOccurredOn(), getEventType(), getEventVersion(), getPayload()

### OrderCreatedEvent
- Type: Class
- eventId: UUID
- occurredOn: Instant
- eventType: "OrderCreated"
- eventVersion: "1.0"
- payload: Order aggregate

### OrderCompletedEvent / OrderModifiedEvent
- Similar structure with different eventType values

### OrderCreatedOutputEvent (extends AbstractEvent<OrderCreatedDTO>)
- eventId: UUID
- occurredOn: Instant
- eventType: "OrderCreated"
- eventVersion: "1.0"
- payload: OrderCreatedDTO
  - orderNumber: Long
  - externalId, orderStatus, locationCode, locationName
  - createDate: ZonedDateTime
  - shipmentType, priority, shippingMethod, productCategory
  - desiredShippingDate: LocalDate
  - shippingCustomerCode, shippingCustomerName, billingCustomerCode
  - willPickUp: boolean, willPickUpPhoneNumber
  - transactionId: UUID
  - orderItems: List<OrderItemCreatedDTO>
    - productFamily, bloodType, quantity, comments
    - attributes: Map<String,String>
  - quarantinedProducts, labelStatus, version

### OrderCompletedOutputEvent (extends AbstractEvent<OrderCompletedDTO>)
- Extends OrderCreatedDTO with:
  - totalShipped, totalRemaining, totalProducts
  - completeEmployeeId, completeDate, completeComments
  - orderItems: List<OrderItemCompletedDTO>
    - Adds: quantityShipped, quantityRemaining

---

## Manufacturing Service - ApheresisPlasma

### Base Event<T> Structure
- eventId: String (UUID as string)
- occurredOn: ZonedDateTime
- eventType: EventType (value object)
- eventVersion: EventVersion (value object)
- payload: T
- getKey(): String (abstract method for partitioning)

### ApheresisPlasmaProductCreatedEvent extends Event<ProductCreated>
- Event Key: {unitNumber}-{productCode}

### ApheresisPlasmaProductCompletedEvent extends Event<ProductCompleted>
- Event Key: {unitNumber}-{productCode}

### ProductCreated Payload (45+ fields)
Core:
- unitNumber: String (Required) - e.g., "W036202412345"
- productCode: String (Required) - e.g., "E086900"
- productDescription: String (Required)
- productFamily: String (Required)
- completionStage: ProductCompletionStage (INTERMEDIATE, FINAL)

Measurements:
- weight: Weight (value object) - Integer value + Unit
- volume: Volume (value object) - Integer value + Unit
- anticoagulantVolume: Volume

Metadata:
- drawTime: ZonedDateTime
- donationType: String
- procedureType: String (e.g., APHERESIS_PLASMA)
- collectionLocation: String
- manufacturingLocation: String
- aboRh: String (e.g., AP, AN, BP, BN)
- performedBy: String (operator ID)
- createDate: ZonedDateTime

Complex:
- inputProducts: List<InputProduct>
  - unitNumber, productCode, completionStage
- additionalSteps: List<Step>
  - stepType, status, lastUpdated: ZonedDateTime

Expiration:
- expirationDate: String
- expirationTime: String
- collectionTimeZone: String
- bagType: String
- autoConverted: Boolean

### ProductCompleted Payload (8 fields)
- unitNumber: String (Required)
- productCode: String (Required)
- completionStage: ProductCompletionStage (Required)
- completionDate: ZonedDateTime
- additionalSteps: List<Step>
- anticoagulantVolume: Volume
- volume: Volume
- aboRh: String (Required)

### Value Objects
- Unit: MILLILITERS, GRAMS (factory methods)
- ProductCompletionStage: INTERMEDIATE, FINAL (factory methods)
- EventType: static methods for each event type
- EventVersion: VERSION_1_0() → "1.0"

---

## Manufacturing Service - ApheresisPlatelet

Events (13+ total):
- ApheresisPlateletProductCreatedEvent
- ApheresisPlateletProductCompletedEvent
- ApheresisPlateletProductUpdatedEvent
- ApheresisPlateletQCRequestedEvent (QC-specific)
- ApheresisPlateletReadyForCADEvent
- ApheresisPlateletVolumeCalculatedEvent
- ApheresisPlateletSampleCollectedEvent
- ProductBottleCreatedEvent
- ProductUnsuitableEvent
- QuarantineProductEvent
- QuarantineUnitEvent
- RemoveQuarantineEvent

All follow same Event<T> pattern as ApheresisPlasma

---

## Manufacturing Service - WholeBlood

Events (7+ total):
- WholeBloodProductCreatedEvent
- WholeBloodProductUpdatedEvent
- WholeBloodProductCompletedEvent
- WholeBloodQCRequestedEvent
- WholeBloodSampleCollectedEvent
- WholeBloodVolumeCalculatedEvent
- ProductUnsuitableEvent

All follow same Event<T> pattern as ApheresisPlasma

---

## Type Mapping for Avro

Java Type → Avro Type
- String → string
- Integer → int
- Long → long
- Boolean → boolean
- UUID → string (logicalType: uuid)
- Instant → long (logicalType: timestamp-millis)
- ZonedDateTime → long (logicalType: timestamp-millis) + timezone field
- LocalDate → int (logicalType: date)
- Enum → enum with symbols
- Record → record
- List<T> → array with items
- Map<String,String> → map with string values
- Optional<T> → ["null", T] union

---

## Recommended Avro Subject Names

Collections:
- collections-received-value
- collections-updated-value

Orders:
- orders-created-value
- orders-completed-value

Manufacturing (ApheresisPlasma):
- apheresis-plasma-product-created-value
- apheresis-plasma-product-completed-value

Manufacturing (ApheresisPlatelet):
- apheresis-platelet-product-created-value
- apheresis-platelet-qc-requested-value

Manufacturing (WholeBlood):
- wholeblood-product-created-value
- wholeblood-qc-requested-value

---

## Schema Count Summary

Collections: 7 schemas (4 events + 2 enums + 1 value object)
Orders: 16+ schemas (11 events + 4 DTOs + 1 base)
Manufacturing ApheresisPlasma: 22+ schemas (5 events + 3 payloads + 10+ value objects)
Manufacturing ApheresisPlatelet: 13+ schemas (similar structure)
Manufacturing WholeBlood: 7+ schemas (similar structure)

TOTAL: 45-55 Avro schemas

---

## Key Patterns

Pattern 1 - Envelope (Orders):
AbstractEvent<T> with eventId, occurredOn, payload, eventType, eventVersion

Pattern 2 - Generic Base (Manufacturing):
Event<T> with eventId, occurredOn, eventType, eventVersion, payload + abstract getKey()

Pattern 3 - Direct Records (Collections):
Simple records with inline nested objects

All services serialize to Serializable format for Kafka.

