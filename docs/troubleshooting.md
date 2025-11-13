# Troubleshooting Guide

Solutions to common issues when using the Immigration Platform.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Crawler Issues](#crawler-issues)
- [Classifier Issues](#classifier-issues)
- [Matcher Issues](#matcher-issues)
- [Assistant Issues](#assistant-issues)
- [General Issues](#general-issues)

## Installation Issues

### Issue: "No module named 'requests'"

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install -r requirements.txt
```

**If that fails:**
```bash
pip install requests beautifulsoup4 pyyaml openai
```

### Issue: Python Version Too Old

**Error:**
```
SyntaxError: invalid syntax
```

**Check version:**
```bash
python --version
```

**Solution:**
Upgrade to Python 3.8+:
- Windows: Download from [python.org](https://python.org)
- Linux: `sudo apt-get install python3.10`
- Mac: `brew install python@3.10`

### Issue: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Linux/Mac
sudo pip install -r requirements.txt

# Or use --user flag
pip install --user -r requirements.txt

# Windows: Run PowerShell as Administrator
```

## Crawler Issues

### Issue: No Pages Crawled

**Symptoms:**
```
✅ Crawled 0 pages for australia
```

**Causes & Solutions:**

1. **Invalid seed URLs:**
   ```bash
   # Check config.yaml
   cat config.yaml | grep -A5 australia
   ```
   Verify URLs are correct and accessible.

2. **Too strict keywords:**
   ```yaml
   # services/crawler/config.yaml
   relevance_keywords:
     required:
       - visa  # Make less restrictive
   ```

3. **Website blocking:**
   ```yaml
   # Increase delays
   delay_between_requests: 3
   ```

### Issue: 403 Forbidden

**Error:**
```
❌ Error fetching https://...: 403 Forbidden
```

**Solutions:**

1. **Change user agent:**
   ```yaml
   user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
   ```

2. **Increase delay:**
   ```yaml
   delay_between_requests: 2
   ```

3. **Check robots.txt:**
   Visit: `https://website.com/robots.txt`

4. **Use official API** (if available)

5. **Manual data collection** (last resort)

### Issue: Connection Timeout

**Error:**
```
⚠️  Timeout fetching https://...
```

**Solutions:**

1. **Increase timeout:**
   ```yaml
   timeout: 60  # 60 seconds
   ```

2. **Check internet connection:**
   ```bash
   ping google.com
   ```

3. **Try again later** (website may be down)

### Issue: Out of Memory

**Symptoms:**
- Process crashes
- System slows down

**Solutions:**

1. **Reduce pages per country:**
   ```yaml
   max_pages_per_country: 50
   ```

2. **Process one country at a time:**
   ```bash
   python main.py crawl --countries australia
   python main.py crawl --countries canada
   ```

## Classifier Issues

### Issue: No Requirements Extracted

**Symptoms:**
```
⚠️  No requirements found for visa
```

**Solutions:**

1. **Check raw content:**
   ```python
   import json
   with open('data/raw/australia/{hash}.json') as f:
       data = json.load(f)
       print(data['content'][:1000])
   ```

2. **Add pattern variations:**
   ```yaml
   # services/classifier/config.yaml
   patterns:
     age:
       - "(?:age|aged)\\s*(\\d+)\\s*(?:to|-|and)\\s*(\\d+)"
       - "applicants\\s*must\\s*be\\s*(\\d+)"  # Add new pattern
   ```

3. **Check if raw data exists:**
   ```bash
   ls data/raw/australia/
   ```

### Issue: Wrong Category

**Symptoms:**
```
Work visa classified as 'tourist'
```

**Solutions:**

1. **Make keywords more specific:**
   ```yaml
   categories:
     work:
       keywords:
         - skilled worker visa  # More specific
         - work permit
       # Not just "work"
   ```

2. **Review classification logic:**
   ```bash
   python tests/test_classifier.py
   ```

### Issue: Incorrect Numbers

**Symptoms:**
```
Age: 2025 (should be 18-45)
```

**Solutions:**

1. **Add validation in extractor:**
   ```python
   # services/classifier/extractor.py
   def extract_age_requirement(self, text):
       match = ...
       age = int(match.group(1))

       # Validate
       if age < 10 or age > 100:
           return None

       return age
   ```

2. **Review patterns for specificity**

## Matcher Issues

### Issue: No Matches Found

**Symptoms:**
```
❌ No eligible visas found
```

**Solutions:**

1. **Check if structured data exists:**
   ```bash
   ls data/structured/
   ```

   If empty, run:
   ```bash
   python main.py classify --all
   ```

2. **Broaden country search:**
   ```json
   {
     "countries_of_interest": ["all"]
   }
   ```

3. **Review gaps in output:**
   Look for what's missing and adjust profile or look at lower-scored matches.

### Issue: Low Scores

**Symptoms:**
```
Top match: 35% (below 50% threshold)
```

**Causes & Solutions:**

1. **Age outside range:**
   - Look for visas with wider age ranges
   - Consider different visa categories

2. **Education too low:**
   - Pursue additional qualifications
   - Look for visas with lower education requirements

3. **Insufficient experience:**
   - Gain more work experience
   - Look for entry-level visa categories

### Issue: Incorrect Scoring

**Symptoms:**
```
Should be 100% but showing 75%
```

**Solutions:**

1. **Check scoring weights:**
   ```yaml
   # services/matcher/config.yaml
   scoring:
     weights:
       age: 0.25
       education: 0.30
       work_experience: 0.25
       language: 0.20
   # Must sum to 1.0
   ```

2. **Review education hierarchy:**
   ```yaml
   education_hierarchy:
     phd: 5
     master: 4
     bachelor: 3
   ```

3. **Run tests:**
   ```bash
   python tests/test_matcher.py
   ```

## Assistant Issues

### Issue: API Key Not Found

**Error:**
```
❌ Error: OPENROUTER_API_KEY environment variable not set!
```

**Solutions:**

**Windows PowerShell:**
```powershell
# Set for current session
$env:OPENROUTER_API_KEY = 'sk-or-v1-...'

# Set permanently
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-v1-...", "User")
```

**Linux/Mac:**
```bash
# Set for current session
export OPENROUTER_API_KEY='sk-or-v1-...'

# Set permanently (~/.bashrc)
echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
source ~/.bashrc
```

**Or put directly in config:**
```yaml
# services/assistant/config.yaml
openrouter:
  api_key_env: "sk-or-v1-actual-key-here"
```

### Issue: No Visa Data Found

**Error:**
```
❌ No relevant visa information found for your query.
```

**Solutions:**

1. **Run classifier:**
   ```bash
   python main.py classify --all
   ```

2. **Be more specific:**
   ```
   Bad: "tell me about visas"
   Good: "what work visas are available in Canada?"
   ```

3. **Check data exists:**
   ```bash
   ls data/structured/
   ```

### Issue: Poor Quality Answers

**Symptoms:**
- Irrelevant answers
- Hallucinations
- Wrong information

**Solutions:**

1. **Lower temperature:**
   ```yaml
   # services/assistant/config.yaml
   llm:
     temperature: 0.1  # More factual
   ```

2. **Provide more context:**
   ```yaml
   context:
     max_visas: 10  # Include more visas
   ```

3. **Switch models:**
   ```yaml
   # Try OpenAI instead
   provider: "openai"
   openai:
     model: "gpt-4o-mini"
   ```

### Issue: Rate Limiting

**Error:**
```
Error: Rate limit exceeded
```

**Solutions:**

1. **Wait a few minutes**

2. **Use different provider:**
   ```yaml
   provider: "openai"  # Switch from openrouter
   ```

3. **Upgrade tier** (for paid services)

### Issue: Slow Responses

**Symptoms:**
- Takes >30 seconds to respond

**Solutions:**

1. **Reduce tokens:**
   ```yaml
   max_tokens: 500  # Shorter responses
   ```

2. **Reduce context:**
   ```yaml
   context:
     max_visas: 3
   ```

3. **Use faster model:**
   ```yaml
   openrouter:
     model: "meta-llama/llama-3.1-8b-instruct:free"  # Fast
   ```

## General Issues

### Issue: Windows Unicode Errors

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character...
```

**Solution:**
Already fixed in `shared/logger.py`!

If still occurs:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

### Issue: File Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
```

**Solution:**

1. **Check current directory:**
   ```bash
   pwd  # Linux/Mac
   cd   # Windows
   ```

2. **Navigate to project root:**
   ```bash
   cd /path/to/immigration-platform
   ```

3. **Verify file exists:**
   ```bash
   ls config.yaml
   ```

### Issue: JSON Decode Error

**Error:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**Solutions:**

1. **Check file is valid JSON:**
   ```bash
   cat data/structured/australia.json | python -m json.tool
   ```

2. **Delete and regenerate:**
   ```bash
   rm data/structured/australia.json
   python main.py classify --country australia
   ```

3. **Check for corrupted files:**
   ```bash
   # Find empty or corrupted files
   find data/structured -name "*.json" -size 0
   ```

### Issue: Permission Denied (Data Directory)

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'data/raw'
```

**Solution:**

```bash
# Linux/Mac
chmod -R 755 data/

# Windows: Right-click data folder → Properties → Security → Edit permissions
```

### Issue: Logs Fill Up Disk

**Symptoms:**
- Large `.log` files
- Low disk space

**Solutions:**

1. **Delete old logs:**
   ```bash
   rm *.log
   ```

2. **Implement log rotation:**
   ```python
   # shared/logger.py
   from logging.handlers import RotatingFileHandler

   handler = RotatingFileHandler(
       'crawler.log',
       maxBytes=10*1024*1024,  # 10MB
       backupCount=3
   )
   ```

## Getting More Help

### Check Logs

```bash
# View recent errors
tail -n 50 crawler.log
tail -n 50 classifier.log
tail -n 50 matcher.log
tail -n 50 assistant.log
```

### Run Tests

```bash
# Test individual services
python tests/test_crawler.py
python tests/test_classifier.py
python tests/test_matcher.py
python tests/test_assistant.py

# Test integration
python tests/test_integration.py
python tests/test_e2e_workflows.py
python tests/test_error_handling.py
```

### Enable Debug Logging

```python
# In any service main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Service Status

```python
# Quick health check
import os
from pathlib import Path

# Check data exists
print(f"Raw data: {len(list(Path('data/raw').rglob('*.json')))}")
print(f"Structured data: {len(list(Path('data/structured').glob('*.json')))}")

# Check configs exist
configs = [
    'config.yaml',
    'services/crawler/config.yaml',
    'services/classifier/config.yaml',
    'services/matcher/config.yaml',
    'services/assistant/config.yaml'
]
for config in configs:
    print(f"{config}: {'✅' if Path(config).exists() else '❌'}")
```

## Still Stuck?

1. **Review documentation:**
   - [Quick Start Guide](guides/quick-start.md)
   - [Service Documentation](services/crawler.md)
   - [Configuration Guide](guides/configuration.md)

2. **Check examples:**
   - Test files in `/tests` directory
   - Sample profiles in documentation

3. **Search issues:**
   - Check if others have encountered similar issues
   - Look for error message in documentation

## Prevention Tips

1. **Run tests after changes:**
   ```bash
   python tests/test_integration.py
   ```

2. **Start small:**
   - Test with one country first
   - Use small `max_pages` values

3. **Check logs regularly:**
   ```bash
   tail -f crawler.log
   ```

4. **Keep backups:**
   - Back up working configurations
   - Version control your changes

5. **Monitor resource usage:**
   - Check disk space
   - Monitor memory usage

---

**See Also:**
- [Quick Start Guide](guides/quick-start.md)
- [Configuration Guide](guides/configuration.md)
- [Service Documentation](services/crawler.md)
