#!/usr/bin/env python3
"""
Immigration Platform - Main Entry Point
"""

import sys
import yaml

def load_config():
    """Load global configuration"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def show_help():
    """Display help message"""
    print("""
Immigration Platform - Command Line Interface

Usage:
  python main.py <service> [options]

Services:
  crawl       - Run data collection crawler
  classify    - Process raw data into structured format
  match       - Match user profile against visa requirements
  assist      - Generate AI-powered answers

Examples:
  python main.py crawl --countries australia,canada
  python main.py classify --country australia
  python main.py match --profile user_profile.json
  python main.py assist --query "Am I eligible for Canada?"

Options:
  --help      - Show this help message
  --config    - Specify custom config file
  --verbose   - Enable detailed logging
    """)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', 'help']:
        show_help()
        return

    service = sys.argv[1]
    args = sys.argv[2:]

    # Import and run services
    if service == "crawl":
        from services.crawler.main import run_crawler
        run_crawler(args)

    elif service == "classify":
        from services.classifier.main import run_classifier
        run_classifier(args)

    elif service == "match":
        from services.matcher.main import run_matcher
        run_matcher(args)

    elif service == "assist":
        from services.assistant.main import run_assistant
        run_assistant(args)

    else:
        print(f"Unknown service: {service}")
        print("Run 'python main.py --help' for usage")
        sys.exit(1)

if __name__ == "__main__":
    main()
