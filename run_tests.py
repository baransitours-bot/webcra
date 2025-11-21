#!/usr/bin/env python3
"""
Enhanced Test Runner with Logging

Runs comprehensive test suite for Immigration Assistant System with:
- Structured logging to file
- Test classification (unit/integration/e2e/manual)
- Performance metrics
- Coverage reports
- Failure tracking

Usage:
    python run_tests.py --all                    # Run all automated tests
    python run_tests.py --suite unit             # Run unit tests only
    python run_tests.py --suite integration      # Run integration tests
    python run_tests.py --suite e2e              # Run end-to-end tests
    python run_tests.py --coverage               # Run with coverage report
    python run_tests.py --log-level DEBUG        # Set log level
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.logger import setup_logger

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class TestRunner:
    """Enhanced test runner with logging and metrics"""

    def __init__(self, log_level='INFO'):
        """Initialize test runner"""
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / 'tests'
        self.log_dir = self.project_root / 'logs'
        self.log_dir.mkdir(exist_ok=True)

        # Setup logger
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f'test_run_{timestamp}.log'

        self.logger = setup_logger(
            'test_runner',
            log_file=str(self.log_file)
        )

        self.logger.info("=" * 70)
        self.logger.info("STARTING TEST RUN")
        self.logger.info(f"Timestamp: {datetime.now()}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("=" * 70)

        # Test results
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'duration': 0.0
        }

        # Test suites
        self.suites = {
            'unit': [
                'test_config_manager.py',
                'test_logger_unicode.py',
                'test_error_handling.py'
            ],
            'integration': [
                'test_integration.py',
                'test_crawler_service.py'
            ],
            'e2e': [
                'test_e2e_workflows.py'
            ],
            'service': [
                'test_crawler.py',
                'test_classifier.py',
                'test_matcher.py',
                'test_assistant.py'
            ]
        }

    def run_all_tests(self, coverage=False):
        """Run all automated test suites"""
        print(f"{BOLD}{'=' * 70}")
        print("RUNNING ALL AUTOMATED TESTS")
        print(f"{'=' * 70}{RESET}\n")

        self.logger.info("Running all automated test suites")

        start_time = datetime.now()

        # Run each suite
        for suite_name in ['unit', 'integration', 'service', 'e2e']:
            self.run_suite(suite_name)

        end_time = datetime.now()
        self.results['duration'] = (end_time - start_time).total_seconds()

        # Generate report
        self.generate_report()

        # Run coverage if requested
        if coverage:
            self.run_coverage()

    def run_suite(self, suite_name: str):
        """Run a specific test suite"""
        if suite_name not in self.suites:
            print(f"{RED}Unknown test suite: {suite_name}{RESET}")
            self.logger.error(f"Unknown test suite: {suite_name}")
            return

        print(f"\n{BLUE}{BOLD}[{suite_name.upper()} TESTS]{RESET}")
        self.logger.info(f"Starting {suite_name} test suite")

        tests = self.suites[suite_name]

        for test_file in tests:
            test_path = self.test_dir / test_file

            if not test_path.exists():
                print(f"  {YELLOW}⚠{RESET} {test_file:30} - NOT FOUND")
                self.logger.warning(f"Test file not found: {test_file}")
                continue

            # Run test
            result = self.run_test(test_file, test_path)

            # Update results
            self.results['total'] += 1

            if result['status'] == 'passed':
                self.results['passed'] += 1
                print(f"  {GREEN}✓{RESET} {test_file:30} - PASSED ({result['duration']:.2f}s)")
                self.logger.info(f"Test PASSED: {test_file} ({result['duration']:.2f}s)")
            elif result['status'] == 'failed':
                self.results['failed'] += 1
                print(f"  {RED}✗{RESET} {test_file:30} - FAILED")
                self.logger.error(f"Test FAILED: {test_file}")
                self.logger.error(f"Error: {result['error']}")
                self.results['errors'].append({
                    'test': test_file,
                    'error': result['error']
                })
            elif result['status'] == 'skipped':
                self.results['skipped'] += 1
                print(f"  {YELLOW}⊘{RESET} {test_file:30} - SKIPPED")
                self.logger.warning(f"Test SKIPPED: {test_file}")

    def run_test(self, test_name: str, test_path: Path) -> Dict:
        """Run a single test file"""
        start_time = datetime.now()

        try:
            # Run test with pytest
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', str(test_path), '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if result.returncode == 0:
                return {'status': 'passed', 'duration': duration, 'error': None}
            elif result.returncode == 5:  # No tests collected
                return {'status': 'skipped', 'duration': duration, 'error': 'No tests found'}
            else:
                return {
                    'status': 'failed',
                    'duration': duration,
                    'error': result.stdout + result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'duration': 300,
                'error': 'Test timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'duration': 0,
                'error': str(e)
            }

    def run_coverage(self):
        """Run tests with coverage report"""
        print(f"\n{BLUE}{BOLD}[COVERAGE REPORT]{RESET}")
        self.logger.info("Generating coverage report")

        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    sys.executable, '-m', 'pytest',
                    '--cov=services',
                    '--cov=shared',
                    '--cov-report=term',
                    '--cov-report=html:logs/coverage_html',
                    'tests/'
                ],
                capture_output=True,
                text=True
            )

            print(result.stdout)
            self.logger.info(f"Coverage report: {result.stdout}")

            if result.returncode == 0:
                print(f"{GREEN}✓ Coverage report generated: logs/coverage_html/index.html{RESET}")
            else:
                print(f"{YELLOW}⚠ Coverage report may be incomplete{RESET}")

        except Exception as e:
            print(f"{RED}✗ Failed to generate coverage: {e}{RESET}")
            self.logger.error(f"Coverage generation failed: {e}")

    def generate_report(self):
        """Generate test run report"""
        print(f"\n{BOLD}{'=' * 70}")
        print("TEST RUN REPORT")
        print(f"{'=' * 70}{RESET}\n")

        # Statistics
        print(f"{BOLD}Statistics:{RESET}")
        print(f"  Total tests:       {self.results['total']}")
        print(f"  Passed:            {GREEN}{self.results['passed']}{RESET}")
        print(f"  Failed:            {RED}{self.results['failed']}{RESET}")
        print(f"  Skipped:           {YELLOW}{self.results['skipped']}{RESET}")
        print(f"  Duration:          {self.results['duration']:.2f}s")
        print()

        # Log statistics
        self.logger.info("=" * 70)
        self.logger.info("TEST RUN REPORT")
        self.logger.info("=" * 70)
        self.logger.info(f"Total tests: {self.results['total']}")
        self.logger.info(f"Passed: {self.results['passed']}")
        self.logger.info(f"Failed: {self.results['failed']}")
        self.logger.info(f"Skipped: {self.results['skipped']}")
        self.logger.info(f"Duration: {self.results['duration']:.2f}s")

        # Errors
        if self.results['errors']:
            print(f"{RED}{BOLD}Failed Tests:{RESET}")
            for error in self.results['errors']:
                print(f"  {RED}✗{RESET} {error['test']}")
                # Don't print full error in console (it's in log file)
            print()

            self.logger.error("=" * 70)
            self.logger.error("FAILED TESTS")
            self.logger.error("=" * 70)
            for error in self.results['errors']:
                self.logger.error(f"Test: {error['test']}")
                self.logger.error(f"Error:\n{error['error']}")
                self.logger.error("-" * 70)

        # Overall status
        print(f"{BOLD}Overall Status:{RESET}")
        if self.results['failed'] == 0:
            if self.results['passed'] == self.results['total']:
                print(f"{GREEN}✓ ALL TESTS PASSED{RESET}")
                self.logger.info("✓ ALL TESTS PASSED")
            else:
                print(f"{YELLOW}⚠ PASS (with skipped tests){RESET}")
                self.logger.warning("⚠ PASS (with skipped tests)")
        else:
            pass_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
            print(f"{RED}✗ FAILED ({pass_rate:.1f}% pass rate){RESET}")
            self.logger.error(f"✗ FAILED ({pass_rate:.1f}% pass rate)")

        print()
        print(f"{BLUE}📄 Full log: {self.log_file}{RESET}")
        print()

        # Save JSON report
        report_file = self.log_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.logger.info(f"JSON report saved: {report_file}")

    def run_manual_scenarios(self):
        """Display manual testing scenarios"""
        print(f"{BOLD}{'=' * 70}")
        print("MANUAL TESTING SCENARIOS")
        print(f"{'=' * 70}{RESET}\n")

        print("Manual tests require human interaction. Please follow these scenarios:\n")

        scenarios = [
            {
                'name': 'Tourism Office Staff Onboarding',
                'steps': [
                    'Open Streamlit UI: streamlit run app.py',
                    'Navigate to Assistant page (page 4)',
                    'Verify system shows "Ready" status',
                    'Ask: "What work visas are available for Canada?"',
                    'Verify answer quality and sources'
                ]
            },
            {
                'name': 'Browser Crawler Testing',
                'steps': [
                    'Navigate to Crawler page (page 1)',
                    'Select "Browser (Playwright)" mode',
                    'Select a country (e.g., Canada)',
                    'Click "Start Crawling"',
                    'Verify pages are crawled without 403 errors'
                ]
            },
            {
                'name': 'Dual Content Extraction',
                'steps': [
                    'Navigate to Classifier page (page 2)',
                    'Select country to classify',
                    'Click "Start Classification"',
                    'Verify both visas and general content extracted',
                    'Check Database page for both content types'
                ]
            },
            {
                'name': 'Comprehensive Question Answering',
                'steps': [
                    'Navigate to Assistant page',
                    'Test visa question: "What are age requirements for skilled worker visas?"',
                    'Test general question: "What healthcare services are available?"',
                    'Test mixed question: "What work opportunities are available in Canada?"',
                    'Verify both content types used'
                ]
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"{BLUE}{BOLD}Scenario {i}: {scenario['name']}{RESET}")
            for j, step in enumerate(scenario['steps'], 1):
                print(f"  {j}. {step}")
            print()

        print(f"{YELLOW}Note: See docs/TESTING_STRATEGY.md for detailed manual testing procedures{RESET}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run Immigration Assistant System tests')

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all automated tests'
    )

    parser.add_argument(
        '--suite',
        choices=['unit', 'integration', 'e2e', 'service'],
        help='Run specific test suite'
    )

    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )

    parser.add_argument(
        '--manual',
        action='store_true',
        help='Display manual testing scenarios'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )

    args = parser.parse_args()

    # Create test runner
    runner = TestRunner(log_level=args.log_level)

    # Run tests based on arguments
    if args.manual:
        runner.run_manual_scenarios()
    elif args.all:
        runner.run_all_tests(coverage=args.coverage)
    elif args.suite:
        runner.run_suite(args.suite)
    elif args.coverage:
        runner.run_coverage()
    else:
        # Default: show help
        parser.print_help()


if __name__ == '__main__':
    main()
