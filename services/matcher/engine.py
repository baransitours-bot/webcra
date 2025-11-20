"""
Matcher Engine - CORE LOGIC LAYER

Core business logic for matching users to visas.
Pure matching algorithms - no database access.
"""

from typing import List, Dict
from shared.models import Visa, UserProfile, MatchResult
from shared.logger import setup_logger
from services.matcher.repository import MatcherRepository
from services.matcher.scorer import EligibilityScorer


class MatcherEngine:
    """
    Core matching logic.

    Responsibilities:
    - Calculate eligibility scores
    - Identify gaps
    - Rank visas for user
    - Determine match levels

    Does NOT:
    - Access database directly
    - Know about UI
    - Handle configuration loading
    """

    def __init__(self, config: dict, repository: MatcherRepository):
        """
        Initialize engine.

        Args:
            config: Matcher configuration
            repository: Data access layer
        """
        self.config = config
        self.repo = repository
        self.logger = setup_logger('matcher_engine')
        self.scorer = EligibilityScorer(config)

    def match_user_to_visas(self, user_profile: Dict, country: str = None) -> List[Dict]:
        """
        Match a user to all available visas.

        Args:
            user_profile: User profile dictionary
            country: Optional country filter

        Returns:
            List of match results sorted by score
        """
        # Get visas from repository
        visas = self.repo.get_all_visas_as_dicts(country)

        if not visas:
            self.logger.warning("No visas found for matching")
            return []

        self.logger.info(f"Matching user against {len(visas)} visas...")

        # Match each visa
        matches = []
        for visa in visas:
            # Filter by target countries if specified
            if user_profile.get('target_countries'):
                target_countries_lower = [c.lower() for c in user_profile['target_countries']]
                if visa['country'].lower() not in target_countries_lower:
                    continue

            match = self._match_single_visa(user_profile, visa)
            matches.append(match)

        # Sort by score (highest first)
        matches.sort(key=lambda x: x['eligibility_score'], reverse=True)

        self.logger.info(f"Found {len(matches)} matches")
        return matches

    def _match_single_visa(self, user_profile: Dict, visa: Dict) -> Dict:
        """
        Match user to a single visa.

        Args:
            user_profile: User profile
            visa: Visa dictionary

        Returns:
            Match result dictionary
        """
        # Calculate score
        score = self.scorer.calculate_total_score(
            user_profile,
            visa.get('requirements', {})
        )

        # Identify gaps
        gaps = self.scorer.identify_gaps(
            user_profile,
            visa.get('requirements', {})
        )

        # Determine eligibility and match level
        thresholds = self.config['thresholds']

        if score >= thresholds['high_match'] and not gaps:
            eligible = True
            match_level = "high"
        elif score >= thresholds['medium_match']:
            eligible = len(gaps) == 0
            match_level = "medium"
        else:
            eligible = False
            match_level = "low"

        return {
            'visa_type': visa['visa_type'],
            'country': visa['country'],
            'category': visa.get('category', 'unknown'),
            'eligibility_score': round(score, 1),
            'match_level': match_level,
            'eligible': eligible,
            'gaps': gaps,
            'fees': visa.get('fees', {}),
            'processing_time': visa.get('processing_time'),
            'language': visa.get('language'),
            'source_urls': visa.get('source_urls', [])
        }

    def get_top_matches(self, user_profile: Dict, country: str = None, limit: int = 10) -> List[Dict]:
        """
        Get top N matches for a user.

        Args:
            user_profile: User profile
            country: Optional country filter
            limit: Number of top matches to return

        Returns:
            Top matches
        """
        all_matches = self.match_user_to_visas(user_profile, country)
        return all_matches[:limit]

    def get_eligible_visas(self, user_profile: Dict, country: str = None) -> List[Dict]:
        """
        Get only eligible visas for a user.

        Args:
            user_profile: User profile
            country: Optional country filter

        Returns:
            List of eligible matches
        """
        all_matches = self.match_user_to_visas(user_profile, country)
        return [m for m in all_matches if m['eligible']]

    def filter_by_category(self, matches: List[Dict], category: str) -> List[Dict]:
        """
        Filter matches by visa category.

        Args:
            matches: List of match results
            category: Visa category (work, study, etc.)

        Returns:
            Filtered matches
        """
        return [m for m in matches if m['category'].lower() == category.lower()]
