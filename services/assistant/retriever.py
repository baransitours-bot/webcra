"""
Context Retriever
Retrieves relevant visa information for LLM context
"""

from typing import List, Dict
from shared.database import DataStore
from shared.logger import setup_logger

class ContextRetriever:
    def __init__(self, config):
        self.config = config
        self.data_store = DataStore()
        self.logger = setup_logger('retriever')

    def retrieve_relevant_visas(self, query: str, user_profile: Dict = None) -> List[Dict]:
        """Retrieve visas relevant to the query"""
        # Load all visas
        all_visas = self.data_store.load_structured_visas()

        if not all_visas:
            self.logger.warning("No structured visa data found")
            return []

        # Simple keyword-based filtering
        query_lower = query.lower()
        relevant_visas = []

        for visa in all_visas:
            # Check if query mentions the country
            if visa['country'].lower() in query_lower:
                relevant_visas.append(visa)
                continue

            # Check if query mentions visa category
            if visa.get('category', '').lower() in query_lower:
                relevant_visas.append(visa)
                continue

            # Check visa type
            visa_type_words = visa['visa_type'].lower().split()
            if any(word in query_lower for word in visa_type_words if len(word) > 3):
                relevant_visas.append(visa)

        # If user profile provided, prioritize matching visas
        if user_profile and relevant_visas:
            # Sort by basic match (this is simplified)
            def match_score(visa):
                score = 0
                requirements = visa.get('requirements', {})

                # Check age
                if requirements.get('age'):
                    age_req = requirements['age']
                    user_age = user_profile.get('age', 0)
                    if age_req.get('min') and user_age >= age_req['min']:
                        score += 1
                    if age_req.get('max') and user_age <= age_req['max']:
                        score += 1

                # Check education
                if requirements.get('education'):
                    if user_profile.get('education', '').lower() == requirements['education'].lower():
                        score += 2

                return score

            relevant_visas.sort(key=match_score, reverse=True)

        # Limit to max visas
        return relevant_visas[:self.config['context']['max_visas']]

    def format_context_for_llm(self, visas: List[Dict]) -> str:
        """Format visa information for LLM context"""
        if not visas:
            return "No relevant visa information found in the database."

        context_parts = []

        for i, visa in enumerate(visas, 1):
            context = f"""
Visa {i}: {visa['visa_type']}
Country: {visa['country']}
Category: {visa.get('category', 'N/A')}

Requirements:
"""
            # Add requirements
            reqs = visa.get('requirements', {})
            if reqs.get('age'):
                age_req = reqs['age']
                if age_req.get('min') and age_req.get('max'):
                    age_str = f"Age {age_req['min']}-{age_req['max']}"
                elif age_req.get('min'):
                    age_str = f"Age {age_req['min']}+"
                elif age_req.get('max'):
                    age_str = f"Age under {age_req['max']}"
                else:
                    age_str = "No specific age requirement"
                context += f"- {age_str}\n"

            if reqs.get('education'):
                context += f"- Education: {reqs['education']}\n"

            if reqs.get('experience_years'):
                context += f"- Experience: {reqs['experience_years']} years\n"

            # Add language
            if visa.get('language'):
                context += f"\nLanguage: {visa['language']}\n"

            # Add fees
            if visa.get('fees'):
                context += f"\nFees: {visa['fees']}\n"

            # Add processing time
            if visa.get('processing_time'):
                context += f"Processing Time: {visa['processing_time']}\n"

            # Add source
            if visa.get('source_urls'):
                context += f"\nSource: {visa['source_urls'][0]}\n"

            context_parts.append(context)

        return "\n---\n".join(context_parts)
