"""
Classifier Interface - INTERACTION LAYER

Provides clean APIs for interacting with the classifier.

INTERIOR Interface: Python API for service-to-service communication
EXTERIOR Interface: Used by UI, CLI, and external systems
"""

from typing import List, Dict, Callable, Optional

from services.classifier.engine import ClassifierEngine
from services.classifier.repository import ClassifierRepository
from shared.logger import setup_logger
from shared.service_config import get_service_config


class ClassifierService:
    """
    INTERIOR Interface: Service-to-Service API

    Clean Python API that other services use.
    Handles setup, configuration, and provides simple methods.
    """

    def __init__(self):
        """Initialize classifier service with centralized configuration"""
        self.logger = setup_logger('classifier_service')

        # Load configuration from centralized system (DB > YAML defaults)
        config_loader = get_service_config()
        self.config = config_loader.get_classifier_config()

        # Initialize layers
        self.repo = ClassifierRepository()  # FUEL TRANSPORT
        self.engine = ClassifierEngine(self.config, self.repo)  # ENGINE

    def classify_country(self, country: str) -> Dict:
        """
        Classify all pages for a country.

        Args:
            country: Country name

        Returns:
            Classification results
        """
        return self.engine.classify_pages(country)

    def classify_all(self) -> Dict:
        """
        Classify all crawled pages.

        Returns:
            Classification results
        """
        return self.engine.classify_pages()

    def get_visas(self, country: Optional[str] = None) -> List:
        """
        Get extracted visas.

        Args:
            country: Optional country filter

        Returns:
            List of Visa objects
        """
        return self.repo.get_visas(country)

    def get_statistics(self) -> Dict:
        """
        Get classification statistics.

        Returns:
            Statistics dictionary
        """
        visas = self.repo.get_visas()
        pages = self.repo.get_pages()

        # Count by country
        by_country = {}
        for visa in visas:
            by_country[visa.country] = by_country.get(visa.country, 0) + 1

        return {
            'total_visas': len(visas),
            'total_pages': len(pages),
            'by_country': by_country,
            'countries': list(by_country.keys())
        }


class ClassifierController:
    """
    EXTERIOR Interface: UI/CLI Controller

    This is what the UI (Streamlit) and CLI interact with.
    Provides callback support for progress tracking.
    """

    def __init__(self):
        """Initialize controller with service"""
        self.service = ClassifierService()
        self.logger = setup_logger('classifier_controller')

    def classify_with_progress(
        self,
        country: Optional[str] = None,
        skip_classified: bool = True,
        on_start: Optional[Callable] = None,
        on_page: Optional[Callable] = None,
        on_visa_found: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> Dict:
        """
        Classify with progress callbacks for UI.

        Args:
            country: Optional country to classify
            skip_classified: If True, skip pages that already have visas (default: True)
            on_start: Called when starting (total_pages)
            on_page: Called after each page (page_num, total, page_title)
            on_visa_found: Called when visa extracted (visa_type)
            on_complete: Called when complete (results)
            on_error: Called on error (error_message)

        Returns:
            Classification results
        """
        try:
            # Get pages (skip already classified if requested)
            pages = self.service.repo.get_pages(country, only_unclassified=skip_classified)

            if not pages:
                if on_error:
                    on_error("No pages found to classify")
                return {
                    'pages_processed': 0,
                    'visas_extracted': 0,
                    'errors': 0
                }

            # Notify start
            if on_start:
                on_start(len(pages))

            # Process each page
            visas_extracted = 0
            errors = 0

            for i, page in enumerate(pages, 1):
                try:
                    # Notify progress
                    if on_page:
                        on_page(i, len(pages), page.title)

                    # Extract visa
                    visa = self.service.engine.extract_visa_from_page(page)

                    if visa:
                        # Save
                        self.service.repo.save_visa(visa)
                        visas_extracted += 1

                        # Notify - pass full visa dict, not just visa_type string
                        if on_visa_found:
                            on_visa_found(visa.to_dict())

                except Exception as e:
                    self.logger.error(f"Error processing page: {e}")
                    errors += 1
                    if on_error:
                        on_error(str(e))

            # Results
            results = {
                'pages_processed': len(pages),
                'visas_extracted': visas_extracted,
                'errors': errors
            }

            # Notify complete
            if on_complete:
                on_complete(results)

            return results

        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            if on_error:
                on_error(str(e))
            raise

    def validate_pages(self, country: Optional[str] = None) -> Dict:
        """
        Validate that pages exist for classification.

        Args:
            country: Optional country filter

        Returns:
            Validation results
        """
        pages = self.service.repo.get_pages(country)

        return {
            'has_pages': len(pages) > 0,
            'page_count': len(pages),
            'countries': list(set(p.country for p in pages))
        }

    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.service.config

    def get_statistics(self) -> Dict:
        """Get classification statistics"""
        return self.service.get_statistics()


# Convenience functions for quick access

def classify_country(country: str) -> Dict:
    """
    Quick function to classify a single country.

    Args:
        country: Country name

    Returns:
        Classification results
    """
    service = ClassifierService()
    return service.classify_country(country)


def classify_all() -> Dict:
    """
    Quick function to classify all pages.

    Returns:
        Classification results
    """
    service = ClassifierService()
    return service.classify_all()
