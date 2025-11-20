"""
Matcher Interface - INTERACTION LAYER

Provides clean APIs for interacting with the matcher.

INTERIOR Interface: Python API for service-to-service communication
EXTERIOR Interface: Used by UI, CLI, and external systems
"""

import yaml
import json
from typing import List, Dict, Callable, Optional
from pathlib import Path

from services.matcher.engine import MatcherEngine
from services.matcher.repository import MatcherRepository
from shared.logger import setup_logger


class MatcherService:
    """
    INTERIOR Interface: Service-to-Service API

    Clean Python API that other services use.
    Handles setup, configuration, and provides simple methods.
    """

    def __init__(self, config_path: str = 'services/matcher/config.yaml'):
        """
        Initialize matcher service.

        Args:
            config_path: Path to config file
        """
        self.logger = setup_logger('matcher_service')

        # Load configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.logger.warning(f"Config not found: {config_path}, using defaults")
            self.config = self._default_config()

        # Initialize layers
        self.repo = MatcherRepository()  # FUEL TRANSPORT
        self.engine = MatcherEngine(self.config, self.repo)  # ENGINE

    def match_user(self, user_profile: Dict, country: str = None) -> List[Dict]:
        """
        Match a user to visas.

        Args:
            user_profile: User profile dictionary
            country: Optional country filter

        Returns:
            List of match results
        """
        return self.engine.match_user_to_visas(user_profile, country)

    def get_top_matches(self, user_profile: Dict, country: str = None, limit: int = 10) -> List[Dict]:
        """
        Get top N matches for a user.

        Args:
            user_profile: User profile
            country: Optional country filter
            limit: Number of top matches

        Returns:
            Top matches
        """
        return self.engine.get_top_matches(user_profile, country, limit)

    def get_eligible_visas(self, user_profile: Dict, country: str = None) -> List[Dict]:
        """
        Get only eligible visas.

        Args:
            user_profile: User profile
            country: Optional country filter

        Returns:
            Eligible matches
        """
        return self.engine.get_eligible_visas(user_profile, country)

    def get_statistics(self) -> Dict:
        """
        Get matching statistics.

        Returns:
            Statistics dictionary
        """
        visa_count = self.repo.get_visa_count()
        return {
            'total_visas': visa_count,
            'ready': visa_count > 0
        }

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'weights': {
                'age': 1.0,
                'education': 2.0,
                'experience': 1.5,
                'language': 1.0
            },
            'thresholds': {
                'high_match': 80.0,
                'medium_match': 60.0
            }
        }


class MatcherController:
    """
    EXTERIOR Interface: UI/CLI Controller

    This is what the UI (Streamlit) and CLI interact with.
    Provides user-friendly methods and progress tracking.
    """

    def __init__(self, config_path: str = 'services/matcher/config.yaml'):
        """Initialize controller with service"""
        self.service = MatcherService(config_path)
        self.logger = setup_logger('matcher_controller')

    def match_with_progress(
        self,
        user_profile: Dict,
        country: Optional[str] = None,
        on_start: Optional[Callable] = None,
        on_match: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> List[Dict]:
        """
        Match with progress callbacks for UI.

        Args:
            user_profile: User profile dictionary
            country: Optional country filter
            on_start: Called when starting (total_visas)
            on_match: Called for each match (match_result)
            on_complete: Called when complete (all_matches)
            on_error: Called on error (error_message)

        Returns:
            List of match results
        """
        try:
            # Get visa count
            visa_count = self.service.repo.get_visa_count()

            if visa_count == 0:
                if on_error:
                    on_error("No visas found. Run Crawler and Classifier first.")
                return []

            # Notify start
            if on_start:
                on_start(visa_count)

            # Match
            matches = self.service.match_user(user_profile, country)

            # Notify for each match
            if on_match:
                for match in matches:
                    on_match(match)

            # Notify complete
            if on_complete:
                on_complete(matches)

            return matches

        except Exception as e:
            self.logger.error(f"Matching failed: {e}")
            if on_error:
                on_error(str(e))
            raise

    def load_profile_from_file(self, filepath: str) -> Dict:
        """
        Load user profile from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            User profile dictionary
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load profile: {e}")
            raise

    def save_results_to_file(self, matches: List[Dict], filepath: str):
        """
        Save match results to JSON file.

        Args:
            matches: List of match results
            filepath: Output file path
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(matches, f, indent=2)
            self.logger.info(f"Saved results to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            raise

    def validate_profile(self, profile: Dict) -> Dict:
        """
        Validate user profile.

        Args:
            profile: User profile dictionary

        Returns:
            Validation result with errors if any
        """
        errors = []

        required_fields = ['age', 'nationality', 'education']
        for field in required_fields:
            if field not in profile or not profile[field]:
                errors.append(f"Missing required field: {field}")

        # Validate age
        if 'age' in profile:
            try:
                age = int(profile['age'])
                if age < 0 or age > 120:
                    errors.append("Age must be between 0 and 120")
            except (ValueError, TypeError):
                errors.append("Age must be a valid number")

        # Validate education level
        if 'education' in profile:
            valid_levels = ['secondary', 'diploma', 'bachelors', 'masters', 'phd']
            if profile['education'].lower() not in valid_levels:
                errors.append(f"Education must be one of: {', '.join(valid_levels)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.service.config

    def get_statistics(self) -> Dict:
        """Get matching statistics"""
        return self.service.get_statistics()


# Convenience functions for quick access

def match_user(user_profile: Dict, country: str = None) -> List[Dict]:
    """
    Quick function to match a user to visas.

    Args:
        user_profile: User profile dictionary
        country: Optional country filter

    Returns:
        List of match results
    """
    service = MatcherService()
    return service.match_user(user_profile, country)


def get_top_matches(user_profile: Dict, limit: int = 10) -> List[Dict]:
    """
    Quick function to get top matches.

    Args:
        user_profile: User profile
        limit: Number of results

    Returns:
        Top matches
    """
    service = MatcherService()
    return service.get_top_matches(user_profile, limit=limit)
