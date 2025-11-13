"""
Crawler Service - Entry Point
(Placeholder - will be implemented in Stage 2)
"""

from shared.logger import setup_logger

def run_crawler(args):
    """
    Run the crawler service

    Usage:
      python main.py crawl --countries australia,canada
      python main.py crawl --all
    """
    logger = setup_logger('crawler')
    logger.info("🕷️  Crawler Service (Coming in Stage 2)")
    logger.info("This service will crawl immigration websites and collect visa data.")
    print("\n⚠️  Crawler service not yet implemented. This will be built in Stage 2.\n")
