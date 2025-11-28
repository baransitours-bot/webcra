"""
Embeddings Management Page

Manage semantic search embeddings for visas and general content.
Embeddings enable the Assistant to understand meaning, not just keywords.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from shared.database import Database
from services.assistant.embeddings import SemanticRetriever
from shared.logger import setup_logger

# Page config
st.set_page_config(
    page_title="Embeddings Management",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Embeddings Management")
st.markdown("Manage semantic search embeddings for enhanced retrieval")

# Initialize
logger = setup_logger('embeddings_page')
db = Database()

# Check if sentence-transformers is installed
try:
    retriever = SemanticRetriever()
    embeddings_available = True
except Exception as e:
    embeddings_available = False
    st.error(f"""
    **⚠️ Embeddings Not Available**

    Sentence-transformers not installed or failed to load.

    Error: {str(e)[:200]}

    **To enable embeddings:**
    ```bash
    pip install sentence-transformers
    ```
    """)
    st.stop()

# Try to load existing embeddings from cache
try:
    retriever._load_model()
    # Try to load caches
    if retriever.visa_cache.exists():
        import pickle
        with open(retriever.visa_cache, 'rb') as f:
            retriever.visa_embeddings = pickle.load(f)
            logger.info(f"Loaded {len(retriever.visa_embeddings)} visa embeddings from cache")

    if retriever.general_cache.exists():
        import pickle
        with open(retriever.general_cache, 'rb') as f:
            retriever.general_embeddings = pickle.load(f)
            logger.info(f"Loaded {len(retriever.general_embeddings)} general embeddings from cache")
except Exception as e:
    logger.warning(f"Could not load caches: {e}")

# Get stats
stats = retriever.get_stats()

# ============ STATUS OVERVIEW ============
st.markdown("## 📊 Current Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Visa Embeddings",
        stats['visa_embeddings'],
        delta="Indexed" if stats['visa_embeddings'] > 0 else "Not indexed"
    )

with col2:
    st.metric(
        "General Content Embeddings",
        stats['general_embeddings'],
        delta="Indexed" if stats['general_embeddings'] > 0 else "Not indexed"
    )

with col3:
    st.metric(
        "Total Embeddings",
        stats['total_embeddings']
    )

with col4:
    model_status = "✅ Loaded" if stats['model_loaded'] else "⏸️ Not loaded"
    st.metric("Model Status", model_status)

# Cache status
st.markdown("### 💾 Cache Status")
col1, col2 = st.columns(2)

with col1:
    visa_cache_status = "✅ Exists" if stats['visa_cache_exists'] else "❌ Missing"
    st.info(f"**Visa Cache:** {visa_cache_status}")

with col2:
    general_cache_status = "✅ Exists" if stats['general_cache_exists'] else "❌ Missing"
    st.info(f"**General Content Cache:** {general_cache_status}")

st.markdown("---")

# ============ INDEXING CONTROLS ============
st.markdown("## 🔄 Indexing Actions")

st.info("""
**What is indexing?**

Indexing converts your visa and general content data into vector embeddings that enable semantic search.
This allows the Assistant to understand meaning, not just match keywords.

**Example:**
- Query: "employment assistance"
- Without embeddings: Matches "employment" keyword only
- With embeddings: Matches "employment", "job services", "career help", "work support"

