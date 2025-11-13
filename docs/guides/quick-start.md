# Quick Start Guide

Get up and running with the Immigration Platform in 5 minutes!

## Prerequisites

- Python 3.8+
- Internet connection
- 2GB RAM
- 1GB disk space

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python main.py --help
```

You should see:

```
Immigration Platform CLI

Usage:
  python main.py <service> [options]

Services:
  crawl      - Crawl government immigration websites
  classify   - Extract and structure visa requirements
  match      - Match user profile to visas
  assist     - AI-powered immigration assistant
```

## Your First Workflow

### Step 1: Crawl Government Websites

Collect immigration data:

```bash
python main.py crawl --countries australia
```

**What it does:**
- Visits official Australian immigration website
- Extracts text about visas
- Saves raw data to `data/raw/australia/`

**Expected output:**
```
🕷️  Starting crawler for: australia
📄 Found relevant page: https://...
✅ Crawled 45 pages for australia
```

**Time**: ~1-2 minutes

### Step 2: Extract Requirements

Structure the crawled data:

```bash
python main.py classify --country australia
```

**What it does:**
- Reads raw pages from Step 1
- Extracts age, education, experience requirements
- Categorizes visas (work, study, family, etc.)
- Saves to `data/structured/australia.json`

**Expected output:**
```
📊 Starting classifier for: australia
📄 Processing 45 pages...
✅ Extracted 12 visa types
💾 Saved to data/structured/australia.json
```

**Time**: ~10 seconds

### Step 3: Match Your Profile

Find visas you're eligible for:

```bash
python main.py match --interactive
```

**What it does:**
- Asks for your age, education, experience
- Scores your eligibility for each visa
- Shows top matches ranked by fit

**Interactive flow:**
```
🤔 Let's build your profile...

What is your age? 28
What is your education level?
  1. PhD/Doctorate
  2. Master's Degree
  3. Bachelor's Degree
  4. Diploma
  5. High School
Choice: 3

How many years of work experience do you have? 5
What is your occupation? software engineer

Do you have English language test scores? (yes/no) yes
What is your IELTS score? 7.5

Which countries are you interested in?
(comma-separated, or 'all'): australia

---

🎯 Top 10 Matches for You:

1. Skilled Independent Visa (Subclass 189) [australia]
   Category: work
   Eligibility Score: 95.5%

   Requirements:
   - Age: 18-45 years ✅ You: 28
   - Education: Bachelor's or higher ✅ You: Bachelor's
   - Experience: 3+ years ✅ You: 5 years
   - IELTS: 6.5+ ✅ You: 7.5

   Strengths:
   ✅ Education meets requirement
   ✅ Experience exceeds requirement (5 years vs 3 required)
   ✅ Strong language scores

   Source: https://immi.homeaffairs.gov.au/...
```

**Time**: ~2 minutes

### Step 4: Ask Questions (Optional)

Get AI-powered answers:

#### 4a. Setup (One-time)

Get a FREE API key from [openrouter.ai/keys](https://openrouter.ai/keys)

**Windows PowerShell:**
```powershell
$env:OPENROUTER_API_KEY = 'your-key-here'
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY='your-key-here'
```

#### 4b. Ask Away!

```bash
python main.py assist --query "What are the requirements for the Skilled Independent visa?"
```

**Expected output:**
```
================================================================================
💬 The Skilled Independent visa (Subclass 189) is a permanent residence visa
for skilled workers. Requirements include:

1. **Age**: Must be under 45 years old
2. **Skills Assessment**: Positive assessment in eligible occupation
3. **Points Test**: Minimum 65 points
4. **English Language**: IELTS 6.0+ (higher for more points)
5. **Education**: Post-secondary qualification

The visa allows you to:
- Live and work permanently in Australia
- Study in Australia
- Enroll in Medicare
- Sponsor eligible relatives

Processing time is typically 6-9 months.

Source: https://immi.homeaffairs.gov.au/...
================================================================================
```

Or use **chat mode** for conversations:

```bash
python main.py assist --chat
```

```
You: What work visas are available in Australia?
Assistant: [Detailed answer with multiple visa options...]

You: Which one is best for software engineers?
Assistant: [Personalized recommendation...]

You: exit
Goodbye! Good luck with your immigration journey! 🌍
```

## Next Steps

### Add More Countries

```bash
# Crawl multiple countries
python main.py crawl --countries canada,uk,germany

# Classify all
python main.py classify --all

# Match again (now with more options)
python main.py match --interactive
```

### Save Your Profile

Instead of interactive mode, save your profile:

**user_profile.json:**
```json
{
  "age": 28,
  "education": "bachelor",
  "work_experience": 5,
  "occupation": "software engineer",
  "language": {
    "english": {
      "ielts": 7.5
    }
  },
  "countries_of_interest": ["australia", "canada", "uk"]
}
```

Then:

```bash
python main.py match --profile user_profile.json
```

### Run Tests

Verify everything works:

```bash
# Individual service tests
python tests/test_crawler.py
python tests/test_classifier.py
python tests/test_matcher.py
python tests/test_assistant.py

# Integration tests
python tests/test_integration.py
python tests/test_e2e_workflows.py
```

## Common Workflows

### Workflow 1: Research Phase

Just want to explore options:

```bash
# Collect data
python main.py crawl --all
python main.py classify --all

# Ask general questions
python main.py assist --chat
```

### Workflow 2: Specific Country

Focused on one country:

```bash
# Canada-specific
python main.py crawl --countries canada
python main.py classify --country canada
python main.py match --profile user.json --country canada
```

### Workflow 3: Compare Options

Compare across multiple countries:

```bash
# Collect data for target countries
python main.py crawl --countries australia,canada,uk
python main.py classify --all

# Get matches across all
python main.py match --profile user.json

# Review top matches from each country
```

## Troubleshooting

### Issue: "No module named 'requests'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No raw data found"

**Solution:**
Run crawler first:
```bash
python main.py crawl --countries australia
```

### Issue: "No matches found"

**Possible causes:**
1. No structured data - Run: `python main.py classify --all`
2. Profile doesn't match any visas - Try different countries
3. Requirements too strict - Review gaps in output

### Issue: Windows Unicode Errors

**Solution:**
Already fixed! If you still encounter issues:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Tips

1. **Start with one country** to test the workflow
2. **Save your profile** as JSON for reuse
3. **Check logs** if something goes wrong (`crawler.log`, `classifier.log`, etc.)
4. **Be patient** - Crawling takes time (respect rate limits)
5. **Use chat mode** for exploration, single queries for specific questions

## Getting Help

- **Documentation**: `/docs` folder
- **Service Guides**: `/docs/services`
- **Troubleshooting**: `/docs/troubleshooting.md`
- **Examples**: Check test files in `/tests`

## Summary

You've learned to:
- ✅ Crawl government websites
- ✅ Extract visa requirements
- ✅ Match your profile to visas
- ✅ Ask AI-powered questions

Happy visa hunting! 🌍✈️

---

**Next**: [Configuration Guide →](configuration.md) | [Service Documentation →](../services/crawler.md)
