"""
Classifier Engine - CORE LOGIC LAYER

Core business logic for visa extraction from text.
Uses LLM or pattern matching to extract structured data.

No direct database access - uses repository.
"""

import json
from typing import Dict, List, Optional
from shared.models import CrawledPage, Visa
from shared.logger import setup_logger
from services.classifier.repository import ClassifierRepository
from services.assistant.llm_client import LLMClient


class ClassifierEngine:
    """
    Core visa extraction logic.

    Responsibilities:
    - Extract visa information from text
    - Use LLM or fallback to patterns
    - Validate extracted data
    - Convert to Visa model

    Does NOT:
    - Access database directly
    - Know about UI
    - Handle configuration loading
    """

    def __init__(self, config: dict, repository: ClassifierRepository):
        """
        Initialize engine.

        Args:
            config: Classifier configuration
            repository: Data access layer
        """
        self.config = config
        self.repo = repository
        self.logger = setup_logger('classifier_engine')

        # Initialize LLM client
        self.llm_client = self._init_llm()

    def _init_llm(self) -> Optional[LLMClient]:
        """Initialize LLM client"""
        try:
            client = LLMClient()
            self.logger.info("✅ LLM-based extraction enabled")
            return client
        except Exception as e:
            self.logger.warning(f"⚠️ LLM not available: {str(e)[:100]}")
            self.logger.info("💡 Will use pattern-based extraction")
            return None

    def classify_pages(self, country: str = None) -> Dict:
        """
        Classify all pages for a country.

        Args:
            country: Optional country filter

        Returns:
            Classification results
        """
        # Get pages from repository
        pages = self.repo.get_pages(country=country)

        if not pages:
            self.logger.warning(f"No pages found for {country or 'all countries'}")
            return {
                'pages_processed': 0,
                'visas_extracted': 0,
                'errors': 0
            }

        self.logger.info(f"Classifying {len(pages)} pages...")

        visas_extracted = 0
        errors = 0

        for i, page in enumerate(pages, 1):
            try:
                # Extract visa from page
                visa = self.extract_visa_from_page(page)

                if visa:
                    # Save via repository
                    self.repo.save_visa(visa)
                    visas_extracted += 1
                    self.logger.info(f"[{i}/{len(pages)}] ✓ {visa.visa_type}")
                else:
                    self.logger.debug(f"[{i}/{len(pages)}] No visa found")

            except Exception as e:
                self.logger.error(f"[{i}/{len(pages)}] Error: {e}")
                errors += 1

        return {
            'pages_processed': len(pages),
            'visas_extracted': visas_extracted,
            'errors': errors
        }

    def extract_visa_from_page(self, page: CrawledPage) -> Optional[Visa]:
        """
        Extract visa information from a single page.

        Args:
            page: CrawledPage object

        Returns:
            Visa object or None if no visa found
        """
        if not page.content or len(page.content.strip()) < 100:
            return None

        # Use LLM if available, otherwise patterns
        if self.llm_client:
            visa_data = self._extract_with_llm(page.content, page.country)
        else:
            visa_data = self._extract_with_patterns(page.content, page.country)

        if not visa_data:
            return None

        # Convert to Visa model
        return self._create_visa_model(visa_data, page)

    def _extract_with_llm(self, text: str, country: str) -> Optional[Dict]:
        """Use LLM to extract visa information"""
        # Truncate text if too long
        text_sample = text[:8000] if len(text) > 8000 else text

        prompt = f"""Extract visa/immigration program information from this webpage content.

Country: {country}

Content:
{text_sample}

Extract the following information in JSON format:
{{
    "visa_type": "Name of the visa/program",
    "category": "work|study|family|business|tourist|unknown",
    "requirements": {{
        "age": {{"min": null, "max": null}},
        "education": "education level or null",
        "experience_years": null,
        "language": "language requirement or null",
        "other": []
    }},
    "fees": {{
        "application_fee": "amount or null"
    }},
    "processing_time": "processing time or null",
    "documents_required": []
}}

Rules:
1. Only extract if this is clearly about a visa/immigration program
2. Return null for fields you cannot find
3. Be precise - don't guess
4. If NOT a visa page, return: {{"visa_type": null}}

Return ONLY valid JSON, no other text."""

        try:
            response = self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            # Parse JSON response
            content = response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            visa_data = json.loads(content)

            # Validate we got a visa
            if not visa_data.get('visa_type'):
                return None

            return visa_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            return None

    def _extract_with_patterns(self, text: str, country: str) -> Optional[Dict]:
        """Fallback: Pattern-based extraction"""
        from services.classifier.extractor import RequirementExtractor

        extractor = RequirementExtractor(self.config)

        # Create fake page_data for old API
        page_data = {
            'content_text': text,
            'country': country,
            'title': text[:100]
        }

        extracted = extractor.extract_all_requirements(page_data)

        # Check if we found anything meaningful
        has_data = (
            extracted.get('category') != 'unknown' or
            extracted.get('age') or
            extracted.get('education')
        )

        if not has_data:
            return None

        return {
            'visa_type': extracted.get('visa_type', f'{country} Visa'),
            'category': extracted.get('category', 'unknown'),
            'requirements': {
                'age': extracted.get('age', {}),
                'education': extracted.get('education'),
                'experience_years': extracted.get('experience_years'),
                'language': extracted.get('language'),
                'other': []
            },
            'fees': extracted.get('fees', {}),
            'processing_time': extracted.get('processing_time'),
            'documents_required': []
        }

    def _create_visa_model(self, data: Dict, page: CrawledPage) -> Visa:
        """Convert extracted data to Visa model"""
        return Visa(
            visa_type=data.get('visa_type', f'{page.country} Visa'),
            country=page.country,
            category=data.get('category', 'unknown'),
            requirements=data.get('requirements', {}),
            fees=data.get('fees', {}),
            processing_time=data.get('processing_time', ''),
            documents_required=data.get('documents_required', []),
            source_urls=[page.url]
        )
