#!/usr/bin/env python3
"""
Architecture Validation Script

Validates that the project structure complies with the Engine/Fuel pattern:
- Layer 1: DATA (shared/)
- Layer 2: FUEL TRANSPORT (repository.py)
- Layer 3: ENGINE (engine.py, browser_engine.py)
- Layer 4: INTERFACES (interface.py)

Also checks:
- Logging setup
- Import patterns (no engine importing database)
- Configuration files
- Missing required files
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class ArchitectureValidator:
    """Validates project architecture against Engine/Fuel pattern"""

    def __init__(self, project_root: str = "/home/user/webcra"):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.shared_dir = self.project_root / "shared"
        self.pages_dir = self.project_root / "pages"

        self.issues = {
            'critical': [],
            'warning': [],
            'info': []
        }

        self.stats = {
            'services_checked': 0,
            'layer_violations': 0,
            'missing_files': 0,
            'correct_structure': 0
        }

    def validate(self):
        """Run all validation checks"""
        print(f"{BOLD}{'='*70}")
        print("ARCHITECTURE VALIDATION - Engine/Fuel Pattern")
        print(f"{'='*70}{RESET}\n")

        # Layer 1: Check shared structure
        self.validate_shared_layer()

        # Layer 2-4: Check each service
        self.validate_services()

        # Check for layer violations
        self.check_layer_violations()

        # Check UI structure
        self.validate_ui_structure()

        # Check logging setup
        self.validate_logging()

        # Generate report
        self.generate_report()

    def validate_shared_layer(self):
        """Validate Layer 1: DATA (shared/)"""
        print(f"{BLUE}[Layer 1: DATA - shared/]{RESET}")

        required_files = {
            'models.py': 'Data models (Visa, CrawledPage, GeneralContent, etc.)',
            'database.py': 'Database operations with versioning',
            'logger.py': 'Logging setup',
            'config_manager.py': 'Configuration management',
            'service_config.py': 'Service configuration loader'
        }

        for filename, description in required_files.items():
            filepath = self.shared_dir / filename
            if filepath.exists():
                print(f"  {GREEN}✓{RESET} {filename:30} - {description}")
            else:
                self.issues['critical'].append(f"Missing {filepath}")
                print(f"  {RED}✗{RESET} {filename:30} - MISSING")

        # Check for extraction schema
        schema_file = self.shared_dir / 'extraction_schema.py'
        if schema_file.exists():
            print(f"  {GREEN}✓{RESET} extraction_schema.py       - LLM extraction prompts")

        print()

    def validate_services(self):
        """Validate Layer 2-4: Services structure"""
        print(f"{BLUE}[Layer 2-4: SERVICES - Engine/Fuel Pattern]{RESET}\n")

        # Get all service directories
        services = [d for d in self.services_dir.iterdir()
                   if d.is_dir() and not d.name.startswith('__')]

        for service_dir in sorted(services):
            self.validate_service_structure(service_dir)
            self.stats['services_checked'] += 1

        print()

    def validate_service_structure(self, service_dir: Path):
        """Validate individual service structure"""
        service_name = service_dir.name
        print(f"  {BOLD}{service_name.upper()}{RESET}")

        required_files = {
            'repository.py': 'Layer 2: FUEL TRANSPORT',
            'engine.py': 'Layer 3: ENGINE',
            'interface.py': 'Layer 4: INTERFACES',
            'config.yaml': 'Configuration'
        }

        missing = []
        has_all = True

        for filename, layer in required_files.items():
            filepath = service_dir / filename
            if filepath.exists():
                print(f"    {GREEN}✓{RESET} {filename:20} - {layer}")
            else:
                print(f"    {YELLOW}⚠{RESET} {filename:20} - Missing (may be optional)")
                missing.append(filename)
                has_all = False
                self.stats['missing_files'] += 1

        # Check for alternate engines (like browser_engine.py)
        for py_file in service_dir.glob('*_engine.py'):
            if py_file.name != 'engine.py':
                print(f"    {GREEN}✓{RESET} {py_file.name:20} - Layer 3: ALTERNATE ENGINE")

        # Check for component directories
        components_dir = service_dir / 'components'
        if components_dir.exists():
            print(f"    {GREEN}✓{RESET} components/          - UI components")

        if has_all:
            self.stats['correct_structure'] += 1

        print()

    def check_layer_violations(self):
        """Check for layer violations (e.g., engine importing database)"""
        print(f"{BLUE}[Layer Violation Check]{RESET}\n")

        violations_found = 0

        # Check all engine files for direct database imports
        for service_dir in self.services_dir.iterdir():
            if not service_dir.is_dir() or service_dir.name.startswith('__'):
                continue

            # Check all engine files
            for engine_file in service_dir.glob('*engine.py'):
                violations = self.check_file_imports(engine_file)
                if violations:
                    violations_found += len(violations)
                    self.stats['layer_violations'] += len(violations)
                    print(f"  {RED}✗{RESET} {engine_file.relative_to(self.project_root)}")
                    for violation in violations:
                        print(f"    {YELLOW}⚠{RESET} {violation}")
                        self.issues['critical'].append(f"{engine_file.name}: {violation}")

        if violations_found == 0:
            print(f"  {GREEN}✓{RESET} No layer violations found! All engines use repository pattern.")

        print()

    def check_file_imports(self, filepath: Path) -> List[str]:
        """Check a file for improper imports"""
        violations = []

        try:
            content = filepath.read_text()

            # Check if engine directly imports Database
            if 'from shared.database import Database' in content:
                violations.append("Direct Database import (should use repository)")

            # Check if engine imports from interface
            if re.search(r'from \.interface import', content):
                violations.append("Engine importing from interface (wrong direction)")

        except Exception as e:
            self.issues['warning'].append(f"Could not read {filepath}: {e}")

        return violations

    def validate_ui_structure(self):
        """Validate UI/Pages structure"""
        print(f"{BLUE}[UI Structure - pages/]{RESET}\n")

        expected_pages = {
            '1_🕷️_Crawler.py': 'Context collection (Browser/Simple mode)',
            '2_📊_Classifier.py': 'Context extraction (Visa + General)',
            '3_🔍_Matcher.py': 'Visa scoring (optional)',
            '4_💬_Assistant.py': 'THE PRODUCT - Q&A interface',
            '5_⚙️_Settings.py': 'LLM configuration',
            '6_💾_Database.py': 'Context viewer'
        }

        for page_name, description in expected_pages.items():
            page_file = self.pages_dir / page_name
            if page_file.exists():
                print(f"  {GREEN}✓{RESET} {page_name:25} - {description}")
            else:
                print(f"  {YELLOW}⚠{RESET} {page_name:25} - Not found")
                self.issues['info'].append(f"Missing UI page: {page_name}")

        print()

    def validate_logging(self):
        """Check logging setup"""
        print(f"{BLUE}[Logging System]{RESET}\n")

        logger_file = self.shared_dir / 'logger.py'
        if logger_file.exists():
            print(f"  {GREEN}✓{RESET} shared/logger.py exists")

            # Check if services use logger
            services_with_logging = 0
            total_services = 0

            for service_dir in self.services_dir.iterdir():
                if not service_dir.is_dir() or service_dir.name.startswith('__'):
                    continue

                total_services += 1

                # Check engine files for logger usage
                for engine_file in service_dir.glob('*engine.py'):
                    content = engine_file.read_text()
                    if 'setup_logger' in content or 'self.logger' in content:
                        services_with_logging += 1
                        break

            print(f"  {GREEN}✓{RESET} {services_with_logging}/{total_services} services use logging")

            if services_with_logging < total_services:
                self.issues['warning'].append(
                    f"Only {services_with_logging}/{total_services} services use logging"
                )
        else:
            print(f"  {RED}✗{RESET} shared/logger.py not found")
            self.issues['critical'].append("Missing logger.py")

        print()

    def generate_report(self):
        """Generate final validation report"""
        print(f"\n{BOLD}{'='*70}")
        print("VALIDATION REPORT")
        print(f"{'='*70}{RESET}\n")

        # Statistics
        print(f"{BOLD}Statistics:{RESET}")
        print(f"  Services checked:      {self.stats['services_checked']}")
        print(f"  Correct structure:     {self.stats['correct_structure']}")
        print(f"  Missing files:         {self.stats['missing_files']}")
        print(f"  Layer violations:      {self.stats['layer_violations']}")
        print()

        # Issues summary
        total_issues = (len(self.issues['critical']) +
                       len(self.issues['warning']) +
                       len(self.issues['info']))

        if total_issues == 0:
            print(f"{GREEN}{BOLD}✓ EXCELLENT! No architecture issues found.{RESET}")
            print(f"{GREEN}  Project structure perfectly follows Engine/Fuel pattern.{RESET}")
            return

        # Critical issues
        if self.issues['critical']:
            print(f"{RED}{BOLD}Critical Issues ({len(self.issues['critical'])}):  {RESET}")
            for issue in self.issues['critical']:
                print(f"  {RED}✗{RESET} {issue}")
            print()

        # Warnings
        if self.issues['warning']:
            print(f"{YELLOW}{BOLD}Warnings ({len(self.issues['warning'])}):  {RESET}")
            for issue in self.issues['warning']:
                print(f"  {YELLOW}⚠{RESET} {issue}")
            print()

        # Info
        if self.issues['info']:
            print(f"{BLUE}{BOLD}Info ({len(self.issues['info'])}):  {RESET}")
            for issue in self.issues['info']:
                print(f"  {BLUE}ℹ{RESET} {issue}")
            print()

        # Overall status
        print(f"\n{BOLD}Overall Status:{RESET}")
        if not self.issues['critical']:
            if not self.issues['warning']:
                print(f"{GREEN}✓ PASS - Architecture is compliant{RESET}")
            else:
                print(f"{YELLOW}⚠ PASS (with warnings) - Minor issues found{RESET}")
        else:
            print(f"{RED}✗ FAIL - Critical issues must be fixed{RESET}")


if __name__ == "__main__":
    validator = ArchitectureValidator()
    validator.validate()
