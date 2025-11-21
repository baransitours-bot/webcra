# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 What This System Actually Is

**This is an AI-Powered Immigration Consultant Assistant for Tourism/Travel Offices.**

### Business Context

This system serves **tourism offices and immigration consultancies** that help clients with visa applications and immigration processes. Instead of staff manually researching visa requirements for hours, this system:

1. **Automatically harvests** immigration data from government websites (Australia, Canada, UK, UAE, Germany, etc.)
2. **Structures and indexes** this data for fast retrieval
3. **Feeds relevant context** to an LLM (Large Language Model) based on client questions
4. **Generates intelligent, accurate answers** that sound like a human immigration consultant

### Core Philosophy: Context Generation for LLM

**Everything in this system exists to FEED THE LLM with relevant text context.**

```
The Problem: LLM = Large Language Model
           → Needs LANGUAGE (text/context) to generate answers
           → But has no knowledge of current visa requirements

The Solution: RAG (Retrieval-Augmented Generation)
           → Crawler: Collects text from government sites
           → Classifier: Structures the text
           → Database: Stores the context
           → Retriever: Finds relevant context for each question
           → LLM: Reads context + generates answer
```

**The crawler, classifier, embeddings, database** → These are NOT the product.
**They are the CONTEXT GENERATION SYSTEM that fuels the LLM.**

### The Complete Data Flow

```
┌─────────────────────────────────────────────────────────┐
│          TOURISM OFFICE DAILY OPERATIONS               │
│                                                         │
│  Client asks: "What work visas are available for me?"  │
│                         ↓                               │
│  System retrieves: Relevant visa requirements (CONTEXT)│
│                         ↓                               │
│  LLM reads: Context + client profile                   │
│                         ↓                               │
│  LLM generates: Personalized answer                    │
│                         ↓                               │
│  Staff delivers: Answer to client                      │
│                                                         │
│  Result: 5 minutes instead of 30+ minutes research     │
└─────────────────────────────────────────────────────────┘

MEANWHILE (Background - Weekly/Monthly):
┌─────────────────────────────────────────────────────────┐
│          CONTEXT GENERATION (Automated)                 │
│                                                         │
│  Browser Crawler → Visits government websites          │
│                         ↓                               │
│  Saves raw HTML → Database (crawled_pages table)       │
│                         ↓                               │
│  Classifier (LLM) → Extracts structured data           │
│                         ↓                               │
│  Saves structured → Database (visas + general_content) │
│                         ↓                               │
│  Embeddings → Enables semantic search (optional)       │
│                         ↓                               │
│  READY → Fresh context available for LLM queries       │
└─────────────────────────────────────────────────────────┘
```

---

## Essential Commands

### Setup & Running

```bash
# Install dependencies (includes Playwright for browser automation)
pip install -r requirements.txt
playwright install chromium

# Create .env file with API key
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY or OPENAI_API_KEY

# Run web application
streamlit run app.py

# Run tests
python -m pytest
python -m pytest tests/test_crawler.py  # Single test file
```

### Development Workflow

```bash
# CLI usage (legacy - UI preferred)
python main.py crawl --countries australia --max-pages 10
python main.py classify --all
python main.py assist --query "question here"

# Database inspection
sqlite3 data/immigration.db

# Add sample data (for testing when crawler is blocked)
python add_sample_data.py
```

---

## Architecture: Engine/Fuel Pattern

This system uses a strict 4-layer architecture called **"Engine/Fuel" pattern**. Think of it like a car:

- **FUEL** = Data (from database)
- **FUEL TRANSPORT** = Repository (delivers data)
- **ENGINE** = Business logic (processes data)
- **INTERFACE** = Controls (how you interact with engine)

**Every service follows this exact structure:**

```
services/<service>/
├── repository.py      # Layer 2: FUEL TRANSPORT - Database access only
├── engine.py          # Layer 3: ENGINE - Pure business logic, no DB imports
├── browser_engine.py  # Layer 3: ALTERNATE ENGINE (for crawler only)
├── interface.py       # Layer 4: INTERFACES - Service (interior) + Controller (exterior)
└── config.yaml        # Configuration
```

