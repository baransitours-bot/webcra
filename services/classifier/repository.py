"""
Classifier Repository - FUEL TRANSPORT LAYER

Handles data flow for the classifier service.
Gets crawled pages, saves extracted visas.
"""

from typing import List, Optional
from shared.database import Database
from shared.models import CrawledPage, Visa


class ClassifierRepository:
    """
    Data access layer for classifier service.

    Responsibilities:
    - Fetch crawled pages from database
    - Save extracted visas to database
    - Check if page already classified
    """

    def __init__(self):
        self.db = Database()

    def get_pages(self, country: Optional[str] = None, only_unclassified: bool = False) -> List[CrawledPage]:
        """
        Get crawled pages to classify.

        Args:
            country: Optional country filter
            only_unclassified: If True, only return pages without visas (default: False for backward compatibility)

        Returns:
            List of CrawledPage objects
        """
        if only_unclassified:
            return self.db.get_unclassified_pages(country=country)
        else:
            return self.db.get_pages(country=country)

    def save_visa(self, visa: Visa) -> int:
        """
        Save extracted visa to database.

        Args:
            visa: Visa model object

        Returns:
            Visa ID
        """
        return self.db.save_visa(
            visa_type=visa.visa_type,
            country=visa.country,
            category=visa.category,
            requirements=visa.requirements,
            fees=visa.fees,
            processing_time=visa.processing_time,
            documents_required=visa.documents_required,
            source_urls=visa.source_urls
        )

    def get_visas(self, country: Optional[str] = None) -> List[Visa]:
        """
        Get all extracted visas.

        Args:
            country: Optional country filter

        Returns:
            List of Visa objects
        """
        return self.db.get_visas(country=country)

    def get_visa_count(self) -> int:
        """Get total number of visas"""
        return len(self.db.get_visas())