**When to index:**
- After running Crawler + Classifier with new data
- After database updates
- If cache files are deleted or corrupted
""")

# Get data counts
visas = db.get_visas()
general_content = db.get_general_content()

visa_count = len(visas) if visas else 0
general_count = len(general_content) if general_content else 0

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎫 Visa Embeddings")
    st.write(f"**Database:** {visa_count} visas")
    st.write(f"**Indexed:** {stats['visa_embeddings']} embeddings")

    if visa_count > stats['visa_embeddings']:
        st.warning(f"⚠️ {visa_count - stats['visa_embeddings']} visas not indexed")

    force_visa = st.checkbox("Force re-index (slower)", key="force_visa", help="Regenerate embeddings even if cached")

    if st.button("📥 Index Visas", type="primary", disabled=visa_count == 0):
        with st.spinner("Indexing visas... This may take 1-2 minutes for 100+ visas"):
            try:
                st.write(f"📊 Converting {len(visas)} visa objects to dicts...")
                visa_dicts = [v.to_dict() for v in visas]
                st.write(f"✅ Converted {len(visa_dicts)} visas")

                st.write(f"🔄 Starting indexing...")
                retriever.index_visas(visa_dicts, force_reindex=force_visa)

                st.write(f"📈 Checking results...")
                new_stats = retriever.get_stats()
                st.write(f"✅ Result: {new_stats['visa_embeddings']} visa embeddings now indexed")

                st.success(f"✅ Successfully indexed {len(visa_dicts)} visas!")
                st.info("🔄 Refreshing page...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Indexing failed: {str(e)}")
                logger.error(f"Visa indexing failed: {e}")
                import traceback
                st.code(traceback.format_exc())

with col2:
    st.markdown("### 📄 General Content Embeddings")
    st.write(f"**Database:** {general_count} items")
    st.write(f"**Indexed:** {stats['general_embeddings']} embeddings")

    if general_count > stats['general_embeddings']:
        st.warning(f"⚠️ {general_count - stats['general_embeddings']} items not indexed")

    force_general = st.checkbox("Force re-index (slower)", key="force_general", help="Regenerate embeddings even if cached")

    if st.button("📥 Index General Content", type="primary", disabled=general_count == 0):
        with st.spinner("Indexing general content..."):
            try:
                st.write(f"📊 Converting {len(general_content)} content objects to dicts...")
                content_dicts = [c.to_dict() for c in general_content]
                st.write(f"✅ Converted {len(content_dicts)} items")

                st.write(f"🔄 Starting indexing...")
                retriever.index_general_content(content_dicts, force_reindex=force_general)

                st.write(f"📈 Checking results...")
                new_stats = retriever.get_stats()
                st.write(f"✅ Result: {new_stats['general_embeddings']} general embeddings now indexed")

                st.success(f"✅ Successfully indexed {len(content_dicts)} content items!")
                st.info("🔄 Refreshing page...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Indexing failed: {str(e)}")
                logger.error(f"General content indexing failed: {e}")
                import traceback
                st.code(traceback.format_exc())

st.markdown("---")

# Index all button
st.markdown("### 🎯 Index Everything")
st.write("Index both visas and general content in one operation")

force_all = st.checkbox("Force re-index all (slower)", key="force_all")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("📥 Index All Content", type="primary", disabled=(visa_count + general_count) == 0):
        with st.spinner(f"Indexing {visa_count} visas + {general_count} general items..."):
            try:
                st.write(f"📊 Preparing data...")
                visa_dicts = [v.to_dict() for v in visas] if visas else []
                content_dicts = [c.to_dict() for c in general_content] if general_content else []
                st.write(f"✅ Prepared {len(visa_dicts)} visas + {len(content_dicts)} general items")

                st.write(f"🔄 Indexing all content...")
                retriever.index_all(visa_dicts, content_dicts, force_reindex=force_all)

                st.write(f"📈 Checking results...")
                new_stats = retriever.get_stats()
                st.write(f"✅ Visa embeddings: {new_stats['visa_embeddings']}")
                st.write(f"✅ General embeddings: {new_stats['general_embeddings']}")
                st.write(f"✅ Total: {new_stats['total_embeddings']}")

                total = len(visa_dicts) + len(content_dicts)
                st.success(f"✅ Successfully indexed {total} total items ({len(visa_dicts)} visas + {len(content_dicts)} general)!")
                st.info("🔄 Refreshing page...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Indexing failed: {str(e)}")
                logger.error(f"Full indexing failed: {e}")
                import traceback
                st.code(traceback.format_exc())

with col2:
    st.write("")  # Spacing

with col3:
    st.info(f"Will index: {visa_count + general_count} total items")

st.markdown("---")

# ============ CACHE MANAGEMENT ============
st.markdown("## 🗑️ Cache Management")

st.warning("""
**⚠️ Warning: Clearing cache will require re-indexing**

