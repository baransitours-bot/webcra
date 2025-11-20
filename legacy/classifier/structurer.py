"""
Visa Structurer
Groups and structures extracted requirements into complete visa profiles
"""

from typing import List, Dict
from collections import defaultdict
from shared.logger import setup_logger

class VisaStructurer:
    def __init__(self):
        self.logger = setup_logger('structurer')

    def group_by_visa_type(self, extracted_data: List[dict]) -> Dict[str, List[dict]]:
        """Group pages by visa type (based on title similarity)"""
        visa_groups = defaultdict(list)

        for data in extracted_data:
            # Use title as grouping key (simplified)
            visa_type = self.normalize_visa_name(data['title'])
            visa_groups[visa_type].append(data)

        return visa_groups

    def normalize_visa_name(self, title: str) -> str:
        """Normalize visa names for grouping"""
        # Remove common words
        title = title.lower()
        remove_words = ['visa', 'subclass', 'the', 'a', 'an', 'for', 'to', 'in', 'and', 'or']
        words = [w for w in title.split() if w not in remove_words]

        # Return normalized name (first 5 significant words)
        return ' '.join(words[:5]) if words else title

    def merge_requirements(self, pages: List[dict]) -> dict:
        """Merge requirements from multiple pages about same visa"""
        merged = {
            'visa_type': pages[0]['title'],
            'country': pages[0]['country'],
            'category': pages[0]['category'],
            'requirements': {},
            'fees': {},
            'processing_time': None,
            'language': None,
            'source_urls': []
        }

        # Collect data from all pages
        for page in pages:
            if page['age']:
                merged['requirements']['age'] = page['age']

            if page['education']:
                merged['requirements']['education'] = page['education']

            if page['experience_years']:
                merged['requirements']['experience_years'] = page['experience_years']

            if page.get('language'):
                merged['language'] = page['language']

            if page['fees']:
                merged['fees'].update(page['fees'])

            if page['processing_time']:
                merged['processing_time'] = page['processing_time']

            merged['source_urls'].append(page['url'])

        # Remove duplicates from source URLs
        merged['source_urls'] = list(set(merged['source_urls']))

        return merged

    def structure_all_visas(self, extracted_data: List[dict]) -> List[dict]:
        """Structure all visas"""
        self.logger.info(f"Structuring {len(extracted_data)} extracted pages...")

        # Filter out pages with unknown category and no requirements
        filtered_data = []
        for data in extracted_data:
            has_requirements = (
                data['age'] or
                data['education'] or
                data['experience_years'] or
                data['fees'] or
                data['processing_time']
            )
            if data['category'] != 'unknown' or has_requirements:
                filtered_data.append(data)

        self.logger.info(f"Filtered to {len(filtered_data)} relevant pages")

        # Group by visa type
        visa_groups = self.group_by_visa_type(filtered_data)

        self.logger.info(f"Found {len(visa_groups)} unique visa types")

        # Merge requirements for each group
        structured_visas = []
        for visa_type, pages in visa_groups.items():
            merged = self.merge_requirements(pages)
            structured_visas.append(merged)
            self.logger.info(f"Structured: {merged['visa_type'][:60]}")

        return structured_visas
