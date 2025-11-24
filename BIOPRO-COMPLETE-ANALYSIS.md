# BioPro Complete Event Analysis Report

## Executive Summary

- **Total Services**: 18
- **Total Events**: 74
- **Event Flows Mapped**: 71

## Services by Repository

### biopro-distribution

| Service | Published | Consumed |
|---------|-----------|----------|
| customer | 0 | 0 |
| eventbridge | 9 | 0 |
| inventory | 2 | 0 |
| irradiation | 2 | 0 |
| order | 6 | 0 |
| partnerorderprovider | 0 | 0 |
| receiving | 2 | 0 |
| recoveredplasmashipping | 7 | 0 |
| shipping | 5 | 0 |

### biopro-donor

| Service | Published | Consumed |
|---------|-----------|----------|
| eventmanagement | 4 | 0 |
| history | 3 | 0 |
| notification | 2 | 0 |
| testresultmanagement | 19 | 0 |

### biopro-interface

| Service | Published | Consumed |
|---------|-----------|----------|
| collections | 2 | 0 |

### biopro-operations

| Service | Published | Consumed |
|---------|-----------|----------|
| device | 3 | 0 |
| research | 3 | 0 |
| role | 5 | 0 |
| supply | 0 | 0 |

## Event Flows

### Complete Event Choreography

**ABORHExceptionCreatedEvent**
- Publishers: testresultmanagement
- Consumers: None

**ABORHExceptionResolvedEvent**
- Publishers: testresultmanagement
- Consumers: None

**AcceptedNewDonationEvent**
- Publishers: collections
- Consumers: None

**AcceptedUpdatedDonationEvent**
- Publishers: collections
- Consumers: None

**BloodTypeReceivedEvent**
- Publishers: testresultmanagement
- Consumers: None

**CreateAboRhExceptionEvent**
- Publishers: testresultmanagement
- Consumers: None

**CreateDeferralEvent**
- Publishers: testresultmanagement
- Consumers: None

**CreateDonorNotificationEvent**
- Publishers: testresultmanagement
- Consumers: None

**DeferralCreatedEvent**
- Publishers: testresultmanagement
- Consumers: None

**DeviceCreatedUpdatedEvent**
- Publishers: device
- Consumers: None

**DonorNotificationCompletedEvent**
- Publishers: notification
- Consumers: None

**DonorNotificationCreatedEvent**
- Publishers: notification
- Consumers: None

**DonorUpdatedEvent**
- Publishers: history
- Consumers: None

**ExternalTransferCompletedEvent**
- Publishers: shipping
- Consumers: None

**FlagUnitForResearchEvent**
- Publishers: eventmanagement
- Consumers: None

**HistoryCreatedEvent**
- Publishers: history
- Consumers: None

**ImportCompletedDomainEvent**
- Publishers: receiving
- Consumers: None

**InventoryCreatedEvent**
- Publishers: inventory
- Consumers: None

**InventoryUpdatedApplicationEvent**
- Publishers: inventory
- Consumers: None

**InventoryUpdatedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**OrderCancelledEvent**
- Publishers: order
- Consumers: None

**OrderCancelledOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**OrderCompletedEvent**
- Publishers: order
- Consumers: None

**OrderCompletedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**OrderCreatedEvent**
- Publishers: order
- Consumers: None

**OrderCreatedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**OrderModifiedEvent**
- Publishers: order
- Consumers: None

**OrderModifiedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**OrderPackingStartedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**OrderRejectedEvent**
- Publishers: order
- Consumers: None

**PickListCreatedEvent**
- Publishers: order
- Consumers: None

**ProductModifiedEvent**
- Publishers: irradiation
- Consumers: None

**ProductQuarantinedEvent**
- Publishers: irradiation
- Consumers: None

**ProductUnsuitableEvent**
- Publishers: eventmanagement, testresultmanagement
- Consumers: None

**QuarantineProductEvent**
- Publishers: eventmanagement
- Consumers: None

**QuarantineUnitEvent**
- Publishers: testresultmanagement
- Consumers: None

**RecoveredPlasmaCartonClosedEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecoveredPlasmaCartonCreatedEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecoveredPlasmaCartonRemovedEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecoveredPlasmaCartonUnpackedEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecoveredPlasmaShipmentClosedEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecoveredPlasmaShipmentClosedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**RecoveredPlasmaShipmentCreatedEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecoveredPlasmaShipmentProcessingEvent**
- Publishers: recoveredplasmashipping
- Consumers: None

**RecruitmentAndEligibilityOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**RemoveQuarantineEvent**
- Publishers: eventmanagement, testresultmanagement
- Consumers: None

**RoleCreatedEvent**
- Publishers: role
- Consumers: None

**ShipmentCompletedEvent**
- Publishers: shipping
- Consumers: None

**ShipmentCompletedOutboundEvent**
- Publishers: eventbridge
- Consumers: None

**ShipmentCreatedEvent**
- Publishers: shipping
- Consumers: None

**ShipmentItemPackedEvent**
- Publishers: shipping
- Consumers: None

**ShipmentPackingStartedEvent**
- Publishers: shipping
- Consumers: None

**StorageConfigurationCreatedEvent**
- Publishers: device
- Consumers: None

**StorageConfigurationUpdatedEvent**
- Publishers: device
- Consumers: None

**SubscribeTestResultsEvent**
- Publishers: testresultmanagement, research
- Consumers: None

**SubscribedUnitsEvent**
- Publishers: testresultmanagement
- Consumers: None

**TestOrderCreatedEvent**
- Publishers: testresultmanagement
- Consumers: None

**TestResultExceptionCreatedEvent**
- Publishers: testresultmanagement
- Consumers: None

**TestResultExceptionResolvedEvent**
- Publishers: testresultmanagement
- Consumers: None

**TestResultPanelCompletedEvent**
- Publishers: testresultmanagement
- Consumers: None

**TestResultReceivedEvent**
- Publishers: testresultmanagement
- Consumers: None

**TransferReceiptCompletedDomainEvent**
- Publishers: receiving
- Consumers: None

**UnSubscribeTestResultsEvent**
- Publishers: research
- Consumers: None

**UnitAssignedEvent**
- Publishers: research
- Consumers: None

**UnitDiscardEvent**
- Publishers: history
- Consumers: None

**UnitUnsuitableEvent**
- Publishers: testresultmanagement
- Consumers: None

**UnsubscribeTestResultsEvent**
- Publishers: testresultmanagement
- Consumers: None

**UserCreatedEvent**
- Publishers: role
- Consumers: None

**UserDeactivatedEvent**
- Publishers: role
- Consumers: None

**UserRolesAssignedEvent**
- Publishers: role
- Consumers: None

**UserUpdatedEvent**
- Publishers: role
- Consumers: None

## All Events

