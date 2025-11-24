#!/usr/bin/env python3
"""
Comprehensive BioPro Manufacturing Event Schema Extractor
Analyzes all 13 manufacturing services and extracts complete event information
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict

@dataclass
class EventField:
    """Represents a field in an event payload"""
    name: str
    type: str
    description: str = ""
    required: bool = False
    example: str = ""

@dataclass
class EventSchema:
    """Represents a complete event schema"""
    service: str
    event_name: str
    event_type: str
    version: str
    payload_class: str
    purpose: str = ""
    fields: List[EventField] = field(default_factory=list)
    file_path: str = ""
    topic_name: str = ""
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

class BioproEventExtractor:
    """Extracts event schemas from BioPro manufacturing services"""

    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.services = [
            'apheresisplasma', 'apheresisplatelet', 'apheresisrbc',
            'checkin', 'discard', 'labeling', 'licensing', 'pooling',
            'productmodification', 'qualitycontrol', 'quarantine',
            'storage', 'wholeblood'
        ]
        self.events: List[EventSchema] = []
        self.stats = defaultdict(int)

    def extract_all(self):
        """Extract events from all services"""
        print("=" * 80)
        print("BIOPRO MANUFACTURING EVENT SCHEMA EXTRACTION")
        print("=" * 80)
        print(f"\nBackend Path: {self.backend_path}")
        print(f"Services to analyze: {len(self.services)}")
        print()

        for service in self.services:
            print(f"\n{'=' * 80}")
            print(f"Analyzing Service: {service.upper()}")
            print('=' * 80)
            self.extract_service_events(service)

        self.print_summary()
        self.save_results()

    def extract_service_events(self, service: str):
        """Extract all events from a specific service"""
        service_path = self.backend_path / service
        if not service_path.exists():
            print(f"  [ERROR] Service directory not found: {service_path}")
            return

        # Find domain event directory
        domain_event_path = service_path / "src/main/java/com/arcone/biopro/manufacturing" / service / "domain/event"

        if not domain_event_path.exists():
            print(f"  [WARN] No domain/event directory found")
            self.stats[f'{service}_no_events'] += 1
            return

        # Find all event files (exclude base classes)
        event_files = list(domain_event_path.glob("*Event.java"))
        exclude_files = {'Event.java', 'EventKey.java', 'package-info.java'}
        event_files = [f for f in event_files if f.name not in exclude_files]

        print(f"  Found {len(event_files)} event definitions")

        for event_file in event_files:
            event = self.extract_event_from_file(service, event_file)
            if event:
                self.events.append(event)
                print(f"    [OK] {event.event_name}")
                self.stats['total_events'] += 1

        # Also check for events in other locations (infrastructure, adapter)
        self.check_additional_event_locations(service, service_path)

    def extract_event_from_file(self, service: str, file_path: Path) -> EventSchema:
        """Extract event schema from a Java file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract class name
            class_match = re.search(r'public class (\w+Event)', content)
            if not class_match:
                return None
            event_name = class_match.group(1)

            # Extract event type from EventType enum reference
            event_type_match = re.search(r'EventType\.(\w+)\(\)', content)
            event_type = event_type_match.group(1) if event_type_match else event_name

            # Extract version
            version_match = re.search(r'EventVersion\.VERSION_(\d+_\d+)\(\)', content)
            version = version_match.group(1).replace('_', '.') if version_match else "1.0"

            # Extract payload class
            payload_match = re.search(r'extends Event<(\w+)>', content)
            payload_class = payload_match.group(1) if payload_match else "Unknown"

            # Extract JavaDoc for purpose
            javadoc_match = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
            purpose = ""
            if javadoc_match:
                javadoc = javadoc_match.group(1)
                purpose = ' '.join(line.strip().lstrip('*').strip() for line in javadoc.split('\n') if line.strip())

            event = EventSchema(
                service=service,
                event_name=event_name,
                event_type=event_type,
                version=version,
                payload_class=payload_class,
                purpose=purpose,
                file_path=str(file_path)
            )

            # Try to extract payload fields
            if payload_class != "Unknown":
                self.extract_payload_fields(service, payload_class, event, file_path)

            return event

        except Exception as e:
            print(f"    [WARN] Error extracting {file_path.name}: {e}")
            return None

    def extract_payload_fields(self, service: str, payload_class: str, event: EventSchema, event_file: Path):
        """Extract fields from the payload class"""
        # Find payload file
        payload_path = event_file.parent / "payload" / f"{payload_class}.java"

        if not payload_path.exists():
            return

        try:
            content = payload_path.read_text(encoding='utf-8')

            # Look for record definition
            record_match = re.search(r'public record ' + payload_class + r'\s*\((.*?)\)', content, re.DOTALL)
            if not record_match:
                # Try to find class definition with fields
                return

            record_params = record_match.group(1)

            # Parse fields from record parameters
            # This is complex due to annotations, so we'll do a simpler extraction
            lines = record_params.split('\n')
            current_field = {}

            for line in lines:
                line = line.strip()

                # Extract @Schema annotations
                schema_name_match = re.search(r'name\s*=\s*"([^"]+)"', line)
                if schema_name_match:
                    current_field['name'] = schema_name_match.group(1)

                schema_desc_match = re.search(r'description\s*=\s*"([^"]+)"', line)
                if schema_desc_match:
                    current_field['description'] = schema_desc_match.group(1)

                schema_example_match = re.search(r'example\s*=\s*"([^"]+)"', line)
                if schema_example_match:
                    current_field['example'] = schema_example_match.group(1)

                schema_required_match = re.search(r'requiredMode\s*=\s*REQUIRED', line)
                if schema_required_match:
                    current_field['required'] = True

                # Check if this is the actual field declaration
                # Format: Type fieldName
                field_decl_match = re.search(r'^\s*([A-Z][\w<>,\s]+)\s+(\w+)\s*[,)]', line)
                if field_decl_match:
                    field_type = field_decl_match.group(1).strip()
                    field_name = field_decl_match.group(2)

                    # Create EventField
                    event_field = EventField(
                        name=current_field.get('name', field_name),
                        type=field_type,
                        description=current_field.get('description', ''),
                        required=current_field.get('required', False),
                        example=current_field.get('example', '')
                    )
                    event.fields.append(event_field)
                    current_field = {}

        except Exception as e:
            print(f"      [WARN] Could not extract fields from {payload_class}: {e}")

    def check_additional_event_locations(self, service: str, service_path: Path):
        """Check for events in infrastructure and adapter packages"""
        # Check infrastructure/event
        infra_event_path = service_path / "src/main/java/com/arcone/biopro/manufacturing" / service / "infrastructure/event"
        if infra_event_path.exists():
            event_files = list(infra_event_path.glob("*Event.java"))
            if event_files:
                print(f"  Found {len(event_files)} additional events in infrastructure/event")

        # Check adapter/output/producer/event
        adapter_event_path = service_path / "src/main/java/com/arcone/biopro/manufacturing" / service / "adapter/output/producer/event"
        if adapter_event_path.exists():
            event_files = list(adapter_event_path.glob("*.java"))
            if event_files:
                print(f"  Found {len(event_files)} files in adapter/output/producer/event")

    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "=" * 80)
        print("EXTRACTION SUMMARY")
        print("=" * 80)
        print(f"\nTotal Events Extracted: {self.stats['total_events']}")
        print(f"Services Analyzed: {len(self.services)}")

        # Group by service
        events_by_service = defaultdict(list)
        for event in self.events:
            events_by_service[event.service].append(event)

        print(f"\nEvents per Service:")
        for service in sorted(events_by_service.keys()):
            count = len(events_by_service[service])
            print(f"  {service:25} {count:3} events")

        # Count unique event types
        unique_types = set(event.event_type for event in self.events)
        print(f"\nUnique Event Types: {len(unique_types)}")

    def save_results(self):
        """Save extraction results to files"""
        output_dir = Path("C:/Users/MelvinJones/work/event-governance/poc")

        # Save as JSON
        json_file = output_dir / "biopro-events-inventory.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([event.to_dict() for event in self.events], f, indent=2)
        print(f"\n[OK] Saved JSON inventory to: {json_file}")

        # Save as detailed markdown report
        md_file = output_dir / "BIOPRO-EVENTS-COMPREHENSIVE-INVENTORY.md"
        self.generate_markdown_report(md_file)
        print(f"[OK] Saved Markdown report to: {md_file}")

    def generate_markdown_report(self, output_file: Path):
        """Generate comprehensive markdown report"""
        events_by_service = defaultdict(list)
        for event in self.events:
            events_by_service[event.service].append(event)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# BioPro Manufacturing Services - Comprehensive Event Inventory\n\n")
            f.write(f"**Generated:** {Path(__file__).name}\n\n")
            f.write(f"**Total Events:** {len(self.events)}\n\n")
            f.write(f"**Services Analyzed:** {len(self.services)}\n\n")

            # Table of Contents
            f.write("## Table of Contents\n\n")
            for service in sorted(events_by_service.keys()):
                count = len(events_by_service[service])
                f.write(f"- [{service}](#{service}) ({count} events)\n")
            f.write("\n---\n\n")

            # Detailed service sections
            for service in sorted(events_by_service.keys()):
                events = sorted(events_by_service[service], key=lambda e: e.event_name)

                f.write(f"## {service}\n\n")
                f.write(f"**Total Events:** {len(events)}\n\n")

                for event in events:
                    f.write(f"### {event.event_name}\n\n")
                    f.write(f"**Event Type:** `{event.event_type}`\n\n")
                    f.write(f"**Version:** {event.version}\n\n")
                    f.write(f"**Payload Class:** `{event.payload_class}`\n\n")

                    if event.purpose:
                        f.write(f"**Purpose:** {event.purpose}\n\n")

                    f.write(f"**Schema Location:** `{event.file_path}`\n\n")

                    if event.fields:
                        f.write("**Key Fields:**\n\n")
                        f.write("| Field | Type | Required | Description |\n")
                        f.write("|-------|------|----------|-------------|\n")
                        for field in event.fields:
                            req = "Yes" if field.required else "No"
                            desc = field.description or field.example or "-"
                            f.write(f"| {field.name} | {field.type} | {req} | {desc} |\n")
                        f.write("\n")

                    f.write("---\n\n")

            # Summary statistics
            f.write("## Summary Statistics\n\n")
            f.write("### Events by Service\n\n")
            f.write("| Service | Event Count |\n")
            f.write("|---------|-------------|\n")
            for service in sorted(events_by_service.keys()):
                count = len(events_by_service[service])
                f.write(f"| {service} | {count} |\n")
            f.write(f"| **TOTAL** | **{len(self.events)}** |\n\n")

            # Event types
            f.write("### All Event Types\n\n")
            event_types = sorted(set(event.event_type for event in self.events))
            for et in event_types:
                services_with_event = [e.service for e in self.events if e.event_type == et]
                f.write(f"- `{et}` (used in: {', '.join(set(services_with_event))})\n")

def main():
    backend_path = "C:/Users/MelvinJones/work/biopro/biopro-manufacturing/backend"

    if not Path(backend_path).exists():
        print(f"Error: Backend path does not exist: {backend_path}")
        return 1

    extractor = BioproEventExtractor(backend_path)
    extractor.extract_all()

    return 0

if __name__ == "__main__":
    exit(main())
