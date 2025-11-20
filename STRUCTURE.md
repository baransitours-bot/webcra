# Project Structure

Clean, organized structure following the Engine/Fuel architecture.

## Directory Overview

```
immigration-crawler-demo/
├── app.py                          # 🏠 Main entry point (Streamlit)
├── pages/                          # 🎨 UI pages
├── services/                       # ⚙️  Backend services
├── shared/                         # 🔧 Common utilities
├── legacy/                         # 📦 Old code (for reference)
├── data/                           # 💾 Database & storage
├── logs/                           # 📝 Log files
└── tests/                          # 🧪 Test files
```

## Services (Following Engine/Fuel Pattern)

Each service has the same structure:

```
services/<service_name>/
├── repository.py      # FUEL TRANSPORT: Database access
├── engine.py          # ENGINE: Business logic
├── interface.py       # INTERFACE: Interior + Exterior APIs
└── config.yaml        # Configuration
```

### Crawler Service ✅ REFACTORED

```
services/crawler/
├── repository.py         # Get/save pages
├── engine.py             # Crawling logic
├── interface.py          # CrawlerService + CrawlerController
├── config.yaml           # Crawler settings
└── components/           # UI components (Streamlit)
    ├── config_tab.py
    ├── run_tab.py
    └── results_tab.py
```

**How to use:**

```python
# Interior (service-to-service)
from services.crawler.interface import CrawlerService
service = CrawlerService()
result = service.crawl_country("Australia", urls)

# Exterior (UI with callbacks)
from services.crawler.interface import CrawlerController
controller = CrawlerController()
controller.crawl_with_progress(countries, on_page=update_ui)
```

### Classifier Service ✅ REFACTORED

```
services/classifier/
├── repository.py         # Get pages, save visas
├── engine.py             # LLM extraction logic
├── interface.py          # ClassifierService + ClassifierController
├── extractor.py          # Pattern fallback (still used)
└── config.yaml           # Classifier settings
```

**How to use:**

```python
# Interior
from services.classifier.interface import ClassifierService
service = ClassifierService()
result = service.classify_country("Australia")

# Exterior (UI with callbacks)
from services.classifier.interface import ClassifierController
controller = ClassifierController()
controller.classify_with_progress(on_visa_found=show_visa)
```

### Matcher Service ⏳ TO BE REFACTORED

```
services/matcher/
├── main.py              # OLD: To be split
├── ranker.py            # Ranking logic
└── scorer.py            # Scoring logic
```

**Will become:**

```
services/matcher/
├── repository.py        # Get visas, profiles
├── engine.py            # Matching logic
├── interface.py         # MatcherService + MatcherController
└── config.yaml
```

### Assistant Service ⏳ TO BE REFACTORED

```
services/assistant/
├── retriever.py         # Simple retrieval
├── enhanced_retriever.py # Hybrid search
├── llm_client.py        # LLM communication
├── embeddings.py        # Semantic search
├── prompts.py           # LLM prompts
└── visa_utils.py        # Utilities
```

**Will become:**

```
services/assistant/
├── repository.py        # Get visas, conversations
├── engine.py            # Retrieval + chat logic
├── interface.py         # AssistantService + AssistantController
├── llm_client.py        # (keep as is)
├── embeddings.py        # (keep as is)
└── config.yaml
```

## Shared Layer (FUEL)

```
shared/
├── models.py            # Data structures (Visa, CrawledPage, etc.)
├── database.py          # SQLite operations
├── config_manager.py    # Configuration management
└── logger.py            # Logging utilities
```

**Usage:**

```python
from shared.models import Visa, CrawledPage
from shared.database import Database

# Load visas as models
db = Database()
visas = db.get_visas()  # Returns List[Visa]

# Work with typed objects
for visa in visas:
    print(visa.country)
    print(visa.age_range)  # Property from model
```

## UI Pages

```
pages/
├── 1_🕷️_Crawler.py       # Crawling UI
├── 2_📊_Classifier.py     # Classification UI
├── 3_🔍_Matcher.py        # Matching UI
├── 4_💬_Assistant.py      # Chat UI
├── 5_⚙️_Settings.py       # Configuration
├── 6_💾_Database.py       # Data viewer
└── 7_🌐_Global_Config.py  # Source management
```

**Usage pattern:**

