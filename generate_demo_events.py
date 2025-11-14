#!/usr/bin/env python3
"""
BioPro Event Governance - Multi-Service Demo Event Generator

Generates a mix of valid and invalid events for all 3 BioPro services:
- Orders Service
- Manufacturing Service
- Collections Service

Usage:
    python generate_demo_events.py --count 100 --invalid-rate 20
    python generate_demo_events.py --count 50 --invalid-rate 30 --delay 100
    python generate_demo_events.py --help
"""

import argparse
import json
import random
import time
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

BLOOD_TYPES = [
    "O_POSITIVE", "O_NEGATIVE",
    "A_POSITIVE", "A_NEGATIVE",
    "B_POSITIVE", "B_NEGATIVE",
    "AB_POSITIVE", "AB_NEGATIVE"
]

PRIORITIES = ["ROUTINE", "URGENT", "LIFE_THREATENING"]

FACILITIES = [
    "FAC-001", "FAC-002", "FAC-003", "FAC-CENTRAL", "FAC-NORTH"
]

PRODUCT_TYPES = ["E086900", "E089900", "E082900", "E087900"]
PRODUCT_STATUSES = ["CREATED", "PROCESSING", "COMPLETED"]

DONATION_TYPES = ["ALLOGENEIC", "AUTOLOGOUS", "DIRECTED"]
COLLECTION_STATUSES = ["RECEIVED", "PROCESSING", "STORED", "SHIPPED"]
BAG_TYPES = ["SINGLE", "DOUBLE", "TRIPLE", "QUADRUPLE"]


# ============================================================================
# Orders Generators
# ============================================================================

def generate_valid_order(num: int) -> Dict[str, Any]:
    """Generate a valid order that will pass schema validation"""
    return {
        "facilityId": random.choice(FACILITIES),
        "bloodType": random.choice(BLOOD_TYPES),
        "quantity": random.randint(1, 10),
        "priority": random.choice(PRIORITIES)
    }


def generate_invalid_order(num: int) -> Dict[str, Any]:
    """Generate an invalid order"""
    failures = [
        # Missing required fields
        lambda: {
            "bloodType": random.choice(BLOOD_TYPES),
            "quantity": random.randint(1, 5)
            # Missing facilityId
        },
        # Invalid enum value
        lambda: {
            "facilityId": random.choice(FACILITIES),
            "bloodType": "INVALID_TYPE",
            "quantity": random.randint(1, 5),
            "priority": random.choice(PRIORITIES)
        },
        # Wrong type for quantity
        lambda: {
            "facilityId": random.choice(FACILITIES),
            "bloodType": random.choice(BLOOD_TYPES),
            "quantity": "not-a-number",
            "priority": random.choice(PRIORITIES)
        },
        # Null for required field
        lambda: {
            "facilityId": None,
            "bloodType": random.choice(BLOOD_TYPES),
            "quantity": random.randint(1, 5),
            "priority": random.choice(PRIORITIES)
        },
        # Extra unknown fields
        lambda: {
            "facilityId": random.choice(FACILITIES),
            "bloodType": random.choice(BLOOD_TYPES),
            "quantity": random.randint(1, 5),
            "priority": random.choice(PRIORITIES),
            "unknownField": "this should not be here",
            "extraField": 12345
        }
    ]
    return random.choice(failures)()


# ============================================================================
# Manufacturing Generators
# ============================================================================

def generate_valid_manufacturing(num: int) -> Dict[str, Any]:
    """Generate a valid manufacturing event that will pass schema validation"""
    return {
        "productId": f"W036{random.randint(10000, 99999)}",
        "productType": random.choice(PRODUCT_TYPES),
        "status": random.choice(PRODUCT_STATUSES)
    }


def generate_invalid_manufacturing(num: int) -> Dict[str, Any]:
    """Generate an invalid manufacturing event"""
    failures = [
        # Missing required productId
        lambda: {
            "productType": random.choice(PRODUCT_TYPES),
            "status": random.choice(PRODUCT_STATUSES)
        },
        # Invalid status
        lambda: {
            "productId": f"W036{random.randint(10000, 99999)}",
            "productType": random.choice(PRODUCT_TYPES),
            "status": "INVALID_STATUS"
        },
        # Null for required field
        lambda: {
            "productId": None,
            "productType": random.choice(PRODUCT_TYPES),
            "status": random.choice(PRODUCT_STATUSES)
        },
        # Wrong data types
        lambda: {
            "productId": 123456,  # Should be string
            "productType": random.choice(PRODUCT_TYPES),
            "status": random.choice(PRODUCT_STATUSES)
        },
        # Empty string
        lambda: {
            "productId": "",
            "productType": random.choice(PRODUCT_TYPES),
            "status": random.choice(PRODUCT_STATUSES)
        }
    ]
    return random.choice(failures)()


# ============================================================================
# Collections Generators
# ============================================================================

