"""
Shared Data Models
Defines data structures used across all services
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class RawPage:
    """Raw crawled page data"""
    url: str
    country: str
    title: str
    content_text: str
    content_html: str
    breadcrumbs: List[str]
    links: List[str]
    attachments: List[Dict]
    crawled_date: datetime
    depth: int

@dataclass
class VisaRequirement:
    """Structured visa requirement"""
    visa_type: str
    country: str
    category: str  # work, study, family, etc.

    # Requirements
    age_min: Optional[int]
    age_max: Optional[int]
    education_level: str
    experience_years: Optional[int]
    language_requirement: Optional[str]

    # Details
    fees: Dict[str, str]
    processing_time: str
    validity_period: str

    # Metadata
    source_url: str
    last_updated: datetime

@dataclass
class UserProfile:
    """User profile for matching"""
    age: int
    nationality: str
    education: str
    profession: str
    experience_years: int
    language_scores: Dict[str, float]
    target_countries: List[str]

@dataclass
class VisaMatch:
    """Match result"""
    visa_type: str
    country: str
    eligibility_score: float
    eligible: bool
    gaps: List[str]
    requirements_met: List[str]
    next_steps: List[str]
