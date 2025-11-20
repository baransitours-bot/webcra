# Immigration Platform - System Overview

**Simple, clear explanation of what exists and how it works.**

---

## What This System Does

Collects visa information from multiple sources → Structures it → Answers questions about it

---

## Current System Pipeline

```
┌──────────────┐
│ 1. COLLECT   │ → Gather visa data
│   DATA       │   • Web crawler (scrapes websites)
└──────┬───────┘   • Manual entry (edit JSON files)
       │
       ▼
┌──────────────┐
│ 2. CLASSIFY  │ → Extract structured info
│   DATA       │   • Uses LLM to extract visa requirements
└──────┬───────┘   • Saves to data/processed/visas.json
       │
       ▼
┌──────────────┐
│ 3. QUERY     │ → Answer questions
│   DATA       │   • Chat with data using LLM
└──────────────┘   • Match visas to user profiles
```

---

## What's Implemented ✅

### 1. Data Collection
- **Crawler**: `services/crawler/` - Scrapes government visa websites
- **Manual Entry**: Edit `data/processed/visas.json` directly

### 2. Data Classification
- **Classifier**: `services/classifier/` - Extracts visa requirements from raw text
- **Output**: Structured JSON with fees, requirements, documents, etc.

### 3. Data Querying
- **Assistant**: `services/assistant/` - Chat interface to ask questions
- **Matcher**: `services/matcher/` - Matches user profiles to eligible visas

### 4. User Interface
- **CLI**: `main.py` - Command-line interface
- **Web UI**: `app.py` - Browser-based interface (Streamlit)

---

## What's NOT Implemented ❌

- PDF parsing
- OCR (image to text)
- Booking/planning features
- Application submission

---

## Quick Start - Validate Your System

### Test 1: Collect Data (Crawler)
```bash
python main.py crawl --countries australia --max-pages 5
# Check: ls data/raw/australia/
```

### Test 2: Classify Data
```bash
python main.py classify --all
# Check: cat data/processed/visas.json
```

### Test 3: Query Data (Needs LLM API key)
```bash
# Set API key first
export OPENROUTER_API_KEY=your_key

python main.py assist --query "What work visas are available?"
```

### Test 4: Web UI
```bash
streamlit run app.py
# Open: http://localhost:8501
```

---

## Project Structure

```
webcra/
├── main.py                      # Main CLI entry point
├── app.py                       # Web UI (Streamlit)
│
├── services/
│   ├── crawler/                 # Web scraping
│   │   ├── main.py              # Crawler logic
│   │   └── config.yaml          # Crawler settings
│   │
│   ├── classifier/              # Data extraction
│   │   ├── main.py              # Classification logic
│   │   └── config.yaml          # LLM settings
│   │
│   ├── matcher/                 # Visa matching
│   │   ├── ranker.py            # Scoring algorithm
│   │   └── config.yaml          # Matching rules
│   │
│   └── assistant/               # Q&A system
│       ├── main.py              # Assistant logic
│       ├── llm_client.py        # LLM interface
│       └── config.yaml          # Assistant settings
│
├── data/
│   ├── raw/                     # Crawled web pages
│   ├── processed/               # Structured visa data
│   │   └── visas.json          # ← MAIN DATA FILE
│   └── example_output.json      # Sample data
│
└── docs/
    └── archive/                 # Old documentation (reference only)
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Run commands: crawl, classify, match, assist |
| `app.py` | Web interface (browser-based) |
| `data/processed/visas.json` | **All your visa data** |
| `services/*/config.yaml` | Configure each service |

---

## Common Commands

```bash
# Crawl websites
python main.py crawl --countries australia canada --max-pages 10

# Extract structured data
python main.py classify --all

# Match visas to profile
python main.py match --profile path/to/profile.json

# Ask questions
python main.py assist --query "What student visas are available in USA?"

# Launch Web UI
streamlit run app.py
```

---

## How to Add Data

### Method 1: Crawler (Automatic)
1. Configure target URLs in `services/crawler/config.yaml`
2. Run: `python main.py crawl --countries <country>`
3. Run: `python main.py classify --all`

### Method 2: Manual Entry (Direct)
1. Open `data/processed/visas.json`
2. Add your visa entry following the existing format
3. Done! No need to run anything else

---

## System Requirements

- **LLM API**: OpenRouter (FREE) or OpenAI (paid)
  - Set in `services/*/config.yaml`
  - Export API key: `export OPENROUTER_API_KEY=your_key`

- **Python Packages**: Install with `pip install -r requirements.txt`

---

## Current Data Coverage

- **Countries**: USA (9 visas), TestCountry (4 visas)
- **Total Visas**: 13
- **Categories**: work, study, investment, tourist, family

---

## Next Steps (Your Choice)

1. **Expand data collection**:
   - Add more countries to crawler
   - Add PDF parsing support
   - Add OCR for images

2. **Improve classification**:
   - Better extraction accuracy
   - More detailed requirements

3. **Add features**:
   - Document verification
   - Application tracking
   - Timeline planning

---

## Troubleshooting

**Problem**: Crawler not working
**Solution**: Check `services/crawler/config.yaml` URLs are valid

**Problem**: Classifier fails
**Solution**: Set LLM API key in environment or config

**Problem**: No data in visas.json
**Solution**: Run `python main.py classify --all` after crawling

---

## Getting Help

1. Check old docs in `docs/archive/` (detailed reference)
2. Check config files: `services/*/config.yaml`
3. Check example data: `data/example_output.json`

---

**That's it! This is your complete system.**
