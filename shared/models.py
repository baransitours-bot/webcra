"""
Data Models - Clear structures for all data in the system

These classes make it easy to understand what data exists and how it's structured.
Use these instead of raw dictionaries for better code clarity.

Usage:
    from shared.models import Visa, UserProfile, CrawledPage

    # Load visa from database
    visa = Visa.from_db_row(row)

    # Access typed properties
    print(visa.country)
    print(visa.requirements.age_range)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import json


# ============ VISA DATA ============

@dataclass
class Visa:
    """
    A visa type with all its information.

    This is the main data structure for visa information.
    All services use this to work with visa data.
    """
    # Required fields
    visa_type: str
    country: str

    # Optional fields
    category: str = ""  # work, study, family, tourist, business
    requirements: Dict = field(default_factory=dict)
    fees: Dict = field(default_factory=dict)
    processing_time: str = ""
    documents_required: List[str] = field(default_factory=list)
    source_urls: List[str] = field(default_factory=list)
    language: str = ""

    # Database fields
    id: Optional[int] = None
    version: int = 1
    created_at: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: dict) -> 'Visa':
        """
        Create Visa from database row.

        Automatically parses JSON fields.

        Args:
            row: Dictionary from database query

        Returns:
            Visa object with all fields populated
        """
        def parse_json(value, default):
            """Parse JSON string or return as-is if already parsed"""
            if isinstance(value, str):
                try:
                    return json.loads(value) if value else default
                except json.JSONDecodeError:
                    return default
            return value if value else default

        return cls(
            id=row.get('id'),
            visa_type=row.get('visa_type', ''),
            country=row.get('country', ''),
            category=row.get('category', ''),
            requirements=parse_json(row.get('requirements'), {}),
            fees=parse_json(row.get('fees'), {}),
            processing_time=row.get('processing_time', ''),
            documents_required=parse_json(row.get('documents_required'), []),
            source_urls=parse_json(row.get('source_urls'), []),
            language=row.get('language', ''),
            version=row.get('version', 1),
            created_at=row.get('created_at')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'visa_type': self.visa_type,
            'country': self.country,
            'category': self.category,
            'requirements': self.requirements,
            'fees': self.fees,
            'processing_time': self.processing_time,
            'documents_required': self.documents_required,
            'source_urls': self.source_urls,
            'language': self.language,
            'version': self.version,
            'created_at': self.created_at
        }

    # Helper properties for easy access
    @property
    def age_range(self) -> str:
        """Get formatted age requirement"""
        age = self.requirements.get('age', {})
        if not age:
            return "No age requirement"

        min_age = age.get('min')
        max_age = age.get('max')

        if min_age and max_age:
            return f"{min_age}-{max_age} years"
        elif min_age:
            return f"{min_age}+ years"
        elif max_age:
            return f"Under {max_age} years"
        return "No age requirement"

    @property
    def education_required(self) -> str:
        """Get education requirement"""
        return self.requirements.get('education', 'Not specified')

    @property
    def experience_required(self) -> int:
        """Get years of experience required"""
        return self.requirements.get('experience_years', 0)

    def matches_query(self, query: str) -> bool:
        """Check if visa matches a search query"""
        query_lower = query.lower()
        return (
            self.country.lower() in query_lower or
            self.category.lower() in query_lower or
            any(word in query_lower for word in self.visa_type.lower().split() if len(word) > 3)
        )


# ============ CRAWLED PAGE ============

@dataclass
class CrawledPage:
    """
    A page crawled from a website.

    Contains the raw content and metadata from crawling.
    """
    url: str
    country: str
    title: str = ""
    content: str = ""
    metadata: Dict = field(default_factory=dict)

    # Database fields
    id: Optional[int] = None
    crawled_at: Optional[str] = None
    version: int = 1

    @classmethod
    def from_db_row(cls, row: dict) -> 'CrawledPage':
        """Create from database row"""
        metadata = row.get('metadata', {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError:
                metadata = {}

        return cls(
            id=row.get('id'),
            url=row.get('url', ''),
            country=row.get('country', ''),
            title=row.get('title', ''),
            content=row.get('content', ''),
            metadata=metadata,
            crawled_at=row.get('crawled_at'),
            version=row.get('version', 1)
        )

    @property
    def breadcrumbs(self) -> List[str]:
        """Get page breadcrumbs"""
        return self.metadata.get('breadcrumbs', [])

    @property
    def links(self) -> List[str]:
        """Get links found on page"""
        return self.metadata.get('links', [])

    @property
    def attachments(self) -> List[Dict]:
        """Get attachments (PDFs, etc.)"""
        return self.metadata.get('attachments', [])


# ============ USER PROFILE ============

@dataclass
class UserProfile:
    """
    A user's profile for visa matching.

    Used by the Matcher service to find suitable visas.
    """
    age: int = 0
    nationality: str = ""
    education: str = ""  # secondary, diploma, bachelors, masters, phd
    profession: str = ""
    experience_years: int = 0
    target_countries: List[str] = field(default_factory=list)
    language_scores: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfile':
        """Create from dictionary"""
        return cls(
            age=data.get('age', 0),
            nationality=data.get('nationality', ''),
            education=data.get('education', ''),
            profession=data.get('profession', ''),
            experience_years=data.get('experience_years', 0),
            target_countries=data.get('target_countries', []),
            language_scores=data.get('language_scores', {})
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


# ============ MATCH RESULT ============

@dataclass
class MatchResult:
    """
    Result of matching a user to a visa.

    Contains the score, eligibility status, and analysis.
    """
    visa: Visa
    score: float  # 0-100
    eligible: bool
    match_level: str  # 'high', 'medium', 'low'
    gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for display"""
        return {
            'visa_type': self.visa.visa_type,
            'country': self.visa.country,
            'category': self.visa.category,
            'eligibility_score': self.score,
            'eligible': self.eligible,
            'match_level': self.match_level,
            'gaps': self.gaps,
            'strengths': self.strengths,
            'fees': self.visa.fees,
            'processing_time': self.visa.processing_time,
            'source_urls': self.visa.source_urls,
            'language': self.visa.language
        }


# ============ HELPER FUNCTIONS ============

def load_visas_from_rows(rows: List[dict]) -> List[Visa]:
    """
    Convert database rows to Visa objects.

    Convenience function for loading multiple visas.

    Args:
        rows: List of dictionaries from database

    Returns:
        List of Visa objects
    """
    return [Visa.from_db_row(row) for row in rows]


def load_pages_from_rows(rows: List[dict]) -> List[CrawledPage]:
    """
    Convert database rows to CrawledPage objects.

    Args:
        rows: List of dictionaries from database

    Returns:
        List of CrawledPage objects
    """
    return [CrawledPage.from_db_row(row) for row in rows]