def generate_valid_collection(num: int) -> Dict[str, Any]:
    """Generate a valid collection event that will pass schema validation"""
    return {
        "unitNumber": f"W036{random.randint(10000, 99999)}",
        "donationType": random.choice(DONATION_TYPES),
        "status": random.choice(COLLECTION_STATUSES),
        "bagType": random.choice(BAG_TYPES),
        "procedureType": "APHERESIS",
        "collectionLocation": random.choice(FACILITIES),
        "aboRh": random.choice(["AP", "AN", "BP", "BN", "OP", "ON", "ABP", "ABN"])
    }


def generate_invalid_collection(num: int) -> Dict[str, Any]:
    """Generate an invalid collection event"""
    failures = [
        # Missing required unitNumber
        lambda: {
            "donationType": random.choice(DONATION_TYPES),
            "status": random.choice(COLLECTION_STATUSES)
        },
        # Invalid donation type
        lambda: {
            "unitNumber": f"W036{random.randint(10000, 99999)}",
            "donationType": "INVALID_TYPE",
            "status": random.choice(COLLECTION_STATUSES)
        },
        # Null for required field
        lambda: {
            "unitNumber": f"W036{random.randint(10000, 99999)}",
            "donationType": None,
            "status": random.choice(COLLECTION_STATUSES)
        },
        # Missing status
        lambda: {
            "unitNumber": f"W036{random.randint(10000, 99999)}",
            "donationType": random.choice(DONATION_TYPES)
        },
        # Extra invalid fields
        lambda: {
            "unitNumber": f"W036{random.randint(10000, 99999)}",
            "donationType": random.choice(DONATION_TYPES),
            "status": random.choice(COLLECTION_STATUSES),
            "invalidField": "bad data",
            "extraProperty": True
        }
    ]
    return random.choice(failures)()


# ============================================================================
# HTTP Clients
# ============================================================================

