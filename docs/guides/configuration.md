# Configuration Guide

Complete reference for configuring the Immigration Platform.

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `config.yaml` | Global settings & countries | Project root |
| `services/crawler/config.yaml` | Crawling settings | Crawler service |
| `services/classifier/config.yaml` | Extraction patterns | Classifier service |
| `services/matcher/config.yaml` | Scoring weights | Matcher service |
| `services/assistant/config.yaml` | LLM settings | Assistant service |

## Global Configuration

File: `config.yaml`

### Adding Countries

```yaml
countries:
  new_country:
    name: "New Country Name"
    code: "NC"
    base_url: "https://immigration.newcountry.gov"
    seed_urls:
      - "https://immigration.newcountry.gov/visas"
      - "https://immigration.newcountry.gov/work-permits"
```

### Example: Adding Germany

```yaml
countries:
  germany:
    name: "Germany"
    code: "DE"
    base_url: "https://www.auswaertiges-amt.de"
    seed_urls:
      - "https://www.auswaertiges-amt.de/en/visa-service"
```

## Crawler Configuration

File: `services/crawler/config.yaml`

### Basic Settings

```yaml
crawling:
  max_depth: 3                    # Link depth from seed URL
  max_pages_per_country: 100      # Stop after N pages
  delay_between_requests: 1       # Seconds between requests
  timeout: 30                     # Request timeout (seconds)
  user_agent: "ImmigrationBot/1.0"
```

### Adjust for Specific Needs

**For large countries:**
```yaml
max_pages_per_country: 500
```

**For slow websites:**
```yaml
timeout: 60
delay_between_requests: 2
```

**For strict websites:**
```yaml
user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
delay_between_requests: 3
```

### Relevance Keywords

```yaml
relevance_keywords:
  required:  # At least one must be present
    - visa
    - immigration
    - migrate
    - work permit
    - student visa

  optional:  # Boost relevance
    - requirements
    - eligibility
    - application
    - fees
```

### URL Exclusions

```yaml
exclude_patterns:
  - "*/print/*"
  - "*/download/*"
  - "*/rss/*"
  - "*.pdf"
  # Add custom patterns:
  - "*/news/*"
  - "*/blog/*"
```

## Classifier Configuration

File: `services/classifier/config.yaml`

### Visa Categories

```yaml
categories:
  work:
    keywords:
      - skilled worker
      - temporary work
      - employer sponsored

  study:
    keywords:
      - student visa
      - study permit

  # Add custom category:
  medical:
    keywords:
      - medical visa
      - health worker
      - doctor visa
```

### Extraction Patterns

#### Age Patterns

```yaml
patterns:
  age:
    - "(?:age|aged)\\s*(\\d+)\\s*(?:to|-|and)\\s*(\\d+)"
    - "between\\s*(\\d+)\\s*and\\s*(\\d+)\\s*years"
    # Add custom pattern:
    - "applicants\\s*must\\s*be\\s*(\\d+)\\s*to\\s*(\\d+)"
```

#### Education Levels

```yaml
education_levels:
  - phd
  - doctorate
  - master
  - bachelor
  - diploma
  - secondary education
  # Add custom levels:
  - vocational training
  - technical certificate
```

#### Custom Patterns

Add new requirement types:

```yaml
patterns:
  # Existing patterns...

  # Custom: Net worth requirement
  net_worth:
    - "net worth of\\s*\\$?([\\d,]+)"
    - "assets totaling\\s*\\$?([\\d,]+)"
```

Then implement extraction in `extractor.py`.

## Matcher Configuration

File: `services/matcher/config.yaml`

### Scoring Weights

```yaml
scoring:
  weights:
    age: 0.25              # 25%
    education: 0.30        # 30%
    work_experience: 0.25  # 25%
    language: 0.20         # 20%
  # Total must equal 1.0
```

### Adjust for Different Priorities

**Prioritize education:**
```yaml
weights:
  age: 0.20
  education: 0.40  # Higher weight
  work_experience: 0.20
  language: 0.20
```

**Prioritize experience:**
```yaml
weights:
  age: 0.15
  education: 0.25
  work_experience: 0.40  # Higher weight
  language: 0.20
```

### Education Hierarchy

```yaml
education_hierarchy:
  phd: 5
  master: 4
  bachelor: 3
  diploma: 2
  secondary: 1
  # Add custom levels:
  vocational: 2
  certificate: 1
```

## Assistant Configuration

File: `services/assistant/config.yaml`

### Provider Selection

**Use OpenRouter (FREE):**
```yaml
llm:
  provider: "openrouter"

  openrouter:
    model: "meta-llama/llama-3.1-8b-instruct:free"
    api_key_env: "OPENROUTER_API_KEY"
    base_url: "https://openrouter.ai/api/v1"
```