```python
# pages/1_Crawler.py
from services.crawler.interface import CrawlerController

controller = CrawlerController()

# UI callbacks
def on_page(num, total, title):
    progress.progress(num / total)
    status.text(title)

# Run with progress
result = controller.crawl_with_progress(
    countries,
    on_page=on_page,
    on_complete=lambda r: st.success(f"Done: {r}")
)
```

## Legacy Directory

```
legacy/
├── README.md            # Explains what's here
├── crawler/
│   ├── spider.py        # Old crawler
│   └── main.py          # Old entry point
├── classifier/
│   ├── main.py          # Old classifier
│   ├── structurer.py    # Old structuring
│   └── visa_extractor.py # Old extraction
└── assistant/
    └── main.py          # Old assistant
```

**⚠️ Do not use these files - they are for reference only.**

## Data Directory

```
data/
└── immigration.db       # SQLite database (single source of truth)
```

All data stored here:
- Crawled pages
- Extracted visas
- Configuration
- User profiles
- Audit trail

## Configuration Hierarchy

```
1. .env file             # Environment variables (API keys)
   ↓
2. Database settings     # Stored in settings table
   ↓
3. YAML configs          # Service-specific configs
```

**Example:**

```bash
# .env
LLM_API_KEY=your_key_here
LLM_MODEL=google/gemini-2.0-flash-001:free
```

## Documentation Files

```
├── ARCHITECTURE.md       # System overview
├── SERVICE_ARCHITECTURE.md  # Engine/Fuel pattern explained
├── STRUCTURE.md          # This file
├── SYSTEM.md             # Full system documentation
├── QUICK_START.md        # Getting started guide
└── README.md             # Project introduction
```

## Architecture Layers

```
┌─────────────────────────────────┐
│  LAYER 4: INTERFACES            │
│  - UI (Streamlit pages)         │
│  - Controllers (progress, etc)  │
│  - Service APIs                 │
└─────────────────────────────────┘
              ↕
┌─────────────────────────────────┐
│  LAYER 3: ENGINES               │
│  - Business logic               │
│  - Algorithms                   │
│  - Pure functions               │
└─────────────────────────────────┘
              ↕
┌─────────────────────────────────┐
│  LAYER 2: REPOSITORIES          │
│  - Data access                  │
│  - CRUD operations              │
│  - Model conversion             │
└─────────────────────────────────┘
              ↕
┌─────────────────────────────────┐
│  LAYER 1: DATA (FUEL)           │
│  - Models                       │
│  - Database                     │
│  - Configuration                │
└─────────────────────────────────┘
```

## How to Navigate

### Want to understand the data?
→ Look at `shared/models.py`

### Want to modify business logic?
→ Look at `services/<service>/engine.py`

### Want to change UI behavior?
→ Look at `pages/<page>.py` and `services/<service>/interface.py` (Controller)

### Want to add/modify database operations?
→ Look at `services/<service>/repository.py`

### Want to change configuration?
→ Look at `services/<service>/config.yaml` or use Settings UI

## Benefits of This Structure

✅ **Clear separation** - Each file has one responsibility

✅ **Easy testing** - Mock any layer independently

✅ **Easy to modify** - Change one layer without affecting others

✅ **Consistent pattern** - All services follow same structure

✅ **Self-documenting** - Structure tells you what each file does

## Migration Status

| Service | Repository | Engine | Interface | Status |
|---------|-----------|---------|-----------|--------|
| Crawler | ✅ | ✅ | ✅ | Complete |
| Classifier | ✅ | ✅ | ✅ | Complete |
| Matcher | ❌ | ❌ | ❌ | Pending |
| Assistant | ❌ | ❌ | ❌ | Pending |

## Next Steps

1. ✅ Refactor Crawler
2. ✅ Refactor Classifier
3. ⏳ Update UI to use new Controllers
4. ⏳ Refactor Matcher
5. ⏳ Refactor Assistant
6. ⏳ Update tests
7. ⏳ Remove legacy files

## Quick Reference

### Run the app
```bash
streamlit run app.py
```

### Use a service programmatically
```python
from services.crawler.interface import CrawlerService
service = CrawlerService()
service.crawl_country("Australia", ["https://..."])
```

### Use from UI
```python
from services.crawler.interface import CrawlerController
controller = CrawlerController()
controller.crawl_with_progress(countries, callbacks...)
```

### Access data
```python
from shared.database import Database
db = Database()
visas = db.get_visas()  # Typed Visa objects
```

### Modify configuration
- UI: Settings page (⚙️)
- Code: Edit `services/<service>/config.yaml`
- Environment: Edit `.env` file
