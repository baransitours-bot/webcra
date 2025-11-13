# Classifier Service Documentation

The Classifier Service extracts structured visa requirements from raw crawled data.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features](#features)
- [Output Format](#output-format)
- [Extraction Patterns](#extraction-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

The Classifier Service:
- Extracts structured requirements from raw HTML/text
- Categorizes visas (work, study, family, business, tourist, other)
- Parses age, education, experience, fees, and processing times
- Groups related pages into complete visa profiles
- Outputs structured JSON for matching

### Key Components
- `extractor.py` - Requirement extraction logic
- `structurer.py` - Visa grouping and categorization
- `config.yaml` - Extraction patterns
- `main.py` - CLI entry point

## Quick Start

### Basic Usage

```bash
# Classify data for a single country
python main.py classify --country australia

# Classify all crawled countries
python main.py classify --all
```

### Prerequisites

Raw data must exist from the Crawler:
```bash
python main.py crawl --countries australia
```

### Output

Structured data saved to: `data/structured/{country}.json`

## Configuration

Configuration file: `services/classifier/config.yaml`

### Visa Categories

```yaml
categories:
  work:
    keywords:
      - skilled worker
      - temporary work
      - employer sponsored
      - working holiday

  study:
    keywords:
      - student visa
      - study permit
      - academic

  family:
    keywords:
      - family reunification
      - spouse visa
      - dependent

  business:
    keywords:
      - investor visa
      - entrepreneur
      - business owner

  tourist:
    keywords:
      - visitor visa
      - tourist
      - short stay

  other:
    keywords:
      - refugee
      - asylum
      - humanitarian
```

### Extraction Patterns

#### Age Requirements

```yaml
patterns:
  age:
    - "(?:age|aged)\\s*(\\d+)\\s*(?:to|-|and)\\s*(\\d+)"
    - "between\\s*(\\d+)\\s*and\\s*(\\d+)\\s*years"
    - "(?:minimum|min)\\s*age\\s*(?:of)?\\s*(\\d+)"
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
  - high school
```

#### Work Experience

```yaml
experience:
  - "(\\d+)\\+?\\s*years?\\s*(?:of)?\\s*(?:work)?\\s*experience"
  - "at least\\s*(\\d+)\\s*years?"
```

#### Language Tests

```yaml
language_tests:
  ielts:
    - "IELTS\\s*(?:score)?\\s*(?:of)?\\s*(\\d+(?:\\.\\d+)?)"
  toefl:
    - "TOEFL\\s*(?:score)?\\s*(?:of)?\\s*(\\d+)"
  pte:
    - "PTE\\s*(?:Academic)?\\s*(?:score)?\\s*(?:of)?\\s*(\\d+)"
```

## Usage

### Command Line Interface

```bash
python main.py classify [OPTIONS]
```

#### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--country` | Classify specific country | `--country australia` |
| `--all` | Classify all crawled countries | `--all` |

### Examples

#### Example 1: Single Country

```bash
python main.py classify --country australia
```

Output:
```
2025-11-13 10:00:00 - classifier - INFO - 📊 Starting classifier for: australia
2025-11-13 10:00:01 - classifier - INFO - 📄 Processing 45 pages...
2025-11-13 10:00:02 - classifier - INFO - ✅ Extracted 12 visa types
2025-11-13 10:00:02 - classifier - INFO - 💾 Saved to data/structured/australia.json
```

#### Example 2: All Countries

```bash
python main.py classify --all
```

### Programmatic Usage

```python
from services.classifier.extractor import RequirementExtractor
from services.classifier.structurer import VisaStructurer
import yaml

# Load configuration
with open('services/classifier/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create components
extractor = RequirementExtractor(config)
structurer = VisaStructurer(config)

# Extract requirements
text = "You must be between 18 and 45 years old with a bachelor's degree..."
requirements = extractor.extract_all_requirements(text)

print(requirements)
# {'age': {'min': 18, 'max': 45}, 'education': ['bachelor'], ...}
```

## Features

### 1. Automatic Visa Categorization

Classifies visas into 6 categories based on keywords:

| Category | Examples |
|----------|----------|
| **work** | Skilled Worker, Temporary Work, Employer Sponsored |
| **study** | Student Visa, Study Permit |
| **family** | Spouse Visa, Family Reunification |
| **business** | Investor Visa, Entrepreneur |
| **tourist** | Visitor Visa, Tourist Visa |
| **other** | Refugee, Humanitarian |

### 2. Age Requirement Extraction

Detects age ranges and requirements:

**Input:**
```
You must be between 18 and 45 years old.
Minimum age: 21 years.
```

**Output:**
```json
{
  "age": {
    "min": 18,
    "max": 45
  }
}
```

### 3. Education Level Extraction

Identifies education requirements:

**Input:**
```
Bachelor's degree or higher qualification required.
```

**Output:**
```json
{
  "education": ["bachelor", "master", "phd"]
}
```

Recognized levels (in order):
1. PhD / Doctorate
2. Master's Degree
3. Bachelor's Degree
4. Diploma / Associate Degree
5. Secondary Education / High School

### 4. Work Experience Parsing

Extracts years of experience required:

**Input:**
```
At least 5 years of work experience in your field.
```

**Output:**
```json
{
  "work_experience": {
    "years": 5
  }
}
```

### 5. Fee Extraction

Finds application fees and costs:

**Input:**
```
Application fee: $2,500 AUD
Processing fee: $500 USD
```

**Output:**
```json
{
  "fees": [
    {"amount": 2500, "currency": "AUD", "type": "application"},
    {"amount": 500, "currency": "USD", "type": "processing"}
  ]
}
```

### 6. Processing Time Extraction

Detects how long processing takes:

**Input:**
```
Processing time: 3-6 months
Decision within 12 weeks
```

**Output:**
```json
{
  "processing_time": "3-6 months"
}
```

### 7. Language Requirement Detection

Parses language test scores:

**Input:**
```
IELTS score of 7.0 or higher
TOEFL iBT score of 100+
```

**Output:**
```json
{
  "language": {
    "ielts": 7.0,
    "toefl": 100
  }
}
```

### 8. Multi-Page Visa Grouping

Combines information from multiple pages about the same visa:

- Main visa page
- Requirements page
- Application process page
- Fees page

All merged into single comprehensive visa profile.

## Output Format

### Structured Visa JSON

Location: `data/structured/{country}.json`

```json
{
  "country": "australia",
  "total_visas": 12,
  "last_updated": "2025-11-13T10:00:00Z",
  "visas": [
    {
      "visa_type": "Skilled Independent Visa (Subclass 189)",
      "category": "work",
      "requirements": {
        "age": {
          "min": 18,
          "max": 45
        },
        "education": ["bachelor", "master", "phd"],
        "work_experience": {
          "years": 3
        },
        "language": {
          "ielts": 7.0
        },
        "fees": [
          {
            "amount": 4115,
            "currency": "AUD",
            "type": "base application"
          }
        ],
        "processing_time": "6-9 months"
      },
      "source_urls": [
        "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/skilled-independent-189"
      ],
      "extracted_at": "2025-11-13T10:00:00Z"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `country` | string | Country code |
| `total_visas` | int | Number of visas extracted |
| `last_updated` | string | ISO 8601 timestamp |
| `visas[]` | array | Array of visa objects |
| `visa_type` | string | Visa name/subclass |
| `category` | string | work/study/family/business/tourist/other |
| `requirements` | object | Structured requirements |
| `source_urls` | array | Original page URLs |

## Extraction Patterns

### Pattern Syntax

Patterns use Python regular expressions (regex).

#### Age Pattern Example

```python
# Pattern
"(?:age|aged)\\s*(\\d+)\\s*(?:to|-|and)\\s*(\\d+)"

# Matches:
"age 18 to 45"
"aged 21-35"
"age 18 and 45"

# Captures:
Group 1: minimum age (18)
Group 2: maximum age (45)
```

#### Experience Pattern Example

```python
# Pattern
"(\\d+)\\+?\\s*years?\\s*(?:of)?\\s*(?:work)?\\s*experience"

# Matches:
"5 years of work experience"
"3+ years experience"
"10 years work experience"

# Captures:
Group 1: years (5, 3, 10)
```

### Custom Patterns

Add custom patterns to `config.yaml`:

```yaml
patterns:
  # Add your custom pattern
  custom_field:
    - "your_regex_pattern_here"
```

Then modify `extractor.py` to use it:

```python
def extract_custom_field(self, text):
    for pattern in self.config['patterns']['custom_field']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
```

## Troubleshooting

### Issue: No Requirements Extracted

**Symptoms:**
```
⚠️  No requirements found for visa
```

**Causes:**
1. Page content doesn't match patterns
2. Patterns too specific
3. Different wording used

**Solutions:**

1. Review raw content:
   ```python
   # Check what was crawled
   with open('data/raw/australia/{hash}.json') as f:
       data = json.load(f)
       print(data['content'][:500])  # First 500 chars
   ```

2. Add more pattern variations:
   ```yaml
   age:
     - "(?:age|aged)\\s*(\\d+)\\s*(?:to|-|and)\\s*(\\d+)"
     - "applicants\\s*must\\s*be\\s*(\\d+)\\s*to\\s*(\\d+)"  # New pattern
   ```

3. Adjust case sensitivity in patterns

### Issue: Wrong Category Assigned

**Symptoms:**
```
Work visa classified as 'tourist'
```

**Causes:**
- Category keywords too broad
- Multiple keywords match different categories

**Solutions:**

1. Make keywords more specific:
   ```yaml
   work:
     keywords:
       - skilled worker visa  # More specific
       - skilled migration visa
       # Not just "work"
   ```

2. Add exclusion keywords (future feature):
   ```yaml
   work:
     keywords: [...]
     exclude:
       - tourist
       - visitor
   ```

### Issue: Duplicate Visas

**Symptoms:**
```
Same visa appears multiple times
```

**Causes:**
- Multiple pages about same visa not grouped
- Different names for same visa

**Solutions:**

1. Improve visa name normalization in `structurer.py`

2. Add alias mapping:
   ```yaml
   visa_aliases:
     "Skilled Worker 189": "Skilled Independent Visa (Subclass 189)"
     "189 Visa": "Skilled Independent Visa (Subclass 189)"
   ```

### Issue: Incorrect Numbers Extracted

**Symptoms:**
```
Age: 2025 (should be 18-45)
Fee: $0
```

**Causes:**
- Pattern matched wrong numbers
- Numbers in unrelated text

**Solutions:**

1. Add validation ranges:
   ```python
   def extract_age(self, text):
       match = ...
       age = int(match.group(1))

       # Validate
       if age < 10 or age > 100:
           return None  # Invalid age

       return age
   ```

2. Add context requirements:
   ```python
   # Only match if "age" keyword nearby
   "(?:age|aged)\\s*(\\d+)"  # Good
   # Not just any number:
   "(\\d+)"  # Too broad
   ```

## Performance

### Benchmarks

| Pages | Time | Memory |
|-------|------|--------|
| 50 | ~5s | ~50MB |
| 100 | ~10s | ~80MB |
| 500 | ~45s | ~200MB |

### Optimization Tips

1. **Batch Processing**: Process multiple countries in sequence
2. **Pattern Caching**: Compile regex patterns once
3. **Memory Management**: Process pages in chunks for large datasets

## Testing

### Run Classifier Tests

```bash
python tests/test_classifier.py
```

### Test Coverage

- ✅ Age extraction
- ✅ Education extraction
- ✅ Experience parsing
- ✅ Fee extraction
- ✅ Language test detection
- ✅ Visa categorization
- ✅ Multi-page grouping

## Integration

### Data Flow

```
data/raw/{country}/*.json
          ↓
Classifier Service (Extraction)
          ↓
Classifier Service (Structuring)
          ↓
data/structured/{country}.json
          ↓
Matcher Service
```

### Next Steps

After classification, run the Matcher:

```bash
# Classify data
python main.py classify --country australia

# Match user to visas
python main.py match --interactive
```

## Advanced Usage

### Custom Extractors

Add custom extraction logic in `extractor.py`:

```python
def extract_custom_requirement(self, text):
    """Extract custom requirement"""
    # Your custom logic
    pattern = r"custom pattern"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return {
            'custom_field': match.group(1)
        }

    return None
```

Then call it in `extract_all_requirements()`:

```python
def extract_all_requirements(self, text):
    requirements = {
        'age': self.extract_age_requirement(text),
        'education': self.extract_education_requirement(text),
        'custom': self.extract_custom_requirement(text),  # Add here
        # ...
    }
    return requirements
```

### Custom Categories

Add new visa categories:

```yaml
categories:
  medical:
    keywords:
      - medical visa
      - health worker
      - doctor visa
      - nurse migration
```

## See Also

- [Crawler Service](crawler.md) - Collect raw data
- [Matcher Service](matcher.md) - Match users to visas
- [Configuration Guide](../guides/configuration.md) - Global configuration
- [Troubleshooting](../troubleshooting.md) - Common issues

---

**Previous**: [← Crawler Service](crawler.md) | **Next**: [Matcher Service →](matcher.md)
