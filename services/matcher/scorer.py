"""
Eligibility Scorer
Calculates match score between user profile and visa requirements
"""

from typing import Dict
from shared.logger import setup_logger

class EligibilityScorer:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger('scorer')

    def score_age(self, user_age: int, requirement: Dict) -> float:
        """Score age requirement match"""
        if not requirement:
            return 1.0  # No requirement = full score

        min_age = requirement.get('min')
        max_age = requirement.get('max')

        if min_age and user_age < min_age:
            return 0.0

        if max_age and user_age > max_age:
            return 0.0

        return 1.0

    def score_education(self, user_education: str, requirement: str) -> float:
        """Score education match"""
        if not requirement:
            return 1.0

        levels = self.config['education_levels']
        user_level = levels.get(user_education.lower(), 0)
        required_level = levels.get(requirement.lower(), 0)

        if user_level >= required_level:
            return 1.0
        else:
            # Partial score if close
            return max(0, user_level / required_level) if required_level > 0 else 0

    def score_experience(self, user_years: int, required_years: int) -> float:
        """Score experience match"""
        if not required_years:
            return 1.0

        if user_years >= required_years:
            return 1.0
        else:
            # Partial score based on percentage
            return user_years / required_years if required_years > 0 else 0

    def calculate_total_score(self, user_profile: Dict, visa_requirements: Dict) -> float:
        """Calculate overall eligibility score"""
        weights = self.config['scoring']

        # Score each component
        age_score = self.score_age(
            user_profile['age'],
            visa_requirements.get('age', {})
        )

        education_score = self.score_education(
            user_profile['education'],
            visa_requirements.get('education')
        )

        experience_score = self.score_experience(
            user_profile.get('experience_years', 0),
            visa_requirements.get('experience_years', 0)
        )

        # Calculate weighted average
        total_weight = weights['age_match'] + weights['education_match'] + weights['experience_match']
        total_score = (
            age_score * weights['age_match'] +
            education_score * weights['education_match'] +
            experience_score * weights['experience_match']
        ) / total_weight

        return total_score * 100  # Convert to percentage

    def identify_gaps(self, user_profile: Dict, visa_requirements: Dict) -> list:
        """Identify what user is missing"""
        gaps = []

        # Check age
        age_req = visa_requirements.get('age', {})
        if age_req:
            if age_req.get('min') and user_profile['age'] < age_req['min']:
                gaps.append(f"Age too low (need {age_req['min']}+)")
            if age_req.get('max') and user_profile['age'] > age_req['max']:
                gaps.append(f"Age too high (max {age_req['max']})")

        # Check education
        edu_req = visa_requirements.get('education')
        if edu_req:
            levels = self.config['education_levels']
            if levels.get(user_profile['education'].lower(), 0) < levels.get(edu_req.lower(), 0):
                gaps.append(f"Need {edu_req} degree (have {user_profile['education']})")

        # Check experience
        exp_req = visa_requirements.get('experience_years')
        if exp_req:
            user_exp = user_profile.get('experience_years', 0)
            if user_exp < exp_req:
                gaps.append(f"Need {exp_req} years experience (have {user_exp})")

        return gaps