### Layer Responsibilities (CRITICAL)

**Layer 1: DATA (shared/)**
- `shared/models.py` - Dataclass models (Visa, CrawledPage, GeneralContent, UserProfile)
- `shared/database.py` - SQLite operations with versioning
- Single source of truth: `data/immigration.db`

**Layer 2: REPOSITORY (repository.py)**
- Database CRUD operations only
- Returns model objects (NOT dicts)
- No business logic allowed
- Example: `get_visas()`, `save_visa()`, `get_general_content()`

**Layer 3: ENGINE (engine.py / browser_engine.py)**
- Pure business logic
- NEVER imports Database directly - uses repository
- No UI knowledge
- Can have multiple engines for same service (e.g., simple HTTP vs browser)
- Example: `CrawlerEngine.crawl_country()`, `BrowserCrawlerEngine.crawl_country()`

**Layer 4: INTERFACES (interface.py)**
- **Service class (INTERIOR)**: Clean Python API for service-to-service calls
- **Controller class (EXTERIOR)**: UI-friendly with callbacks (on_start, on_complete, on_error, on_progress)
- Both use same engine + repository
- Can switch between engines without changing interface

### Data Flow Rules

**Always flows DOWN:**
```
UI → Controller → Service → Engine → Repository → Database
```

**NEVER:**
- Repository → Engine ❌
- Engine → Interface ❌
- Engine importing Database ❌

### Service Pipeline (Context Generation)

```
Crawler → Classifier → Assistant
(collect)  (extract)   (use context)
```

1. **Crawler**: Scrapes government websites → saves raw HTML to `crawled_pages` table
   - **Simple mode**: Fast HTTP requests (may get blocked by bot detection)
   - **Browser mode**: Playwright automation (bypasses 403 errors)

2. **Classifier**: LLM extracts structured data from HTML → saves to `visas` + `general_content` tables
   - Extracts visa programs (requirements, fees, processing time)
   - Extracts general content (employment services, healthcare, benefits, education)

3. **Matcher** (Optional): Scores visas against user profiles → eligibility checking

4. **Assistant**: **THE PRODUCT** - Q&A using LLM + retrieved context
   - Retrieves relevant visas + general content
   - Formats as context for LLM
   - LLM generates natural language answer
   - Returns answer + sources to user

---

## Context Generation System (What Makes This Work)

### The Dual Crawler System

**Problem**: Government websites (Australia, Canada, UK, Germany, UAE) block automated crawlers with 403 Forbidden errors.

**Solution**: Two crawler engines in the same service:

```python
services/crawler/
├── engine.py          # Simple HTTP crawler (fast, may be blocked)
├── browser_engine.py  # Browser automation (slower, bypasses blocks)
└── interface.py       # Switches between engines based on mode
```

**How it works:**
```python
# In interface.py
class CrawlerService:
    def __init__(self, mode='simple'):
        if mode == 'browser':
            # Use Playwright browser automation
            self.engine_class = BrowserCrawlerEngine
        else:
            # Use simple HTTP requests
            self.engine = CrawlerEngine(config, repo)
```

**In UI**: User selects "Simple" or "Browser" mode in Configuration tab.

**Use cases:**
- **Simple mode**: Test crawling, open websites, development
- **Browser mode**: Production crawling of government sites

### Data Models (What We Store)

**For Context Generation:**
- `CrawledPage`: Raw HTML + metadata (URL, title, country, depth, timestamp)
- `Visa`: Structured visa data (type, requirements, fees, processing_time, documents)
- `GeneralContent`: Non-visa immigration info (employment, healthcare, benefits, education)

**For LLM Context:**
- `Visa.to_dict()`: Serialized for LLM prompt
- `GeneralContent.to_dict()`: Serialized for LLM prompt
- Both include: title, country, key_points, summary, source_urls

