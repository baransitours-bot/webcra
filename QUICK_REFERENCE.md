# Quick Reference Guide

Fast answers to common development questions.

---

## Common Tasks

### Add a New Field to Visa

1. Update `shared/models.py`:
   ```python
   @dataclass
   class Visa:
       # ... existing fields
       new_field: str = ""  # Add here
   ```

2. Update `shared/database.py`:
   ```python
   # Add to schema
   cursor.execute("""
       ALTER TABLE visas ADD COLUMN new_field TEXT
   """)

   # Add to save_visa()
   def save_visa(..., new_field: str):
       cursor.execute("""
           INSERT INTO visas (..., new_field)
           VALUES (..., ?)
       """, (..., new_field))
   ```

3. Done! Models automatically handle the new field.

---

### Create a New Service

Copy the pattern from existing service:

```bash
# Create directory
mkdir services/myservice

# Create files
touch services/myservice/__init__.py
touch services/myservice/repository.py
touch services/myservice/engine.py
touch services/myservice/interface.py
touch services/myservice/config.yaml
```

Then follow SYSTEM_DEVELOPMENT_GUIDE.md

---

### Add a UI Page

1. Create `pages/X_MyPage.py`:
   ```python
   import streamlit as st
   from services.myservice.interface import MyServiceController

   st.title("My Page")

   controller = MyServiceController()
   # Use controller methods
   ```

2. Restart Streamlit - page appears automatically!

---

### Access Database

```python
from shared.database import Database

db = Database()

# Get visas
visas = db.get_visas()  # Returns List[Visa]

# Get pages
pages = db.get_pages(country="Australia")

# Get statistics
stats = db.get_stats()
```

---

### Use a Service Programmatically

```python
from services.crawler.interface import CrawlerService

service = CrawlerService()
result = service.crawl_country("Australia", urls)
print(f"Crawled {result['pages_saved']} pages")
```

---

### Use a Controller in UI

```python
from services.crawler.interface import CrawlerController

controller = CrawlerController()

# With callbacks
def on_complete(result):
    st.success(f"Done: {result}")

controller.crawl_with_progress(
    countries,
    on_complete=on_complete
)
```

---

### Run Tests

```bash
# All tests
python -m pytest tests/

# Specific test
python -m pytest tests/test_crawler.py

# With coverage
python -m pytest --cov=services tests/
```

---

### Debug an Issue

1. Check logs:
   ```bash
   tail -f logs/app.log
   ```

2. Add debug logging:
   ```python
   self.logger.debug(f"Debug info: {variable}")
   ```

3. Use Database viewer (page 6) to inspect data

---

### Update Configuration

**Environment variables** (`.env`):
```bash
LLM_API_KEY=your_key_here
LLM_MODEL=google/gemini-2.0-flash-001:free
```

**Service config** (`services/*/config.yaml`):
```yaml
setting_name: value
```

**Database settings** (via UI):
- Go to Settings page (5)
- Update values
- Save

---

## File Locations

| What | Where |
|------|-------|
| Data models | `shared/models.py` |
| Database operations | `shared/database.py` |
| Service logic | `services/*/engine.py` |
| Data access | `services/*/repository.py` |
| APIs | `services/*/interface.py` |
| UI pages | `pages/*.py` |
| Configuration | `services/*/config.yaml` |
| Database | `data/immigration.db` |
| Logs | `logs/*.log` |

---

## Code Patterns

### Pattern: Get Data

```python
# In Repository
def get_items(self) -> List[Item]:
    return self.db.get_items()

# In Engine
def process(self):
    items = self.repo.get_items()
    # ... process
```

### Pattern: Save Data

```python
# In Repository
def save_item(self, item: Item) -> int:
    return self.db.save_item(item)

# In Engine
def process(self, data):
    result = self._do_work(data)
    self.repo.save_item(result)
```

### Pattern: Progress Callback

```python
# In Controller
def process_with_progress(self, items, on_progress=None):
    total = len(items)
    for i, item in enumerate(items, 1):
        result = self.service.process(item)
        if on_progress:
            on_progress(i, total)
```

### Pattern: Error Handling

```python
# In Engine
try:
    result = self._process(data)
    return {'status': 'success', 'result': result}
except ValueError as e:
    self.logger.error(f"Validation error: {e}")
    return {'status': 'error', 'message': str(e)}
```

---

## Import Statements

### Common Imports

```python
# Models
from shared.models import Visa, CrawledPage, UserProfile

# Database
from shared.database import Database

# Logging
from shared.logger import setup_logger

# Type hints
from typing import List, Dict, Optional, Callable

# Config
import yaml
from pathlib import Path
```

### Service Imports

```python
# Use Service (interior)
from services.crawler.interface import CrawlerService

# Use Controller (exterior)
from services.crawler.interface import CrawlerController

# Use Repository (rare - usually internal)
from services.crawler.repository import CrawlerRepository
```

---

## Database Queries

### Get Latest Visas

