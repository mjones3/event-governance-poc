#!/usr/bin/env python3
"""
BioPro Event Governance - Demo Order Generator

Generates a mix of valid and invalid orders for demonstrating
the DLQ framework and Grafana dashboards.

Usage:
    python generate_demo_orders.py --count 100 --invalid-rate 30
    python generate_demo_orders.py --count 50 --invalid-rate 50 --delay 100
    python generate_demo_orders.py --help
"""

import argparse
import json
import random
import time
import sys
from typing import Dict, List, Any
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
    "FAC-001", "FAC-002", "FAC-003", "FAC-004", "FAC-005",
    "FAC-CENTRAL", "FAC-NORTH", "FAC-SOUTH", "FAC-EAST", "FAC-WEST"
]

DOCTORS = [
    "DR-SMITH", "DR-JOHNSON", "DR-WILLIAMS", "DR-BROWN", "DR-JONES",
    "DR-GARCIA", "DR-MILLER", "DR-DAVIS", "DR-RODRIGUEZ", "DR-MARTINEZ"
]


# ============================================================================
# Order Generators
# ============================================================================

def generate_valid_order(order_num: int) -> Dict[str, Any]:
    """Generate a valid order that will pass schema validation"""
    return {
        "orderId": f"ORD-DEMO-{order_num:04d}",
        "bloodType": random.choice(BLOOD_TYPES),
        "quantity": random.randint(1, 10),
        "priority": random.choice(PRIORITIES),
        "facilityId": random.choice(FACILITIES),
        "requestedBy": random.choice(DOCTORS)
    }


def generate_invalid_order_missing_fields(order_num: int) -> Dict[str, Any]:
    """Generate order missing required fields"""
    order = {
        "orderId": f"ORD-INVALID-MISSING-{order_num:04d}",
        "bloodType": random.choice(BLOOD_TYPES),
        "quantity": random.randint(1, 5)
        # Missing: facilityId, requestedBy
    }
    return order


def generate_invalid_order_unknown_fields(order_num: int) -> Dict[str, Any]:
    """Generate order with fields not in schema"""
    return {
        "orderId": f"ORD-INVALID-UNKNOWN-{order_num:04d}",
        "invalidField": "this field does not exist",
        "unknownProperty": "bad data",
        "extraField": 12345,
        "anotherBadField": True
    }


def generate_invalid_order_type_mismatch(order_num: int) -> Dict[str, Any]:
    """Generate order with wrong data types"""
    return {
        "orderId": f"ORD-INVALID-TYPE-{order_num:04d}",
        "bloodType": random.choice(BLOOD_TYPES),
        "quantity": "not-a-number",  # Should be int
        "priority": random.choice(PRIORITIES),
        "facilityId": random.choice(FACILITIES),
        "requestedBy": random.choice(DOCTORS)
    }


def generate_invalid_order_null_required(order_num: int) -> Dict[str, Any]:
    """Generate order with null for required fields"""
    return {
        "orderId": f"ORD-INVALID-NULL-{order_num:04d}",
        "bloodType": None,  # Required field set to null
        "quantity": random.randint(1, 5),
        "priority": random.choice(PRIORITIES),
        "facilityId": random.choice(FACILITIES),
        "requestedBy": random.choice(DOCTORS)
    }


def generate_invalid_order_empty_strings(order_num: int) -> Dict[str, Any]:
    """Generate order with empty strings"""
    return {
        "orderId": "",  # Empty string for required field
        "bloodType": random.choice(BLOOD_TYPES),
        "quantity": random.randint(1, 5),
        "priority": "",
        "facilityId": random.choice(FACILITIES),
        "requestedBy": ""
    }


def generate_invalid_order_wrong_enum(order_num: int) -> Dict[str, Any]:
    """Generate order with invalid enum values"""
    return {
        "orderId": f"ORD-INVALID-ENUM-{order_num:04d}",
        "bloodType": "INVALID_BLOOD_TYPE",  # Not in enum
        "quantity": random.randint(1, 5),
        "priority": "SUPER_CRITICAL",  # Not in enum
        "facilityId": random.choice(FACILITIES),
        "requestedBy": random.choice(DOCTORS)
    }


# Invalid order generators with weights (probability of selection)
INVALID_ORDER_GENERATORS = [
    (generate_invalid_order_missing_fields, 30),      # 30% - Most common
    (generate_invalid_order_unknown_fields, 20),      # 20%
    (generate_invalid_order_type_mismatch, 20),       # 20%
    (generate_invalid_order_null_required, 15),       # 15%
    (generate_invalid_order_empty_strings, 10),       # 10%
    (generate_invalid_order_wrong_enum, 5),           # 5% - Least common
]


def generate_invalid_order(order_num: int) -> Dict[str, Any]:
    """Generate a random invalid order based on weights"""
    generators, weights = zip(*INVALID_ORDER_GENERATORS)
    generator = random.choices(generators, weights=weights)[0]
    return generator(order_num)


# ============================================================================
# HTTP Client
# ============================================================================

