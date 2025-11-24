#!/usr/bin/env python3
"""
Complete BioPro Event Extraction Across All Repositories

Extracts events from:
- biopro-interface (collections)
- biopro-distribution (customer, eventbridge, inventory, irradiation, order, partnerorderprovider, receiving, recoveredplasmashipping, shipping)
- biopro-donor (eventmanagement, history, notification, testresultmanagement)
- biopro-operations (device, research, role, supply)
- biopro-manufacturing (already done - 13 services)
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

# Repository configurations
REPOS = [
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

    # Look for domain/event directories
    for root, dirs, files in os.walk(service_path):
        if 'domain' in root and 'event' in root:
            for file in files:
                if file.endswith('Event.java'):
                    event_files.append(os.path.join(root, file))

    return event_files

def find_kafka_listeners(service_path: str) -> List[str]:
    """Find all Kafka listener files to identify consumers"""
    listener_files = []

    for root, dirs, files in os.walk(service_path):
        if 'listener' in root.lower() or 'consumer' in root.lower():
            for file in files:
                if file.endswith('.java'):
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
        print(f"Error processing {file_path}: {e}")
        return None

def extract_kafka_consumers(file_path: str) -> List[Dict[str, str]]:
    """Extract Kafka consumer information"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        consumers = []

        # Find @KafkaListener annotations
        listener_pattern = r'@KafkaListener\s*\([^)]+topics\s*=\s*["\']([^"\']+)["\'][^)]*\)[^{]*public\s+void\s+(\w+)\s*\([^)]*(\w+Event)'

        for match in re.finditer(listener_pattern, content):
            topic = match.group(1)
            method = match.group(2)
            event_type = match.group(3)

            consumers.append({
                "topic": topic,
                "event": event_type,
                "method": method,
                "file": file_path
            })

        return consumers
    except Exception as e:
        print(f"Error processing listener {file_path}: {e}")
        return []

def main():
    print("="* 80)
    print("BioPro Complete Event Extraction")
    print("="* 80)

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
            print(f"      Found {len(event_files)} event files")

            # Find listeners
            listener_files = find_kafka_listeners(service_path)
            print(f"      Found {len(listener_files)} listener files")

            # Extract event details
            service_events = []
            for event_file in event_files:
                event_info = extract_event_info(event_file)
                if event_info:
                    event_info['service'] = service_name
                    event_info['repository'] = repo['name']
                    service_events.append(event_info)
                    all_events.append(event_info)

            # Extract consumer information
            service_consumers = []
            for listener_file in listener_files:
                consumers = extract_kafka_consumers(listener_file)
                service_consumers.extend(consumers)

            # Build service record
            service_record = {
                "name": service_name,
                "repository": repo['name'],
                "events_published": len(service_events),
                "events_consumed": len(service_consumers),
                "published_events": [e['name'] for e in service_events],
                "consumed_events": [c['event'] for c in service_consumers],
                "event_details": service_events,
                "consumer_details": service_consumers
            }

            all_services.append(service_record)

            # Track event flows
            for event in service_events:
                if event['name'] not in event_flows:
                    event_flows[event['name']] = {
                        "publishers": [],
                        "consumers": []
                    }
                event_flows[event['name']]['publishers'].append(service_name)

            for consumer in service_consumers:
                event_name = consumer['event']
                if event_name not in event_flows:
                    event_flows[event_name] = {
                        "publishers": [],
                        "consumers": []
                    }
                event_flows[event_name]['consumers'].append(service_name)

            print(f"       [OK] Published: {len(service_events)} events")
            print(f"       [OK] Consumes: {len(service_consumers)} events")

    # Generate summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total Repositories: {len(REPOS)}")
    print(f"Total Services: {len(all_services)}")
    print(f"Total Events: {len(all_events)}")
    print(f"Total Event Flows: {len(event_flows)}")

    # Save results
    output = {
        "summary": {
            "repositories": len(REPOS),
            "services": len(all_services),
            "events": len(all_events),
            "event_flows": len(event_flows)
        },
        "services": all_services,
        "events": all_events,
        "event_flows": event_flows
    }

    output_file = "biopro-complete-inventory.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n[OK] Complete inventory saved to: {output_file}")

    # Generate markdown report
    generate_markdown_report(all_services, all_events, event_flows)

    return output

def generate_markdown_report(services, events, event_flows):
    """Generate human-readable markdown report"""

    report = f"""# BioPro Complete Event Analysis Report

## Executive Summary

- **Total Services**: {len(services)}
- **Total Events**: {len(events)}
- **Event Flows Mapped**: {len(event_flows)}

## Services by Repository

"""

    # Group by repository
    repos = {}
    for service in services:
        repo = service['repository']
        if repo not in repos:
            repos[repo] = []
        repos[repo].append(service)

    for repo_name, repo_services in sorted(repos.items()):
        report += f"### {repo_name}\n\n"
        report += f"| Service | Published | Consumed |\n"
        report += f"|---------|-----------|----------|\n"
        for svc in repo_services:
            report += f"| {svc['name']} | {svc['events_published']} | {svc['events_consumed']} |\n"
        report += "\n"

    report += "## Event Flows\n\n"
    report += "### Complete Event Choreography\n\n"

    for event_name, flow in sorted(event_flows.items()):
        publishers = flow['publishers'] or ['Unknown']
        consumers = flow['consumers'] or ['None']
        report += f"**{event_name}**\n"
        report += f"- Publishers: {', '.join(publishers)}\n"
        report += f"- Consumers: {', '.join(consumers)}\n\n"

    report += "## All Events\n\n"
    report += "| Event Name | Service | Repository | Fields |\n"
    report += "|------------|---------|------------|--------|\n"

    for event in sorted(events, key=lambda x: x['name']):
        report += f"| {event['name']} | {event['service']} | {event['repository']} | {len(event['fields'])} |\n"

    with open('BIOPRO-COMPLETE-ANALYSIS.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[OK] Analysis report saved to: BIOPRO-COMPLETE-ANALYSIS.md")

if __name__ == "__main__":
    result = main()
