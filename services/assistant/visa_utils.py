"""
Visa Utility Functions
Provides document checklist generation, timeline estimation, and cost calculation
"""

from typing import Dict, List, Optional
import json
from pathlib import Path


class VisaDocumentGenerator:
    """Generate document checklists for visa applications"""

    def __init__(self):
        self.common_documents = {
            "all": [
                "Valid passport (minimum 6 months validity)",
                "Passport-sized photos (usually 2)",
                "Birth certificate",
                "Police clearance certificate"
            ],
            "work": [
                "Resume/CV",
                "Educational certificates and transcripts",
                "Employment letters from previous employers",
                "Job offer letter",
                "Proof of professional qualifications"
            ],
            "study": [
                "University acceptance letter",
                "Academic transcripts",
                "Standardized test scores",
                "Proof of financial support",
                "Scholarship letters (if applicable)"
            ],
            "family": [
                "Marriage certificate (if applicable)",
                "Spouse/partner documents",
                "Children's birth certificates",
                "Relationship evidence (photos, communications)",
                "Sponsor's financial documents"
            ],
            "investment": [
                "Business plan",
                "Proof of investment funds",
                "Bank statements (6-12 months)",
                "Company registration documents",
                "Financial projections",
                "Source of funds documentation"
            ],
            "tourist": [
                "Travel itinerary",
                "Hotel reservations",
                "Return flight tickets",
                "Proof of ties to home country",
                "Bank statements",
                "Employment letter"
            ]
        }

    def generate_checklist(self, visa_data: Dict) -> Dict:
        """
        Generate a complete document checklist for a visa

        Args:
            visa_data: Visa information dictionary

        Returns:
            Dictionary with categorized documents
        """
        checklist = {
            "visa_type": visa_data.get("visa_type"),
            "country": visa_data.get("country"),
            "documents": {
                "required": [],
                "recommended": [],
                "optional": []
            }
        }

        # Add visa-specific documents from data
        if "documents_required" in visa_data:
            checklist["documents"]["required"] = visa_data["documents_required"]
        else:
            # Fallback: use common documents
            category = visa_data.get("category", "work")
            checklist["documents"]["required"] = (
                self.common_documents.get("all", []) +
                self.common_documents.get(category, [])
            )

        # Add recommended documents based on category
        category = visa_data.get("category", "work")
        if category == "work":
            checklist["documents"]["recommended"] = [
                "Reference letters from supervisors",
                "Professional licenses/certifications",
                "Portfolio of work (if applicable)",
                "Salary slips from previous employment"
            ]
        elif category == "study":
            checklist["documents"]["recommended"] = [
                "Statement of purpose",
                "Recommendation letters from professors",
                "Previous degree certificates",
                "English language proficiency certificate"
            ]
        elif category == "investment":
            checklist["documents"]["recommended"] = [
                "Tax returns (3-5 years)",
                "Property ownership documents",
                "Investment portfolio",
                "Business references"
            ]

        # Optional documents
        checklist["documents"]["optional"] = [
            "Previous visa copies",
            "Travel history documentation",
            "Additional financial proof",
            "Medical insurance",
            "Cover letter explaining application"
        ]

        return checklist

    def get_checklist_progress(self, checklist: Dict, completed_docs: List[str]) -> Dict:
        """
        Calculate checklist completion progress

        Args:
            checklist: Document checklist dictionary
            completed_docs: List of completed document names

        Returns:
            Progress statistics
        """
        total_required = len(checklist["documents"]["required"])
        completed_required = sum(1 for doc in checklist["documents"]["required"]
                                if any(comp in doc.lower() for comp in [c.lower() for c in completed_docs]))

        return {
            "total_required": total_required,
            "completed": completed_required,
            "remaining": total_required - completed_required,
            "percentage": round((completed_required / total_required * 100) if total_required > 0 else 0, 1)
        }


