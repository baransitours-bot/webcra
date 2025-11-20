"""
Assistant Engine - CORE LOGIC LAYER

Core business logic for Q&A assistant.
Combines retrieval + LLM for answering questions.
"""

from typing import List, Dict, Optional
from shared.logger import setup_logger
from services.assistant.repository import AssistantRepository
from services.assistant.retriever import ContextRetriever
from services.assistant.enhanced_retriever import EnhancedRetriever
from services.assistant.llm_client import LLMClient


class AssistantEngine:
    """
    Core Q&A logic.

    Responsibilities:
    - Retrieve relevant visas for context
    - Generate answers using LLM
    - Maintain conversation history
    - Format responses

    Does NOT:
    - Access database directly
    - Know about UI
    - Handle configuration loading
    """

    def __init__(self, config: dict, repository: AssistantRepository):
        """
        Initialize engine.

        Args:
            config: Assistant configuration
            repository: Data access layer
        """
        self.config = config
        self.repo = repository
        self.logger = setup_logger('assistant_engine')

        # Initialize components
        self.llm_client = self._init_llm()
        self.retriever = self._init_retriever()

        # Conversation state
        self.conversation_history: List[Dict] = []

    def _init_llm(self) -> Optional[LLMClient]:
        """Initialize LLM client"""
        try:
            client = LLMClient()
            self.logger.info("✅ LLM client initialized")
            return client
        except Exception as e:
            self.logger.warning(f"⚠️ LLM not available: {str(e)[:100]}")
            return None

    def _init_retriever(self):
        """Initialize retriever (enhanced if available, else basic)"""
        use_enhanced = self.config.get('use_enhanced_retrieval', True)

        if use_enhanced:
            try:
                retriever = EnhancedRetriever(self.config)
                self.logger.info("✅ Using enhanced retrieval (hybrid search)")
                return retriever
            except Exception as e:
                self.logger.warning(f"Enhanced retrieval failed: {e}")

        # Fallback to basic retriever
        retriever = ContextRetriever(self.config)
        self.logger.info("Using basic keyword retrieval")
        return retriever

    def ask(self, question: str, user_profile: Dict = None) -> Dict:
        """
        Ask a question and get an answer.

        Args:
            question: User's question
            user_profile: Optional user profile for personalization

        Returns:
            Answer dictionary with response and sources
        """
        if not self.llm_client:
            return {
                'answer': "LLM is not configured. Please set up API key in Settings.",
                'sources': [],
                'error': True
            }

        try:
            # Step 1: Retrieve both visas and general content
            relevant_visas, relevant_general_content = self.retriever.retrieve_all_context(
                question,
                user_profile
            )

            if not relevant_visas and not relevant_general_content:
                return {
                    'answer': "I couldn't find any relevant information for your question. Try rephrasing or asking about immigration, visas, employment, benefits, or services.",
                    'sources': [],
                    'error': False
                }

            # Step 2: Format context for LLM (includes both visas and general content)
            context = self.retriever.format_context_for_llm(relevant_visas, relevant_general_content)

            # Step 3: Build LLM prompt
            system_prompt = self._build_system_prompt()
            user_message = self._build_user_message(question, context, user_profile)

            # Step 4: Get LLM response
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history,
                {"role": "user", "content": user_message}
            ]

            answer = self.llm_client.chat(messages)

            # Step 5: Update conversation history
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Keep only last N messages
            max_history = self.config.get('context', {}).get('max_history', 10)
            if len(self.conversation_history) > max_history:
                self.conversation_history = self.conversation_history[-max_history:]

            # Step 6: Extract sources from both visas and general content
            sources = self._extract_sources(relevant_visas, relevant_general_content)

            return {
                'answer': answer,
                'sources': sources,
                'error': False
            }

        except Exception as e:
            self.logger.error(f"Failed to answer question: {e}")
            return {
                'answer': f"An error occurred: {str(e)}",
                'sources': [],
                'error': True
            }

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM"""
        return """You are an expert immigration assistant helping people understand visa requirements, immigration options, and life in new countries.

Your role:
- Answer questions about visa requirements clearly and accurately
- Provide information about employment, healthcare, benefits, and settlement services
- Use ONLY the information provided in the context (both visa programs and general information)
- If information is not in the context, say "I don't have that information"
- Be specific about requirements (age, education, fees, processing time)
- Provide practical advice when appropriate
- Include application links when available

Guidelines:
- Be friendly and professional
- Use bullet points for clarity
- Cite specific visa types and information sources when relevant
- Don't make assumptions or guess
- If asked about multiple countries, compare them clearly
- For questions about employment, healthcare, benefits, or services, use the general information provided"""

    def _build_user_message(self, question: str, context: str, user_profile: Dict = None) -> str:
        """Build user message with context"""
        message = f"""Context Information:
{context}

"""
        if user_profile:
            message += f"""User Profile:
- Age: {user_profile.get('age', 'N/A')}
- Education: {user_profile.get('education', 'N/A')}
- Experience: {user_profile.get('experience_years', 'N/A')} years
- Target Countries: {', '.join(user_profile.get('target_countries', ['N/A']))}

"""
        message += f"Question: {question}"

        return message

    def _extract_sources(self, visas: List[Dict], general_content: List[Dict] = None) -> List[Dict]:
        """Extract source URLs from visas and general content"""
        sources = []

        # Extract visa sources
        for visa in visas:
            if visa.get('source_urls'):
                sources.append({
                    'type': 'visa',
                    'title': visa['visa_type'],
                    'country': visa['country'],
                    'url': visa['source_urls'][0]
                })

        # Extract general content sources
        if general_content:
            for content in general_content:
                if content.get('source_url'):
                    sources.append({
                        'type': 'general',
                        'title': content['title'],
                        'country': content['country'],
                        'url': content['source_url']
                    })

        return sources

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation reset")

    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history.copy()