**For Client Profiling:**
- `UserProfile`: Client details (nationality, age, education, work_experience)
- Used by Matcher to score visa eligibility
- Used by Assistant to personalize answers

### Retrieval Strategy (How We Find Context)

**Three retrieval methods:**

1. **Keyword Matching** (Basic - Always works):
   ```python
   # In retriever.py
   def _matches_query(self, visa, query):
       # Check if query keywords appear in visa data
       return any(keyword in visa.visa_type.lower()
                  for keyword in query_words)
   ```

2. **Enhanced Retrieval** (Better - Requires numpy):
   ```python
   # Uses hybrid search:
   # - Keyword matching + semantic similarity
   # - Ranks results by relevance score
   ```

3. **Semantic Search** (Best - Requires embeddings):
   ```python
   # Uses sentence-transformers
   # - Understands meaning, not just keywords
   # - "work visa" matches "employment permit"
   ```

**Formatted Context for LLM:**
```
=== VISA PROGRAMS ===
Visa 1: Skilled Worker Visa (Canada)
Category: Work
Requirements: Age 18-45, Bachelor degree, 2+ years experience...

=== GENERAL INFORMATION ===
Content 1: Employment Services for New Immigrants (Canada)
Summary: Free job search assistance, resume workshops...
Key Points:
- Free employment counseling
- Resume and interview prep
```

---

## Building New Features

### Step-by-Step (follow exactly)

1. **Define Model** (`shared/models.py`):
```python
@dataclass
class MyModel:
    field1: str
    field2: int

    @classmethod
    def from_db_row(cls, row: dict) -> 'MyModel':
        return cls(field1=row['field1'], field2=row['field2'])

    def to_dict(self) -> dict:
        return {'field1': self.field1, 'field2': self.field2}
```

2. **Update Database** (`shared/database.py`):
```python
def get_my_data(self) -> List[MyModel]:
    # Always return model objects using from_db_row
```

3. **Create Repository** (`services/myservice/repository.py`):
```python
class MyServiceRepository:
    def __init__(self):
        self.db = Database()

    def get_data(self) -> List[MyModel]:
        return self.db.get_my_data()  # Returns models, not dicts
```

4. **Create Engine** (`services/myservice/engine.py`):
```python
class MyServiceEngine:
    def __init__(self, config: dict, repository: MyServiceRepository):
        self.config = config
        self.repo = repository  # NO Database import!
        self.logger = setup_logger('myservice_engine')

    def process(self):
        data = self.repo.get_data()  # Get via repository
        # ... business logic ...
        self.repo.save_result(result)  # Save via repository
```

5. **Create Interfaces** (`services/myservice/interface.py`):
```python
class MyService:  # INTERIOR
    def __init__(self):
        self.repo = MyServiceRepository()
        self.engine = MyServiceEngine(config, self.repo)

    def process(self):
        return self.engine.process()

class MyServiceController:  # EXTERIOR
    def __init__(self):
        self.service = MyService()

    def process_with_progress(self, on_complete=None):
        result = self.service.process()
        if on_complete:
            on_complete(result)
        return result
```

6. **Create UI Page** (`pages/X_MyService.py`):
```python
from services.myservice.interface import MyServiceController

controller = MyServiceController()
controller.process_with_progress(
    on_complete=lambda r: st.success(f"Done: {r}")
)
```

### Adding Multiple Engines (Like Browser Crawler)

If you need alternate logic for same service:

```python
# Create alternate engine
services/myservice/alternate_engine.py

# Update interface to switch engines
class MyService:
    def __init__(self, mode='default'):
        self.repo = MyServiceRepository()

        if mode == 'alternate':
            self.engine = AlternateEngine(config, self.repo)
        else:
            self.engine = MyServiceEngine(config, self.repo)
```

**Use cases:**
- Different data sources (HTTP vs API vs Browser)
- Different algorithms (fast vs accurate)
- Different providers (OpenAI vs OpenRouter)

---

## Critical Patterns

