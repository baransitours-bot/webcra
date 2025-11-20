# System Architecture

A simple guide to understanding and editing this codebase.

## Quick Overview

```
immigration-crawler-demo/
├── app.py                    # Main Streamlit app (start here)
├── pages/                    # UI pages for each service
├── services/                 # Backend logic
│   ├── crawler/             # Web scraping
│   ├── classifier/          # LLM data extraction
│   ├── matcher/             # User-visa matching
│   └── assistant/           # Q&A chatbot
├── shared/                   # Common utilities
│   ├── database.py          # SQLite operations
│   ├── models.py            # Data structures
│   ├── config_manager.py    # Settings management
│   └── logger.py            # Logging
└── data/
    └── immigration.db       # SQLite database (single source of truth)
```

## Data Flow

```
1. CRAWL         2. CLASSIFY        3. USE
---------        -----------        --------
Websites   →    Raw Pages     →    Structured     →    Matcher
              (crawled_pages)     Visas (visas)        Assistant
                                                       Database Viewer
```

## Key Concepts

### 1. Single Source of Truth: SQLite Database

All data lives in `data/immigration.db`. No file storage.

```python
from shared.database import Database

db = Database()

# Get visas as model objects (preferred)
visas = db.get_visas()           # Returns List[Visa]
pages = db.get_pages()           # Returns List[CrawledPage]

# Get as dictionaries (legacy)
visas = db.get_latest_visas()    # Returns List[Dict]
```

### 2. Data Models

Clear data structures in `shared/models.py`:

```python
from shared.models import Visa, CrawledPage, UserProfile

# Create from database row
visa = Visa.from_db_row(row)

# Access properties
print(visa.country)              # "Australia"
print(visa.age_range)            # "18-45 years"
print(visa.education_required)   # "Bachelors"

# Convert back to dict
data = visa.to_dict()
```

### 3. Configuration

Settings come from: `.env` → Database → YAML files

```python
from shared.config_manager import get_config

config = get_config()
api_key = config.get_api_key()
model = config.get('llm.model')
```

## Services Explained

### Crawler (`services/crawler/`)

**What it does:** Scrapes immigration websites

**Key file:** `spider.py`

```python
class ImmigrationCrawler:
    def crawl_country(self, country_name, seed_urls):
        # Visits each URL, extracts content
        # Saves to database
        self.db.save_crawled_page(url, country, title, content, metadata)
```

**To modify:**
- Add countries: Edit `config.yaml` countries section
- Change scraping behavior: Edit `spider.py` extract methods
- Add keywords: Edit `config.yaml` keywords section

### Classifier (`services/classifier/`)

**What it does:** Extracts structured visa info using LLM

**Key file:** `extractor.py`

```python
class VisaExtractor:
    def extract_visa_info(self, page_content, country):
        # Sends content to LLM
        # Parses response into visa structure
        # Returns structured visa data
```

**To modify:**
- Change extraction prompt: Edit `extractor.py` prompt
- Add new fields: Update extraction prompt + `shared/models.py`

### Matcher (`services/matcher/`)

**What it does:** Matches users to eligible visas

**Key file:** `ranker.py`

```python
class VisaRanker:
    def rank_all_visas(self, user_profile, visas):
        # Calculates eligibility score for each visa
        # Returns sorted matches
```

**To modify:**
- Change scoring: Edit `ranker.py` score calculation
- Add criteria: Update `config.yaml` weights

### Assistant (`services/assistant/`)

**What it does:** Answers questions about visas

**Key files:**
- `retriever.py` - Simple keyword search
- `enhanced_retriever.py` - Hybrid search (semantic + keyword)
- `chat.py` - LLM conversation

```python
class ContextRetriever:
    def retrieve_relevant_visas(self, query):
        # Finds visas matching the query
        # Returns top matches
```

**To modify:**
- Add search features: Edit retriever methods
- Change response style: Edit `chat.py` prompts

## UI Pages

Each page in `pages/` corresponds to a service:

| Page | Purpose | Key Components |
|------|---------|----------------|
| 1_Crawler | Run web scraping | Country selector, URL config |
| 2_Classifier | Extract visa data | Debug mode, progress tracking |
| 3_Matcher | Match users | Profile form, results display |
| 4_Assistant | Q&A chat | Chat interface |
| 5_Settings | Configure system | API keys, model selection |
| 6_Database | View data | Tables, export/import |
| 7_Global_Config | Manage sources | Countries, keywords |

## Common Tasks

### Add a New Country

1. Go to Global Config page in UI
2. Add country name and seed URLs
3. Run Crawler
4. Run Classifier

### Change LLM Model

1. Go to Settings page
2. Select new model from dropdown
3. Save

Or edit `.env`:
```
LLM_MODEL=google/gemini-2.0-flash-001:free
```

### Add New Visa Fields

1. Update `shared/models.py` - add to Visa class
2. Update `services/classifier/extractor.py` - add to extraction prompt
3. Update `shared/database.py` - add to schema if needed
4. Update UI pages to display new field

### Debug Issues

Check logs in `logs/` directory:
- `crawler.log` - Crawling issues
- `classifier.log` - Extraction issues
- `app.log` - General app issues

### Export/Import Data

Use Database page (6_Database):
- Export: Downloads JSON
- Import: Uploads JSON to database

## Code Patterns

### Service Initialization

All services follow this pattern:

```python
class MyService:
    def __init__(self, config):
        self.config = config
        self.db = Database()
        self.logger = setup_logger('my_service')
```

### Error Handling

Services handle errors gracefully:

```python
try:
    result = self.do_something()
except Exception as e:
    self.logger.error(f"Failed: {e}")
    return default_value
```

### Database Operations

Always use context manager:

```python
with self.db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visas")
    rows = cursor.fetchall()
```

## Testing

Run tests:
```bash
python -m pytest tests/
```

Key test files:
- `test_database.py` - Database operations
- `test_crawler.py` - Crawling
- `test_classifier.py` - Extraction
- `test_matcher.py` - Matching
- `test_assistant.py` - Q&A

## Performance Tips

1. **Use model methods** - `db.get_visas()` instead of `db.get_latest_visas()`
2. **Limit results** - Always use `max_visas` config
3. **Cache configs** - Use `@st.cache_resource` in Streamlit
4. **Batch operations** - Commit after multiple inserts

## Troubleshooting

### No visas found
- Check database has data: Database page
- Run Crawler then Classifier

### API errors
- Check API key in Settings
- Verify model name is correct
- Check logs for details

### Import errors
- Activate virtual environment
- Install requirements: `pip install -r requirements.txt`
