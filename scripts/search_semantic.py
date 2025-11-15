"""
Semantic Search Tester
Search visas using semantic similarity (meaning-based, not keyword-based)
"""

import numpy as np
from shared.database import Database


def semantic_search(query: str, top_k: int = 5):
    """
    Search visas using semantic similarity

    Args:
        query: Natural language query (e.g., "work visa for software engineers")
        top_k: Number of results to return
    """
    print("=" * 80)
    print("🔍 SEMANTIC VISA SEARCH")
    print("=" * 80)
    print(f"\nQuery: \"{query}\"")
    print(f"Finding top {top_k} most relevant visas...\n")

    # Load model
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except ImportError:
        print("❌ Error: sentence-transformers not installed")
        print("Install with: pip install sentence-transformers")
        return

    # Create query embedding
    query_embedding = model.encode(query, convert_to_numpy=True)

    # Load all embeddings from database
    db = Database()
    stored_embeddings = db.get_embeddings()

    if not stored_embeddings:
        print("⚠️  No embeddings found in database!")
        print("\nRun indexing first:")
        print("  python index_embeddings.py")
        return

    print(f"Searching through {len(stored_embeddings)} indexed visas...\n")

    # Calculate similarities
    similarities = []

    for item in stored_embeddings:
        # Convert bytes back to numpy array
        visa_embedding = np.frombuffer(item['embedding'], dtype=np.float32)

        # Cosine similarity
        similarity = np.dot(query_embedding, visa_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(visa_embedding)
        )

        similarities.append({
            'visa_id': item['visa_id'],
            'visa_type': item['visa_type'],
            'country': item['country'],
            'similarity': float(similarity)
        })

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    # Get full visa details for top results
    print("Results:")
    print("-" * 80)

    for i, result in enumerate(similarities[:top_k], 1):
        # Get full visa details
        visas = db.get_latest_visas()
        visa = next((v for v in visas if v['id'] == result['visa_id']), None)

        if not visa:
            continue

        print(f"\n{i}. {result['visa_type']} ({result['country'].upper()})")
        print(f"   Similarity: {result['similarity']:.2%}")
        print(f"   Category: {visa.get('category', 'unknown').title()}")
        print(f"   Processing time: {visa.get('processing_time', 'N/A')}")

        # Show requirements
        reqs = visa.get('requirements', {})
        if reqs:
            print(f"   Requirements:")
            if reqs.get('age'):
                age = reqs['age']
                if age.get('min') or age.get('max'):
                    print(f"     - Age: {age.get('min', 'No min')}-{age.get('max', 'No max')}")
            if reqs.get('education'):
                print(f"     - Education: {reqs['education']}")
            if reqs.get('experience_years'):
                print(f"     - Experience: {reqs['experience_years']} years")

    print()
    print("=" * 80)


def main():
    """Interactive search"""
    print("=" * 80)
    print("🔍 SEMANTIC VISA SEARCH")
    print("=" * 80)
    print()
    print("Search visas using natural language!")
    print()
    print("Examples:")
    print("  - 'work visa for software engineers'")
    print("  - 'student visa for master degree'")
    print("  - 'family visa for spouse'")
    print("  - 'investment visa for entrepreneurs'")
    print()

    while True:
        query = input("Enter search query (or 'quit' to exit): ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            break

        if not query:
            continue

        print()
        semantic_search(query, top_k=5)
        print()


if __name__ == "__main__":
    main()