class EventClient:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        self.services = {
            "orders": "http://localhost:8080/api/orders",
            "manufacturing": "http://localhost:8082/api/manufacturing/products",
            "collections": "http://localhost:8083/api/collections"
        }

    def send_event(self, service: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Send event to specified service"""
        url = self.services.get(service)
        if not url:
            return {"success": False, "error": f"Unknown service: {service}"}

        try:
            response = self.session.post(
                url,
                json=event,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text[:200] if response.text else ""
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "status_code": 0,
                "error": str(e)
            }


# ============================================================================
# Statistics Tracker
# ============================================================================

class StatsTracker:
    def __init__(self):
        self.total = 0
        self.by_service = {
            "orders": {"valid": 0, "invalid": 0, "success": 0, "failed": 0},
            "manufacturing": {"valid": 0, "invalid": 0, "success": 0, "failed": 0},
            "collections": {"valid": 0, "invalid": 0, "success": 0, "failed": 0}
        }
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    def record(self, service: str, is_valid: bool, success: bool):
        self.total += 1
        stats = self.by_service[service]

        if is_valid:
            stats["valid"] += 1
        else:
            stats["invalid"] += 1

        if success:
            stats["success"] += 1
        else:
            stats["failed"] += 1

    def get_duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    def get_rate(self) -> float:
        duration = self.get_duration()
        if duration > 0:
            return self.total / duration
        return 0

    def print_summary(self):
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        for service, stats in self.by_service.items():
            total = stats["valid"] + stats["invalid"]
            if total == 0:
                continue

            print(f"\n{service.upper()} Service:")
            print(f"  Total Events:        {total}")
            print(f"  Valid Events:        {stats['valid']} ({stats['valid']/total*100:.1f}%)")
            print(f"  Invalid Events:      {stats['invalid']} ({stats['invalid']/total*100:.1f}%)")
            print(f"  HTTP Success:        {stats['success']}")
            print(f"  HTTP Failed:         {stats['failed']}")

        print(f"\nOVERALL:")
        total_valid = sum(s["valid"] for s in self.by_service.values())
        total_invalid = sum(s["invalid"] for s in self.by_service.values())
        total_success = sum(s["success"] for s in self.by_service.values())
        total_failed = sum(s["failed"] for s in self.by_service.values())

        print(f"  Total Events:        {self.total}")
        print(f"  Valid Events:        {total_valid} ({total_valid/self.total*100:.1f}%)")
        print(f"  Invalid Events:      {total_invalid} ({total_invalid/self.total*100:.1f}%)")
        print(f"  HTTP Success:        {total_success}")
        print(f"  HTTP Failed:         {total_failed}")
        print(f"\nPerformance:")
        print(f"  Duration:            {self.get_duration():.2f} seconds")
        print(f"  Rate:                {self.get_rate():.2f} events/second")
        print("=" * 80)


# ============================================================================
# Progress Display
# ============================================================================

def print_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", length: int = 50):
    """Print a progress bar"""
    percent = current / total
    filled = int(length * percent)
    bar = "#" * filled + "-" * (length - filled)
    print(f"\r{prefix} |{bar}| {current}/{total} ({percent*100:.1f}%) {suffix}", end="", flush=True)


# ============================================================================
# Main Generator
# ============================================================================

def generate_events(
    count: int,
    invalid_rate: int,
    delay_ms: int,
    verbose: bool = False
):
    """Generate and send events to all services"""

    # Calculate counts per service
    events_per_service = count // 3
    remainder = count % 3

    print("\n" + "=" * 80)
    print("BioPro Multi-Service Demo Event Generator")
    print("=" * 80)
    print(f"Total Events:          {count}")
    print(f"  Per Service:         ~{events_per_service}")
    print(f"  Invalid Rate:        {invalid_rate}%")
    print(f"Delay:                 {delay_ms}ms between requests")
    print(f"Verbose:               {verbose}")
    print("=" * 80)

    # Initialize
    client = EventClient()
    stats = StatsTracker()

    # Generate events for each service
    events = []

    # Orders events
    for i in range(events_per_service + (1 if remainder > 0 else 0)):
        is_valid = random.randint(1, 100) > invalid_rate
        event_data = generate_valid_order(i) if is_valid else generate_invalid_order(i)
        events.append(("orders", is_valid, event_data))

    # Manufacturing events
    for i in range(events_per_service + (1 if remainder > 1 else 0)):
        is_valid = random.randint(1, 100) > invalid_rate
        event_data = generate_valid_manufacturing(i) if is_valid else generate_invalid_manufacturing(i)
        events.append(("manufacturing", is_valid, event_data))

    # Collections events
    for i in range(events_per_service):
        is_valid = random.randint(1, 100) > invalid_rate
        event_data = generate_valid_collection(i) if is_valid else generate_invalid_collection(i)
        events.append(("collections", is_valid, event_data))

    # Shuffle for realistic distribution
    random.shuffle(events)

    # Send events
    print("\nSending events to all services...")
    stats.start()

    for idx, (service, is_valid, event_data) in enumerate(events, 1):
        # Send event
        result = client.send_event(service, event_data)

        # Track stats
        stats.record(service, is_valid, result["success"])

        # Verbose output
        if verbose:
            status = "[OK]" if result["success"] else "[FAIL]"
            validity = "VALID" if is_valid else "INVALID"
            print(f"[{idx}/{count}] {status} {service:15s} {validity:8s}")
        else:
            # Progress bar
            total_success = sum(s["success"] for s in stats.by_service.values())
            total_failed = sum(s["failed"] for s in stats.by_service.values())
            suffix = f"| {total_success} success, {total_failed} failed"
            print_progress_bar(idx, count, prefix="Progress:", suffix=suffix)

        # Delay
        if delay_ms > 0 and idx < count:
            time.sleep(delay_ms / 1000.0)

    stats.finish()

    if not verbose:
        print()  # New line after progress bar

    # Print summary
    stats.print_summary()

    # Grafana instructions
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Open Grafana: http://localhost:3000")
    print("2. Navigate to 'BioPro Event Governance - DLQ Monitoring' dashboard")
    print("3. Observe metrics for all 3 services")
    print("\n4. Check Redpanda Console: http://localhost:8090")
    print("   - View topics: biopro.orders.events, biopro.manufacturing.events, biopro.collections.events")
    print("   - View DLQ topics for failed events")
    print("=" * 80 + "\n")


# ============================================================================
# CLI
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate demo events for all BioPro services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 300 events (20% invalid) across all 3 services
  python generate_demo_events.py --count 300 --invalid-rate 20

  # Generate 150 events (30% invalid) with 100ms delay
  python generate_demo_events.py --count 150 --invalid-rate 30 --delay 100

  # Generate 60 events as fast as possible
  python generate_demo_events.py --count 60 --invalid-rate 25 --delay 0

  # Verbose output
  python generate_demo_events.py --count 30 --verbose
        """
    )

    parser.add_argument(
        "--count",
        type=int,
        default=300,
        help="Total number of events to generate (default: 300)"
    )

    parser.add_argument(
        "--invalid-rate",
        type=int,
        default=20,
        help="Percentage of invalid events (0-100, default: 20)"
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=50,
        help="Delay between requests in milliseconds (default: 50)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output for each request"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Validate arguments
    if args.count <= 0:
        print("ERROR: count must be positive")
        sys.exit(1)

    if not (0 <= args.invalid_rate <= 100):
        print("ERROR: invalid-rate must be between 0 and 100")
        sys.exit(1)

    if args.delay < 0:
        print("ERROR: delay must be non-negative")
        sys.exit(1)

    # Check connectivity to all services
    print("\nChecking connectivity to all services...")
    services = {
        "Orders": "http://localhost:8080/actuator/health",
        "Manufacturing": "http://localhost:8082/actuator/health",
        "Collections": "http://localhost:8083/actuator/health"
    }

    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name} service is reachable")
            else:
                print(f"[WARN] {name} service returned status {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Cannot reach {name} service: {e}")
            all_ok = False

    if not all_ok:
        print("\nTroubleshooting:")
        print("  1. Verify services are running: docker-compose ps")
        print("  2. Check logs: docker-compose logs")
        sys.exit(1)

    # Generate events
    try:
        generate_events(
            count=args.count,
            invalid_rate=args.invalid_rate,
            delay_ms=args.delay,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