### Database Access Pattern
```python
# In Repository only:
def get_items(self) -> List[Item]:
    return self.db.get_items()  # Use Database methods

# In Engine - NEVER:
from shared.database import Database  # ❌ WRONG
# Instead:
items = self.repo.get_items()  # ✅ CORRECT
```

### Model Usage Pattern
```python
# Always use models, not dicts:
visas = db.get_visas()  # Returns List[Visa]
for visa in visas:
    print(visa.country)  # Typed access
    print(visa.age_range)  # Property from model

# Legacy method (avoid):
visas_raw = db.get_latest_visas()  # Returns List[Dict]
```

### Context Formatting Pattern (For LLM)
```python
# In retriever.py
def format_context_for_llm(self, visas: List[Dict], general: List[Dict]) -> str:
    """Format BOTH visa and general content for LLM"""

    # Separate sections
    context = "=== VISA PROGRAMS ===\n"
    for visa in visas:
        context += self._format_visa(visa)

    context += "\n=== GENERAL INFORMATION ===\n"
    for content in general:
        context += self._format_general_content(content)

    return context
```

### Controller Callbacks Pattern
```python
def process_with_progress(
    self,
    items: List,
    on_start: Optional[Callable] = None,
    on_progress: Optional[Callable] = None,  # (current, total, item_name)
    on_complete: Optional[Callable] = None,  # (result)
    on_error: Optional[Callable] = None      # (error_message)
) -> Dict:
    if on_start:
        on_start()

    for i, item in enumerate(items, 1):
        result = self.service.process(item)
        if on_progress:
            on_progress(i, len(items), item.name)

    if on_complete:
        on_complete(result)
    return result
```

---

## Configuration Hierarchy

Priority (highest to lowest):
1. Runtime parameters (function arguments)
2. Service configs (`services/*/config.yaml`)
3. Database settings (`settings` table)
4. Environment variables (`.env` file)

### Key Configuration Files

**`.env`** (Required - Not in git):
```bash
# LLM API Keys
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_API_KEY=sk-...

# LLM Configuration
LLM_PROVIDER=openrouter
OPENROUTER_MODEL=google/gemini-2.0-flash-001:free
```

**`services/crawler/config.yaml`**:
```yaml
# Crawler mode selection
mode: "simple"  # or "browser"

# Browser settings (for mode="browser")
browser:
  headless: true
  browser_type: "chromium"
```

---

## Database Schema

Key tables (all with versioning):

- `crawled_pages` - Raw scraped HTML content
- `visas` - Structured visa programs data
- `general_content` - Non-visa immigration content (NEW in Phase 4)
- `clients` - User profiles for personalization
- `eligibility_checks` - Audit trail for matcher
- `embeddings` - Semantic search vectors (optional)
- `settings` - Configuration storage

All versioned tables have: `version`, `is_latest` (only query `is_latest=1`)

---

## LLM Integration (The Core Product)

### How Context Feeds the LLM

**1. User asks question:**
```
"What work visas are available for Canada?"
```

**2. Retriever finds context:**
```python
# In assistant/retriever.py
visas = self.retrieve_relevant_visas(query)
general = self.retrieve_relevant_general_content(query)
context = self.format_context_for_llm(visas, general)
```

**3. LLM receives prompt:**
```
System: You are an immigration consultant...

Context Information:
=== VISA PROGRAMS ===
Visa 1: Skilled Worker Visa (Canada)...

=== GENERAL INFORMATION ===
Content 1: Employment Services for New Immigrants...

User Question: What work visas are available for Canada?
```

**4. LLM generates answer:**
```
Based on the information provided, Canada offers several work visa
options:

1. **Skilled Worker Visa (Express Entry)**
   - Requirements: Age 18-45, Bachelor degree...
   - Fees: $850 application + $500 processing
   - Processing: 6-12 months

Additionally, new immigrants can access free employment services...
```

**5. System returns answer + sources:**
```json
{
  "answer": "Based on the information...",
  "sources": [
    {
      "type": "visa",
      "title": "Skilled Worker Visa",
      "country": "Canada",
      "url": "https://..."
    },
    {
      "type": "general",
      "title": "Employment Services",
      "country": "Canada",
      "url": "https://..."
    }
  ]
}
```

