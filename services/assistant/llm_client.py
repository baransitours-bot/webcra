"""
LLM Client
Handles communication with OpenAI/Anthropic APIs
"""

import os
from shared.logger import setup_logger

class LLMClient:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger('llm_client')

        # Check if API key is set
        api_key = os.getenv(config['api_key_env'])
        if not api_key:
            raise ValueError(
                f"API key not found. Set {config['api_key_env']} environment variable.\n"
                f"Example: export {config['api_key_env']}='your-api-key-here'"
            )

        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.logger.info("OpenAI client initialized successfully")
        except ImportError:
            raise ImportError(
                "OpenAI library not found. Install it with: pip install openai"
            )

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.config['llm']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config['llm']['temperature'],
                max_tokens=self.config['llm']['max_tokens']
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error generating answer: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}\nPlease try again or check your API key."
