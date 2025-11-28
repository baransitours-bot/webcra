"""
Semantic Embeddings for Enhanced Retrieval
Uses FREE sentence-transformers model (runs locally, no API costs)

NOW SUPPORTS:
- Visa embeddings (for visa programs)
- General content embeddings (for employment, healthcare, benefits, etc.)
- Unified search across both types
- Separate caching for efficient updates
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from shared.logger import setup_logger

class SemanticRetriever:
    """
    Semantic search using sentence-transformers

    Supports TWO types of content:
    1. Visas - Immigration programs
    2. General Content - Employment, healthcare, settlement services, etc.

    100% FREE - runs locally on CPU
    """

    def __init__(self):
        self.logger = setup_logger('semantic_retriever')
        self.model = None

        # Separate embeddings for visas and general content
        self.visa_embeddings = {}
        self.general_embeddings = {}

        # Separate cache files for efficient updates
        self.visa_cache = Path('data/.visa_embeddings.pkl')
        self.general_cache = Path('data/.general_embeddings.pkl')

        # Lazy load model
        self._model_loaded = False

    def _load_model(self):
        """Load model on first use (lazy loading)"""
        if self._model_loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer

            # Small, fast model (90MB, runs on CPU)
            # Accuracy: 68.06% on semantic similarity tasks
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._model_loaded = True
            self.logger.info("✅ Loaded semantic search model (all-MiniLM-L6-v2)")
        except ImportError:
            self.logger.warning("⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")
            raise ImportError("Install sentence-transformers: pip install sentence-transformers")

    def _visa_to_text(self, visa: Dict) -> str:
        """Convert visa data to searchable text"""
        parts = [
            visa.get('visa_type', ''),
            visa.get('category', ''),
            visa.get('country', ''),
        ]

        # Add requirements as text
        reqs = visa.get('requirements', {})
        if reqs:
            if 'education' in reqs and reqs['education']:
                parts.append(' '.join(reqs['education']))
            if 'work_experience' in reqs and reqs['work_experience']:
                parts.append(f"{reqs['work_experience'].get('years', '')} years experience")

        return ' '.join(str(p) for p in parts if p)

    def index_visas(self, visas: List[Dict], force_reindex: bool = False):
        """
        Create embeddings for all visas

        Args:
            visas: List of visa dictionaries
            force_reindex: If True, regenerate embeddings even if cached
        """
        # Try to load from cache
        if not force_reindex and self.visa_cache.exists():
            try:
                with open(self.visa_cache, 'rb') as f:
                    self.visa_embeddings = pickle.load(f)
                self.logger.info(f"✅ Loaded {len(self.visa_embeddings)} visa embeddings from cache")
                return
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load visa cache: {e}. Reindexing...")

        # Need to index
        self._load_model()

        self.logger.info(f"🔄 Indexing {len(visas)} visas (this may take 1-2 minutes)...")

        self.visa_embeddings = {}

        for visa in visas:
            visa_id = f"{visa.get('country', 'unknown')}_{visa.get('visa_type', 'unknown')}"
            text = self._visa_to_text(visa)

            # Create embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            self.visa_embeddings[visa_id] = {
                'embedding': embedding,
                'visa': visa
            }

        # Save to cache
        self.visa_cache.parent.mkdir(parents=True, exist_ok=True)
        with open(self.visa_cache, 'wb') as f:
            pickle.dump(self.visa_embeddings, f)

        self.logger.info(f"✅ Indexed {len(self.visa_embeddings)} visas. Cache saved.")

    def _general_content_to_text(self, content: Dict) -> str:
        """Convert general content to searchable text"""
        parts = [
            content.get('title', ''),
            content.get('content_type', ''),  # employment, healthcare, benefits, etc.
            content.get('country', ''),
            content.get('summary', ''),
        ]

        # Add key points (most important!)
        key_points = content.get('key_points', [])
        if key_points:
            parts.extend(key_points[:10])  # Top 10 key points

        # Add audience info
        metadata = content.get('metadata', {})
        if metadata.get('audience'):
            parts.append(metadata['audience'])

        # Add topics
        topics = metadata.get('topics', [])
        if topics:
            parts.extend(topics)

        return ' '.join(str(p) for p in parts if p)

    def index_general_content(self, content_list: List[Dict], force_reindex: bool = False):
        """
        Create embeddings for all general content (employment, healthcare, etc.)

        Args:
            content_list: List of general content dictionaries
            force_reindex: If True, regenerate embeddings even if cached
        """
        # Try to load from cache
        if not force_reindex and self.general_cache.exists():
            try:
                with open(self.general_cache, 'rb') as f:
                    self.general_embeddings = pickle.load(f)
                self.logger.info(f"✅ Loaded {len(self.general_embeddings)} general content embeddings from cache")
                return
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load general content cache: {e}. Reindexing...")

        # Need to index
        self._load_model()

        self.logger.info(f"🔄 Indexing {len(content_list)} general content items...")

        self.general_embeddings = {}

        for content in content_list:
            content_id = f"{content.get('country', 'unknown')}_{content.get('title', 'unknown')}"
            text = self._general_content_to_text(content)

            # Create embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            self.general_embeddings[content_id] = {
                'embedding': embedding,
                'content': content
            }

        # Save to cache
        self.general_cache.parent.mkdir(parents=True, exist_ok=True)
        with open(self.general_cache, 'wb') as f:
            pickle.dump(self.general_embeddings, f)

        self.logger.info(f"✅ Indexed {len(self.general_embeddings)} general content items. Cache saved.")

    def index_all(self, visas: List[Dict], general_content: List[Dict], force_reindex: bool = False):
        """
        Index both visas and general content in one call

        Args:
            visas: List of visa dictionaries
            general_content: List of general content dictionaries
            force_reindex: If True, regenerate all embeddings
        """
        self.logger.info(f"🔄 Indexing ALL content: {len(visas)} visas + {len(general_content)} general items")

        # Index both
        if visas:
            self.index_visas(visas, force_reindex)

        if general_content:
            self.index_general_content(general_content, force_reindex)

        total = len(self.visa_embeddings) + len(self.general_embeddings)
        self.logger.info(f"✅ Total indexed: {total} items ({len(self.visa_embeddings)} visas + {len(self.general_embeddings)} general)")

    def search(self, query: str, top_k: int = 10) -> List[tuple]:
        """
        LEGACY METHOD - Find most semantically similar visas only

        For new code, use search_all() to search both visas and general content

        Args:
            query: User query
            top_k: Number of results to return

        Returns:
            List of (similarity_score, visa) tuples, sorted by similarity
        """
        return self.search_visas(query, top_k)

    def search_visas(self, query: str, top_k: int = 10) -> List[Tuple[float, Dict]]:
        """
        Search only visa embeddings

        Args:
            query: User query
            top_k: Number of results

        Returns:
            List of (similarity_score, visa_dict) tuples
        """
        if not self.visa_embeddings:
            self.logger.warning("⚠️  No visa embeddings found. Run index_visas() first.")
            return []

        self._load_model()

        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Calculate similarities
        similarities = []
        for visa_id, data in self.visa_embeddings.items():
            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, data['embedding'])
            similarities.append((float(similarity), data['visa']))

        # Sort by similarity (highest first)
        similarities.sort(reverse=True, key=lambda x: x[0])

        return similarities[:top_k]

    def search_general_content(self, query: str, top_k: int = 10) -> List[Tuple[float, Dict]]:
        """
        Search only general content embeddings

        Args:
            query: User query
            top_k: Number of results

        Returns:
            List of (similarity_score, content_dict) tuples
        """
        if not self.general_embeddings:
            self.logger.warning("⚠️  No general content embeddings found. Run index_general_content() first.")
            return []

        self._load_model()

        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Calculate similarities
        similarities = []
        for content_id, data in self.general_embeddings.items():
            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, data['embedding'])
            similarities.append((float(similarity), data['content']))

        # Sort by similarity (highest first)
        similarities.sort(reverse=True, key=lambda x: x[0])

        return similarities[:top_k]

    def search_all(
        self,
        query: str,
        max_visas: int = 10,
        max_general: int = 5,
        visa_weight: float = 1.0,
        general_weight: float = 1.0
    ) -> Tuple[List[Tuple[float, Dict]], List[Tuple[float, Dict]]]:
        """
        Search BOTH visas and general content with separate limits

        This is the RECOMMENDED method for comprehensive results.

        Args:
            query: User query
            max_visas: Max visa results
            max_general: Max general content results
            visa_weight: Weight for visa scores (for ranking)
            general_weight: Weight for general content scores (for ranking)

        Returns:
            Tuple of (visa_results, general_results)
            - visa_results: List of (score, visa_dict)
            - general_results: List of (score, content_dict)
        """
        visa_results = []
        general_results = []

        # Search visas
        if self.visa_embeddings:
            visa_results = self.search_visas(query, max_visas)
            # Apply weight
            if visa_weight != 1.0:
                visa_results = [(score * visa_weight, visa) for score, visa in visa_results]

        # Search general content
        if self.general_embeddings:
            general_results = self.search_general_content(query, max_general)
            # Apply weight
            if general_weight != 1.0:
                general_results = [(score * general_weight, content) for score, content in general_results]

        self.logger.info(f"🔍 Search results: {len(visa_results)} visas + {len(general_results)} general content")

        return visa_results, general_results

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def get_stats(self) -> Dict:
        """Get embeddings statistics"""
        return {
            'visa_embeddings': len(self.visa_embeddings),
            'general_embeddings': len(self.general_embeddings),
            'total_embeddings': len(self.visa_embeddings) + len(self.general_embeddings),
            'visa_cache_exists': self.visa_cache.exists(),
            'general_cache_exists': self.general_cache.exists(),
            'model_loaded': self._model_loaded
        }

    def clear_cache(self, cache_type: str = 'all'):
        """
        Clear embeddings cache

        Args:
            cache_type: 'all', 'visas', or 'general'
        """
        if cache_type in ['all', 'visas']:
            if self.visa_cache.exists():
                self.visa_cache.unlink()
                self.logger.info("✅ Visa embeddings cache cleared")
                self.visa_embeddings = {}

        if cache_type in ['all', 'general']:
            if self.general_cache.exists():
                self.general_cache.unlink()
                self.logger.info("✅ General content embeddings cache cleared")
                self.general_embeddings = {}

        if cache_type == 'all':
            self.logger.info("✅ All embeddings caches cleared")