### LLM Client Setup

- **ConfigManager** auto-loads API keys from `.env` → Database → YAML
- **LLMClient** (`services/assistant/llm_client.py`) handles all LLM calls
- Supports OpenRouter (free models) and OpenAI
- Classifier and Assistant use LLM; Crawler and Matcher do not

**Free models (OpenRouter):**
- `google/gemini-2.0-flash-001:free` - Fast, good quality
- `meta-llama/llama-3.2-3b-instruct:free` - Lightweight

---

## Common Mistakes to Avoid

1. **❌ Engine importing Database**
   ```python
   # In engine.py - WRONG:
   from shared.database import Database
   ```
   Use repository instead.

2. **❌ Repository with business logic**
   ```python
   # In repository.py - WRONG:
   def get_matching_visas(self, user_age):
       visas = self.db.get_visas()
       return [v for v in visas if v.age_min <= user_age]  # Logic here!
   ```
   Keep repository to pure data access. Logic goes in engine.

3. **❌ Service methods with callbacks**
   ```python
   # In Service class - WRONG:
   def process(self, on_progress=None):  # Callbacks in Service
   ```
   Callbacks belong in Controller only. Service should be simple.

4. **❌ Returning dicts instead of models**
   ```python
   # In repository.py - WRONG:
   def get_visas(self) -> List[dict]:
       return [dict(row) for row in rows]
   ```
   Always return model objects: `return [Visa.from_db_row(r) for r in rows]`

5. **❌ Not providing BOTH visas and general content to LLM**
   ```python
   # WRONG - Only visas:
   context = format_context(visas)

   # CORRECT - Both types:
   context = format_context(visas, general_content)
   ```

6. **❌ Forgetting this is a CONTEXT GENERATION system**
   - Don't optimize for crawler speed alone - optimize for context quality
   - Don't just extract visa requirements - extract ALL relevant text
   - Don't limit to visas - include employment, healthcare, benefits
   - Don't forget: More context = Better LLM answers

---

## Key Files Reference

All detailed documentation is now in `docs/claude-references/`:

- `docs/claude-references/SYSTEM_DEVELOPMENT_GUIDE.md` - Complete feature building guide
- `docs/claude-references/SYSTEM_MAP.md` - Visual architecture diagrams
- `docs/claude-references/QUICK_REFERENCE.md` - Common code patterns
- `docs/claude-references/SERVICE_ARCHITECTURE.md` - Deep dive on Engine/Fuel pattern
- `docs/claude-references/ARCHITECTURE.md` - Overall system architecture
- `docs/claude-references/STRUCTURE.md` - Project structure overview
- `docs/claude-references/QUICK_START.md` - Getting started guide
- `docs/claude-references/CONFIG_GUIDE.md` - Configuration system guide
- `docs/claude-references/CONFIGURATION_LIFECYCLE.md` - Config lifecycle details
- `docs/claude-references/DOCUMENTATION_INDEX.md` - Complete documentation index
- `docs/claude-references/BUILD_SUMMARY.md` - Build and deployment summary
- `docs/claude-references/REFACTORING_COMPLETE.md` - Refactoring history
- `docs/claude-references/SYSTEM.md` - System overview
- `legacy/` - Old code (DO NOT USE - reference only)

---

## Testing Pattern

```python
# Test Repository (with real DB):
def test_repository():
    repo = MyRepository()
    result = repo.get_data()
    assert len(result) > 0

# Test Engine (with mock repo):
class MockRepo:
    def get_data(self):
        return [MyModel("test", 42)]

def test_engine():
    engine = MyEngine(config, MockRepo())
    result = engine.process()
    assert result['status'] == 'success'

# Test LLM Context Generation:
def test_context_retrieval():
    retriever = ContextRetriever(config)
    visas, general = retriever.retrieve_all_context("work visa Canada")
    assert len(visas) > 0 or len(general) > 0

    # Verify context formatting
    context = retriever.format_context_for_llm(visas, general)
    assert "=== VISA PROGRAMS ===" in context
    assert "=== GENERAL INFORMATION ===" in context
```

