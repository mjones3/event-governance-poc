#!/usr/bin/env python3
"""
Comprehensive BioPro Repository Analysis Script
Extracts ALL events, services, and relationships from 4 BioPro repositories
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict

# Repository configurations
REPOSITORIES = {
    "biopro-interface": {
        "path": "C:/Users/MelvinJones/work/biopro/biopro-interface",
        "services": ["collections"]
    },
    "biopro-distribution": {
        "path": "C:/Users/MelvinJones/work/biopro/biopro-distribution",
        "services": ["customer", "eventbridge", "inventory", "irradiation", "order",
                    "partnerorderprovider", "receiving", "recoveredplasmashipping", "shipping"]
    },
    "biopro-donor": {
        "path": "C:/Users/MelvinJones/work/biopro/biopro-donor",
        "services": ["eventmanagement", "history", "notification", "testresultmanagement"]
    },
    "biopro-operations": {
        "path": "C:/Users/MelvinJones/work/biopro/biopro-operations",
        "services": ["device", "research", "role", "supply"]
    }
}

class JavaEventExtractor:
    """Extracts event information from Java files"""

    def __init__(self):
        self.events = []
        self.listeners = []
        self.producers = []

    def extract_class_name(self, content: str, filepath: str) -> str:
        """Extract class name from Java file"""
        match = re.search(r'public\s+class\s+(\w+)', content)
        if match:
            return match.group(1)
        return Path(filepath).stem

    def extract_fields(self, content: str) -> List[Dict]:
        """Extract field definitions from Java class"""
        fields = []
        # Match private/protected/public fields
        field_pattern = r'(?:private|protected|public)\s+(\w+(?:<[\w\s,<>]+>)?)\s+(\w+);'
        for match in re.finditer(field_pattern, content):
            field_type = match.group(1)
            field_name = match.group(2)
            fields.append({
                "name": field_name,
                "type": field_type
            })
        return fields

    def extract_kafka_topic(self, content: str) -> str:
        """Extract Kafka topic from producer/listener"""
        # Look for @KafkaListener(topics = ...)
        match = re.search(r'@KafkaListener\s*\(\s*topics\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)

        # Look for KafkaTemplate.send(topic, ...)
        match = re.search(r'kafkaTemplate\.send\s*\(\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)

        # Look for topic property references
        match = re.search(r'topics\s*=\s*"\$\{([^}]+)\}"', content)
        if match:
            return match.group(1)

        return None

    def extract_event_type(self, content: str, class_name: str) -> str:
        """Determine event type from class content"""
        if 'Event' not in class_name:
            return "unknown"

        # Common event type patterns
        if 'Created' in class_name:
            return "CREATED"
        elif 'Updated' in class_name or 'Modified' in class_name:
            return "UPDATED"
        elif 'Deleted' in class_name or 'Removed' in class_name:
            return "DELETED"
        elif 'Cancelled' in class_name:
            return "CANCELLED"
        elif 'Completed' in class_name:
            return "COMPLETED"
        elif 'Received' in class_name:
            return "RECEIVED"
        elif 'Assigned' in class_name:
            return "ASSIGNED"
        elif 'Quarantine' in class_name:
            return "QUARANTINE"
        elif 'Unsuitable' in class_name:
            return "UNSUITABLE"
        else:
            return "DOMAIN_EVENT"

    def is_event_file(self, filepath: str) -> bool:
        """Check if file is an event definition"""
        filename = Path(filepath).name
        # Event files typically have 'Event' in the name
        if 'Event' in filename and filename.endswith('.java'):
            # Exclude test files
            if 'Test' not in filename and '/test/' not in filepath:
                # Exclude abstract/base event classes (we want concrete events)
                if not any(x in filename for x in ['AbstractEvent', 'DomainEvent', 'EventMessage']):
                    return True
        return False

    def is_listener_file(self, filepath: str) -> bool:
        """Check if file is an event listener/consumer"""
        filename = Path(filepath).name
        return 'Listener' in filename and filename.endswith('.java') and '/test/' not in filepath

    def is_producer_file(self, filepath: str) -> bool:
        """Check if file is an event producer/publisher"""
        filename = Path(filepath).name
        return ('Producer' in filename or 'Publisher' in filename) and filename.endswith('.java') and '/test/' not in filepath

class ServiceAnalyzer:
    """Analyzes a single microservice"""

    def __init__(self, repo_name: str, service_name: str, service_path: str):
        self.repo_name = repo_name
        self.service_name = service_name
        self.service_path = service_path
        self.extractor = JavaEventExtractor()

        self.published_events = []
        self.consumed_events = []
        self.event_details = []

    def analyze(self) -> Dict:
        """Analyze the service"""
        print(f"  Analyzing {self.service_name}...")

        # Find all Java files
        java_files = list(Path(self.service_path).rglob("*.java"))

        # Process event files
        for jfile in java_files:
            try:
                content = jfile.read_text(encoding='utf-8', errors='ignore')
                filepath = str(jfile)

                if self.extractor.is_event_file(filepath):
                    self._process_event_file(filepath, content)
                elif self.extractor.is_listener_file(filepath):
                    self._process_listener_file(filepath, content)
                elif self.extractor.is_producer_file(filepath):
                    self._process_producer_file(filepath, content)
            except Exception as e:
                print(f"    Warning: Could not process {jfile}: {e}")

        return self._build_service_info()

    def _process_event_file(self, filepath: str, content: str):
        """Process an event definition file"""
        class_name = self.extractor.extract_class_name(content, filepath)

        # Only process actual event classes (not DTOs or mappers)
        if not class_name.endswith('Event'):
            return

        event_type = self.extractor.extract_event_type(content, class_name)
        fields = self.extractor.extract_fields(content)

        # Determine if this is published or consumed by checking file location
        is_outbound = 'output' in filepath or 'producer' in filepath.lower() or 'outbound' in filepath.lower()
        is_inbound = 'input' in filepath or 'listener' in filepath.lower() or 'consumer' in filepath.lower() or 'inbound' in filepath.lower()

        event_info = {
            "name": class_name,
            "type": event_type,
            "version": "1.0",  # Default, would need to parse actual version if available
            "fields": fields,
            "file_path": filepath,
            "direction": "outbound" if is_outbound else ("inbound" if is_inbound else "unknown")
        }

        self.event_details.append(event_info)

        if is_outbound:
            self.published_events.append(class_name)
        elif is_inbound:
            self.consumed_events.append(class_name)

    def _process_listener_file(self, filepath: str, content: str):
        """Process an event listener file"""
        class_name = self.extractor.extract_class_name(content, filepath)
        topic = self.extractor.extract_kafka_topic(content)

        # Extract consumed event names from the listener
        # Look for event type in method parameters
        event_pattern = r'public\s+void\s+\w+\s*\([^)]*?(\w+Event)[^)]*\)'
        for match in re.finditer(event_pattern, content):
            event_name = match.group(1)
            if event_name not in self.consumed_events:
                self.consumed_events.append(event_name)

    def _process_producer_file(self, filepath: str, content: str):
        """Process an event producer file"""
        class_name = self.extractor.extract_class_name(content, filepath)
        topic = self.extractor.extract_kafka_topic(content)

        # Extract produced event names
        # Look for kafkaTemplate.send or event publishing patterns
        event_pattern = r'kafkaTemplate\.send\s*\([^,]*,\s*(\w+Event)'
        for match in re.finditer(event_pattern, content):
            event_name = match.group(1)
            if event_name not in self.published_events:
                self.published_events.append(event_name)

    def _build_service_info(self) -> Dict:
        """Build service information dictionary"""
        return {
            "name": self.service_name,
            "repository": self.repo_name,
            "purpose": self._infer_purpose(),
            "publishes": sorted(list(set(self.published_events))),
            "consumes": sorted(list(set(self.consumed_events))),
            "events": self.event_details
        }

    def _infer_purpose(self) -> str:
        """Infer service purpose from name"""
        purposes = {
            "collections": "Manages blood collection interfaces and donation processing",
            "customer": "Manages customer information and relationships",
            "eventbridge": "Bridges events between distribution services",
            "inventory": "Manages blood product inventory",
            "irradiation": "Manages blood product irradiation processing",
            "order": "Manages blood product orders",
            "partnerorderprovider": "Provides partner order integration",
            "receiving": "Manages receiving of blood products",
            "recoveredplasmashipping": "Manages recovered plasma shipping",
            "shipping": "Manages blood product shipping",
            "eventmanagement": "Manages donor events and incidents",
            "history": "Manages donor history",
            "notification": "Manages notifications",
            "testresultmanagement": "Manages test results",
            "device": "Manages medical devices",
            "research": "Manages research operations",
            "role": "Manages user roles and permissions",
            "supply": "Manages medical supplies"
        }
        return purposes.get(self.service_name, f"Manages {self.service_name} operations")

class RepositoryAnalyzer:
    """Analyzes a complete repository"""

    def __init__(self, repo_name: str, repo_config: Dict):
        self.repo_name = repo_name
        self.repo_config = repo_config
        self.services = []

    def analyze(self) -> Dict:
        """Analyze the entire repository"""
        print(f"\nAnalyzing repository: {self.repo_name}")

        repo_path = Path(self.repo_config['path'])
        if not repo_path.exists():
            print(f"  Warning: Repository path does not exist: {repo_path}")
            return {"name": self.repo_name, "services": []}

        for service_name in self.repo_config['services']:
            service_path = repo_path / "backend" / service_name
            if service_path.exists():
                analyzer = ServiceAnalyzer(self.repo_name, service_name, str(service_path))
                service_info = analyzer.analyze()
                self.services.append(service_info)
            else:
                print(f"  Warning: Service path not found: {service_path}")

        return {
            "name": self.repo_name,
            "path": str(repo_path),
            "services": self.services
        }

class EventFlowMapper:
    """Maps event flows between services"""

    def __init__(self, repositories: List[Dict]):
        self.repositories = repositories
        self.event_flows = []

    def map_flows(self) -> List[Dict]:
        """Map all event flows"""
        print("\nMapping event flows...")

        # Build event name to service mapping
        event_publishers = defaultdict(list)
        event_consumers = defaultdict(list)

        for repo in self.repositories:
            for service in repo['services']:
                service_id = f"{repo['name']}/{service['name']}"

                for event_name in service['publishes']:
                    event_publishers[event_name].append(service_id)

                for event_name in service['consumes']:
                    event_consumers[event_name].append(service_id)

        # Create flow mappings
        all_events = set(event_publishers.keys()) | set(event_consumers.keys())

        for event_name in sorted(all_events):
            publishers = event_publishers.get(event_name, [])
            consumers = event_consumers.get(event_name, [])

            self.event_flows.append({
                "event": event_name,
                "publishers": publishers,
                "consumers": consumers,
                "is_orphaned": len(publishers) == 0 or len(consumers) == 0
            })

        return self.event_flows

def main():
    """Main analysis function"""
    print("BioPro Comprehensive Repository Analysis")
    print("=" * 80)

    # Analyze all repositories
    all_repositories = []
    for repo_name, repo_config in REPOSITORIES.items():
        analyzer = RepositoryAnalyzer(repo_name, repo_config)
        repo_info = analyzer.analyze()
        all_repositories.append(repo_info)

    # Map event flows
    flow_mapper = EventFlowMapper(all_repositories)
    event_flows = flow_mapper.map_flows()

    # Build comprehensive inventory
    inventory = {
        "analysis_date": "2025-11-16",
        "repositories": all_repositories,
        "event_flows": event_flows,
        "summary": {
            "total_repositories": len(all_repositories),
            "total_services": sum(len(r['services']) for r in all_repositories),
            "total_events": len(event_flows),
            "orphaned_events": len([f for f in event_flows if f['is_orphaned']])
        }
    }

    # Save JSON inventory
    json_file = "C:/Users/MelvinJones/work/event-governance/poc/BIOPRO-COMPLETE-INVENTORY.json"
    with open(json_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"\nJSON inventory saved to: {json_file}")

    # Generate markdown report
    generate_markdown_report(inventory)

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Repositories analyzed: {inventory['summary']['total_repositories']}")
    print(f"Services discovered: {inventory['summary']['total_services']}")
    print(f"Events discovered: {inventory['summary']['total_events']}")
    print(f"Orphaned events: {inventory['summary']['orphaned_events']}")
    print("\nOrphaned events (no publisher or no consumer):")
    for flow in event_flows:
        if flow['is_orphaned']:
            pub = ', '.join(flow['publishers']) if flow['publishers'] else 'NONE'
            con = ', '.join(flow['consumers']) if flow['consumers'] else 'NONE'
            print(f"  - {flow['event']}")
            print(f"    Publishers: {pub}")
            print(f"    Consumers: {con}")

def generate_markdown_report(inventory: Dict):
    """Generate human-readable markdown report"""
    md_file = "C:/Users/MelvinJones/work/event-governance/poc/BIOPRO-COMPLETE-ANALYSIS.md"

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# BioPro Complete Repository Analysis\n\n")
        f.write(f"**Analysis Date:** {inventory['analysis_date']}\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"- **Repositories Analyzed:** {inventory['summary']['total_repositories']}\n")
        f.write(f"- **Services Discovered:** {inventory['summary']['total_services']}\n")
        f.write(f"- **Events Discovered:** {inventory['summary']['total_events']}\n")
        f.write(f"- **Orphaned Events:** {inventory['summary']['orphaned_events']}\n\n")

        f.write("## Repository Overview\n\n")
        for repo in inventory['repositories']:
            f.write(f"### {repo['name']}\n\n")
            f.write(f"**Path:** `{repo.get('path', 'N/A')}`\n\n")
            f.write(f"**Services:** {len(repo['services'])}\n\n")

            for service in repo['services']:
                f.write(f"#### {service['name']}\n\n")
                f.write(f"**Purpose:** {service['purpose']}\n\n")
                f.write(f"**Publishes:** {len(service['publishes'])} events\n\n")
                if service['publishes']:
                    for event in service['publishes']:
                        f.write(f"- {event}\n")
                    f.write("\n")

                f.write(f"**Consumes:** {len(service['consumes'])} events\n\n")
                if service['consumes']:
                    for event in service['consumes']:
                        f.write(f"- {event}\n")
                    f.write("\n")

                if service['events']:
                    f.write(f"**Event Details:**\n\n")
                    for event in service['events']:
                        f.write(f"##### {event['name']}\n\n")
                        f.write(f"- **Type:** {event['type']}\n")
                        f.write(f"- **Version:** {event['version']}\n")
                        f.write(f"- **Direction:** {event['direction']}\n")
                        if event['fields']:
                            f.write(f"- **Fields:** {len(event['fields'])}\n")
                            for field in event['fields'][:10]:  # Limit to first 10 fields
                                f.write(f"  - `{field['name']}`: {field['type']}\n")
                            if len(event['fields']) > 10:
                                f.write(f"  - ... and {len(event['fields']) - 10} more fields\n")
                        f.write("\n")
                f.write("\n")

        f.write("## Event Flows\n\n")
        f.write("This section maps all event flows between services.\n\n")

        for flow in inventory['event_flows']:
            f.write(f"### {flow['event']}\n\n")

            if flow['publishers']:
                f.write(f"**Publishers:**\n\n")
                for pub in flow['publishers']:
                    f.write(f"- {pub}\n")
                f.write("\n")
            else:
                f.write(f"**Publishers:** NONE ⚠️\n\n")

            if flow['consumers']:
                f.write(f"**Consumers:**\n\n")
                for con in flow['consumers']:
                    f.write(f"- {con}\n")
                f.write("\n")
            else:
                f.write(f"**Consumers:** NONE ⚠️\n\n")

            if flow['is_orphaned']:
                f.write("⚠️ **WARNING: This is an orphaned event (missing publisher or consumer)**\n\n")

        f.write("## Orphaned Events Report\n\n")
        orphaned = [f for f in inventory['event_flows'] if f['is_orphaned']]
        if orphaned:
            f.write(f"Found {len(orphaned)} orphaned events that need attention:\n\n")
            for flow in orphaned:
                f.write(f"### {flow['event']}\n\n")
                pub = ', '.join(flow['publishers']) if flow['publishers'] else 'NONE'
                con = ', '.join(flow['consumers']) if flow['consumers'] else 'NONE'
                f.write(f"- Publishers: {pub}\n")
                f.write(f"- Consumers: {con}\n\n")
        else:
            f.write("No orphaned events found. All events have both publishers and consumers.\n\n")

    print(f"Markdown report saved to: {md_file}")

if __name__ == "__main__":
    main()
