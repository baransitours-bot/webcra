"""
Assistant Repository - FUEL TRANSPORT LAYER

Handles data flow for the assistant service.
Gets visas and general content for Q&A, optionally saves conversations.
"""

from typing import List, Optional
from shared.database import Database
from shared.models import Visa, GeneralContent


class AssistantRepository:
    """
    Data access layer for assistant service.

    Responsibilities:
    - Fetch visas for context
    - Fetch general content for context
    - Save conversations (optional)
    - Get embeddings
    """

    def __init__(self):
        self.db = Database()

    def get_visas(self, country: Optional[str] = None) -> List[Visa]:
        """
        Get visas for Q&A context.

        Args:
            country: Optional country filter

        Returns:
            List of Visa objects
        """
        return self.db.get_visas(country=country)

    def get_visas_as_dicts(self, country: Optional[str] = None) -> List[dict]:
        """
        Get visas as dictionaries (for backward compatibility with retrievers).

        Args:
            country: Optional country filter

        Returns:
            List of visa dictionaries
        """
        visas = self.get_visas(country)
        return [visa.to_dict() for visa in visas]

    def get_visa_count(self) -> int:
        """Get total number of visas"""
        return len(self.db.get_visas())

    def get_general_content(self, country: Optional[str] = None) -> List[GeneralContent]:
        """
        Get general immigration content for Q&A context.

        Args:
            country: Optional country filter

        Returns:
            List of GeneralContent objects
        """
        return self.db.get_general_content(country=country)

    def get_general_content_as_dicts(self, country: Optional[str] = None) -> List[dict]:
        """
        Get general content as dictionaries (for backward compatibility with retrievers).

        Args:
            country: Optional country filter

        Returns:
            List of general content dictionaries
        """
        content_list = self.get_general_content(country)
        return [content.to_dict() for content in content_list]

    def get_general_content_count(self) -> int:
        """Get total number of general content items"""
        return len(self.db.get_general_content())

    def save_conversation(self, messages: List[dict], metadata: dict = None):
        """
        Save conversation for audit/history (optional feature).

        Args:
            messages: List of conversation messages
            metadata: Optional metadata
        """
        # This could be implemented if we add a conversations table
        pass

    def get_embeddings(self, model_name: str = "all-MiniLM-L6-v2") -> List[dict]:
        """
        Get stored embeddings for semantic search.

        Args:
            model_name: Embedding model name

        Returns:
            List of embeddings with visa info
        """
        return self.db.get_embeddings(model_name)
