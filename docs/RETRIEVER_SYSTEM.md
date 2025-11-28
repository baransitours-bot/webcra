# Retriever System & Embeddings Guide

## 📚 Table of Contents

1. [Overview](#overview)
2. [Two Retriever Types](#two-retriever-types)
3. [How Embeddings Work](#how-embeddings-work)
4. [When to Use Each Retriever](#when-to-use-each-retriever)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Assistant service uses a **retrieval system** to find relevant visa programs and general immigration content before sending queries to the LLM. Think of it as a smart search engine that helps the LLM answer questions accurately.

### The Flow

```
User Question
     ↓
Retriever (finds relevant visas + general content)
     ↓
Format Context (structures the data)
     ↓
LLM (reads context + generates answer)
     ↓
User Answer
```

**Why Retrievers Matter:**
- LLMs need **context** to answer questions accurately
- Database may have 100+ visas - can't send all to LLM (token limits!)
- Retriever finds the **most relevant** 5-10 visas for each question
- Also retrieves general content (employment services, healthcare info, etc.)

---

## Two Retriever Types

We have **two retriever implementations** that can be switched via configuration:

### 1. **ContextRetriever** (Basic - Always Works)

**Location:** `services/assistant/retriever.py`

**How it works:**
- Simple **keyword matching**
- Checks if query words appear in visa type, category, country
- Fast and reliable
- **No dependencies** - always available

**Example:**
```
Query: "Canada work visa"
Finds: Visas with "Canada" in country AND "work" in category
```

**Advantages:**
- ✅ No setup required
- ✅ No external dependencies
- ✅ Fast
- ✅ Predictable results

**Disadvantages:**
- ❌ Only matches exact keywords
- ❌ Misses synonyms ("employment" vs "work")
- ❌ Can't understand meaning

### 2. **EnhancedRetriever** (Advanced - Better Results)

**Location:** `services/assistant/enhanced_retriever.py`

**How it works:**
- **Hybrid search:** Combines semantic (meaning-based) + keyword matching
- Uses embeddings to understand query meaning
- Reranks results for better quality
- **Gracefully falls back** to keyword-only if embeddings not installed

**Example:**
```
Query: "skilled worker visa"
Finds:
- Exact matches: "Skilled Worker Visa"
- Semantic matches: "Professional Employment Visa", "Qualified Worker Program"
- Understands: skilled = qualified = professional
```

**Advantages:**
- ✅ Understands synonyms and related concepts
- ✅ Better ranking of results
- ✅ More accurate matches
- ✅ Falls back gracefully if embeddings unavailable

**Disadvantages:**
- ❌ Requires optional dependencies (`sentence-transformers`)
- ❌ Slightly slower first run (loads models)
- ❌ Uses ~500MB RAM for models

---

## How Embeddings Work

### What are Embeddings?

**Embeddings** convert text into numbers (vectors) that capture **meaning**.

```
Text: "skilled worker visa"
       ↓ Embedding Model
Vector: [0.23, -0.45, 0.12, 0.89, ...]  (384 numbers)
```

**Similar meanings → Similar vectors**

```
"skilled worker"   → [0.23, -0.45, 0.12, ...]
"qualified worker" → [0.24, -0.44, 0.13, ...]  ← Very close!
"tourist visa"     → [-0.56, 0.78, -0.34, ...] ← Far away
```

### Components

#### 1. **Semantic Retriever** (Optional)

**Location:** `services/assistant/embeddings.py` (if exists)

**What it does:**
- Creates embeddings for all visas in database
- Creates embedding for user's query
- Finds visas with **similar meanings** (cosine similarity)

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`
- Size: ~80MB
- Speed: Fast
- Quality: Good for general use
- **100% free** and runs locally

#### 2. **Reranker** (Optional)

**Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

**What it does:**
- Takes top 20 candidates from hybrid search
- Re-scores each one by reading query + visa content together
- Returns best 5-10 results

**Why reranking?**
- More accurate than embeddings alone
- Considers query-document **interactions**
- Eliminates false positives

---

## When to Use Each Retriever

### Use **ContextRetriever** (Basic) when:
- 🚀 You want **fastest** setup (no installation)
- 💻 Limited RAM (<4GB available)
- 📦 Don't want to install extra dependencies
- ✅ Keyword matching works well for your use case
- 🧪 Testing or development

### Use **EnhancedRetriever** (Advanced) when:
- 🎯 You need **best search quality**
- 💾 Have enough RAM (>=4GB)
- 📚 Large visa database (50+ visas)
- 🔍 Users ask questions with varied terminology
- 🏢 Production deployment

### Configuration Toggle

**File:** `services/assistant/config.yaml` or Global Config UI

```yaml
# Enable/disable enhanced retrieval
use_enhanced_retrieval: true  # EnhancedRetriever
# OR
use_enhanced_retrieval: false # ContextRetriever
```

**How it works:**
1. Engine tries to initialize `EnhancedRetriever`
2. If embeddings dependencies missing → Falls back to `ContextRetriever`
3. You'll see log message: "Using basic keyword retrieval"

---

## Installation & Setup

### Basic Retriever (No Setup Needed)

Already works! No installation required.

### Enhanced Retriever with Embeddings

#### Step 1: Install Dependencies

```bash
pip install sentence-transformers
```

This installs:
- `sentence-transformers` - Embedding models
- `torch` or `onnxruntime` - Model runtime
- Dependencies: ~1GB download

#### Step 2: Test Installation

```python
# Test if embeddings are available
python -c "from sentence_transformers import SentenceTransformer; print('✅ Embeddings available')"
```

#### Step 3: Enable in Configuration

**Option A: Config File**

Edit `services/assistant/config.yaml`:
```yaml
use_enhanced_retrieval: true
```

**Option B: Global Config UI**

1. Navigate to: **Settings** → **Global Config** → **System**
2. Find "Enhanced Retrieval"
3. Toggle ON
4. Save settings

#### Step 4: Restart Application

```bash
streamlit run app.py
```

You should see in logs:
```
✅ Using enhanced retrieval (hybrid search)
✅ Semantic search enabled
✅ Reranking enabled
```

---

## Configuration

### Assistant Config Structure

**Location:** `services/assistant/config.yaml` or Database (`settings` table)

```yaml
# Retrieval settings
use_enhanced_retrieval: true   # Use EnhancedRetriever vs ContextRetriever

context:
  max_visas: 5                 # Max visas to retrieve
  max_general_content: 5       # Max general content items
  max_history: 10              # Conversation history limit

# LLM settings
llm:
  provider: openrouter
  model: google/gemini-2.0-flash-001:free
  temperature: 0.3
  max_tokens: 1000

# Response style
response_style: professional   # professional | friendly | detailed
```

### Retrieval Configuration

**Context limits** control how much data is sent to the LLM:

```yaml
context:
  max_visas: 5              # ← Increase for more comprehensive answers
  max_general_content: 5    # ← Increase to include more guides
```

**Trade-offs:**
- **Higher limits:** More comprehensive answers, but uses more tokens (costs more)
- **Lower limits:** Faster, cheaper, but may miss relevant information

**Recommended:**
- Development: `max_visas: 3`, `max_general_content: 3`
- Production: `max_visas: 5`, `max_general_content: 5`
- Research: `max_visas: 10`, `max_general_content: 10`

---

## Troubleshooting

### Error: "'EnhancedRetriever' object has no attribute 'retrieve_all_context'"

**Fixed in latest version!** If you see this:

1. Pull latest code: `git pull`
2. EnhancedRetriever now has all required methods

### Error: "No module named 'sentence_transformers'"

**Cause:** Embeddings dependencies not installed

**Solution:**
```bash
pip install sentence-transformers
```

**Alternative:** Disable enhanced retrieval in config:
```yaml
use_enhanced_retrieval: false
```

### Warning: "Semantic search not available"

**This is OK!** Enhanced retriever will use keyword-only search.

**To enable semantic search:**
```bash
pip install sentence-transformers
```

### Slow First Query

**Normal behavior:** First query with EnhancedRetriever:
- Downloads models (~80MB) - only once
- Loads models into RAM - only once per session
- Indexes visas - only once per session

**Subsequent queries:** Fast (uses cached models + index)

### High Memory Usage

**Cause:** Embedding models loaded in RAM

**Current usage:**
- Model: ~500MB
- Reranker: ~200MB
- **Total:** ~700MB

**Solutions:**
1. **Disable reranking** (saves 200MB):
   - Edit `enhanced_retriever.py`
   - Return `None` from `_init_reranker()`

2. **Use basic retriever**:
   - Set `use_enhanced_retrieval: false`
   - Uses ~0MB (no models)

3. **Upgrade RAM** (recommended for production)

### Results Not Relevant

**Check:**
1. **Database has data:**
   - Navigate to: **Database** page
   - Check: "Visas Total" > 0
   - Check: "General Content" > 0

2. **Run Classifier:**
   - Visas must be classified (structured) before retrieval
   - Navigate to: **Classifier** page
   - Run classification

3. **Review query:**
   - Be specific: "Canada work visa" ✅
   - Avoid vague: "visa" ❌

4. **Check retrieval logs:**
   - Look for: "Returning X visas"
   - If 0 results → Adjust query or check data

---

## API Reference

### Both Retrievers Support

```python
# Retrieve visas only
visas: List[Dict] = retriever.retrieve_relevant_visas(
    query="work visa canada",
    user_profile={"age": 30, "education": "bachelors"}  # Optional
)

# Retrieve general content only
content: List[Dict] = retriever.retrieve_relevant_general_content(
    query="employment services"
)

# Retrieve both (recommended)
visas, content = retriever.retrieve_all_context(
    query="moving to canada for work",
    user_profile={"age": 30}  # Optional
)

# Format for LLM
context_str: str = retriever.format_context_for_llm(
    visas=visas,
    general_content=content
)
```

### Response Format

**Visas:**
```python
[
    {
        'visa_type': 'Skilled Worker Visa',
        'country': 'Canada',
        'category': 'work',
        'requirements': {
            'age': {'min': 18, 'max': 45},
            'education': 'bachelors',
            'experience_years': 2
        },
        'fees': {'application_fee': '$850'},
        'processing_time': '6-12 months',
        'source_urls': ['https://...']
    }
]
```

**General Content:**
```python
[
    {
        'title': 'Employment Services for Newcomers',
        'content_type': 'employment',
        'country': 'Canada',
        'summary': 'Free job search assistance...',
        'key_points': [
            'Resume workshops',
            'Interview preparation',
            'Job matching services'
        ],
        'source_url': 'https://...'
    }
]
```

---

## Summary

✅ **Two retrievers:** Basic (keyword) and Enhanced (semantic + keyword)
✅ **Embeddings are optional:** System works without them
✅ **EnhancedRetriever falls back gracefully** if embeddings unavailable
✅ **Both retrievers support same API:** Easy to switch
✅ **General content included:** Employment, healthcare, benefits info
✅ **Configurable:** Toggle via config file or Global Config UI

**For most users:** Start with Basic (ContextRetriever), upgrade to Enhanced when you have 50+ visas and want better search quality.

**For production:** Use Enhanced with embeddings for best results.