```python
db = Database()
visas = db.get_visas()  # All visas as Visa objects
visas = db.get_visas(country="Australia")  # Filtered
```

### Get Raw Data

```python
db = Database()
raw_visas = db.get_latest_visas()  # Returns dicts, not models
```

### Save Visa

```python
db = Database()
visa_id = db.save_visa(
    visa_type="Work Visa",
    country="Australia",
    category="work",
    requirements={...},
    fees={...},
    processing_time="2 months",
    source_urls=["https://..."]
)
```

---

## Streamlit UI Patterns

### Progress Bar

```python
progress = st.progress(0)
for i in range(100):
    progress.progress(i / 100)
```

### Status Updates

```python
status = st.empty()
status.text("Processing...")
# ... do work
status.text("Done!")
```

### Callbacks

```python
def update_ui(current, total, item_name):
    progress.progress(current / total)
    status.text(f"{current}/{total}: {item_name}")

controller.process_with_progress(
    items,
    on_progress=update_ui
)
```

---

## Testing Patterns

### Test Repository

```python
def test_repository():
    repo = MyRepository()
    item = MyModel(field="value")

    id = repo.save_item(item)

    assert id > 0
    items = repo.get_items()
    assert len(items) == 1
```

### Test Engine (with mock)

```python
class MockRepo:
    def get_items(self):
        return [MyModel("test")]

def test_engine():
    engine = MyEngine(config, MockRepo())
    result = engine.process()

    assert result['status'] == 'success'
```

### Test Service

```python
def test_service():
    service = MyService()
    result = service.process("input")

    assert 'status' in result
```

---

## Debugging Tips

### Enable Debug Logging

```python
# In service
self.logger.setLevel(logging.DEBUG)
self.logger.debug(f"Variable value: {var}")
```

### Inspect Database

```bash
# Open database
sqlite3 data/immigration.db

# List tables
.tables

# View data
SELECT * FROM visas LIMIT 5;

# Exit
.quit
```

### Check Logs

```bash
# View logs
tail -f logs/crawler.log
tail -f logs/classifier.log

# Search logs
grep ERROR logs/*.log
```

---

## Common Errors

### Import Error

```
ModuleNotFoundError: No module named 'services'
```

**Fix:** Ensure project root is in PYTHONPATH
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Database Locked

```
sqlite3.OperationalError: database is locked
```

**Fix:** Use context manager
```python
with self.db.get_connection() as conn:
    # Your code here
```

### Circular Import

```
ImportError: cannot import name 'X' from partially initialized module
```

**Fix:** Move import inside function
```python
def my_method(self):
    from services.other import Thing  # Import here
```

---

## Performance Tips

### Batch Operations

```python
# Bad: Save one at a time
for item in items:
    db.save_item(item)

# Good: Batch insert
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO ...",
        [(item.field1, item.field2) for item in items]
    )
```

### Limit Results

```python
# Always limit queries
visas = db.get_visas()[:max_results]
```

### Use Caching

```python
# In Streamlit
@st.cache_resource
def load_service():
    return MyService()

service = load_service()  # Cached
```

---

## Git Workflow

### Before Coding

```bash
git pull origin main
git checkout -b feature/my-feature
```

### During Development

```bash
git add services/myservice/
git commit -m "Add myservice feature"
```

### After Testing

```bash
git push origin feature/my-feature
# Create pull request on GitHub
```

---

## Documentation Standards

### Module Docstring

```python
"""
Module Name - Purpose

Brief description of what this module does.
"""
```

### Class Docstring

```python
class MyClass:
    """
    Brief description.

    Responsibilities:
    - What it does

    Does NOT:
    - What it doesn't do
    """
```

### Method Docstring

```python
def my_method(self, param: str) -> Dict:
    """
    Brief description.

    Args:
        param: Parameter description

    Returns:
        Return value description
    """
```

---

## Useful Commands

### Run Application

```bash
streamlit run app.py
```

### Run Tests

```bash
python -m pytest
```

### Check Code Style

```bash
# Install flake8
pip install flake8

# Check style
flake8 services/
```

### View Database

```bash
# Install DB browser
# https://sqlitebrowser.org/

# Or use CLI
sqlite3 data/immigration.db
```

### Export Data

```bash
# From UI: Database page → Export
# Or programmatically:
python
>>> from shared.database import Database
>>> db = Database()
>>> visas = db.get_visas()
>>> import json
>>> with open('export.json', 'w') as f:
...     json.dump([v.to_dict() for v in visas], f)
```

---

## Need More Help?

| Question | Document |
|----------|----------|
| How to build features? | `SYSTEM_DEVELOPMENT_GUIDE.md` |
| How does it work? | `SYSTEM_MAP.md` |
| Architecture details? | `SERVICE_ARCHITECTURE.md` |
| File structure? | `STRUCTURE.md` |
| What was changed? | `REFACTORING_COMPLETE.md` |

---

Keep this file handy for quick answers while developing!
