"""
Classifier Engine - CORE LOGIC LAYER

Core business logic for visa extraction from text.
Uses LLM or pattern matching to extract structured data.
Supports dual extraction: visa-specific + general immigration content.

No direct database access - uses repository.
"""

import json
from typing import Dict, List, Optional, Tuple
from shared.models import CrawledPage, Visa, GeneralContent
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

    def classify_pages(self, country: str = None, skip_classified: bool = True) -> Dict:
        """
        Classify all pages for a country using dual extraction.
        Extracts both visa-specific and general immigration content.

        Args:
            country: Optional country filter
            skip_classified: If True, skip pages that already have visas (default: True to save LLM costs)

        Returns:
            Classification results
        """
        # Get pages from repository
        pages = self.repo.get_pages(country=country, only_unclassified=skip_classified)

        if not pages:
            self.logger.warning(f"No pages found for {country or 'all countries'}")
            return {
                'pages_processed': 0,
                'visas_extracted': 0,
                'general_content_extracted': 0,
                'errors': 0
            }

        self.logger.info(f"Classifying {len(pages)} pages with dual extraction...")

        visas_extracted = 0
        general_content_extracted = 0
        errors = 0

        for i, page in enumerate(pages, 1):
            try:
                # Extract BOTH visa and general content from page
                visa, general_content = self.extract_from_page(page)

                if visa:
                    # Save via repository
                    self.repo.save_visa(visa)
                    visas_extracted += 1
                    self.logger.info(f"[{i}/{len(pages)}] ✓ Visa: {visa.visa_type}")

                if general_content:
                    # Save general content
                    self.repo.save_general_content(general_content)
                    general_content_extracted += 1
                    self.logger.info(f"[{i}/{len(pages)}] ✓ General: {general_content.title[:50]}")

                if not visa and not general_content:
                    self.logger.debug(f"[{i}/{len(pages)}] No content extracted")

            except Exception as e:
                self.logger.error(f"[{i}/{len(pages)}] Error: {e}")
                errors += 1

        return {
            'pages_processed': len(pages),
            'visas_extracted': visas_extracted,
            'general_content_extracted': general_content_extracted,
            'errors': errors
        }

    def extract_from_page(self, page: CrawledPage) -> Tuple[Optional[Visa], Optional[GeneralContent]]:
        """
        Extract BOTH visa and general content from a single page (dual extraction).

        Args:
            page: CrawledPage object

        Returns:
            Tuple of (Visa object or None, GeneralContent object or None)
        """
        if not page.content or len(page.content.strip()) < 100:
            return None, None

        # Use LLM if available, otherwise patterns (legacy)
        if self.llm_client:
            return self._extract_with_llm_dual(page.content, page.country, page)
        else:
            # Fallback to visa-only extraction for pattern-based
            visa_data = self._extract_with_patterns(page.content, page.country)
            visa = self._create_visa_model(visa_data, page) if visa_data else None
            return visa, None

    def extract_visa_from_page(self, page: CrawledPage) -> Optional[Visa]:
        """
        Extract visa information from a single page (legacy method).
        Use extract_from_page() for dual extraction.

        Args:
            page: CrawledPage object

        Returns:
            Visa object or None if no visa found
        """
        visa, _ = self.extract_from_page(page)
        return visa

    def _extract_with_llm_dual(self, text: str, country: str, page: CrawledPage) -> Tuple[Optional[Visa], Optional[GeneralContent]]:
        """
        Use LLM to extract BOTH visa and general content (dual extraction).
        Returns array with both types if both are present.
        """
        # Get extraction schema from config
        schema_config = self.config.get('extraction_schema')

        # Build dual extraction prompt
        from shared.extraction_schema import build_dual_extraction_prompt

        if not schema_config:
            # Use default standard schema if not configured
            from shared.extraction_schema import SCHEMA_PRESETS
            schema_config = SCHEMA_PRESETS['standard']

        prompt = build_dual_extraction_prompt(text, country, schema_config)

        try:
            response = self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            # Parse JSON response (should be an array)
            content = response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            extraction_array = json.loads(content)

            # Handle case where LLM returns object instead of array
            if isinstance(extraction_array, dict):
                extraction_array = [extraction_array]

            # Process array to separate visa and general content
            visa = None
            general_content = None

            for item in extraction_array:
                item_type = item.get('type', '').lower()
                data = item.get('data', {})

                if item_type == 'visa' and data.get('visa_type'):
                    # Create Visa model
                    visa = self._create_visa_model(data, page)

                elif item_type == 'general' and data.get('content_type'):
                    # Create GeneralContent model
                    general_content = self._create_general_content_model(data, page)

            return visa, general_content

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            return None, None
        except Exception as e:
            self.logger.error(f"LLM dual extraction failed: {e}")
            return None, None

    def _extract_with_llm(self, text: str, country: str) -> Optional[Dict]:
        """
        Use LLM to extract visa information using configurable schema (legacy method).
        Kept for backward compatibility - use _extract_with_llm_dual() for new code.
        """
        # Get extraction schema from config
        schema_config = self.config.get('extraction_schema')

        # Build prompt dynamically based on schema
        if schema_config:
            from shared.extraction_schema import build_extraction_prompt
            prompt = build_extraction_prompt(schema_config, text, country)
        else:
            # Fallback to basic extraction if no schema configured
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
        "language": "language requirement or null"
    }},
    "fees": {{
        "application_fee": "amount or null"
    }},
    "processing_time": "processing time or null"
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

    def _create_general_content_model(self, data: Dict, page: CrawledPage) -> GeneralContent:
        """Convert extracted data to GeneralContent model"""
        return GeneralContent(
            country=page.country,
            title=data.get('title', page.title or 'Immigration Information'),
            content_type=data.get('content_type', 'overview'),
            summary=data.get('summary', ''),
            key_points=data.get('key_points', []),
            content=data.get('content', ''),
            application_links=data.get('application_links', []),
            source_url=page.url,
            metadata=data.get('metadata', {})
        )
