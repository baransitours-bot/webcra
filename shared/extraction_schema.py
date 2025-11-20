"""
Configurable Extraction Schema for Classifier
Defines what fields the LLM should extract from visa pages
"""

from typing import Dict, List

# ============ EXTRACTION SCHEMA PRESETS ============

SCHEMA_PRESETS = {
    "basic": {
        "name": "Basic",
        "description": "Essential visa information only (fast, low cost)",
        "fields": {
            "visa_type": {"enabled": True, "required": True},
            "country": {"enabled": True, "required": True},
            "category": {"enabled": True, "required": False},
            "requirements": {
                "enabled": True,
                "subfields": {
                    "age": True,
                    "education": True,
                    "experience_years": False,
                    "language": False,
                    "skills": False,
                    "other": False
                }
            },
            "fees": {
                "enabled": True,
                "subfields": {
                    "application_fee": True,
                    "total_estimated": False
                }
            },
            "processing_time": {"enabled": True},
            "documents_required": {"enabled": False}
        }
    },

    "standard": {
        "name": "Standard",
        "description": "Balanced extraction (recommended for most use cases)",
        "fields": {
            "visa_type": {"enabled": True, "required": True},
            "country": {"enabled": True, "required": True},
            "category": {"enabled": True, "required": False},
            "requirements": {
                "enabled": True,
                "subfields": {
                    "age": True,
                    "education": True,
                    "experience_years": True,
                    "language": True,
                    "skills": True,
                    "occupation": True,
                    "other": True
                }
            },
            "fees": {
                "enabled": True,
                "subfields": {
                    "application_fee": True,
                    "biometrics_fee": True,
                    "processing_fee": True,
                    "total_estimated": True,
                    "currency": True
                }
            },
            "processing_time": {"enabled": True},
            "documents_required": {"enabled": True},
            "eligibility": {
                "enabled": True,
                "subfields": {
                    "must_have": True,
                    "recommended": True
                }
            },
            "benefits": {
                "enabled": True,
                "subfields": {
                    "work_rights": True,
                    "study_rights": True,
                    "family_inclusion": True,
                    "pathway_to_pr": True,
                    "duration": True
                }
            }
        }
    },

    "comprehensive": {
        "name": "Comprehensive",
        "description": "Extract all available information (slower, higher cost)",
        "fields": {
            "visa_type": {"enabled": True, "required": True},
            "country": {"enabled": True, "required": True},
            "category": {"enabled": True, "required": False},
            "requirements": {
                "enabled": True,
                "subfields": {
                    "age": True,
                    "education": True,
                    "experience_years": True,
                    "language": True,
                    "skills": True,
                    "occupation": True,
                    "health": True,
                    "character": True,
                    "other": True
                }
            },
            "fees": {
                "enabled": True,
                "subfields": {
                    "application_fee": True,
                    "biometrics_fee": True,
                    "processing_fee": True,
                    "medical_fee": True,
                    "translation_fee": True,
                    "service_fee": True,
                    "total_estimated": True,
                    "currency": True
                }
            },
            "cost_breakdown": {
                "enabled": True,
                "subfields": {
                    "government_fees": True,
                    "third_party_costs": True,
                    "optional_costs": True
                }
            },
            "processing_time": {"enabled": True},
            "timeline_stages": {
                "enabled": True,
                "subfields": {
                    "submission": True,
                    "review": True,
                    "interview": True,
                    "decision": True,
                    "issuance": True
                }
            },
            "documents_required": {"enabled": True},
            "eligibility": {
                "enabled": True,
                "subfields": {
                    "must_have": True,
                    "recommended": True,
                    "disqualifiers": True
                }
            },
            "benefits": {
                "enabled": True,
                "subfields": {
                    "work_rights": True,
                    "study_rights": True,
                    "family_inclusion": True,
                    "pathway_to_pr": True,
                    "duration": True,
                    "travel_freedom": True,
                    "social_benefits": True
                }
            },
            "restrictions": {"enabled": True},
            "renewal": {
                "enabled": True,
                "subfields": {
                    "renewable": True,
                    "max_renewals": True,
                    "renewal_fee": True,
                    "renewal_requirements": True
                }
            },
            "conditions": {"enabled": True},
            "appeal_process": {"enabled": True}
        }
    }
}


