#!/usr/bin/env python3
"""
Enhanced BioPro Event Extraction with Consumer Detection

This script properly detects event consumers by:
1. Finding all *Listener.java files
2. Extracting the event name from the class name
3. Determining which service is consuming which events
4. Building complete producer-consumer mappings
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

# Repository configurations
REPOS = [
    {
        "name": "biopro-manufacturing",
        "path": r"C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend",
        "services": ["apheresisplasma", "apheresisplatelet", "apheresisrbc", "checkin",
                    "discard", "labeling", "licensing", "pooling", "productmodification",
                    "qualitycontrol", "quarantine", "storage", "wholeblood"]
    },
    {
        "name": "biopro-interface",
        "path": r"C:\Users\MelvinJones\work\biopro\biopro-interface\backend",
        "services": ["collections"]
    },
    {
        "name": "biopro-distribution",
        "path": r"C:\Users\MelvinJones\work\biopro\biopro-distribution\backend",
        "services": ["customer", "eventbridge", "inventory", "irradiation", "order",
                    "partnerorderprovider", "receiving", "recoveredplasmashipping", "shipping"]
    },
    {
        "name": "biopro-donor",
        "path": r"C:\Users\MelvinJones\work\biopro\biopro-donor\backend",
        "services": ["eventmanagement", "history", "notification", "testresultmanagement"]
    },
    {
        "name": "biopro-operations",
        "path": r"C:\Users\MelvinJones\work\biopro\biopro-operations\backend",
        "services": ["device", "research", "role", "supply"]
    }
]


def find_event_files(service_path: str) -> List[str]:
    """Find all event-related Java files"""
    event_files = []
    for root, dirs, files in os.walk(service_path):
        if 'domain' in root and 'event' in root:
            for file in files:
                if file.endswith('Event.java'):
                    event_files.append(os.path.join(root, file))
    return event_files


def find_listener_files(service_path: str) -> List[str]:
    """Find all listener Java files"""
    listener_files = []
    for root, dirs, files in os.walk(service_path):
        for file in files:
            if file.endswith('Listener.java') and not file.startswith('Abstract'):
                listener_files.append(os.path.join(root, file))
    return listener_files


def extract_event_info(file_path: str) -> Dict[str, Any]:
    """Extract event information from Java file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract package
        package_match = re.search(r'package\s+([\w.]+);', content)
        package = package_match.group(1) if package_match else ""

        # Extract class name
        class_match = re.search(r'public\s+(?:record|class)\s+(\w+Event)', content)
        if not class_match:
            return None
        event_name = class_match.group(1)

        # Extract event type enum
        type_match = re.search(r'EventType\.(\w+)', content)
        event_type = type_match.group(1) if type_match else event_name.replace('Event', '').upper()

        # Extract fields from record or class
        fields = []

        # For records
        record_match = re.search(r'public\s+record\s+\w+Event\s*\((.*?)\)', content, re.DOTALL)
        if record_match:
            params = record_match.group(1)
            field_pattern = r'(\w+(?:<[\w<>, ]+>)?)\s+(\w+)'
            for match in re.finditer(field_pattern, params):
                fields.append({
                    "name": match.group(2),
                    "type": match.group(1),
                    "required": True
                })

        # For classes with fields
        field_matches = re.finditer(r'private\s+(?:final\s+)?(\w+(?:<[\w<>, ]+>)?)\s+(\w+);', content)
        for match in field_matches:
            fields.append({
                "name": match.group(2),
                "type": match.group(1),
                "required": False
            })

        return {
            "name": event_name,
            "package": package,
            "type": event_type,
            "version": "1.0",
            "file_path": file_path,
            "fields": fields
        }
    except Exception as e:
        print(f"       [ERROR] processing {file_path}: {e}")
        return None


