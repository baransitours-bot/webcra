"""
Visa Ranker
Ranks visa options based on eligibility scores
"""

from typing import List, Dict
from services.matcher.scorer import EligibilityScorer
from shared.logger import setup_logger

class VisaRanker:
    def __init__(self, config):
        self.config = config
        self.scorer = EligibilityScorer(config)
        self.logger = setup_logger('ranker')

    def match_user_to_visa(self, user_profile: Dict, visa: Dict) -> Dict:
        """Match a user profile to a specific visa"""
        score = self.scorer.calculate_total_score(
            user_profile,
            visa.get('requirements', {})
        )

        gaps = self.scorer.identify_gaps(
            user_profile,
            visa.get('requirements', {})
        )

        # Determine eligibility
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

    def rank_all_visas(self, user_profile: Dict, all_visas: List[Dict]) -> List[Dict]:
        """Rank all visas for a user"""
        self.logger.info(f"Matching user profile against {len(all_visas)} visas...")

        matches = []
        for visa in all_visas:
            # Filter by target countries if specified
            if user_profile.get('target_countries'):
                if visa['country'].lower() not in [c.lower() for c in user_profile['target_countries']]:
                    continue

            match = self.match_user_to_visa(user_profile, visa)
            matches.append(match)

        # Sort by score (highest first)
        matches.sort(key=lambda x: x['eligibility_score'], reverse=True)

        self.logger.info(f"Found {len(matches)} matches")
        return matches