def build_extraction_prompt(schema_config: Dict, text: str, country: str) -> str:
    """
    Build LLM extraction prompt based on configured schema.

    Args:
        schema_config: Schema configuration (from ConfigManager)
        text: Page content to extract from
        country: Country name

    Returns:
        LLM prompt string
    """
    # Truncate text if too long
    text_sample = text[:8000] if len(text) > 8000 else text

    # Build JSON schema dynamically
    json_schema = {}
    field_descriptions = []

    fields = schema_config.get('fields', {})

    for field_name, field_config in fields.items():
        if not field_config.get('enabled', False):
            continue

        # Handle nested fields
        if 'subfields' in field_config:
            subfield_schema = {}
            for subfield, enabled in field_config['subfields'].items():
                if enabled:
                    subfield_schema[subfield] = "null or value"
            json_schema[field_name] = subfield_schema
        else:
            json_schema[field_name] = "null or value"

    # Build field descriptions
    if fields.get('visa_type', {}).get('enabled'):
        field_descriptions.append('- visa_type: Name of the visa/immigration program')
    if fields.get('category', {}).get('enabled'):
        field_descriptions.append('- category: Type (work|study|family|business|tourist|permanent|temporary)')
    if fields.get('requirements', {}).get('enabled'):
        field_descriptions.append('- requirements: Eligibility requirements')
    if fields.get('fees', {}).get('enabled'):
        field_descriptions.append('- fees: All costs and fees')
    if fields.get('processing_time', {}).get('enabled'):
        field_descriptions.append('- processing_time: How long processing takes')
    if fields.get('documents_required', {}).get('enabled'):
        field_descriptions.append('- documents_required: Required documents list')
    if fields.get('timeline_stages', {}).get('enabled'):
        field_descriptions.append('- timeline_stages: Application timeline by stage')
    if fields.get('benefits', {}).get('enabled'):
        field_descriptions.append('- benefits: Rights and benefits of this visa')
    if fields.get('restrictions', {}).get('enabled'):
        field_descriptions.append('- restrictions: Conditions and restrictions')
    if fields.get('renewal', {}).get('enabled'):
        field_descriptions.append('- renewal: Renewal/extension information')

    prompt = f"""Extract visa/immigration program information from this webpage content.

Country: {country}

Content:
{text_sample}

Extract the following information in JSON format:
{json_schema}

Field Descriptions:
{chr(10).join(field_descriptions)}

Rules:
1. Only extract if this is clearly about a visa/immigration program
2. Return null for fields you cannot find
3. Be precise - don't guess or infer
4. If NOT a visa page, return: {{"visa_type": null}}
5. Extract ALL enabled fields where information is available
6. For fees, include currency if mentioned
7. For timeline_stages, list stages with durations if mentioned
8. Be comprehensive but accurate

Return ONLY valid JSON, no other text."""

    return prompt


def get_default_schema() -> str:
    """Get default schema preset name"""
    return "standard"


# ============ GENERAL CONTENT EXTRACTION SCHEMA ============

GENERAL_CONTENT_TYPES = [
    "guide",        # How-to guides and instructions
    "faq",          # Frequently asked questions
    "process",      # Application or procedural steps
    "requirements", # General document/eligibility requirements
    "timeline",     # Time expectations and deadlines
    "overview"      # General information or introduction
]


def build_general_content_prompt(text: str, country: str) -> str:
    """
    Build LLM extraction prompt for general immigration content.

    Args:
        text: Page content to extract from
        country: Country name

    Returns:
        LLM prompt string for general content extraction
    """
    text_sample = text[:8000] if len(text) > 8000 else text

    prompt = f"""Extract general immigration information from this webpage content.

Country: {country}

Content:
{text_sample}

This page may contain GENERAL IMMIGRATION INFORMATION (not specific visa details).

Extract the following information in JSON format:
{{
    "content_type": "guide|faq|process|requirements|timeline|overview",
    "title": "Descriptive title of the content",
    "summary": "200-word summary of key information",
    "key_points": ["List", "of", "5-10", "main", "takeaways"],
    "content": "Full content text (cleaned)",
    "application_links": [
        {{"label": "Apply here", "url": "https://example.com/apply"}},
        {{"label": "More info", "url": "https://example.com/info"}}
    ],
    "metadata": {{
        "audience": "skilled_workers|students|families|general",
        "difficulty": "beginner|intermediate|advanced",
        "topics": ["immigration", "work_permit", "study", "pr", "citizenship"]
    }}
}}

Content Type Definitions:
- guide: How-to guides, step-by-step instructions
- faq: Frequently asked questions and answers
- process: Application procedures, process descriptions
- requirements: General document or eligibility requirements
- timeline: Time expectations, deadlines, processing stages
- overview: General information, introductions, high-level summaries

Rules:
1. Extract if this contains general immigration guidance or information
2. The "summary" should be 150-200 words covering main points
3. The "key_points" should be 5-10 actionable takeaways
4. Include ALL application links and important URLs in "application_links"
5. Set "audience" based on who this content is for
6. Set "difficulty" based on complexity level
7. Add relevant "topics" tags from the list
8. If NOT an immigration content page, return: {{"content_type": null}}

Return ONLY valid JSON, no other text."""

    return prompt


