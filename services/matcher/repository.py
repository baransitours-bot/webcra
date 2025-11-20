"""
Matcher Repository - FUEL TRANSPORT LAYER

Handles data flow for the matcher service.
Gets visas, saves match results.
"""

from typing import List, Optional
from shared.database import Database
from shared.models import Visa, UserProfile


class MatcherRepository:
    """
    Data access layer for matcher service.

    Responsibilities:
    - Fetch visas from database
    - Save match results (optional)
    - Get user profiles
    """

    def __init__(self):
        self.db = Database()

    def get_visas(self, country: Optional[str] = None) -> List[Visa]:
        """
        Get visas to match against.

        Args:
            country: Optional country filter

        Returns:
            List of Visa objects
        """
        return self.db.get_visas(country=country)

    def get_visa_count(self) -> int:
        """Get total number of visas"""
        return len(self.db.get_visas())

    def save_match_result(self, user_profile: dict, visa: Visa, score: float,
                         eligible: bool, gaps: List[str]) -> int:
        """
        Save match result to database (for audit trail).

        Args:
            user_profile: User profile dict
            visa: Visa object
            score: Match score
            eligible: Whether eligible
            gaps: List of gaps

        Returns:
            Match result ID
        """
        # This would use db.save_eligibility_check if we had client_id
        # For now, just return a dummy ID
        return 0

    def get_all_visas_as_dicts(self, country: Optional[str] = None) -> List[dict]:
        """
        Get visas as dictionaries (for backward compatibility).

        Args:
            country: Optional country filter

        Returns:
            List of visa dictionaries
        """
        visas = self.get_visas(country)
        return [visa.to_dict() for visa in visas]