class VisaTimelineEstimator:
    """Estimate visa processing timelines"""

    def get_timeline(self, visa_data: Dict) -> Dict:
        """
        Get detailed timeline for visa processing

        Args:
            visa_data: Visa information dictionary

        Returns:
            Timeline with stages and estimates
        """
        timeline = {
            "visa_type": visa_data.get("visa_type"),
            "country": visa_data.get("country"),
            "total_time": visa_data.get("processing_time", "Not specified"),
            "stages": []
        }

        # Check if visa has detailed timeline stages
        if "timeline_stages" in visa_data:
            stages_data = visa_data["timeline_stages"]
            for key in sorted(stages_data.keys()):
                stage_name = stages_data[key]
                timeline["stages"].append({
                    "step": key.split("_")[0],
                    "name": stage_name.split("(")[0].strip(),
                    "description": stage_name,
                    "estimated_time": self._extract_time_from_stage(stage_name)
                })
        else:
            # Generic timeline based on category
            category = visa_data.get("category", "work")
            timeline["stages"] = self._get_generic_timeline(category)

        return timeline

    def _extract_time_from_stage(self, stage_description: str) -> str:
        """Extract time estimate from stage description"""
        import re
        time_pattern = r'\(([^)]*(?:week|month|day)[^)]*)\)'
        match = re.search(time_pattern, stage_description)
        if match:
            return match.group(1)
        return "Varies"

    def _get_generic_timeline(self, category: str) -> List[Dict]:
        """Get generic timeline stages for category"""
        generic_timelines = {
            "work": [
                {"step": "1", "name": "Document Preparation", "description": "Gather all required documents", "estimated_time": "2-4 weeks"},
                {"step": "2", "name": "Application Submission", "description": "Submit visa application", "estimated_time": "1-2 days"},
                {"step": "3", "name": "Processing", "description": "Government reviews application", "estimated_time": "4-8 weeks"},
                {"step": "4", "name": "Interview", "description": "Attend visa interview (if required)", "estimated_time": "1-2 weeks"},
                {"step": "5", "name": "Decision", "description": "Receive visa decision", "estimated_time": "1-3 weeks"}
            ],
            "study": [
                {"step": "1", "name": "University Admission", "description": "Get acceptance from university", "estimated_time": "Varies"},
                {"step": "2", "name": "Document Collection", "description": "Gather visa documents", "estimated_time": "2-3 weeks"},
                {"step": "3", "name": "Application", "description": "Submit visa application", "estimated_time": "1 week"},
                {"step": "4", "name": "Interview", "description": "Attend embassy interview", "estimated_time": "1-2 weeks"},
                {"step": "5", "name": "Visa Issuance", "description": "Receive student visa", "estimated_time": "1-2 weeks"}
            ],
            "tourist": [
                {"step": "1", "name": "Documentation", "description": "Prepare required documents", "estimated_time": "1-2 weeks"},
                {"step": "2", "name": "Application", "description": "Submit online/paper application", "estimated_time": "1-3 days"},
                {"step": "3", "name": "Processing", "description": "Application review", "estimated_time": "1-3 weeks"},
                {"step": "4", "name": "Visa Issuance", "description": "Receive visa", "estimated_time": "3-7 days"}
            ]
        }

        return generic_timelines.get(category, generic_timelines["work"])


