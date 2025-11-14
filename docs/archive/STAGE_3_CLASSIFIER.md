# Stage 3: Classifier Service - Complete

## Overview
The classifier service successfully processes raw crawled data and extracts structured visa requirements using pattern matching and NLP techniques.

## Implementation

### Files Created
- `services/classifier/config.yaml` - Classification patterns and categories
- `services/classifier/extractor.py` - Requirement extraction engine
- `services/classifier/structurer.py` - Visa grouping and merging
- `services/classifier/main.py` - Service entry point (updated)
- `tests/test_classifier.py` - Comprehensive test suite

### Features Implemented
✅ **Visa Category Identification**: Automatically categorizes visas (work, study, family, investment, tourism, retirement)
✅ **Age Extraction**: Parses age requirements (min, max, ranges)
✅ **Education Requirements**: Identifies education levels (PhD, Masters, Bachelors, Diploma, Secondary)
✅ **Experience Extraction**: Extracts years of work experience required
✅ **Fee Information**: Finds application fees and costs
✅ **Processing Time**: Extracts visa processing timeframes
✅ **Language Requirements**: Identifies language tests and scores (IELTS, TOEFL, PTE)
✅ **Visa Grouping**: Groups multiple pages about the same visa
✅ **Requirement Merging**: Combines information from multiple sources
✅ **Data Structuring**: Creates complete visa profiles

### Extraction Patterns

#### Age Patterns
- "age between 18 and 30"
- "under 45 years old"
- "at least 21 years old"

#### Education Patterns
- Bachelor's degree
- Master's degree
- PhD/Doctorate
- Diploma
- Secondary education

#### Experience Patterns
- "3+ years experience"
- "Minimum 5 years"
- "At least 2 years of work experience"

#### Fees Patterns
- "Application fee: $4,115"
- "$630 visa fee"
- "7,850 AUD"

#### Processing Time Patterns
- "6 to 8 months"
- "Within 4 weeks"
- "Processing time: 12-24 months"

#### Language Patterns
- "IELTS 6.5"
- "TOEFL score of 80"
- "PTE 58 or equivalent"

## Data Structure

### Input (Raw Page)
```json
{
  "url": "...",
  "country": "...",
  "title": "Skilled Worker Visa",
  "content_text": "Requirements: Age under 45, Bachelor's degree, 3 years experience..."
}
```

### Output (Structured Visa)
```json
{
  "visa_type": "Skilled Worker Visa (Subclass 189)",
  "country": "TestCountry",
  "category": "work",
  "requirements": {
    "age": {"min": null, "max": 45},
    "education": "bachelors",
    "experience_years": 3
  },
  "language": "IELTS 6.5",
  "fees": {"application_fee": "$4,115"},
  "processing_time": "6-8 months",
  "source_urls": ["..."]
}
```

## Usage

### Classify Single Country
```bash
python main.py classify --country TestCountry
```

### Classify All Countries
```bash
python main.py classify --all
```

### Run Tests
```bash
python tests/test_classifier.py
```

## Test Results

All tests passing ✅:
- ✅ Visa category identification
- ✅ Age extraction (ranges, min, max)
- ✅ Education level detection
- ✅ Experience years parsing
- ✅ Fee extraction
- ✅ Processing time parsing
- ✅ Language requirement detection
- ✅ Visa name normalization
- ✅ Requirement merging
- ✅ Full pipeline integration
- ✅ Data persistence

### Sample Output
```
1. Skilled Worker Visa (Subclass 189)
   Country: TestCountry
   Category: work
   Requirements:
      - age: {'min': None, 'max': 45}
      - education: bachelors
      - experience_years: 3
   Language: IELTS 6.5
   Fees: {'application_fee': '$4115'}
   Processing Time: 6-8 months

2. Student Visa for International Students
   Country: TestCountry
   Category: study
   Requirements:
      - age: {'min': 18, 'max': 30}
   Language: IELTS 6.0
   Processing Time: 4-6 weeks

3. Partner Visa (Family Reunion)
   Country: TestCountry
   Category: family
   Fees: {'application_fee': '$7850'}
   Processing Time: 12-24 months

4. Business Innovation and Investment Visa
   Country: TestCountry
   Category: investment
   Requirements:
      - age: {'min': None, 'max': 55}
      - experience_years: 5
   Fees: {'application_fee': '$5375'}
   Processing Time: 10-12 months
```

## Configuration

### Adding New Patterns
Edit `services/classifier/config.yaml`:

```yaml
patterns:
  your_field:
    - "pattern 1"
    - "pattern 2"
```

### Adding New Visa Categories
```yaml
visa_categories:
  - "your_category"

visa_type_keywords:
  your_category:
    - "keyword1"
    - "keyword2"
```

## Architecture

```
Raw Pages (JSON)
    ↓
[RequirementExtractor]
    ↓
Extracted Data (age, edu, exp, fees, etc.)
    ↓
[VisaStructurer]
    ↓
Structured Visas (grouped and merged)
    ↓
data/processed/visas.json
```

## Limitations & Future Improvements

### Current Limitations
- Regex-based extraction (not ML)
- English-only support
- Simple grouping algorithm
- May miss complex requirements

### Future Enhancements
1. **ML-Based Extraction**: Use NER models for better accuracy
2. **Multi-language Support**: Process non-English pages
3. **Advanced Grouping**: Use embeddings for semantic similarity
4. **Confidence Scores**: Add reliability scores to extractions
5. **Structured Data Validation**: Validate extracted requirements
6. **PDF Processing**: Extract from PDF attachments
7. **Table Extraction**: Parse requirement tables

## Next Steps
With the classifier complete, we can move to **Stage 4: Matcher Service** which will:
- Score user profiles against visa requirements
- Calculate eligibility percentages
- Identify gaps and missing requirements
- Rank visa options by match quality
- Provide personalized recommendations
