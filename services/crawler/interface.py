"""
Crawler Interface - INTERACTION LAYER

Provides clean APIs for interacting with the crawler.

INTERIOR Interface: Python API for service-to-service communication
EXTERIOR Interface: Used by UI, CLI, and external systems
"""

from typing import List, Dict, Callable, Optional

from services.crawler.engine import CrawlerEngine
from services.crawler.repository import CrawlerRepository
from shared.logger import setup_logger
from shared.service_config import get_service_config


class CrawlerService:
    """
    INTERIOR Interface: Service-to-Service API

    This is the clean Python API that other services use.
    Handles setup, configuration, and provides simple methods.
    """

    def __init__(self):
        """Initialize crawler service with centralized configuration"""
        self.logger = setup_logger('crawler_service')

        # Load configuration from centralized system (DB > YAML defaults)
        config_loader = get_service_config()
        self.config = config_loader.get_crawler_config()

        # Initialize layers
        self.repo = CrawlerRepository()  # FUEL TRANSPORT
        self.engine = CrawlerEngine(self.config, self.repo)  # ENGINE

    def crawl_country(self, country_name: str, seed_urls: List[str]) -> Dict:
        """
        Crawl a single country.

        Args:
            country_name: Country to crawl
            seed_urls: Starting URLs

        Returns:
            Crawl statistics
        """
        return self.engine.crawl_country(country_name, seed_urls)

    def crawl_all_countries(self) -> List[Dict]:
        """
        Crawl all configured countries.

        Returns:
            List of crawl results for each country
        """
        results = []

        for country in self.config['countries']:
            result = self.crawl_country(
                country['name'],
                country['seed_urls']
            )
            results.append(result)

            # Reset engine for next country
            self.engine.reset()

        return results

    def get_crawled_pages(self, country: Optional[str] = None) -> List:
        """
        Get crawled pages.

        Args:
            country: Optional country filter

        Returns:
            List of CrawledPage objects
        """
        if country:
            return self.repo.get_pages_by_country(country)
        return self.repo.get_all_pages()

    def get_statistics(self) -> Dict:
        """
        Get crawling statistics.

        Returns:
            Statistics dictionary
        """
        pages = self.repo.get_all_pages()

        # Count by country
        by_country = {}
        for page in pages:
            by_country[page.country] = by_country.get(page.country, 0) + 1

        return {
            'total_pages': len(pages),
            'by_country': by_country,
            'countries': list(by_country.keys())
        }


class CrawlerController:
    """
    EXTERIOR Interface: UI/CLI Controller

    This is what the UI (Streamlit) and CLI interact with.
    Provides callback support for progress tracking.
    """

    def __init__(self):
        """Initialize controller with service"""
        self.service = CrawlerService()
        self.logger = setup_logger('crawler_controller')

    def crawl_with_progress(
        self,
        countries: List[Dict],
        on_start: Optional[Callable] = None,
        on_page: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> List[Dict]:
        """
        Crawl with progress callbacks for UI.

        Args:
            countries: List of {name, seed_urls}
            on_start: Called when starting a country
            on_page: Called after each page (page_num, total, title)
            on_complete: Called when country complete
            on_error: Called on error

        Returns:
            List of results
        """
        results = []

        for country in countries:
            try:
                # Notify start
                if on_start:
                    on_start(country['name'])

                # Crawl
                result = self.service.crawl_country(
                    country['name'],
                    country['seed_urls']
                )

                # Notify complete
                if on_complete:
                    on_complete(country['name'], result)

                results.append(result)

                # Reset for next country
                self.service.engine.reset()

            except Exception as e:
                self.logger.error(f"Error crawling {country['name']}: {e}")
                if on_error:
                    on_error(country['name'], str(e))

        return results

    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.service.config

    def update_config(self, updates: Dict):
        """
        Update configuration.

        Args:
            updates: Configuration updates
        """
        self.service.config.update(updates)

    def validate_urls(self, urls: List[str]) -> Dict[str, bool]:
        """
        Validate URLs are accessible.

        Args:
            urls: List of URLs to check

        Returns:
            Dict of {url: is_valid}
        """
        results = {}
        import requests

        for url in urls:
            try:
                response = requests.head(url, timeout=5)
                results[url] = response.status_code < 400
            except:
                results[url] = False

        return results

    def get_statistics(self) -> Dict:
        """Get crawling statistics"""
        return self.service.get_statistics()


# Convenience functions for quick access

def crawl_country(country_name: str, seed_urls: List[str]) -> Dict:
    """
    Quick function to crawl a single country.

    Args:
        country_name: Country name
        seed_urls: Starting URLs

    Returns:
        Crawl result
    """
    service = CrawlerService()
    return service.crawl_country(country_name, seed_urls)


def crawl_all() -> List[Dict]:
    """
    Quick function to crawl all configured countries.

    Returns:
        List of crawl results
    """
    service = CrawlerService()
    return service.crawl_all_countries()
