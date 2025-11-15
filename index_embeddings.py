"""
Embedding Indexer
Creates and stores semantic embeddings for all visas in database
"""

import numpy as np
from shared.database import Database
from shared.logger import setup_logger


def index_all_visas():
    """Create embeddings for all visas in database"""
    logger = setup_logger('indexer')

    print("=" * 80)
    print("🔍 EMBEDDING INDEXER")
    print("=" * 80)
    print("\nCreating semantic embeddings for all visas...")
    print("This enables semantic search (find similar visas by meaning)")
    print()

    # Load sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model...")
        print("📥 Loading model (all-MiniLM-L6-v2, ~90MB)...")

        model = SentenceTransformer('all-MiniLM-L6-v2')
        model_name = "all-MiniLM-L6-v2"

        print("✅ Model loaded\n")

    except ImportError:
        print("❌ Error: sentence-transformers not installed")
        print("\nInstall with:")
        print("  pip install sentence-transformers")
        return

    # Load visas from database
    db = Database()
    visas = db.get_latest_visas()

    if not visas:
        print("⚠️  No visas found in database!")
        print("\nRun the Classifier service first to extract visas.")
        return

    print(f"Found {len(visas)} visas to index\n")

    # Create embeddings
    indexed = 0
    skipped = 0

    for i, visa in enumerate(visas, 1):
        try:
            # Create text representation
            text_parts = [
                visa.get('visa_type', ''),
                visa.get('category', ''),
                visa.get('country', ''),
            ]

            # Add requirements
            reqs = visa.get('requirements', {})
            if reqs:
                if reqs.get('education'):
                    text_parts.append(f"education: {reqs['education']}")
                if reqs.get('experience_years'):
                    text_parts.append(f"experience: {reqs['experience_years']} years")
                if reqs.get('age'):
                    age = reqs['age']
                    if age.get('min') or age.get('max'):
                        text_parts.append(f"age: {age.get('min', 0)}-{age.get('max', 100)}")

            text = ' '.join(str(p) for p in text_parts if p)

            # Create embedding
            embedding = model.encode(text, convert_to_numpy=True)

            # Convert numpy array to bytes for storage
            embedding_bytes = embedding.tobytes()

            # Save to database
            db.save_embedding(
                visa_id=visa['id'],
                embedding=embedding_bytes,
                model_name=model_name
            )

            indexed += 1

            # Progress
            if indexed % 5 == 0:
                print(f"  Indexed {indexed}/{len(visas)} visas...")

        except Exception as e:
            logger.error(f"Error indexing visa {visa.get('visa_type', 'Unknown')}: {e}")
            skipped += 1
            continue

    print()
    print("=" * 80)
    print("✅ INDEXING COMPLETE")
    print("=" * 80)
    print(f"\nResults:")
    print(f"  Successfully indexed: {indexed} visas")
    print(f"  Skipped (errors): {skipped} visas")
    print(f"\nEmbeddings stored in: data/immigration.db (embeddings table)")
    print(f"Model: {model_name}")
    print(f"Dimensions: 384")
    print()
    print("Next steps:")
    print("  - Semantic search is now enabled")
    print("  - Use Assistant service to ask questions")
    print("  - Re-run this script when you add new visas")
    print()


if __name__ == "__main__":
    index_all_visas()
