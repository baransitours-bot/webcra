# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Setup & Running

```bash
# Install dependencies
pip install -r requirements.txt

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
```

## Architecture: Engine/Fuel Pattern

This system uses a strict 4-layer architecture called "Engine/Fuel" pattern. **Every service follows this exact structure:**

```
services/<service>/
├── repository.py      # Layer 2: FUEL TRANSPORT - Database access only
├── engine.py          # Layer 3: ENGINE - Pure business logic, no DB imports
├── interface.py       # Layer 4: INTERFACES - Service (interior) + Controller (exterior)
└── config.yaml        # Configuration
```

### Layer Responsibilities (CRITICAL)

**Layer 1: DATA (shared/)**
- `shared/models.py` - Dataclass models (Visa, CrawledPage, UserProfile, etc.)
- `shared/database.py` - SQLite operations with versioning
- Single source of truth: `data/immigration.db`

**Layer 2: REPOSITORY (repository.py)**
- Database CRUD operations only
- Returns model objects (NOT dicts)
- No business logic allowed
- Example: `get_visas()`, `save_visa()`

**Layer 3: ENGINE (engine.py)**
- Pure business logic
- NEVER imports Database directly - uses repository
- No UI knowledge
- Example: `CrawlerEngine.crawl_country()`, `ClassifierEngine.classify_pages()`

**Layer 4: INTERFACES (interface.py)**
- **Service class (INTERIOR)**: Clean Python API for service-to-service calls
- **Controller class (EXTERIOR)**: UI-friendly with callbacks (on_start, on_complete, on_error, on_progress)
- Both use same engine + repository

### Data Flow Rules

**Always flows DOWN:**
```
UI → Controller → Service → Engine → Repository → Database
```

**NEVER:**
- Repository → Engine ❌
- Engine → Interface ❌
- Engine importing Database ❌

### Service Pipeline

```
Crawler → Classifier → Matcher/Assistant
(collect)  (extract)   (use data)
```

1. **Crawler**: Scrapes government websites → saves to `crawled_pages` table
2. **Classifier**: LLM extracts structured data → saves to `visas` table
3. **Matcher**: Scores visas against user profiles
4. **Assistant**: Q&A using LLM + visa context

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

## Configuration Hierarchy

Priority (highest to lowest):
1. Runtime parameters (function arguments)
2. Service configs (`services/*/config.yaml`)
3. Database settings (`settings` table)
4. Environment variables (`.env` file)

## Database Schema

Key tables:
- `crawled_pages` - Raw scraped content (versioned)
- `visas` - Structured visa data (versioned)
- `clients` - User profiles
- `eligibility_checks` - Audit trail for matches
- `embeddings` - Semantic search vectors
- `settings` - Configuration

All versioned tables have: `version`, `is_latest` (only query `is_latest=1`)

## LLM Integration

- **ConfigManager** auto-loads API keys from `.env` → Database → YAML
- **LLMClient** (`services/assistant/llm_client.py`) handles all LLM calls
- Supports OpenRouter (free models) and OpenAI
- Classifier and Assistant use LLM; Crawler and Matcher do not

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

5. **❌ Not using convenience methods**
   ```python
   # WRONG (old way):
   visas_raw = db.get_latest_visas()
   for v in visas_raw:
       visa = dict(v)
       visa['requirements'] = json.loads(visa['requirements'])  # Manual parsing

   # CORRECT (new way):
   visas = db.get_visas()  # Already parsed as Visa objects
   ```

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
```

## UI Development

- All pages in `pages/` auto-discovered by Streamlit
- Always use **Controller** (not Service) in UI
- Use callbacks for progress: `on_start`, `on_progress`, `on_complete`, `on_error`
- See `pages/1_🕷️_Crawler.py` and `services/crawler/components/run_tab.py` for complete example

## When Modifying Existing Services

1. **Never break the layer pattern** - if it's in engine.py, it stays pure logic
2. **Keep repository simple** - only data access, no algorithms
3. **Use existing patterns** - look at crawler/ for reference
4. **Update all 3 files** - repository, engine, interface when adding features
5. **Maintain backward compatibility** - old code may still use Service directly

## Documentation Expectations

- Module docstrings: Purpose of the module
- Class docstrings: Responsibilities + "Does NOT" section
- Public methods: Args, Returns, brief description
- Use type hints always: `def method(param: str) -> Dict:`