class OrderClient:
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def send_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Send order to orders service"""
        url = f"{self.base_url}/api/orders"
        try:
            response = self.session.post(
                url,
                json=order,
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
        self.valid = 0
        self.invalid = 0
        self.success = 0
        self.failed = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    def record_valid(self, success: bool):
        self.total += 1
        self.valid += 1
        if success:
            self.success += 1
        else:
            self.failed += 1

    def record_invalid(self, success: bool):
        self.total += 1
        self.invalid += 1
        if success:
            self.success += 1
        else:
            self.failed += 1

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
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total Orders Sent:     {self.total}")
        print(f"  Valid Orders:        {self.valid} ({self.valid/self.total*100:.1f}%)")
        print(f"  Invalid Orders:      {self.invalid} ({self.invalid/self.total*100:.1f}%)")
        print(f"\nHTTP Responses:")
        print(f"  Success (200):       {self.success}")
        print(f"  Failed:              {self.failed}")
        print(f"\nPerformance:")
        print(f"  Duration:            {self.get_duration():.2f} seconds")
        print(f"  Rate:                {self.get_rate():.2f} orders/second")
        print("=" * 70)


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

def generate_orders(
    count: int,
    invalid_rate: int,
    delay_ms: int,
    base_url: str,
    verbose: bool = False
):
    """Generate and send orders"""

    # Calculate counts
    invalid_count = int(count * invalid_rate / 100)
    valid_count = count - invalid_count

    print("\n" + "=" * 70)
    print("BioPro Demo Order Generator")
    print("=" * 70)
    print(f"Target URL:            {base_url}/api/orders")
    print(f"Total Orders:          {count}")
    print(f"  Valid Orders:        {valid_count} ({valid_count/count*100:.1f}%)")
    print(f"  Invalid Orders:      {invalid_count} ({invalid_count/count*100:.1f}%)")
    print(f"Delay:                 {delay_ms}ms between requests")
    print(f"Verbose:               {verbose}")
    print("=" * 70)

    # Initialize
    client = OrderClient(base_url)
    stats = StatsTracker()

    # Create shuffled order list
    orders = []

    # Add valid orders
    for i in range(valid_count):
        orders.append(("valid", generate_valid_order(i)))

    # Add invalid orders
    for i in range(invalid_count):
        orders.append(("invalid", generate_invalid_order(i)))

    # Shuffle for realistic distribution
    random.shuffle(orders)

    # Send orders
    print("\nSending orders...")
    stats.start()

    for idx, (order_type, order) in enumerate(orders, 1):
        # Send order
        result = client.send_order(order)

        # Track stats
        if order_type == "valid":
            stats.record_valid(result["success"])
        else:
            stats.record_invalid(result["success"])

        # Verbose output
        if verbose:
            status = "[OK]" if result["success"] else "[FAIL]"
            print(f"[{idx}/{count}] {status} {order_type.upper():8s} - {order.get('orderId', 'N/A')}")
        else:
            # Progress bar
            suffix = f"| {stats.success} success, {stats.failed} failed"
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
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Open Grafana: http://localhost:3000")
    print("2. Navigate to 'BioPro Event Governance - DLQ Monitoring' dashboard")
    print("3. Observe the following panels:")
    print("   - Event Throughput (spike should be visible)")
    print(f"   - DLQ Rate (should be around {invalid_rate}%)")
    print("   - Error Distribution (SCHEMA_VALIDATION should dominate)")
    print("   - Success vs Failure (red area represents invalid events)")
    print("\n4. View DLQ messages:")
    print("   ./kcat.sh -C -t biopro.orders.dlq -e | jq")
    print("=" * 70 + "\n")


# ============================================================================
# CLI
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate demo orders for BioPro Event Governance framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 1000 orders (30% invalid) with default 50ms delay
  python generate_demo_orders.py

  # Generate 100 orders (30% invalid) with 50ms delay
  python generate_demo_orders.py --count 100 --invalid-rate 30 --delay 50

  # Generate 50 orders (50% invalid) as fast as possible
  python generate_demo_orders.py --count 50 --invalid-rate 50 --delay 0

  # Verbose output
  python generate_demo_orders.py --count 20 --verbose

  # Use from inside Docker network
  python generate_demo_orders.py --host http://orders-service:8080
        """
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="Number of orders to generate (default: 1000)"
    )

    parser.add_argument(
        "--invalid-rate",
        type=int,
        default=30,
        help="Percentage of invalid orders (0-100, default: 30)"
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=50,
        help="Delay between requests in milliseconds (default: 50)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:8080",
        help="Orders service host (default: http://localhost:8080)"
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

    # Check connectivity
    print(f"\nChecking connectivity to {args.host}...")
    try:
        response = requests.get(f"{args.host}/actuator/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Orders service is reachable")
        else:
            print(f"[WARN] Orders service returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Cannot reach orders service: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify services are running: docker ps")
        print("  2. If running from host: use --host http://localhost:8080")
        print("  3. If running from Docker: use --host http://orders-service:8080")
        sys.exit(1)

    # Generate orders
    try:
        generate_orders(
            count=args.count,
            invalid_rate=args.invalid_rate,
            delay_ms=args.delay,
            base_url=args.host,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