Cache files store pre-computed embeddings for fast loading.
Clearing them will require re-indexing all content (takes 1-2 minutes).

Only clear cache if:
- Embeddings are corrupted
- You want to free disk space
- Testing/debugging
""")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Clear Visa Cache"):
        try:
            retriever.clear_cache('visas')
            st.success("✅ Visa cache cleared")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {str(e)}")

with col2:
    if st.button("🗑️ Clear General Cache"):
        try:
            retriever.clear_cache('general')
            st.success("✅ General content cache cleared")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {str(e)}")

with col3:
    if st.button("🗑️ Clear All Caches", type="secondary"):
        try:
            retriever.clear_cache('all')
            st.success("✅ All caches cleared")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {str(e)}")

st.markdown("---")

# ============ INFORMATION ============
with st.expander("ℹ️ How Embeddings Work"):
    st.markdown("""
    ### What are Embeddings?

    Embeddings convert text into numbers (vectors) that capture **meaning**.

    **Example:**
    ```
    Text: "skilled worker visa"
           ↓ Embedding Model
    Vector: [0.23, -0.45, 0.12, ...] (384 numbers)
    ```

    **Similar meanings → Similar vectors:**
    - "skilled worker" → [0.23, -0.45, 0.12, ...]
    - "qualified employee" → [0.24, -0.44, 0.13, ...] ← Very close!
    - "tourist visa" → [-0.56, 0.78, -0.34, ...] ← Far away

    ### Why This Helps

    **Without embeddings (keyword only):**
    - Query: "employment help"
    - Finds: Documents with "employment" or "help"
    - Misses: "Job services", "Career assistance", "Work support"

    **With embeddings (semantic search):**
    - Query: "employment help"
    - Finds: "Employment help" + "Job services" + "Career assistance" + "Work support"
    - Understands: employment = job = career = work

    ### Model Used

    - **Model:** all-MiniLM-L6-v2
    - **Size:** ~90MB
    - **Speed:** Fast (CPU only)
    - **Quality:** Good for general use
    - **Cost:** 100% FREE (runs locally)

    ### Performance

    **Indexing speed** (on typical laptop):
    - 100 visas: ~30 seconds
    - 100 general content: ~30 seconds
    - Total 200 items: ~1 minute

    **Search speed:**
    - First query: ~500ms (loads model)
    - Subsequent queries: <100ms (cached)

    ### Files Created

    - `data/.visa_embeddings.pkl` - Visa embeddings cache
    - `data/.general_embeddings.pkl` - General content cache
    - Total size: ~1-5MB per 100 items
    """)

with st.expander("🚀 Quick Start Guide"):
    st.markdown("""
    ### Step-by-Step: Enable Semantic Search

    **1. Install Dependencies**
    ```bash
    pip install sentence-transformers
    ```

    **2. Ensure Data Exists**
    - Run **Crawler** to collect pages
    - Run **Classifier** to extract visas + general content
    - Verify in **Database** page: Visas > 0, General Content > 0

    **3. Index Content**
    - Click **"📥 Index All Content"** above
    - Wait 1-2 minutes for indexing
    - See success message

    **4. Enable Enhanced Retrieval**
    - Go to **Global Config** → **System** tab
    - Enable "Use Enhanced Retrieval"
    - Save settings

    **5. Test It!**
    - Go to **Assistant** page
    - Ask: "What employment services are available in Canada?"
    - Should return both visas AND employment guides

    **6. Re-index When Needed**
    - After running Crawler + Classifier with new data
    - If you see warnings about unindexed items
    - Click "Force re-index" to regenerate

    ### That's it! 🎉

    Your Assistant now understands meaning, not just keywords.
    """)
