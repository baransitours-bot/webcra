"""
Requirement Extractor
Extracts structured requirements from raw text
"""

import re
from typing import Dict, List, Optional
from shared.logger import setup_logger

class RequirementExtractor:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger('extractor')

    def identify_visa_category(self, text: str) -> str:
        """Identify visa category based on keywords"""
        text_lower = text.lower()

        category_scores = {}
        for category, keywords in self.config['visa_type_keywords'].items():
            score = sum(1 for kw in keywords if kw in text_lower)
            category_scores[category] = score

        # Return category with highest score
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)

        return "unknown"

    def extract_age_requirement(self, text: str) -> Dict:
        """Extract age requirements"""
        for pattern in self.config['patterns']['age']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:
                    return {'min': int(groups[0]), 'max': int(groups[1])}
                elif 'under' in text.lower() or 'below' in text.lower():
                    return {'min': None, 'max': int(groups[0])}
                elif 'over' in text.lower() or 'above' in text.lower() or 'at least' in text.lower():
                    return {'min': int(groups[0]), 'max': None}

        return {}

    def extract_education_requirement(self, text: str) -> Optional[str]:
        """Extract education requirement"""
        text_lower = text.lower()

        # Check in priority order (highest to lowest)
        education_levels = [
            ('phd', ['phd', 'doctorate']),
            ('masters', ["master's", 'masters']),
            ('bachelors', ["bachelor's", 'bachelors', 'degree qualification']),
            ('diploma', ['diploma']),
            ('secondary', ['secondary education', 'high school'])
        ]

        for level, keywords in education_levels:
            if any(kw in text_lower for kw in keywords):
                return level

        return None

    def extract_experience_requirement(self, text: str) -> Optional[int]:
        """Extract years of experience required"""
        for pattern in self.config['patterns']['experience']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def extract_fees(self, text: str) -> Dict[str, str]:
        """Extract fee information"""
        fees = {}
        for pattern in self.config['patterns']['fees']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = match.group(1).replace(',', '')
                try:
                    # Verify it's a valid number
                    int(amount)
                    fees['application_fee'] = f"${amount}"
                    break  # Take first match
                except ValueError:
                    continue

        return fees

    def extract_processing_time(self, text: str) -> Optional[str]:
        """Extract processing time"""
        for pattern in self.config['patterns']['processing_time']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:
                    # Range format
                    unit = self._extract_time_unit(match.group(0))
                    return f"{groups[0]}-{groups[1]} {unit}"
                else:
                    # Single value
                    unit = self._extract_time_unit(match.group(0))
                    return f"{groups[0]} {unit}"

        return None

    def _extract_time_unit(self, text: str) -> str:
        """Extract time unit from text"""
        text_lower = text.lower()
        if 'month' in text_lower:
            return 'months'
        elif 'week' in text_lower:
            return 'weeks'
        elif 'day' in text_lower:
            return 'days'
        return 'months'  # Default

    def extract_language_requirement(self, text: str) -> Optional[str]:
        """Extract language requirement"""
        for pattern in self.config['patterns']['language']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 0:
                    # Has score
                    test_type = self._extract_test_type(match.group(0))
                    score = match.group(1)
                    return f"{test_type} {score}"
                else:
                    # General requirement
                    return "English proficiency required"

        return None

    def _extract_test_type(self, text: str) -> str:
        """Extract language test type"""
        text_upper = text.upper()
        if 'IELTS' in text_upper:
            return 'IELTS'
        elif 'TOEFL' in text_upper:
            return 'TOEFL'
        elif 'PTE' in text_upper:
            return 'PTE'
        return 'Language Test'

    def extract_all_requirements(self, page_data: dict) -> dict:
        """Extract all requirements from a page"""
        text = page_data['content_text']
        title = page_data.get('title', '')

        return {
            'url': page_data['url'],
            'country': page_data['country'],
            'title': title,
            'category': self.identify_visa_category(text + ' ' + title),
            'age': self.extract_age_requirement(text),
            'education': self.extract_education_requirement(text),
            'experience_years': self.extract_experience_requirement(text),
            'language': self.extract_language_requirement(text),
            'fees': self.extract_fees(text),
            'processing_time': self.extract_processing_time(text),
            'source_url': page_data['url'],
            'raw_content': text[:2000]  # Keep snippet for reference
        }