class VisaCostCalculator:
    """Calculate total visa costs with detailed breakdown"""

    def calculate_costs(self, visa_data: Dict, include_optional: bool = False) -> Dict:
        """
        Calculate total visa costs

        Args:
            visa_data: Visa information dictionary
            include_optional: Include optional costs like premium processing

        Returns:
            Cost breakdown and total
        """
        cost_info = {
            "visa_type": visa_data.get("visa_type"),
            "country": visa_data.get("country"),
            "breakdown": {},
            "total_min": 0,
            "total_max": 0,
            "currency": "USD"  # Default to USD
        }

        # Check if visa has detailed cost breakdown
        if "cost_breakdown" in visa_data:
            breakdown = visa_data["cost_breakdown"]

            for item, cost_str in breakdown.items():
                if item == "total_estimate":
                    continue  # Skip, we'll calculate it

                # Skip optional costs if not included
                if not include_optional and "optional" in cost_str.lower():
                    continue

                cost_range = self._parse_cost(cost_str)
                if cost_range:
                    cost_info["breakdown"][item] = {
                        "description": self._format_item_name(item),
                        "cost": cost_str,
                        "min": cost_range["min"],
                        "max": cost_range["max"],
                        "optional": "optional" in cost_str.lower()
                    }

                    if "optional" not in cost_str.lower():
                        cost_info["total_min"] += cost_range["min"]
                        cost_info["total_max"] += cost_range["max"]
        else:
            # Use basic fees if no breakdown available
            fees = visa_data.get("fees", {})
            for fee_name, fee_value in fees.items():
                cost_range = self._parse_cost(fee_value)
                if cost_range:
                    cost_info["breakdown"][fee_name] = {
                        "description": self._format_item_name(fee_name),
                        "cost": fee_value,
                        "min": cost_range["min"],
                        "max": cost_range["max"],
                        "optional": False
                    }
                    cost_info["total_min"] += cost_range["min"]
                    cost_info["total_max"] += cost_range["max"]

        # Add common additional costs
        cost_info["additional_costs"] = self._get_additional_costs(visa_data.get("category"))

        return cost_info

    def _parse_cost(self, cost_str: str) -> Optional[Dict]:
        """Parse cost string to extract min and max values"""
        import re

        if not cost_str or cost_str in ["Varies", "N/A"]:
            return None

        # Remove currency symbols and commas
        cost_str = cost_str.replace(",", "")

        # Try to find numbers
        numbers = re.findall(r'\d+(?:\.\d+)?', cost_str)

        if not numbers:
            return None

        numbers = [float(n) for n in numbers]

        if len(numbers) == 1:
            return {"min": numbers[0], "max": numbers[0]}
        else:
            return {"min": min(numbers), "max": max(numbers)}

    def _format_item_name(self, item: str) -> str:
        """Format item name for display"""
        return item.replace("_", " ").title()

    def _get_additional_costs(self, category: str) -> List[Dict]:
        """Get common additional costs by category"""
        common_costs = {
            "work": [
                {"item": "Document translations", "cost": "$50-$200 per document"},
                {"item": "Police clearance", "cost": "$20-$100"},
                {"item": "Medical examination", "cost": "$100-$500"},
                {"item": "Courier/shipping fees", "cost": "$20-$50"},
                {"item": "Photos", "cost": "$10-$30"}
            ],
            "study": [
                {"item": "Credential evaluation", "cost": "$100-$300"},
                {"item": "English test (TOEFL/IELTS)", "cost": "$200-$300"},
                {"item": "Medical exam", "cost": "$100-$300"},
                {"item": "Travel to interview", "cost": "Varies"},
                {"item": "Document copies/notarization", "cost": "$20-$100"}
            ],
            "investment": [
                {"item": "Business consultant fees", "cost": "$2000-$10000"},
                {"item": "Accountant fees", "cost": "$1000-$5000"},
                {"item": "Document notarization", "cost": "$100-$500"},
                {"item": "Translation services", "cost": "$200-$1000"}
            ],
            "tourist": [
                {"item": "Travel insurance", "cost": "$50-$200"},
                {"item": "Document copies", "cost": "$10-$30"},
                {"item": "Courier fees", "cost": "$20-$40"}
            ]
        }

        return common_costs.get(category, common_costs["work"])


def load_visa_data() -> List[Dict]:
    """Load all visa data from file"""
    visa_file = Path("data/processed/visas.json")
    if visa_file.exists():
        with open(visa_file, 'r') as f:
            return json.load(f)
    return []


def get_visa_by_type(visa_type: str, country: str = None) -> Optional[Dict]:
    """Get specific visa by type and optionally country"""
    visas = load_visa_data()
    for visa in visas:
        if visa_type.lower() in visa["visa_type"].lower():
            if country is None or visa["country"].lower() == country.lower():
                return visa
    return None


# Example usage functions
def generate_full_visa_package(visa_type: str, country: str = None) -> Dict:
    """
    Generate complete visa package with documents, timeline, and costs

    Args:
        visa_type: Type of visa
        country: Target country (optional)

    Returns:
        Complete package with all information
    """
    visa = get_visa_by_type(visa_type, country)

    if not visa:
        return {"error": "Visa not found"}

    doc_gen = VisaDocumentGenerator()
    timeline_est = VisaTimelineEstimator()
    cost_calc = VisaCostCalculator()

    return {
        "visa_info": {
            "type": visa["visa_type"],
            "country": visa["country"],
            "category": visa["category"]
        },
        "documents": doc_gen.generate_checklist(visa),
        "timeline": timeline_est.get_timeline(visa),
        "costs": cost_calc.calculate_costs(visa),
        "requirements": visa.get("requirements", {}),
        "success_rate": visa.get("success_rate", "N/A"),
        "valid_duration": visa.get("valid_duration", "N/A")
    }