def extract_consumed_events_from_listener(file_path: str) -> List[str]:
    """Extract event names from listener file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        consumed_events = []

        # Extract from class name pattern: SomeEventListener -> SomeEvent
        filename = os.path.basename(file_path)
        if filename.endswith('Listener.java'):
            # Remove "Listener.java" and add "Event"
            event_name = filename.replace('Listener.java', 'Event')
            consumed_events.append(event_name)

        # Also look for imports of event classes
        import_pattern = r'import\s+[\w.]+\.event\.(\w+Event);'
        for match in re.finditer(import_pattern, content):
            event_name = match.group(1)
            if event_name not in consumed_events:
                consumed_events.append(event_name)

        # Look for generic type parameters like <SomeEvent>
        generic_pattern = r'<(\w+Event)>'
        for match in re.finditer(generic_pattern, content):
            event_name = match.group(1)
            if event_name not in consumed_events:
                consumed_events.append(event_name)

        return consumed_events
    except Exception as e:
        print(f"       [ERROR] processing listener {file_path}: {e}")
        return []


def main():
    print("=" * 80)
    print("BioPro Complete Event Extraction with Consumer Detection")
    print("=" * 80)

    all_events = []
    all_services = []
    event_flows = {}

    for repo in REPOS:
        print(f"\n[REPO] Processing Repository: {repo['name']}")
        print(f"       Path: {repo['path']}")
        print(f"       Services: {len(repo['services'])}")

        for service_name in repo['services']:
            service_path = os.path.join(repo['path'], service_name)

            if not os.path.exists(service_path):
                print(f"       [WARNING] Service not found: {service_name}")
                continue

            print(f"\n       [SERVICE] Analyzing Service: {service_name}")

            # Find events
            event_files = find_event_files(service_path)
            print(f"                Found {len(event_files)} event files")

            # Find listeners
            listener_files = find_listener_files(service_path)
            print(f"                Found {len(listener_files)} listener files")

            # Extract event details
            service_events = []
            for event_file in event_files:
                event_info = extract_event_info(event_file)
                if event_info:
                    event_info['service'] = service_name
                    event_info['repository'] = repo['name']
                    service_events.append(event_info)
                    all_events.append(event_info)

            # Extract consumed events
            service_consumed_events = set()
            for listener_file in listener_files:
                consumed_events = extract_consumed_events_from_listener(listener_file)
                for event_name in consumed_events:
                    service_consumed_events.add(event_name)

            # Build service record
            published_event_names = [e['name'] for e in service_events]
            consumed_event_names = list(service_consumed_events)

            service_record = {
                "name": service_name,
                "repository": repo['name'],
                "events_published": len(service_events),
                "events_consumed": len(consumed_event_names),
                "published_events": published_event_names,
                "consumed_events": consumed_event_names,
                "event_details": service_events
            }

            all_services.append(service_record)

            # Track event flows - publishers
            for event in service_events:
                if event['name'] not in event_flows:
                    event_flows[event['name']] = {
                        "publishers": [],
                        "consumers": []
                    }
                if service_name not in event_flows[event['name']]['publishers']:
                    event_flows[event['name']]['publishers'].append(service_name)

            # Track event flows - consumers
            for event_name in consumed_event_names:
                if event_name not in event_flows:
                    event_flows[event_name] = {
                        "publishers": [],
                        "consumers": []
                    }
                if service_name not in event_flows[event_name]['consumers']:
                    event_flows[event_name]['consumers'].append(service_name)

            print(f"                [OK] Published: {len(service_events)} events")
            print(f"                [OK] Consumes: {len(consumed_event_names)} events")
            if consumed_event_names:
                print(f"                     Consuming: {', '.join(consumed_event_names[:5])}")

    # Generate summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Total Repositories: {len(REPOS)}")
    print(f"Total Services: {len(all_services)}")
    print(f"Total Events: {len(all_events)}")
    print(f"Total Event Flows: {len(event_flows)}")

    # Count events with consumers
    events_with_consumers = sum(1 for flow in event_flows.values() if flow['consumers'])
    print(f"Events with consumers: {events_with_consumers}/{len(event_flows)}")

    # Save results
    output = {
        "summary": {
            "repositories": len(REPOS),
            "services": len(all_services),
            "events": len(all_events),
            "event_flows": len(event_flows),
            "events_with_consumers": events_with_consumers
        },
        "services": all_services,
        "events": all_events,
        "event_flows": event_flows
    }

    output_file = "biopro-complete-inventory-with-consumers.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n[OK] Complete inventory saved to: {output_file}")

    # Show sample event flows
    print(f"\n[SAMPLE EVENT FLOWS]")
    sample_count = 0
    for event_name, flow in event_flows.items():
        if flow['publishers'] and flow['consumers']:
            publishers = ', '.join(flow['publishers'])
            consumers = ', '.join(flow['consumers'])
            print(f"  {event_name}")
            print(f"    Publishers: {publishers}")
            print(f"    Consumers: {consumers}")
            sample_count += 1
            if sample_count >= 10:
                break

    return output


if __name__ == "__main__":
    result = main()
