# Legacy Code

This directory contains old implementations that have been replaced by the new layered architecture.

**⚠️ These files are kept for reference only - do not use in production.**

## Why These Files Are Here

The codebase was refactored to follow the **Engine/Fuel architecture pattern**:
- **Engine** = Core business logic
- **Fuel** = Data (models, database)
- **Fuel Transport** = Repository pattern
- **Interface** = Interior (service API) + Exterior (UI controller)

## What's in Legacy

### Crawler (`legacy/crawler/`)
- `spider.py` - Old crawler implementation
  - **Replaced by:** `services/crawler/engine.py` + `repository.py` + `interface.py`
  - **Why replaced:** Mixed concerns (data access + business logic + configuration)

### Classifier (`legacy/classifier/`)
- `main.py` - Old classifier entry point
  - **Replaced by:** `services/classifier/interface.py`
- `structurer.py` - Old data structuring logic
  - **Replaced by:** `services/classifier/engine.py`
- `visa_extractor.py` - Old LLM extractor
  - **Replaced by:** `services/classifier/engine.py`

## Still Active (Not Legacy)

These files are still used:
- `services/classifier/extractor.py` - Pattern-based extraction (fallback when LLM unavailable)

## Can I Delete Legacy Files?

**Not recommended yet.** Keep them for:
1. Reference during migration
2. Understanding old logic
3. Rollback if needed

After full testing of the new architecture (1-2 weeks), these can be safely deleted.

## New Architecture

See `SERVICE_ARCHITECTURE.md` for the new pattern.

### Quick comparison:

**OLD WAY:**
```python
# Mixed concerns
spider = ImmigrationCrawler(countries, config)
spider.crawl_all()  # Does everything: fetch, parse, save
```

**NEW WAY:**
```python
# Separated concerns
from services.crawler.interface import CrawlerService

service = CrawlerService()
result = service.crawl_country("Australia", urls)

# Or with UI callbacks
from services.crawler.interface import CrawlerController

controller = CrawlerController()
controller.crawl_with_progress(
    countries,
    on_page=lambda n, t, title: print(f"{n}/{t}: {title}")
)
```

## Migration Checklist

- [x] Crawler refactored
- [x] Classifier refactored
- [ ] Matcher refactored
- [ ] Assistant refactored
- [ ] UI updated to use Controllers
- [ ] Tests updated
- [ ] Full system test

Once all items are checked, legacy files can be removed.