| Event Name | Service | Repository | Fields |
|------------|---------|------------|--------|
| ABORHExceptionCreatedEvent | testresultmanagement | biopro-donor | 2 |
| ABORHExceptionResolvedEvent | testresultmanagement | biopro-donor | 2 |
| AcceptedNewDonationEvent | collections | biopro-interface | 1 |
| AcceptedUpdatedDonationEvent | collections | biopro-interface | 1 |
| BloodTypeReceivedEvent | testresultmanagement | biopro-donor | 2 |
| CreateAboRhExceptionEvent | testresultmanagement | biopro-donor | 2 |
| CreateDeferralEvent | testresultmanagement | biopro-donor | 2 |
| CreateDonorNotificationEvent | testresultmanagement | biopro-donor | 2 |
| DeferralCreatedEvent | testresultmanagement | biopro-donor | 2 |
| DeviceCreatedUpdatedEvent | device | biopro-operations | 5 |
| DonorNotificationCompletedEvent | notification | biopro-donor | 0 |
| DonorNotificationCreatedEvent | notification | biopro-donor | 0 |
| DonorUpdatedEvent | history | biopro-donor | 5 |
| ExternalTransferCompletedEvent | shipping | biopro-distribution | 3 |
| FlagUnitForResearchEvent | eventmanagement | biopro-donor | 0 |
| HistoryCreatedEvent | history | biopro-donor | 1 |
| ImportCompletedDomainEvent | receiving | biopro-distribution | 3 |
| InventoryCreatedEvent | inventory | biopro-distribution | 1 |
| InventoryUpdatedApplicationEvent | inventory | biopro-distribution | 2 |
| InventoryUpdatedOutboundEvent | eventbridge | biopro-distribution | 3 |
| OrderCancelledEvent | order | biopro-distribution | 3 |
| OrderCancelledOutboundEvent | eventbridge | biopro-distribution | 0 |
| OrderCompletedEvent | order | biopro-distribution | 3 |
| OrderCompletedOutboundEvent | eventbridge | biopro-distribution | 0 |
| OrderCreatedEvent | order | biopro-distribution | 3 |
| OrderCreatedOutboundEvent | eventbridge | biopro-distribution | 0 |
| OrderModifiedEvent | order | biopro-distribution | 3 |
| OrderModifiedOutboundEvent | eventbridge | biopro-distribution | 0 |
| OrderPackingStartedOutboundEvent | eventbridge | biopro-distribution | 3 |
| OrderRejectedEvent | order | biopro-distribution | 3 |
| PickListCreatedEvent | order | biopro-distribution | 3 |
| ProductModifiedEvent | irradiation | biopro-distribution | 0 |
| ProductQuarantinedEvent | irradiation | biopro-distribution | 0 |
| ProductUnsuitableEvent | eventmanagement | biopro-donor | 0 |
| ProductUnsuitableEvent | testresultmanagement | biopro-donor | 2 |
| QuarantineProductEvent | eventmanagement | biopro-donor | 0 |
| QuarantineUnitEvent | testresultmanagement | biopro-donor | 2 |
| RecoveredPlasmaCartonClosedEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecoveredPlasmaCartonCreatedEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecoveredPlasmaCartonRemovedEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecoveredPlasmaCartonUnpackedEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecoveredPlasmaShipmentClosedEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecoveredPlasmaShipmentClosedOutboundEvent | eventbridge | biopro-distribution | 3 |
| RecoveredPlasmaShipmentCreatedEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecoveredPlasmaShipmentProcessingEvent | recoveredplasmashipping | biopro-distribution | 3 |
| RecruitmentAndEligibilityOutboundEvent | eventbridge | biopro-distribution | 3 |
| RemoveQuarantineEvent | eventmanagement | biopro-donor | 0 |
| RemoveQuarantineEvent | testresultmanagement | biopro-donor | 2 |
| RoleCreatedEvent | role | biopro-operations | 6 |
| ShipmentCompletedEvent | shipping | biopro-distribution | 3 |
| ShipmentCompletedOutboundEvent | eventbridge | biopro-distribution | 3 |
| ShipmentCreatedEvent | shipping | biopro-distribution | 3 |
| ShipmentItemPackedEvent | shipping | biopro-distribution | 3 |
| ShipmentPackingStartedEvent | shipping | biopro-distribution | 3 |
| StorageConfigurationCreatedEvent | device | biopro-operations | 2 |
| StorageConfigurationUpdatedEvent | device | biopro-operations | 2 |
| SubscribeTestResultsEvent | testresultmanagement | biopro-donor | 2 |
| SubscribeTestResultsEvent | research | biopro-operations | 3 |
| SubscribedUnitsEvent | testresultmanagement | biopro-donor | 2 |
| TestOrderCreatedEvent | testresultmanagement | biopro-donor | 2 |
| TestResultExceptionCreatedEvent | testresultmanagement | biopro-donor | 2 |
| TestResultExceptionResolvedEvent | testresultmanagement | biopro-donor | 2 |
| TestResultPanelCompletedEvent | testresultmanagement | biopro-donor | 2 |
| TestResultReceivedEvent | testresultmanagement | biopro-donor | 2 |
| TransferReceiptCompletedDomainEvent | receiving | biopro-distribution | 3 |
| UnSubscribeTestResultsEvent | research | biopro-operations | 3 |
| UnitAssignedEvent | research | biopro-operations | 3 |
| UnitDiscardEvent | history | biopro-donor | 5 |
| UnitUnsuitableEvent | testresultmanagement | biopro-donor | 2 |
| UnsubscribeTestResultsEvent | testresultmanagement | biopro-donor | 2 |
| UserCreatedEvent | role | biopro-operations | 6 |
| UserDeactivatedEvent | role | biopro-operations | 6 |
| UserRolesAssignedEvent | role | biopro-operations | 7 |
| UserUpdatedEvent | role | biopro-operations | 6 |
