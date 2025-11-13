"""
Semantic Embeddings for Enhanced Retrieval
Uses FREE sentence-transformers model (runs locally, no API costs)
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict
import numpy as np
from shared.logger import setup_logger

class SemanticRetriever:
    """
    Semantic search using sentence-transformers
    100% FREE - runs locally on CPU
    """

    def __init__(self):
        self.logger = setup_logger('semantic_retriever')
        self.model = None
        self.visa_embeddings = {}
        self.embeddings_cache = Path('data/.embeddings_cache.pkl')

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
        if not force_reindex and self.embeddings_cache.exists():
            try:
                with open(self.embeddings_cache, 'rb') as f:
                    self.visa_embeddings = pickle.load(f)
                self.logger.info(f"✅ Loaded {len(self.visa_embeddings)} visa embeddings from cache")
                return
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load cache: {e}. Reindexing...")

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
        self.embeddings_cache.parent.mkdir(parents=True, exist_ok=True)
        with open(self.embeddings_cache, 'wb') as f:
            pickle.dump(self.visa_embeddings, f)

        self.logger.info(f"✅ Indexed {len(self.visa_embeddings)} visas. Cache saved.")

    def search(self, query: str, top_k: int = 10) -> List[tuple]:
        """
        Find most semantically similar visas

        Args:
            query: User query
            top_k: Number of results to return

        Returns:
            List of (similarity_score, visa) tuples, sorted by similarity
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
            similarity = np.dot(query_embedding, data['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding'])
            )
            similarities.append((float(similarity), data['visa']))

        # Sort by similarity (highest first)
        similarities.sort(reverse=True, key=lambda x: x[0])

        return similarities[:top_k]

    def clear_cache(self):
        """Clear embeddings cache"""
        if self.embeddings_cache.exists():
            self.embeddings_cache.unlink()
            self.logger.info("✅ Embeddings cache cleared")