def build_dual_extraction_prompt(text: str, country: str, visa_schema: Dict) -> str:
    """
    Build combined extraction prompt for BOTH visa and general content.
    Returns array with both types if both are present.

    Args:
        text: Page content to extract from
        country: Country name
        visa_schema: Visa extraction schema config

    Returns:
        LLM prompt string for dual extraction
    """
    text_sample = text[:8000] if len(text) > 8000 else text

    # Build visa fields from schema
    visa_fields = []
    fields = visa_schema.get('fields', {})
    if fields.get('visa_type', {}).get('enabled'):
        visa_fields.append('- visa_type: Name of the visa/immigration program')
    if fields.get('category', {}).get('enabled'):
        visa_fields.append('- category: Type (work|study|family|business|tourist|permanent|temporary)')
    if fields.get('requirements', {}).get('enabled'):
        visa_fields.append('- requirements: Eligibility requirements (age, education, etc.)')
    if fields.get('fees', {}).get('enabled'):
        visa_fields.append('- fees: All costs and fees')
    if fields.get('processing_time', {}).get('enabled'):
        visa_fields.append('- processing_time: How long processing takes')
    if fields.get('documents_required', {}).get('enabled'):
        visa_fields.append('- documents_required: Required documents list')

    prompt = f"""Extract information from this Canadian government webpage.

Country: {country}

Content:
{text_sample}

This page may contain:
1. SPECIFIC VISA/PROGRAM information (visa types, requirements, fees)
2. GENERAL VALUABLE INFORMATION (guides, FAQs, processes, benefits, services, employment, healthcare, social programs, travel, settlement)
3. BOTH types of information
4. NEITHER (truly irrelevant page)

Extract and return as a JSON ARRAY with objects for each type found:

[
    {{
        "type": "visa",
        "data": {{
            "visa_type": "Name of visa",
            "category": "work|study|family|business|tourist|permanent|temporary",
            "requirements": {{...}},
            "fees": {{...}},
            "processing_time": "...",
            "documents_required": [...]
        }}
    }},
    {{
        "type": "general",
        "data": {{
            "content_type": "guide|faq|process|requirements|timeline|overview",
            "title": "Page title",
            "summary": "200-word summary",
            "key_points": ["point 1", "point 2", ...],
            "content": "Full content",
            "application_links": [{{"label": "...", "url": "..."}}],
            "metadata": {{
                "audience": "skilled_workers|students|families|general|newcomers|residents",
                "difficulty": "beginner|intermediate|advanced",
                "topics": ["immigration", "work_permit", "employment", "healthcare", "benefits", "education", "settlement", "travel", ...]
            }}
        }}
    }}
]

Visa Fields to Extract:
{chr(10).join(visa_fields)}

General Content Types:
- guide: How-to guides, step-by-step instructions
- faq: Frequently asked questions
- process: Application procedures, how things work
- requirements: General eligibility/document requirements
- timeline: Time expectations and deadlines
- overview: General information, introductions, program overviews

Rules:
1. Return ARRAY with 0, 1, or 2 objects depending on what's found
2. If page has SPECIFIC VISA info → include visa object
3. If page has ANY VALUABLE INFORMATION (immigration, employment, benefits, healthcare, services, settlement, travel) → include general object
4. If page has BOTH → include both objects in array
5. If page has NEITHER (only navigation, footers, truly empty) → return empty array []
6. For visa: extract specific immigration program details (fees, requirements, etc.)
7. For general: extract ANY valuable government information - employment, benefits, healthcare, social programs, immigration processes, settlement info, travel info, etc.
8. Include ALL application links in general content (even if URL is not in text, include label)
9. Be VERY inclusive - if page has useful information for someone moving to/living in Canada, extract it
10. Default to EXTRACTING rather than skipping - when uncertain, include it

Return ONLY valid JSON array, no other text."""

    return prompt


def validate_schema(schema: Dict) -> tuple:
    """
    Validate extraction schema configuration.

    Returns:
        (is_valid: bool, errors: List[str])
    """
    errors = []

    if 'fields' not in schema:
        errors.append("Schema must have 'fields' key")
        return False, errors

    fields = schema['fields']

    # Check required fields
    if not fields.get('visa_type', {}).get('enabled'):
        errors.append("visa_type field is required and must be enabled")

    if not fields.get('country', {}).get('enabled'):
        errors.append("country field is required and must be enabled")

    # Check at least one field is enabled
    enabled_count = sum(1 for f in fields.values() if f.get('enabled', False))
    if enabled_count < 2:
        errors.append("At least visa_type and country must be enabled")

    return len(errors) == 0, errors
