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

        # Get provider from config
        provider = config['llm'].get('provider', 'openai')

        # Initialize based on provider
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not found. Install it with: pip install openai"
            )

        if provider == 'openrouter':
            # OpenRouter configuration
            api_key_env = config['llm']['openrouter']['api_key_env']
            api_key = os.getenv(api_key_env)

            if not api_key:
                raise ValueError(
                    f"OpenRouter API key not found. Set {api_key_env} environment variable.\n"
                    f"Example: export {api_key_env}='your-api-key-here'\n"
                    f"Get your free API key from: https://openrouter.ai/keys"
                )

            base_url = config['llm']['openrouter']['base_url']
            self.model = config['llm']['openrouter']['model']
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.logger.info(f"OpenRouter client initialized with model: {self.model}")

        else:  # Default to OpenAI
            # OpenAI configuration
            api_key_env = config['llm']['openai']['api_key_env']
            api_key = os.getenv(api_key_env)

            if not api_key:
                raise ValueError(
                    f"OpenAI API key not found. Set {api_key_env} environment variable.\n"
                    f"Example: export {api_key_env}='your-api-key-here'\n"
                    f"Get your API key from: https://platform.openai.com/api-keys"
                )

            self.model = config['llm']['openai']['model']
            self.client = OpenAI(api_key=api_key)
            self.logger.info(f"OpenAI client initialized with model: {self.model}")

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
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
