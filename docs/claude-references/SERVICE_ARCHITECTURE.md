# Service Architecture Pattern

## The Engine/Fuel Philosophy

Each service follows this layered architecture:

```
┌─────────────────────────────────────────────────────┐
│  EXTERIOR INTERFACE (UI, CLI, API)                  │
│  File: interface.py → CrawlerController             │
│                                                      │
│  • Used by Streamlit pages                         │
│  • Provides callbacks for progress                  │
│  • Handles user-facing operations                   │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  INTERIOR INTERFACE (Service-to-Service)            │
│  File: interface.py → CrawlerService                │
│                                                      │
│  • Clean Python API                                 │
│  • Used by other services                           │
│  • Simple, typed methods                            │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  ENGINE (Core Business Logic)                       │
│  File: engine.py → CrawlerEngine                    │
│                                                      │
│  • Pure business logic                              │
│  • No database access                               │
│  • No UI concerns                                   │
│  • Highly testable                                  │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  FUEL TRANSPORT (Repository Pattern)                │
│  File: repository.py → CrawlerRepository            │
│                                                      │
│  • All database operations                          │
│  • Data fetching/storing                            │
│  • Transforms DB rows to Models                     │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  FUEL (Data Layer)                                  │
│  Files: shared/models.py, shared/database.py        │
│                                                      │
│  • Data models (Visa, CrawledPage)                 │
│  • Database (SQLite)                                │
│  • Configuration                                    │
└─────────────────────────────────────────────────────┘
```

## Example: Crawler Service

### Layer 1: FUEL (Data)

```python
# shared/models.py
@dataclass
class CrawledPage:
    url: str
    country: str
    title: str
    content: str
    metadata: Dict
```

### Layer 2: FUEL TRANSPORT (Repository)

```python
# services/crawler/repository.py
class CrawlerRepository:
    def save_page(self, page: CrawledPage) -> int:
        """Store page in database"""
        return self.db.save_crawled_page(...)

    def get_pages_by_country(self, country: str):
        """Fetch pages from database"""
        return self.db.get_pages(country=country)
```

**Responsibilities:**
- All database operations
- Convert DB rows to Models
- No business logic

### Layer 3: ENGINE (Core Logic)

```python
# services/crawler/engine.py
class CrawlerEngine:
    def __init__(self, config: dict, repository: CrawlerRepository):
        self.config = config
        self.repo = repository  # Uses repo, not DB directly

    def crawl_country(self, country: str, urls: List[str]) -> Dict:
        """Core crawling logic"""
        for url in urls:
            page = self._crawl_page(url)
            self.repo.save_page(page)  # Save via repository
```

**Responsibilities:**
- Business logic only
- Fetches/stores via repository
- No database knowledge
- No UI knowledge

### Layer 4a: INTERIOR INTERFACE (Service API)

```python
# services/crawler/interface.py
class CrawlerService:
    """Python API for other services"""

    def __init__(self):
        self.repo = CrawlerRepository()
        self.engine = CrawlerEngine(config, self.repo)

    def crawl_country(self, name: str, urls: List[str]) -> Dict:
        """Simple API method"""
        return self.engine.crawl_country(name, urls)

    def get_statistics(self) -> Dict:
        """Get stats"""
        pages = self.repo.get_all_pages()
        return self._calculate_stats(pages)
```

**Usage by other services:**

```python
from services.crawler.interface import CrawlerService

crawler = CrawlerService()
result = crawler.crawl_country("Australia", ["https://..."])
stats = crawler.get_statistics()
```

### Layer 4b: EXTERIOR INTERFACE (UI Controller)

```python
# services/crawler/interface.py
class CrawlerController:
    """UI/CLI interface with callbacks"""

    def crawl_with_progress(
        self,
        countries: List[Dict],
        on_start=None,
        on_page=None,
        on_complete=None
    ):
        """Crawl with progress tracking for UI"""
        for country in countries:
            if on_start:
                on_start(country['name'])

            result = self.service.crawl_country(...)

            if on_complete:
                on_complete(result)
```

**Usage in Streamlit:**

```python
from services.crawler.interface import CrawlerController

controller = CrawlerController()

# Callbacks for UI updates
def on_page(page_num, total, title):
    progress_bar.progress(page_num / total)
    status.text(f"Crawling: {title}")

results = controller.crawl_with_progress(
    countries,
    on_page=on_page
)
```

## Benefits of This Pattern

