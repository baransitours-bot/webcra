"""
Crawler Service - Entry Point
"""

import yaml
from services.crawler.spider import ImmigrationCrawler
from shared.logger import setup_logger

def parse_arguments(args):
    """Parse command line arguments"""
    options = {
        'countries': None,
        'all': False
    }

    i = 0
    while i < len(args):
        if args[i] == '--countries' and i + 1 < len(args):
            options['countries'] = args[i + 1].split(',')
            i += 2
        elif args[i] == '--all':
            options['all'] = True
            i += 1
        else:
            i += 1

    return options

def run_crawler(args):
    """
    Run the crawler service

    Usage:
      python main.py crawl --countries australia,canada
      python main.py crawl --all
    """
    logger = setup_logger('crawler', 'crawler.log')
    logger.info("🕷️  Starting Crawler Service...")

    # Load configurations
    with open('config.yaml', 'r') as f:
        global_config = yaml.safe_load(f)

    with open('services/crawler/config.yaml', 'r') as f:
        crawler_config = yaml.safe_load(f)

    # Parse arguments
    options = parse_arguments(args)

    # Select countries to crawl
    if options['all']:
        countries_to_crawl = list(global_config['countries'].values())
    elif options['countries']:
        countries_to_crawl = [
            global_config['countries'][c]
            for c in options['countries']
            if c in global_config['countries']
        ]
    else:
        logger.error("No countries specified. Use --countries or --all")
        return

    # Initialize and run crawler
    crawler = ImmigrationCrawler(countries_to_crawl, crawler_config)
    crawler.crawl_all()

    logger.info("✅ Crawler service complete!")
