"""
LLM-based Visa Extractor
Uses AI to intelligently extract visa information from web pages
"""

import json
from typing import Dict, Optional
from shared.logger import setup_logger
from services.assistant.llm_client import LLMClient


class VisaExtractor:
    """Extract visa information using LLM for intelligent parsing"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = setup_logger('visa_extractor')

        # Initialize LLM client if config has LLM section
        self.llm_client = None
        if 'llm' in config:
            try:
                self.llm_client = LLMClient(config)
                self.logger.info("✅ LLM-based extraction enabled")
            except Exception as e:
                self.logger.warning(f"⚠️ LLM client initialization failed: {str(e)}")
                self.logger.info("Falling back to pattern-based extraction")
        else:
            self.logger.info("No LLM config - using pattern-based extraction only")

    def extract_visa_from_text(self, text: str, country: str) -> Optional[Dict]:
        """
        Extract structured visa information from raw text

        Args:
            text: Raw HTML/text content from crawled page
            country: Country name for context

        Returns:
            Dict with visa information or None if no visa found
        """
        if not text or len(text.strip()) < 100:
            return None

        # Use LLM extraction if available
        if self.llm_client:
            return self._extract_with_llm(text, country)
        else:
            return self._extract_with_patterns(text, country)

    def _extract_with_llm(self, text: str, country: str) -> Optional[Dict]:
        """Use LLM to extract visa information"""
        # Truncate text if too long (keep first 8000 chars)
        text_sample = text[:8000] if len(text) > 8000 else text

        prompt = f"""Extract visa/immigration program information from this webpage content.

Country: {country}

Content:
{text_sample}

Extract the following information in JSON format:
{{
    "visa_type": "Name of the visa/program",
    "category": "work|study|family|investment|tourism|retirement|unknown",
    "requirements": {{
        "age": {{"min": null, "max": null}},
        "education": "education level required or null",
        "experience_years": null,
        "language": "language requirement or null",
        "other": ["list of other requirements"]
    }},
    "fees": {{
        "application_fee": "fee amount or null",
        "other_fees": {{"description": "amount"}}
    }},
    "processing_time": "processing time or null",
    "eligibility_criteria": ["list of who can apply"],
    "benefits": ["list of benefits/rights"],
    "restrictions": ["list of restrictions/limitations"]
}}

Rules:
1. Only extract if this is clearly about a visa/immigration program
2. Return null for fields you cannot find
3. Be precise - don't guess or make up information
4. Use the exact category names provided
5. If this is not a visa page, return: {{"visa_type": null}}

Return ONLY valid JSON, no other text."""

        try:
            response = self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            # Parse JSON response
            # Try to extract JSON from markdown code blocks if present
            content = response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            visa_data = json.loads(content)

            # Validate we got a visa
            if not visa_data.get('visa_type'):
                self.logger.debug("LLM determined this is not a visa page")
                return None

            self.logger.info(f"✅ Extracted: {visa_data['visa_type']}")
            return visa_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            self.logger.debug(f"Response was: {response[:200]}")
            return None
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {str(e)}")
            return None

    def _extract_with_patterns(self, text: str, country: str) -> Optional[Dict]:
        """Fallback: Use pattern matching (basic extraction)"""
        # Import the pattern-based extractor
        from services.classifier.extractor import RequirementExtractor

        extractor = RequirementExtractor(self.config)

        # Create a fake page_data dict for the old API
        page_data = {
            'content_text': text,
            'url': '',
            'country': country,
            'title': text[:100]  # Use first 100 chars as title approximation
        }

        # Extract using patterns
        extracted = extractor.extract_all_requirements(page_data)

        # Check if we found anything meaningful
        has_data = (
            extracted.get('category') != 'unknown' or
            extracted.get('age') or
            extracted.get('education') or
            extracted.get('experience_years') or
            extracted.get('fees') or
            extracted.get('processing_time')
        )

        if not has_data:
            return None

        # Convert to new format
        visa_data = {
            'visa_type': extracted.get('title', 'Unknown Visa'),
            'category': extracted.get('category', 'unknown'),
            'requirements': {
                'age': extracted.get('age'),
                'education': extracted.get('education'),
                'experience_years': extracted.get('experience_years'),
                'language': extracted.get('language'),
                'other': []
            },
            'fees': extracted.get('fees', {}),
            'processing_time': extracted.get('processing_time'),
            'eligibility_criteria': [],
            'benefits': [],
            'restrictions': []
        }

        return visa_data
