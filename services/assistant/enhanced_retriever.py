"""
Enhanced Context Retriever with Hybrid Search
- Semantic search (sentence-transformers)
- Keyword search (current method)
- Metadata filtering
- Reranking (cross-encoder)

100% FREE - All models run locally
"""

from typing import List, Dict, Tuple
from shared.database import DataStore
from shared.logger import setup_logger
import re

class EnhancedRetriever:
    """
    Enhanced retrieval using hybrid search + reranking
    Falls back to keyword-only if models not installed
    """

    def __init__(self, config):
        self.config = config
        self.data_store = DataStore()
        self.logger = setup_logger('enhanced_retriever')

        # Try to load semantic retriever
        self.semantic_retriever = None
        self.reranker = None

        try:
            from services.assistant.embeddings import SemanticRetriever
            self.semantic_retriever = SemanticRetriever()
            self.logger.info("✅ Semantic search enabled")
        except ImportError:
            self.logger.warning("⚠️  Semantic search not available. Install: pip install sentence-transformers")

        # Try to load reranker
        try:
            from sentence_transformers import CrossEncoder
            # Lightweight reranker model (50MB)
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            self.logger.info("✅ Reranking enabled")
        except ImportError:
            self.logger.warning("⚠️  Reranking not available. Install: pip install sentence-transformers")

        # Index visas on init (if semantic search available)
        if self.semantic_retriever:
            self._index_visas()

    def _index_visas(self):
        """Index all visas for semantic search"""
        try:
            all_visas = self.data_store.load_structured_visas()
            if all_visas:
                self.semantic_retriever.index_visas(all_visas)
        except Exception as e:
            self.logger.error(f"Failed to index visas: {e}")

    def _extract_metadata_filters(self, query: str) -> Dict:
        """
        Extract country and category from query

        Examples:
        - "Canada work visa" → {country: "canada", category: "work"}
        - "student visa Australia" → {country: "australia", category: "study"}
        """
        query_lower = query.lower()
        filters = {}

        # Extract country
        countries = ['australia', 'canada', 'uk', 'germany', 'uae', 'united kingdom', 'united arab emirates']
        for country in countries:
            if country in query_lower:
                filters['country'] = country.replace('united kingdom', 'uk').replace('united arab emirates', 'uae')
                break

        # Extract category
        category_keywords = {
            'work': ['work', 'job', 'employment', 'skilled', 'worker', 'professional'],
            'study': ['study', 'student', 'education', 'university', 'academic'],
            'family': ['family', 'spouse', 'partner', 'dependent', 'reunion'],
            'business': ['business', 'investor', 'entrepreneur', 'startup'],
            'tourist': ['tourist', 'visitor', 'travel', 'holiday', 'vacation']
        }

        for category, keywords in category_keywords.items():
            if any(kw in query_lower for kw in keywords):
                filters['category'] = category
                break

        return filters

    def _filter_by_metadata(self, visas: List[Dict], filters: Dict) -> List[Dict]:
        """Apply metadata filters"""
        if not filters:
            return visas

        filtered = []
        for visa in visas:
            # Check country filter
            if 'country' in filters:
                if visa.get('country', '').lower() != filters['country']:
                    continue

            # Check category filter
            if 'category' in filters:
                if visa.get('category', '').lower() != filters['category']:
                    continue

            filtered.append(visa)

        return filtered

    def _keyword_search(self, query: str, visas: List[Dict], top_k: int = 20) -> List[Tuple[float, Dict]]:
        """
        Keyword-based search (current method)
        Returns: List of (score, visa) tuples
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        scored_visas = []

        for visa in visas:
            score = 0.0

            # Country exact match
            if visa['country'].lower() in query_lower:
                score += 3.0

            # Category exact match
            if visa.get('category', '').lower() in query_lower:
                score += 2.0

            # Visa type keywords
            visa_type_words = set(re.findall(r'\w+', visa['visa_type'].lower()))
            common_words = query_words & visa_type_words
            score += len(common_words) * 0.5

            # Requirements keywords
            reqs = visa.get('requirements', {})
            if reqs:
                reqs_text = str(reqs).lower()
                for word in query_words:
                    if len(word) > 3 and word in reqs_text:
                        score += 0.3

            if score > 0:
                scored_visas.append((score, visa))

        # Sort by score
        scored_visas.sort(reverse=True, key=lambda x: x[0])

        return scored_visas[:top_k]

    def _semantic_search(self, query: str, visas: List[Dict], top_k: int = 20) -> List[Tuple[float, Dict]]:
        """
        Semantic search using embeddings
        Returns: List of (similarity, visa) tuples
        """
        if not self.semantic_retriever:
            return []

        try:
            results = self.semantic_retriever.search(query, top_k=top_k)
            return results
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []

    def _hybrid_search(self, query: str, visas: List[Dict], top_k: int = 20) -> List[Tuple[float, Dict]]:
        """
        Combine semantic and keyword search

        Scoring: 60% semantic + 40% keyword
        """
        # Get semantic results
        semantic_results = self._semantic_search(query, visas, top_k=top_k)

        # Get keyword results
        keyword_results = self._keyword_search(query, visas, top_k=top_k)

        # Normalize scores to 0-1 range
        def normalize_scores(results):
            if not results:
                return []
            max_score = max(score for score, _ in results)
            if max_score == 0:
                return [(0.0, visa) for _, visa in results]
            return [(score / max_score, visa) for score, visa in results]

        semantic_normalized = normalize_scores(semantic_results)
        keyword_normalized = normalize_scores(keyword_results)

        # Combine scores
        visa_scores = {}

        # Add semantic scores (weight: 0.6)
        for score, visa in semantic_normalized:
            visa_id = f"{visa['country']}_{visa['visa_type']}"
            visa_scores[visa_id] = {
                'visa': visa,
                'score': score * 0.6
            }

        # Add keyword scores (weight: 0.4)
        for score, visa in keyword_normalized:
            visa_id = f"{visa['country']}_{visa['visa_type']}"
            if visa_id in visa_scores:
                visa_scores[visa_id]['score'] += score * 0.4
            else:
                visa_scores[visa_id] = {
                    'visa': visa,
                    'score': score * 0.4
                }

        # Sort by combined score
        combined = [(data['score'], data['visa']) for data in visa_scores.values()]
        combined.sort(reverse=True, key=lambda x: x[0])

        return combined[:top_k]

    def _rerank(self, query: str, candidates: List[Tuple[float, Dict]], top_k: int = 5) -> List[Dict]:
        """
        Rerank candidates using cross-encoder
        Returns: List of visas (best first)
        """
        if not self.reranker or not candidates:
            # No reranker, just return top candidates
            return [visa for _, visa in candidates[:top_k]]

        try:
            # Create query-document pairs
            pairs = []
            for _, visa in candidates:
                doc = f"{visa['visa_type']} {visa.get('category', '')} {visa['country']}"
                pairs.append([query, doc])

            # Get reranking scores
            scores = self.reranker.predict(pairs)

            # Combine with original visas
            reranked = list(zip(scores, [visa for _, visa in candidates]))
            reranked.sort(reverse=True, key=lambda x: x[0])

            return [visa for _, visa in reranked[:top_k]]

        except Exception as e:
            self.logger.error(f"Reranking failed: {e}")
            # Fallback to original ranking
            return [visa for _, visa in candidates[:top_k]]

    def retrieve_relevant_visas(self, query: str, user_profile: Dict = None) -> List[Dict]:
        """
        Retrieve visas using enhanced hybrid search

        Pipeline:
        1. Extract metadata filters (country, category)
        2. Filter visas by metadata
        3. Hybrid search (semantic + keyword)
        4. Rerank top 20 → top 5
        5. Return final results
        """
        # Load all visas
        all_visas = self.data_store.load_structured_visas()

        if not all_visas:
            self.logger.warning("No structured visa data found")
            return []

        # Step 1: Extract filters
        filters = self._extract_metadata_filters(query)
        if filters:
            self.logger.info(f"🔍 Applying filters: {filters}")

        # Step 2: Filter by metadata
        filtered_visas = self._filter_by_metadata(all_visas, filters)

        if not filtered_visas:
            self.logger.warning(f"No visas match filters: {filters}. Using all visas.")
            filtered_visas = all_visas

        # Step 3: Hybrid search
        if self.semantic_retriever:
            # Use hybrid (semantic + keyword)
            candidates = self._hybrid_search(query, filtered_visas, top_k=20)
            self.logger.info(f"🔄 Hybrid search found {len(candidates)} candidates")
        else:
            # Fall back to keyword only
            candidates = self._keyword_search(query, filtered_visas, top_k=20)
            self.logger.info(f"🔍 Keyword search found {len(candidates)} candidates")

        # Step 4: Rerank
        max_results = self.config['context']['max_visas']
        final_results = self._rerank(query, candidates, top_k=max_results)

        self.logger.info(f"✅ Returning {len(final_results)} visas")

        return final_results

    def format_context_for_llm(self, visas: List[Dict]) -> str:
        """Format visa information for LLM context (same as original)"""
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