### 1. Separation of Concerns
- Engine doesn't know about database
- Engine doesn't know about UI
- Repository doesn't know about business logic

### 2. Easy Testing

```python
# Mock the repository
class MockRepository:
    def save_page(self, page):
        return 1

# Test engine in isolation
engine = CrawlerEngine(config, MockRepository())
result = engine.crawl_country("Test", ["https://test.com"])
```

### 3. Flexible Interfaces

```python
# Use from Python
service = CrawlerService()
service.crawl_country("Australia", urls)

# Use from UI with progress
controller = CrawlerController()
controller.crawl_with_progress(countries, callbacks...)

# Use as one-liner
from services.crawler.interface import crawl_country
crawl_country("Australia", urls)
```

### 4. Easy to Modify

**Change database?** → Update `repository.py` only

**Change business logic?** → Update `engine.py` only

**Add UI feature?** → Update `interface.py` (Controller) only

**Change data structure?** → Update `models.py` only

## File Structure

```
services/crawler/
├── __init__.py
├── config.yaml          # Configuration
├── repository.py        # FUEL TRANSPORT: Data access
├── engine.py            # ENGINE: Business logic
├── interface.py         # INTERFACES: APIs (Interior + Exterior)
└── spider.py            # OLD FILE (can remove)
```

## How to Apply to Other Services

### Classifier Service

```
services/classifier/
├── repository.py        # Get pages, save visas
├── engine.py            # LLM extraction logic
├── interface.py         # ClassifierService + ClassifierController
└── config.yaml
```

### Matcher Service

```
services/matcher/
├── repository.py        # Get visas, save matches
├── engine.py            # Scoring/ranking logic
├── interface.py         # MatcherService + MatcherController
└── config.yaml
```

### Assistant Service

```
services/assistant/
├── repository.py        # Get visas, save conversations
├── engine.py            # Retrieval + LLM logic
├── interface.py         # AssistantService + AssistantController
└── config.yaml
```

## Migration Plan

1. **Crawler** ✅ (Done - example above)
2. **Classifier** - Next
3. **Matcher** - After Classifier
4. **Assistant** - Last

Each service gets:
- `repository.py` - Data access
- `engine.py` - Business logic
- `interface.py` - Two interfaces (Interior + Exterior)

## Usage Examples

### From Streamlit UI

```python
# pages/1_Crawler.py
from services.crawler.interface import CrawlerController

controller = CrawlerController()

if st.button("Start Crawl"):
    progress = st.progress(0)
    status = st.empty()

    def on_page(num, total, title):
        progress.progress(num / total)
        status.text(f"Page {num}/{total}: {title}")

    results = controller.crawl_with_progress(
        countries,
        on_page=on_page
    )

    st.success(f"Crawled {results['pages_saved']} pages")
```

### From Another Service

```python
# services/classifier/engine.py
from services.crawler.interface import CrawlerService

class ClassifierEngine:
    def __init__(self):
        self.crawler = CrawlerService()

    def classify_country(self, country):
        # Get crawled pages
        pages = self.crawler.get_crawled_pages(country)

        # Classify them
        for page in pages:
            visa = self.extract_visa(page)
            ...
```

### From CLI

```python
# cli.py
from services.crawler.interface import crawl_all

results = crawl_all()
print(f"Crawled {len(results)} countries")
```

## Rules for Each Layer

### FUEL (Models, Database)
- ✅ Define data structures
- ✅ Database schema
- ❌ No business logic
- ❌ No UI code

### FUEL TRANSPORT (Repository)
- ✅ CRUD operations
- ✅ Convert DB rows to Models
- ❌ No business logic
- ❌ No HTTP requests
- ❌ No UI code

### ENGINE (Core Logic)
- ✅ Business logic
- ✅ Algorithms
- ✅ Use repository for data
- ❌ No database imports
- ❌ No UI code
- ❌ No callbacks

### INTERIOR INTERFACE (Service)
- ✅ Clean Python API
- ✅ Setup/initialization
- ✅ Simple method signatures
- ❌ No callbacks
- ❌ No UI concerns

### EXTERIOR INTERFACE (Controller)
- ✅ UI-friendly methods
- ✅ Progress callbacks
- ✅ Error handling for users
- ✅ Validation
- ✅ Uses Service internally

This pattern makes the system:
- **Modular** - Each layer is independent
- **Testable** - Mock any layer
- **Maintainable** - Change one layer without affecting others
- **Understandable** - Clear responsibilities
