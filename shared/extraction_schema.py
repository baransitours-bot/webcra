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
