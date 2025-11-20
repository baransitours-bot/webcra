"""
Crawler Repository - FUEL TRANSPORT LAYER

Handles data flow between the engine and the database.
The engine doesn't know about the database, only the repository.
"""

from typing import List, Optional
from shared.database import Database
from shared.models import CrawledPage


class CrawlerRepository:
    """
    Data access layer for crawler service.

    Responsibilities:
    - Fetch data from database
    - Store crawled pages
    - Check if URL already crawled
    """

    def __init__(self):
        self.db = Database()

    def save_page(self, page: CrawledPage) -> int:
        """
        Store a crawled page.

        Args:
            page: CrawledPage model

        Returns:
            Page ID
        """
        return self.db.save_crawled_page(
            url=page.url,
            country=page.country,
            title=page.title,
            content=page.content,
            metadata=page.metadata
        )

    def get_pages_by_country(self, country: str) -> List[CrawledPage]:
        """
        Get all pages for a country.

        Args:
            country: Country name

        Returns:
            List of CrawledPage objects
        """
        return self.db.get_pages(country=country)

    def url_exists(self, url: str) -> bool:
        """
        Check if URL has been crawled.

        Args:
            url: URL to check

        Returns:
            True if URL exists in database
        """
        pages = self.db.get_pages()
        return any(p.url == url for p in pages)

    def get_all_pages(self) -> List[CrawledPage]:
        """Get all crawled pages"""
        return self.db.get_pages()
