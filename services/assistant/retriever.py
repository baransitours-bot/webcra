"""
Context Retriever
Retrieves relevant visa and general content information for LLM context

This module provides:
- Keyword-based visa search
- Keyword-based general content search
- Context formatting for LLM prompts
"""

from typing import List, Dict, Tuple
from shared.database import Database
from shared.models import Visa, GeneralContent
from shared.logger import setup_logger


class ContextRetriever:
    """
    Retrieves relevant visas and general content for a query.

    Uses keyword matching to find visas and general content that match the user's question.
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

    def retrieve_relevant_general_content(self, query: str) -> List[Dict]:
        """
        Retrieve general content relevant to the query.

        Args:
            query: User's question or search terms

        Returns:
            List of general content dictionaries
        """
        # Load all general content
        all_content = self.db.get_general_content()

        if not all_content:
            self.logger.warning("No general content found in database")
            return []

        # Filter by query keywords
        relevant_content = [
            content for content in all_content
            if self._matches_query_general(content, query)
        ]

        # Sort by relevance (simple scoring)
        relevant_content.sort(
            key=lambda c: self._general_content_score(c, query),
            reverse=True
        )

        # Limit results and convert to dicts
        max_content = self.config['context'].get('max_general_content', 5)
        return [content.to_dict() for content in relevant_content[:max_content]]

    def retrieve_all_context(self, query: str, user_profile: Dict = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Retrieve both visas and general content for comprehensive answers.

        Args:
            query: User's question
            user_profile: Optional user profile

        Returns:
            Tuple of (visa_list, general_content_list)
        """
        visas = self.retrieve_relevant_visas(query, user_profile)
        general_content = self.retrieve_relevant_general_content(query)
        return visas, general_content

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

    def _matches_query_general(self, content: GeneralContent, query: str) -> bool:
        """Check if general content matches query keywords"""
        query_lower = query.lower()

        # Country match
        if content.country.lower() in query_lower:
            return True

        # Title match
        if any(word in content.title.lower() for word in query_lower.split() if len(word) > 3):
            return True

        # Content type match (employment, healthcare, benefits, etc.)
        if content.content_type.lower() in query_lower:
            return True

        # Check key points for matches
        for point in content.key_points:
            if any(word in point.lower() for word in query_lower.split() if len(word) > 3):
                return True

        # Check topics metadata
        topics = content.metadata.get('topics', [])
        for topic in topics:
            if topic.lower() in query_lower:
                return True

        return False

    def _general_content_score(self, content: GeneralContent, query: str) -> int:
        """Score general content by relevance to query"""
        score = 0
        query_lower = query.lower()
        query_words = [w for w in query_lower.split() if len(w) > 3]

        # Title matches are highly relevant
        title_words = content.title.lower().split()
        score += sum(3 for word in query_words if word in title_words)

        # Key points matches
        key_points_text = ' '.join(content.key_points).lower()
        score += sum(2 for word in query_words if word in key_points_text)

        # Topic matches
        topics = content.metadata.get('topics', [])
        score += sum(2 for topic in topics if topic.lower() in query_lower)

        # Audience match (if query mentions specific audience)
        audience_keywords = ['student', 'worker', 'family', 'skilled']
        if any(kw in query_lower for kw in audience_keywords):
            if any(kw in content.audience.lower() for kw in audience_keywords):
                score += 3

        return score

    def format_context_for_llm(self, visas: List[Dict], general_content: List[Dict] = None) -> str:
        """
        Format visa and general content information for LLM context.

        Creates a structured text representation that the LLM can use to answer questions.

        Args:
            visas: List of visa dictionaries
            general_content: Optional list of general content dictionaries

        Returns:
            Formatted string for LLM context
        """
        context_parts = []

        # Format visas
        if visas:
            visa_parts = []
            for i, visa in enumerate(visas, 1):
                context = self._format_single_visa(i, visa)
                visa_parts.append(context)

            context_parts.append("=== VISA PROGRAMS ===\n" + "\n---\n".join(visa_parts))

        # Format general content
        if general_content:
            general_parts = []
            for i, content in enumerate(general_content, 1):
                context = self._format_single_general_content(i, content)
                general_parts.append(context)

            context_parts.append("=== GENERAL INFORMATION ===\n" + "\n---\n".join(general_parts))

        if not context_parts:
            return "No relevant information found in the database."

        return "\n\n".join(context_parts)

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

    def _format_single_general_content(self, index: int, content: Dict) -> str:
        """Format a single general content item for display"""
        lines = [
            f"\nGeneral Content {index}: {content['title']}",
            f"Type: {content.get('content_type', 'N/A')}",
            f"Country: {content['country']}",
            f"Audience: {content.get('metadata', {}).get('audience', 'general')}",
            "",
            "Summary:",
            content.get('summary', 'No summary available'),
            ""
        ]

        # Key points
        key_points = content.get('key_points', [])
        if key_points:
            lines.append("Key Points:")
            for point in key_points[:5]:  # Limit to 5 key points
                lines.append(f"- {point}")
            lines.append("")

        # Application links
        app_links = content.get('application_links', [])
        if app_links:
            lines.append("Application Links:")
            for link in app_links[:3]:  # Limit to 3 links
                label = link.get('label', 'Link')
                url = link.get('url', '')
                if url:
                    lines.append(f"- {label}: {url}")
                else:
                    lines.append(f"- {label}")
            lines.append("")

        # Source
        if content.get('source_url'):
            lines.append(f"Source: {content['source_url']}")

        return "\n".join(lines)
