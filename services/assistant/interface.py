"""
Assistant Interface - INTERACTION LAYER

Provides clean APIs for interacting with the assistant.

INTERIOR Interface: Python API for service-to-service communication
EXTERIOR Interface: Used by UI, CLI, and external systems
"""

import yaml
from typing import List, Dict, Callable, Optional
from pathlib import Path

from services.assistant.engine import AssistantEngine
from services.assistant.repository import AssistantRepository
from shared.logger import setup_logger


class AssistantService:
    """
    INTERIOR Interface: Service-to-Service API

    Clean Python API that other services use.
    Handles setup, configuration, and provides simple methods.
    """

    def __init__(self, config_path: str = 'services/assistant/config.yaml'):
        """
        Initialize assistant service.

        Args:
            config_path: Path to config file
        """
        self.logger = setup_logger('assistant_service')

        # Load configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.logger.warning(f"Config not found: {config_path}, using defaults")
            self.config = self._default_config()

        # Initialize layers
        self.repo = AssistantRepository()  # FUEL TRANSPORT
        self.engine = AssistantEngine(self.config, self.repo)  # ENGINE

    def ask(self, question: str, user_profile: Dict = None) -> Dict:
        """
        Ask a question and get an answer.

        Args:
            question: User's question
            user_profile: Optional user profile

        Returns:
            Answer dictionary
        """
        return self.engine.ask(question, user_profile)

    def reset_conversation(self):
        """Reset conversation history"""
        self.engine.reset_conversation()

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.engine.get_conversation_history()

    def get_statistics(self) -> Dict:
        """
        Get assistant statistics.

        Returns:
            Statistics dictionary
        """
        visa_count = self.repo.get_visa_count()
        return {
            'total_visas': visa_count,
            'ready': visa_count > 0 and self.engine.llm_client is not None,
            'llm_available': self.engine.llm_client is not None
        }

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'use_enhanced_retrieval': True,
            'context': {
                'max_visas': 5,
                'max_history': 10
            }
        }


class AssistantController:
    """
    EXTERIOR Interface: UI/CLI Controller

    This is what the UI (Streamlit) and CLI interact with.
    Provides user-friendly methods and streaming support.
    """

    def __init__(self, config_path: str = 'services/assistant/config.yaml'):
        """Initialize controller with service"""
        self.service = AssistantService(config_path)
        self.logger = setup_logger('assistant_controller')

    def chat(
        self,
        question: str,
        user_profile: Dict = None,
        on_start: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> Dict:
        """
        Chat with the assistant (with callbacks for UI).

        Args:
            question: User's question
            user_profile: Optional user profile
            on_start: Called when starting
            on_complete: Called when complete (answer)
            on_error: Called on error (error_message)

        Returns:
            Answer dictionary
        """
        try:
            # Validate
            if not question or not question.strip():
                if on_error:
                    on_error("Please enter a question")
                return {
                    'answer': "Please enter a question.",
                    'sources': [],
                    'error': True
                }

            # Notify start
            if on_start:
                on_start()

            # Get answer
            result = self.service.ask(question, user_profile)

            # Notify complete
            if on_complete:
                on_complete(result)

            return result

        except Exception as e:
            self.logger.error(f"Chat failed: {e}")
            if on_error:
                on_error(str(e))
            return {
                'answer': f"An error occurred: {str(e)}",
                'sources': [],
                'error': True
            }

    def validate_setup(self) -> Dict:
        """
        Validate that assistant is ready to use.

        Returns:
            Validation result
        """
        stats = self.service.get_statistics()
        errors = []

        if not stats['llm_available']:
            errors.append("LLM not configured. Set API key in Settings.")

        if stats['total_visas'] == 0:
            errors.append("No visa data found. Run Crawler and Classifier first.")

        return {
            'ready': len(errors) == 0,
            'errors': errors,
            'stats': stats
        }

    def reset_conversation(self):
        """Reset conversation history"""
        self.service.reset_conversation()

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.service.get_conversation_history()

    def export_conversation(self, filepath: str):
        """
        Export conversation to file.

        Args:
            filepath: Output file path
        """
        import json

        history = self.get_conversation_history()
        with open(filepath, 'w') as f:
            json.dump(history, f, indent=2)

        self.logger.info(f"Exported conversation to {filepath}")

    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.service.config

    def get_statistics(self) -> Dict:
        """Get assistant statistics"""
        return self.service.get_statistics()


# Convenience functions for quick access

def ask(question: str, user_profile: Dict = None) -> Dict:
    """
    Quick function to ask a question.

    Args:
        question: User's question
        user_profile: Optional user profile

    Returns:
        Answer dictionary
    """
    service = AssistantService()
    return service.ask(question, user_profile)
