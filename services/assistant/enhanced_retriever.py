"""
Enhanced Context Retriever with Hybrid Search

Provides better search results using:
- Semantic search (sentence-transformers) - optional
- Keyword search (always available)
- Metadata filtering
- Reranking (cross-encoder) - optional

All models run locally - 100% FREE
Falls back gracefully if models not installed.
"""

from typing import List, Dict, Tuple
import re
from shared.database import Database
from shared.models import Visa, GeneralContent
from shared.logger import setup_logger


class EnhancedRetriever:
    """
    Enhanced retrieval using hybrid search + reranking.

    Combines semantic and keyword search for better results.
    Falls back to keyword-only if models not installed.
    """

    def __init__(self, config):
        self.config = config
        self.db = Database()
        self.logger = setup_logger('enhanced_retriever')

        # Initialize optional components
        self.semantic_retriever = self._init_semantic_search()
        self.reranker = self._init_reranker()

        # Load existing embeddings from cache (fast!)
        # Only index if caches don't exist (slow, only first time)
        if self.semantic_retriever:
            self._load_or_index_content()

    def _init_semantic_search(self):
        """Try to initialize semantic search"""
        try:
            from services.assistant.embeddings import SemanticRetriever
            retriever = SemanticRetriever()
            self.logger.info("Semantic search enabled")
            return retriever
        except Exception as e:
            self.logger.info(f"Semantic search not available: {str(e)[:50]}")
            self.logger.info("Using keyword-only search (works fine!)")
            return None

    def _init_reranker(self):
        """Try to initialize reranker"""
        try:
            from sentence_transformers import CrossEncoder
            reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            self.logger.info("Reranking enabled")
            return reranker
        except Exception as e:
            self.logger.info(f"Reranking not available: {str(e)[:50]}")
            return None

    def _load_or_index_content(self):
        """
        Load embeddings from cache if exist, otherwise index content.

        This is MUCH faster than always indexing:
        - Loading from cache: <1 second
        - Indexing from scratch: 1-2 minutes

        Only indexes if:
        1. No cache files exist, OR
        2. Cache files exist but are empty/corrupted
        """
        try:
            # Try to load from existing caches (FAST!)
            visa_cache_exists = self.semantic_retriever.visa_cache.exists()
            general_cache_exists = self.semantic_retriever.general_cache.exists()

            # Load visas from cache if possible
            if visa_cache_exists:
                try:
                    import pickle
                    with open(self.semantic_retriever.visa_cache, 'rb') as f:
                        self.semantic_retriever.visa_embeddings = pickle.load(f)
                    self.logger.info(f"✅ Loaded {len(self.semantic_retriever.visa_embeddings)} visa embeddings from cache")
                except Exception as e:
                    self.logger.warning(f"Failed to load visa cache: {e}. Will re-index.")
                    visa_cache_exists = False

            # Load general content from cache if possible
            if general_cache_exists:
                try:
                    import pickle
                    with open(self.semantic_retriever.general_cache, 'rb') as f:
                        self.semantic_retriever.general_embeddings = pickle.load(f)
                    self.logger.info(f"✅ Loaded {len(self.semantic_retriever.general_embeddings)} general embeddings from cache")
                except Exception as e:
                    self.logger.warning(f"Failed to load general cache: {e}. Will re-index.")
                    general_cache_exists = False

            # Only index if caches don't exist or failed to load
            if not visa_cache_exists or not general_cache_exists:
                self.logger.info("⚠️ Embeddings not cached. Indexing content (this will take 1-2 minutes)...")
                self._index_all_content()

        except Exception as e:
            self.logger.error(f"Failed to load or index content: {e}")

    def _index_all_content(self):
        """Index both visas AND general content for semantic search"""
        try:
            # Get visas
            visas = self.db.get_visas()
            visa_dicts = [v.to_dict() for v in visas] if visas else []

            # Get general content
            general_content = self.db.get_general_content()
            content_dicts = [c.to_dict() for c in general_content] if general_content else []

            # Index both types
            if visa_dicts or content_dicts:
                self.semantic_retriever.index_all(visa_dicts, content_dicts, force_reindex=False)
                self.logger.info(f"✅ Indexed {len(visa_dicts)} visas + {len(content_dicts)} general content items")
            else:
                self.logger.warning("⚠️ No content to index. Run Crawler + Classifier first.")
        except Exception as e:
            self.logger.error(f"Failed to index content: {e}")

    # ============ SEARCH METHODS ============

    def retrieve_relevant_visas(self, query: str, user_profile: Dict = None) -> List[Dict]:
        """
        Retrieve visas using enhanced hybrid search.

        Pipeline:
        1. Load visas from database
        2. Extract metadata filters (country, category)
        3. Filter by metadata
        4. Search (hybrid or keyword-only)
        5. Rerank top results
        6. Return final results
        """
        # Load all visas
        all_visas = self.db.get_visas()

        if not all_visas:
            self.logger.warning("No visa data found")
            return []

        # Convert to dicts for processing
        visa_dicts = [v.to_dict() for v in all_visas]

        # Step 1: Extract and apply filters
        filters = self._extract_filters(query)
        if filters:
            self.logger.info(f"Applying filters: {filters}")

        filtered = self._apply_filters(visa_dicts, filters)

        if not filtered:
            self.logger.warning(f"No visas match filters, using all")
            filtered = visa_dicts

        # Step 2: Search
        if self.semantic_retriever:
            candidates = self._hybrid_search(query, filtered)
            self.logger.info(f"Hybrid search: {len(candidates)} candidates")
        else:
            candidates = self._keyword_search(query, filtered)
            self.logger.info(f"Keyword search: {len(candidates)} candidates")

        # Step 3: Rerank
        max_results = self.config['context']['max_visas']
        results = self._rerank(query, candidates, max_results)

        self.logger.info(f"Returning {len(results)} visas")
        return results

    def retrieve_relevant_general_content(self, query: str) -> List[Dict]:
        """
        Retrieve general content relevant to the query.

        Uses SEMANTIC search if available, falls back to keyword search.

        Args:
            query: User's question or search terms

        Returns:
            List of general content dictionaries
        """
        # Load all general content
        all_content = self.db.get_general_content()

        if not all_content:
            self.logger.warning("No general content found in database")
            return []

        # Convert to dicts for processing
        content_dicts = [c.to_dict() for c in all_content]

        max_content = self.config['context'].get('max_general_content', 5)

        # Try semantic search first (if available)
        if self.semantic_retriever:
            try:
                semantic_results = self.semantic_retriever.search_general_content(query, top_k=max_content)
                if semantic_results:
                    results = [content for _, content in semantic_results]
                    self.logger.info(f"🔍 Semantic search: {len(results)} general content items")
                    return results
            except Exception as e:
                self.logger.warning(f"Semantic search failed, falling back to keyword: {e}")

        # Fallback to keyword search
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        scored = []
        for content in content_dicts:
            score = 0.0

            # Country match
            if content['country'].lower() in query_lower:
                score += 3.0

            # Content type match
            if content.get('content_type', '').lower() in query_lower:
                score += 2.0

            # Title match
            title_words = set(re.findall(r'\w+', content['title'].lower()))
            score += len(query_words & title_words) * 0.8

            # Key points match
            key_points_text = ' '.join(content.get('key_points', [])).lower()
            for word in query_words:
                if len(word) > 3 and word in key_points_text:
                    score += 0.5

            # Topics match
            topics = content.get('metadata', {}).get('topics', [])
            for topic in topics:
                if topic.lower() in query_lower:
                    score += 1.0

            if score > 0:
                scored.append((score, content))

        # Sort by score
        scored.sort(reverse=True, key=lambda x: x[0])

        # Limit results
        results = [content for _, content in scored[:max_content]]

        self.logger.info(f"📝 Keyword search: {len(results)} general content items")
        return results

    def retrieve_all_context(self, query: str, user_profile: Dict = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Retrieve both visas and general content for comprehensive answers.

        Args:
            query: User's question
            user_profile: Optional user profile

        Returns:
            Tuple of (visa_list, general_content_list)
        """
        visas = self.retrieve_relevant_visas(query, user_profile)
        general_content = self.retrieve_relevant_general_content(query)
        return visas, general_content

    def _extract_filters(self, query: str) -> Dict:
        """Extract country and category from query"""
        query_lower = query.lower()
        filters = {}

        # Country detection
        countries = {
            'australia': 'australia',
            'canada': 'canada',
            'uk': 'uk',
            'united kingdom': 'uk',
            'germany': 'germany',
            'uae': 'uae',
            'united arab emirates': 'uae'
        }

        for name, code in countries.items():
            if name in query_lower:
                filters['country'] = code
                break

        # Category detection
        categories = {
            'work': ['work', 'job', 'employment', 'skilled', 'worker'],
            'study': ['study', 'student', 'education', 'university'],
            'family': ['family', 'spouse', 'partner', 'dependent'],
            'business': ['business', 'investor', 'entrepreneur'],
            'tourist': ['tourist', 'visitor', 'travel', 'holiday']
        }

        for category, keywords in categories.items():
            if any(kw in query_lower for kw in keywords):
                filters['category'] = category
                break

        return filters

    def _apply_filters(self, visas: List[Dict], filters: Dict) -> List[Dict]:
        """Apply metadata filters to visa list"""
        if not filters:
            return visas

        result = []
        for visa in visas:
            if 'country' in filters:
                if visa.get('country', '').lower() != filters['country']:
                    continue
            if 'category' in filters:
                if visa.get('category', '').lower() != filters['category']:
                    continue
            result.append(visa)

        return result

    def _keyword_search(self, query: str, visas: List[Dict], top_k: int = 20) -> List[Tuple[float, Dict]]:
        """Keyword-based search with scoring"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        scored = []
        for visa in visas:
            score = 0.0

            # Country match
            if visa['country'].lower() in query_lower:
                score += 3.0

            # Category match
            if visa.get('category', '').lower() in query_lower:
                score += 2.0

            # Visa type keywords
            type_words = set(re.findall(r'\w+', visa['visa_type'].lower()))
            score += len(query_words & type_words) * 0.5

            # Requirements keywords
            reqs = visa.get('requirements', {})
            if reqs:
                reqs_text = str(reqs).lower()
                for word in query_words:
                    if len(word) > 3 and word in reqs_text:
                        score += 0.3

            if score > 0:
                scored.append((score, visa))

        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:top_k]

    def _semantic_search(self, query: str, visas: List[Dict], top_k: int = 20) -> List[Tuple[float, Dict]]:
        """Semantic search using embeddings"""
        if not self.semantic_retriever:
            return []

        try:
            return self.semantic_retriever.search(query, top_k=top_k)
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []

    def _hybrid_search(self, query: str, visas: List[Dict], top_k: int = 20) -> List[Tuple[float, Dict]]:
        """Combine semantic (60%) and keyword (40%) search"""
        semantic = self._semantic_search(query, visas, top_k)
        keyword = self._keyword_search(query, visas, top_k)

        # Normalize scores
        def normalize(results):
            if not results:
                return []
            max_score = max(s for s, _ in results) or 1
            return [(s / max_score, v) for s, v in results]

        semantic_norm = normalize(semantic)
        keyword_norm = normalize(keyword)

        # Combine with weights
        scores = {}

        for score, visa in semantic_norm:
            key = f"{visa['country']}_{visa['visa_type']}"
            scores[key] = {'visa': visa, 'score': score * 0.6}

        for score, visa in keyword_norm:
            key = f"{visa['country']}_{visa['visa_type']}"
            if key in scores:
                scores[key]['score'] += score * 0.4
            else:
                scores[key] = {'visa': visa, 'score': score * 0.4}

        # Sort by combined score
        combined = [(d['score'], d['visa']) for d in scores.values()]
        combined.sort(reverse=True, key=lambda x: x[0])

        return combined[:top_k]

    def _rerank(self, query: str, candidates: List[Tuple[float, Dict]], top_k: int) -> List[Dict]:
        """Rerank candidates using cross-encoder"""
        if not self.reranker or not candidates:
            return [visa for _, visa in candidates[:top_k]]

        try:
            # Create query-document pairs
            pairs = []
            for _, visa in candidates:
                doc = f"{visa['visa_type']} {visa.get('category', '')} {visa['country']}"
                pairs.append([query, doc])

            # Get scores
            scores = self.reranker.predict(pairs)

            # Sort by reranking score
            reranked = list(zip(scores, [v for _, v in candidates]))
            reranked.sort(reverse=True, key=lambda x: x[0])

            return [visa for _, visa in reranked[:top_k]]

        except Exception as e:
            self.logger.error(f"Reranking failed: {e}")
            return [visa for _, visa in candidates[:top_k]]

    # ============ FORMATTING ============

    def format_context_for_llm(self, visas: List[Dict], general_content: List[Dict] = None) -> str:
        """
        Format visa and general content information for LLM context.

        Creates a structured text representation that the LLM can use to answer questions.

        Args:
            visas: List of visa dictionaries
            general_content: Optional list of general content dictionaries

        Returns:
            Formatted string for LLM context
        """
        context_parts = []

        # Format visas
        if visas:
            visa_parts = []
            for i, visa in enumerate(visas, 1):
                context = self._format_visa(i, visa)
                visa_parts.append(context)

            context_parts.append("=== VISA PROGRAMS ===\n" + "\n---\n".join(visa_parts))

        # Format general content
        if general_content:
            general_parts = []
            for i, content in enumerate(general_content, 1):
                context = self._format_general_content(i, content)
                general_parts.append(context)

            context_parts.append("=== GENERAL INFORMATION ===\n" + "\n---\n".join(general_parts))

        if not context_parts:
            return "No relevant information found in the database."

        return "\n\n".join(context_parts)

    def _format_visa(self, index: int, visa: Dict) -> str:
        """Format single visa for display"""
        lines = [
            f"\nVisa {index}: {visa['visa_type']}",
            f"Country: {visa['country']}",
            f"Category: {visa.get('category', 'N/A')}",
            "",
            "Requirements:"
        ]

        reqs = visa.get('requirements', {})

        # Age
        if reqs.get('age'):
            age = reqs['age']
            if age.get('min') and age.get('max'):
                lines.append(f"- Age {age['min']}-{age['max']}")
            elif age.get('min'):
                lines.append(f"- Age {age['min']}+")
            elif age.get('max'):
                lines.append(f"- Age under {age['max']}")

        # Education
        if reqs.get('education'):
            lines.append(f"- Education: {reqs['education']}")

        # Experience
        if reqs.get('experience_years'):
            lines.append(f"- Experience: {reqs['experience_years']} years")

        # Language
        if visa.get('language'):
            lines.append(f"\nLanguage: {visa['language']}")

        # Fees
        if visa.get('fees'):
            lines.append(f"\nFees: {visa['fees']}")

        # Processing time
        if visa.get('processing_time'):
            lines.append(f"Processing Time: {visa['processing_time']}")

        # Source
        if visa.get('source_urls'):
            lines.append(f"\nSource: {visa['source_urls'][0]}")

        return "\n".join(lines)

    def _format_general_content(self, index: int, content: Dict) -> str:
        """Format single general content item for display"""
        lines = [
            f"\nGeneral Content {index}: {content['title']}",
            f"Type: {content.get('content_type', 'N/A')}",
            f"Country: {content['country']}",
            f"Audience: {content.get('metadata', {}).get('audience', 'general')}",
            "",
            "Summary:",
            content.get('summary', 'No summary available'),
            ""
        ]

        # Key points
        key_points = content.get('key_points', [])
        if key_points:
            lines.append("Key Points:")
            for point in key_points[:5]:  # Limit to 5 key points
                lines.append(f"- {point}")
            lines.append("")

        # Application links
        app_links = content.get('application_links', [])
        if app_links:
            lines.append("Application Links:")
            for link in app_links[:3]:  # Limit to 3 links
                label = link.get('label', 'Link')
                url = link.get('url', '')
                if url:
                    lines.append(f"- {label}: {url}")
                else:
                    lines.append(f"- {label}")
            lines.append("")

        # Source
        if content.get('source_url'):
            lines.append(f"Source: {content['source_url']}")

        return "\n".join(lines)