**Use OpenAI:**
```yaml
llm:
  provider: "openai"

  openai:
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
```

### LLM Parameters

```yaml
llm:
  # Temperature: 0.0-1.0
  temperature: 0.3  # Conservative (factual)

  # Max tokens: response length
  max_tokens: 1000  # ~750 words
```

**For brief answers:**
```yaml
temperature: 0.2
max_tokens: 500
```

**For detailed answers:**
```yaml
temperature: 0.4
max_tokens: 2000
```

### Context Settings

```yaml
context:
  max_visas: 5              # Include top 5 visas
  max_tokens_per_visa: 500  # Limit visa details
```

**For comprehensive context:**
```yaml
context:
  max_visas: 10
  max_tokens_per_visa: 1000
```

## Environment Variables

### Setting API Keys

**Windows PowerShell:**
```powershell
# Temporary (current session)
$env:OPENROUTER_API_KEY = 'sk-or-v1-...'
$env:OPENAI_API_KEY = 'sk-...'

# Permanent (user profile)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-v1-...", "User")
```

**Linux/Mac:**
```bash
# Temporary (current session)
export OPENROUTER_API_KEY='sk-or-v1-...'
export OPENAI_API_KEY='sk-...'

# Permanent (~/.bashrc or ~/.zshrc)
echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
source ~/.bashrc
```

### Alternative: Direct in Config

```yaml
# Instead of environment variable name:
openrouter:
  api_key_env: "OPENROUTER_API_KEY"

# Put key directly:
openrouter:
  api_key_env: "sk-or-v1-actual-key-here"
```

## Data Storage

### Directory Structure

```
data/
├── raw/                    # Crawled pages
│   ├── australia/
│   │   └── *.json
│   ├── canada/
│   └── ...
└── structured/             # Extracted requirements
    ├── australia.json
    ├── canada.json
    └── ...
```

### Custom Data Paths

Modify in service files:

```python
# shared/database.py
class Database:
    def __init__(self, base_path='data'):  # Change default
        self.base_path = Path(base_path)
```

Or use environment variable:

```bash
export IMMIGRATION_DATA_PATH='/custom/path/data'
```

## Performance Tuning

### Crawler Performance

**Faster crawling (use cautiously):**
```yaml
delay_between_requests: 0.5  # Reduce delay
max_workers: 5               # Parallel workers (future)
```

**More respectful:**
```yaml
delay_between_requests: 3
timeout: 60
```

### Classifier Performance

**Process in batches:**
```python
# In classifier/main.py
batch_size = 50  # Process 50 pages at a time
for i in range(0, len(pages), batch_size):
    batch = pages[i:i+batch_size]
    # Process batch
```

### Assistant Performance

**Reduce latency:**
```yaml
llm:
  max_tokens: 500      # Shorter responses
  temperature: 0.1     # More deterministic

context:
  max_visas: 3         # Fewer visas in context
```

## Security

### API Key Security

**DO NOT:**
- ❌ Commit API keys to git
- ❌ Share config files with keys
- ❌ Log API keys

**DO:**
- ✅ Use environment variables
- ✅ Add `.env` to `.gitignore`
- ✅ Use separate keys for dev/prod

### .gitignore

```
# API keys
.env
*.key

# Sensitive configs
config.local.yaml
```

## Validation

### Validate Configuration

```python
import yaml

def validate_config(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Check required fields
    assert 'llm' in config
    assert 'provider' in config['llm']

    # Check weights sum to 1.0
    if 'scoring' in config:
        weights = config['scoring']['weights']
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, not 1.0"

    print("✅ Configuration valid")

validate_config('services/matcher/config.yaml')
```

## Best Practices

1. **Start with defaults** - Only change what's needed
2. **Test changes** - Run tests after configuration changes
3. **Document changes** - Comment why you changed values
4. **Version control** - Commit config changes with descriptive messages
5. **Backup** - Keep a copy of working configurations

## Troubleshooting

### YAML Syntax Errors

**Error:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solution:**
Check indentation (use spaces, not tabs):

```yaml
# Bad
categories:
work:  # Missing indentation

# Good
categories:
  work:  # Proper indentation
```

### Missing Fields

**Error:**
```
KeyError: 'provider'
```

**Solution:**
Ensure all required fields present:

```yaml
llm:
  provider: "openrouter"  # Required field
```

## See Also

- [Quick Start Guide](quick-start.md) - Getting started
- [Service Documentation](../services/crawler.md) - Individual services
- [Troubleshooting](../troubleshooting.md) - Common issues

---

**Previous**: [← Quick Start](quick-start.md) | **Next**: [Troubleshooting →](../troubleshooting.md)