---

## UI Development

- All pages in `pages/` auto-discovered by Streamlit
- Always use **Controller** (not Service) in UI
- Use callbacks for progress: `on_start`, `on_progress`, `on_complete`, `on_error`
- See `pages/1_🕷️_Crawler.py` and `services/crawler/components/run_tab.py` for complete example

**Key UI Pages:**
- Page 1 - Crawler: Collects context (choose Simple or Browser mode)
- Page 2 - Classifier: Structures context (extracts visas + general content)
- Page 3 - Matcher: Scores visa eligibility (optional)
- **Page 4 - Assistant: THE PRODUCT** - Q&A interface for tourism office
- Page 5 - Settings: Configure LLM API keys
- Page 6 - Database: View stored context

---

## When Modifying Existing Services

1. **Never break the layer pattern** - if it's in engine.py, it stays pure logic
2. **Keep repository simple** - only data access, no algorithms
3. **Use existing patterns** - look at crawler/ for reference (especially dual engines)
4. **Update all 3 files** - repository, engine, interface when adding features
5. **Maintain backward compatibility** - old code may still use Service directly
6. **Remember the goal** - Every change should improve context quality for LLM

---

## Development Phases (Completed)

### ✅ Phase 1: Database & Models for General Content
- Added `GeneralContent` model
- Added `general_content` table with versioning
- Stores: employment, healthcare, benefits, education info

### ✅ Phase 2: Dual Extraction (Visa + General)
- Updated Classifier to extract BOTH types
- Uses same LLM, same extraction pipeline
- Filters visa vs general content based on categories

### ✅ Phase 3: UI for General Content Viewing
- Added tabs to view general content
- Search, filter, export capabilities

### ✅ Phase 4: Assistant Integration with General Content
- Retriever gets BOTH visas and general content
- LLM receives comprehensive context
- Sources show type: "🎫 Visa" or "📄 Guide"

### ✅ Phase 5: Browser Crawler Engine
- Added `BrowserCrawlerEngine` using Playwright
- Bypasses bot detection (403 errors)
- UI lets user choose crawler mode
- Preserves existing simple HTTP crawler

---

## Production Deployment Checklist

For tourism office deployment:

1. **Data Collection** (One-time, then monthly):
   - [ ] Run Browser Crawler for all countries
   - [ ] Run Classifier to extract visas + general content
   - [ ] Verify data quality in Database page

2. **LLM Configuration**:
   - [ ] Add API key to `.env` file
   - [ ] Test with sample questions
   - [ ] Optimize retrieval settings (max_visas, max_general_content)

3. **Staff Training**:
   - [ ] Show how to use Assistant page
   - [ ] Explain source verification
   - [ ] Demonstrate profile-based personalization

4. **Maintenance Schedule**:
   - [ ] Re-crawl monthly (government sites update)
   - [ ] Monitor LLM API usage/costs
   - [ ] Review and improve extraction schema

---

## Documentation Expectations

- Module docstrings: Purpose + "This is context generation for LLM" when applicable
- Class docstrings: Responsibilities + "Does NOT" section
- Public methods: Args, Returns, brief description
- Use type hints always: `def method(param: str) -> Dict:`
- Comment WHY not just WHAT: `# Bypass SSL for testing environments` not `# Set ignore_https_errors`

---

## Remember

**This is NOT a web scraping project.**
**This is NOT a visa database project.**
**This IS a CONTEXT GENERATION SYSTEM for an LLM-powered immigration assistant.**

Every component exists to make the LLM smarter and more helpful for tourism office staff serving their clients.

**The crawler** → Gathers text context
**The classifier** → Structures text context
**The database** → Stores text context
**The retriever** → Finds relevant context
**The LLM** → Reads context and generates natural language answers
**The Assistant UI** → **This is what the tourism office uses every day**
