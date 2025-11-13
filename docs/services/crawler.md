# Crawler Service Documentation

The Crawler Service is responsible for collecting raw immigration data from government websites across multiple countries.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features](#features)
- [Output Format](#output-format)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Crawler Service:
- Scrapes official government immigration websites
- Extracts text content and metadata
- Filters pages by relevance (keyword-based)
- Respects robots.txt and rate limits
- Stores raw data for later processing

### Key Components
- `spider.py` - Core crawling logic
- `config.yaml` - Crawling configuration
- `main.py` - CLI entry point

## Quick Start

### Basic Usage

```bash
# Crawl a single country
python main.py crawl --countries australia

# Crawl multiple countries
python main.py crawl --countries australia canada uk

# Crawl all configured countries
python main.py crawl --all
```

### Output

Raw data is saved to: `data/raw/{country}/{hash}.json`

## Configuration

Configuration file: `services/crawler/config.yaml`

### Full Configuration Example

```yaml
crawling:
  # Maximum depth to follow links
  max_depth: 3

  # Maximum pages to crawl per country
  max_pages_per_country: 100

  # Delay between requests (seconds)
  delay_between_requests: 1

  # Request timeout (seconds)
  timeout: 30

  # User agent string
  user_agent: "ImmigrationBot/1.0"

# Keywords for relevance filtering
relevance_keywords:
  required:
    - visa
    - immigration
    - migrate
    - work permit
    - student visa
    - family reunification

  optional:
    - requirements
    - eligibility
    - application
    - fees
    - processing time
    - documents

# URL patterns to exclude
exclude_patterns:
  - "*/print/*"
  - "*/download/*"
  - "*/feed/*"
  - "*/rss/*"
  - "*.pdf"  # PDFs detected separately
  - "*.doc"
  - "*.xls"

# Document types to detect
document_types:
  - pdf
  - doc
  - docx
  - xls
  - xlsx
```

### Configuration Parameters

#### Crawling Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_depth` | int | 3 | Maximum link depth from seed URL |
| `max_pages_per_country` | int | 100 | Stop after N pages per country |
| `delay_between_requests` | float | 1.0 | Seconds between requests (rate limiting) |
| `timeout` | int | 30 | Request timeout in seconds |
| `user_agent` | string | - | User agent for requests |

#### Relevance Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| `relevance_keywords.required` | list | Page must contain at least one |
| `relevance_keywords.optional` | list | Boost relevance score |

#### URL Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| `exclude_patterns` | list | Skip URLs matching these patterns |
| `document_types` | list | File extensions to detect as documents |

## Usage

### Command Line Interface

```bash
python main.py crawl [OPTIONS]
```

#### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--countries` | Comma-separated country codes | `--countries australia,canada` |
| `--all` | Crawl all configured countries | `--all` |
| `--max-depth` | Override max depth | `--max-depth 2` |
| `--max-pages` | Override max pages | `--max-pages 50` |

### Examples

#### Example 1: Single Country

```bash
python main.py crawl --countries australia
```

Output:
```
2025-11-13 10:00:00 - crawler - INFO - 🕷️  Starting crawler for: australia
2025-11-13 10:00:01 - crawler - INFO - 📄 Found relevant page: https://...
2025-11-13 10:00:02 - crawler - INFO - ⏭️  Skipping (no relevant keywords): https://...
2025-11-13 10:00:10 - crawler - INFO - ✅ Crawled 45 pages for australia
```

#### Example 2: Multiple Countries

```bash
python main.py crawl --countries canada,uk,germany
```

#### Example 3: All Countries

```bash
python main.py crawl --all
```

#### Example 4: Custom Depth

```bash
python main.py crawl --countries australia --max-depth 2
```

### Programmatic Usage

```python
from services.crawler.spider import WebSpider
import yaml

# Load configuration
with open('services/crawler/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create spider
spider = WebSpider(config)

# Crawl a country
seed_urls = [
    "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing"
]

results = spider.crawl_country("australia", seed_urls)

print(f"Crawled {len(results)} pages")
```

## Features

### 1. Keyword-Based Relevance Filtering

The crawler only saves pages that contain immigration-related keywords.

**Required Keywords** (at least one must be present):
- visa, immigration, migrate, work permit, student visa, etc.

**Optional Keywords** (boost relevance):
- requirements, eligibility, application, fees, documents

### 2. URL Exclusion

Automatically skips:
- Print versions (`*/print/*`)
- Download pages (`*/download/*`)
- RSS feeds (`*/rss/*`)
- Already visited URLs

### 3. Document Detection

Detects and logs document attachments:
- PDF files
- Word documents (.doc, .docx)
- Excel files (.xls, .xlsx)

Note: Document content is not downloaded (requires separate tool).

### 4. Breadcrumb Extraction

Extracts navigation breadcrumbs when available:
```
Home > Visas > Work Visas > Skilled Worker
```

Useful for understanding page hierarchy and categorization.

### 5. Depth-Limited Crawling

Prevents infinite loops by limiting link depth from seed URLs.

Example with `max_depth=2`:
```
Seed URL (depth 0)
  ↓
Linked Page (depth 1)
  ↓
Nested Page (depth 2)
  ↓
❌ Too deep (depth 3) - skipped
```

### 6. Rate Limiting

Respectful crawling with configurable delays between requests.

Default: 1 second between requests

### 7. Error Handling

Gracefully handles:
- Connection timeouts
- HTTP errors (404, 403, etc.)
- Invalid HTML
- Network failures

## Output Format

### Raw Page JSON

Location: `data/raw/{country}/{hash}.json`

```json
{
  "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia",
  "title": "Working in Australia - Skilled Worker Visa",
  "content": "To be eligible for a Skilled Worker visa, you must...",
  "breadcrumbs": ["Home", "Visas", "Work Visas", "Skilled Worker"],
  "links": [
    "https://immi.homeaffairs.gov.au/visas/working-in-australia/requirements",
    "https://immi.homeaffairs.gov.au/visas/working-in-australia/apply"
  ],
  "attachments": [
    {
      "type": "pdf",
      "url": "https://immi.homeaffairs.gov.au/forms/application-form.pdf",
      "text": "Application Form"
    }
  ],
  "crawled_at": "2025-11-13T10:00:00Z"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Original page URL |
| `title` | string | Page title |
| `content` | string | Extracted text content |
| `breadcrumbs` | list | Navigation breadcrumbs |
| `links` | list | All extracted links |
| `attachments` | list | Detected documents (PDFs, etc.) |
| `crawled_at` | string | ISO 8601 timestamp |

## Best Practices

### 1. Start Small

Begin with a single country to test configuration:

```bash
python main.py crawl --countries australia --max-pages 10
```

### 2. Monitor Logs

Watch crawler logs for issues:

```bash
tail -f crawler.log
```

### 3. Respect Rate Limits

Government websites may block aggressive crawling. Use appropriate delays:

```yaml
delay_between_requests: 2  # 2 seconds between requests
```

### 4. Handle 403 Errors

If you encounter 403 Forbidden errors:

**Option 1**: Use official APIs (if available)
**Option 2**: Request permission from website administrators
**Option 3**: Use browser automation (Playwright/Selenium)
**Option 4**: Manual data collection

### 5. Regular Updates

Immigration rules change frequently. Schedule regular crawls:

```bash
# Weekly cron job
0 0 * * 0 cd /path/to/project && python main.py crawl --all
```

### 6. Verify Seed URLs

Before crawling, verify seed URLs are correct:

```python
# Check config.yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for country, info in config['countries'].items():
    print(f"{country}: {info['seed_urls']}")
```

## Troubleshooting

### Issue: No Pages Crawled

**Symptoms:**
```
✅ Crawled 0 pages for australia
```

**Causes:**
1. Seed URLs are incorrect
2. All pages filtered out by relevance keywords
3. Website blocking requests (403 Forbidden)

**Solutions:**
1. Verify seed URLs in `config.yaml`
2. Check `relevance_keywords` aren't too restrictive
3. Increase `delay_between_requests`
4. Check website's `robots.txt`

### Issue: 403 Forbidden Errors

**Symptoms:**
```
❌ Error fetching https://...: 403 Forbidden
```

**Causes:**
- Website blocking automated requests
- User agent detected as bot
- Rate limiting triggered

**Solutions:**
1. Add realistic user agent:
   ```yaml
   user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
   ```

2. Increase delay:
   ```yaml
   delay_between_requests: 3
   ```

3. Use Playwright for JavaScript sites (future feature)

### Issue: Timeout Errors

**Symptoms:**
```
⚠️  Timeout fetching https://...
```

**Causes:**
- Slow website response
- Network issues
- Timeout too short

**Solutions:**
1. Increase timeout:
   ```yaml
   timeout: 60  # 60 seconds
   ```

2. Check internet connection
3. Try again later (website may be down)

### Issue: Out of Memory

**Symptoms:**
- Process crashes
- System slows down

**Causes:**
- Too many pages stored in memory
- Large pages

**Solutions:**
1. Reduce `max_pages_per_country`:
   ```yaml
   max_pages_per_country: 50
   ```

2. Process countries individually:
   ```bash
   python main.py crawl --countries australia
   python main.py crawl --countries canada
   ```

### Issue: Irrelevant Pages Saved

**Symptoms:**
- Pages about tourism, not immigration
- News articles

**Causes:**
- Relevance keywords too broad

**Solutions:**
1. Add more specific required keywords:
   ```yaml
   required:
     - visa
     - immigration
     - work permit
   ```

2. Expand exclude patterns:
   ```yaml
   exclude_patterns:
     - "*/news/*"
     - "*/blog/*"
     - "*/tourism/*"
   ```

## Performance

### Benchmarks

| Pages | Time | Memory |
|-------|------|--------|
| 10 | ~15s | ~50MB |
| 50 | ~1min | ~100MB |
| 100 | ~2min | ~150MB |

*Depends on website response time and network speed*

### Optimization Tips

1. **Parallel Crawling**: Crawl multiple countries in parallel (future feature)
2. **Caching**: Cache DNS lookups and SSL connections
3. **Compression**: Request gzip-compressed responses
4. **Incremental Crawling**: Only crawl changed pages (future feature)

## Testing

### Run Crawler Tests

```bash
python tests/test_crawler.py
```

### Test Coverage

- ✅ Configuration loading
- ✅ Relevance filtering
- ✅ Breadcrumb extraction
- ✅ Link extraction
- ✅ Document detection
- ✅ Data storage

## Integration

### Next Steps

After crawling, run the Classifier:

```bash
# Crawl data
python main.py crawl --countries australia

# Extract requirements
python main.py classify --country australia
```

### Data Flow

```
Crawler → data/raw/{country}/*.json
              ↓
Classifier → data/structured/{country}.json
              ↓
Matcher → User eligibility scores
              ↓
Assistant → AI-powered answers
```

## Advanced Usage

### Custom Seed URLs

Modify `config.yaml` to add custom seed URLs:

```yaml
countries:
  my_country:
    name: "My Country"
    code: "MC"
    base_url: "https://immigration.mycountry.gov"
    seed_urls:
      - "https://immigration.mycountry.gov/visas"
      - "https://immigration.mycountry.gov/work-permits"
```

### Custom Keywords

Adjust relevance filtering for specific countries:

```python
# In spider.py, you can customize keyword weights
def is_relevant(self, text):
    required_count = sum(1 for kw in required_keywords if kw in text.lower())
    optional_count = sum(1 for kw in optional_keywords if kw in text.lower())

    return required_count >= 1  # At least one required keyword
```

## API Reference

### WebSpider Class

```python
class WebSpider:
    def __init__(self, config: dict)
    def crawl_country(self, country_name: str, seed_urls: list) -> list
    def is_relevant(self, text: str) -> bool
    def extract_links(self, soup, base_url: str) -> list
    def extract_breadcrumbs(self, soup) -> list
    def detect_attachments(self, soup, base_url: str) -> list
```

## See Also

- [Classifier Service](classifier.md) - Process crawled data
- [Configuration Guide](../guides/configuration.md) - Global configuration
- [Troubleshooting](../troubleshooting.md) - Common issues
- [Data Flow](../guides/data-flow.md) - Understanding the pipeline

---

**Next**: [Classifier Service →](classifier.md)
