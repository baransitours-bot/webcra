"""
Context Retriever
Retrieves relevant visa information for LLM context

This module provides:
- Keyword-based visa search
- Context formatting for LLM prompts
"""

from typing import List, Dict
from shared.database import Database
from shared.models import Visa
from shared.logger import setup_logger


class ContextRetriever:
    """
    Retrieves relevant visas for a query.

    Uses keyword matching to find visas that match the user's question.
    """

    def __init__(self, config):
        self.config = config
        self.db = Database()
        self.logger = setup_logger('retriever')

    def retrieve_relevant_visas(self, query: str, user_profile: Dict = None) -> List[Dict]:
        """
        Retrieve visas relevant to the query.

        Args:
            query: User's question or search terms
            user_profile: Optional user profile for prioritization

        Returns:
            List of visa dictionaries (for backward compatibility)
        """
        # Load all visas as Visa objects
        all_visas = self.db.get_visas()

        if not all_visas:
            self.logger.warning("No visa data found in database")
            return []

        # Filter by query keywords
        relevant_visas = [
            visa for visa in all_visas
            if self._matches_query(visa, query)
        ]

        # Prioritize by user profile if provided
        if user_profile and relevant_visas:
            relevant_visas.sort(
                key=lambda v: self._profile_match_score(v, user_profile),
                reverse=True
            )

        # Limit results and convert to dicts
        max_visas = self.config['context']['max_visas']
        return [visa.to_dict() for visa in relevant_visas[:max_visas]]

    def _matches_query(self, visa: Visa, query: str) -> bool:
        """Check if visa matches query keywords"""
        query_lower = query.lower()

        # Country match
        if visa.country.lower() in query_lower:
            return True

        # Category match
        if visa.category.lower() in query_lower:
            return True

        # Visa type keywords
        visa_words = visa.visa_type.lower().split()
        if any(word in query_lower for word in visa_words if len(word) > 3):
            return True

        return False

    def _profile_match_score(self, visa: Visa, profile: Dict) -> int:
        """Calculate how well visa matches user profile"""
        score = 0
        reqs = visa.requirements

        # Check age
        age_req = reqs.get('age', {})
        user_age = profile.get('age', 0)
        if age_req:
            if age_req.get('min') and user_age >= age_req['min']:
                score += 1
            if age_req.get('max') and user_age <= age_req['max']:
                score += 1

        # Check education
        if reqs.get('education'):
            if profile.get('education', '').lower() == reqs['education'].lower():
                score += 2

        return score

    def format_context_for_llm(self, visas: List[Dict]) -> str:
        """
        Format visa information for LLM context.

        Creates a structured text representation of visas
        that the LLM can use to answer questions.

        Args:
            visas: List of visa dictionaries

        Returns:
            Formatted string for LLM context
        """
        if not visas:
            return "No relevant visa information found in the database."

        context_parts = []

        for i, visa in enumerate(visas, 1):
            context = self._format_single_visa(i, visa)
            context_parts.append(context)

        return "\n---\n".join(context_parts)

    def _format_single_visa(self, index: int, visa: Dict) -> str:
        """Format a single visa for display"""
        lines = [
            f"\nVisa {index}: {visa['visa_type']}",
            f"Country: {visa['country']}",
            f"Category: {visa.get('category', 'N/A')}",
            "",
            "Requirements:"
        ]

        # Age requirement
        reqs = visa.get('requirements', {})
        if reqs.get('age'):
            age = reqs['age']
            if age.get('min') and age.get('max'):
                lines.append(f"- Age {age['min']}-{age['max']}")
            elif age.get('min'):
                lines.append(f"- Age {age['min']}+")
            elif age.get('max'):
                lines.append(f"- Age under {age['max']}")

        # Education
        if reqs.get('education'):
            lines.append(f"- Education: {reqs['education']}")

        # Experience
        if reqs.get('experience_years'):
            lines.append(f"- Experience: {reqs['experience_years']} years")

        # Language
        if visa.get('language'):
            lines.append(f"\nLanguage: {visa['language']}")

        # Fees
        if visa.get('fees'):
            lines.append(f"\nFees: {visa['fees']}")

        # Processing time
        if visa.get('processing_time'):
            lines.append(f"Processing Time: {visa['processing_time']}")

        # Source
        if visa.get('source_urls'):
            lines.append(f"\nSource: {visa['source_urls'][0]}")

        return "\n".join(lines)
