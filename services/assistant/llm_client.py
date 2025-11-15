"""
LLM Client - Updated to use ConfigManager
Handles communication with OpenAI/OpenRouter APIs
"""

import os
from shared.logger import setup_logger


class LLMClient:
    def __init__(self, config=None):
        """
        Initialize LLM client

        Args:
            config: Can be:
                - ConfigManager instance (recommended)
                - Dict with traditional structure (backward compatible)
                - None (will create ConfigManager automatically)
        """
        self.logger = setup_logger('llm_client')

        # Import here to avoid circular dependency
        from shared.config_manager import get_config

        # Determine if we got ConfigManager or dict
        if config is None:
            # Auto-create ConfigManager
            self.config_manager = get_config()
            self.use_config_manager = True
        elif hasattr(config, 'get') and hasattr(config, 'get_api_key'):
            # It's a ConfigManager instance
            self.config_manager = config
            self.use_config_manager = True
        else:
            # It's a traditional dict config (backward compatible)
            self.config_dict = config
            self.use_config_manager = False

        # Get LLM configuration
        if self.use_config_manager:
            provider = self.config_manager.get('llm.provider', 'openrouter')
            model = self.config_manager.get('llm.model', 'google/gemini-2.0-flash-001:free')
            api_key = self.config_manager.get_api_key(provider)

            if not api_key:
                raise ValueError(
                    f"{provider.title()} API key not found!\n\n"
                    f"Quick fix:\n"
                    f"1. Go to Settings page (⚙️) in the UI\n"
                    f"2. Tab 3 → API Key Quick Setup\n"
                    f"3. Paste your {provider} API key and save\n\n"
                    f"Or create .env file:\n"
                    f"   {provider.upper()}_API_KEY=your-key-here\n\n"
                    f"Get FREE OpenRouter key: https://openrouter.ai/keys"
                )

            temperature = self.config_manager.get('llm.temperature', 0.3)
            max_tokens = self.config_manager.get('llm.max_tokens', 2000)

        else:
            # Backward compatible - use dict config
            provider = self.config_dict['llm'].get('provider', 'openai')
            api_key_env = self.config_dict['llm'][provider]['api_key_env']

            # Support direct key or env variable
            if api_key_env.startswith('sk-'):
                api_key = api_key_env
            else:
                api_key = os.getenv(api_key_env)
                if not api_key:
                    raise ValueError(
                        f"{provider.title()} API key not found. Set {api_key_env} environment variable."
                    )

            model = self.config_dict['llm'][provider]['model']
            temperature = self.config_dict['llm'].get('temperature', 0.3)
            max_tokens = self.config_dict['llm'].get('max_tokens', 2000)

        # Initialize OpenAI client
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not found. Install it with: pip install openai"
            )

        # Set up client based on provider
        if provider == 'openrouter':
            base_url = "https://openrouter.ai/api/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.logger.info(f"✅ OpenRouter initialized: {model}")
        else:
            self.client = OpenAI(api_key=api_key)
            self.logger.info(f"✅ OpenAI initialized: {model}")

        # Store settings
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider = provider

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"LLM API error: {str(e)}")
            raise

    def chat(self, messages: list, stream: bool = False) -> str:
        """
        Chat with LLM

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            stream: Whether to stream response (not implemented yet)

        Returns:
            Response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"LLM chat error: {str(e)}")
            raise
