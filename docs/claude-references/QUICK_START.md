# Quick Start Guide - Immigration Platform

## 🎯 All Issues Fixed!

✅ **Database Viewer** - See everything in your database
✅ **Custom Models** - Add any model you want
✅ **Fixed Errors** - No more AttributeError or deprecation warnings
✅ **Classifier CLI** - Works with database now
✅ **Proper Indexing** - Clear workflow for data

---

## 🚀 Setup (First Time)

### 1. Create .env file with your API key

```bash
# Copy template
cp .env.example .env

# Edit and add your OpenRouter API key
# (Get FREE key from https://openrouter.ai/keys)
nano .env
```

Add this line:
```
OPENROUTER_API_KEY=sk-or-your-key-here
```

### 2. Start the app

```bash
streamlit run app.py
```

---

## 📊 View Your Database

### New Database Viewer Page (💾)

Go to **💾 Database** page in sidebar to see:

- **📊 Overview** - Stats and table schemas
- **🕷️ Crawled Pages** - All scraped pages (paginated, filterable)
- **📋 Visas** - Extracted visas (filter by country/category)
- **👤 Clients** - Client profiles
- **✅ Eligibility Checks** - Match results
- **⚙️ Settings** - All config values and sources
- **🔍 Embeddings** - Semantic search indices

**Features:**
- Pagination (5-50 items per page)
- Filter by country, category
- Search visa types
- Export to JSON
- See where config comes from (.env vs database)

---

## 🔧 Add Custom Models

### Settings Page (⚙️)

1. Go to **⚙️ Settings** page
2. Tab 2: Edit Settings
3. Check **"Use custom model"**
4. Enter any model name:
   - `google/gemini-pro`
   - `anthropic/claude-3.5-sonnet`
   - `openai/gpt-4o`
   - Any model from your provider
5. Click **Save**

**Predefined models available:**
- OpenRouter: `google/gemini-2.0-flash-001:free`, `meta-llama/llama-3.2-3b-instruct:free`, `anthropic/claude-3.5-sonnet`
- OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`

---

## 📋 Complete Workflow

### Step 1: Crawl Pages

**Option A: Use UI** (Recommended)
```bash
streamlit run app.py
# → 🕷️ Crawler page
# → Configure countries and settings
# → Click "Start Crawling"
```

**Option B: Use CLI**
```bash
python main.py crawl --all
# OR
python main.py crawl --country canada
```

**Check results:**
- Go to 💾 Database page → Crawled Pages tab
- Or run: `python scripts/check_database.py`

---

### Step 2: Extract Visas

**Option A: Use UI** (Recommended)
```bash
streamlit run app.py
# → 📊 Classifier page
# → Select LLM provider (needs API key)
# → Click "Start Classification"
```

**Option B: Use CLI**
```bash
python main.py classify --all
# OR
python main.py classify --country canada
```

**Check results:**
- Go to 💾 Database page → Visas tab
- Filter by country, category
- Export to JSON if needed

---

### Step 3: Create Embeddings (Optional)

For semantic search:

```bash
python scripts/index_embeddings.py
```

This creates vector embeddings for all visas.

**Check results:**
- Go to 💾 Database page → Embeddings tab
- Or run: `python scripts/search_semantic.py`

---

### Step 4: Test Semantic Search

```bash
python scripts/search_semantic.py
```

Enter natural language queries:
- "work visa for software engineers"
- "student visa for masters degree"
- "family visa for spouse"

---

## 🔍 Check System Status

### Option 1: Home Page

Open app and look at banner:
- ✅ Green = System ready with API key
- ⚠️ Yellow = No API key (limited features)

### Option 2: Database Viewer

Go to **💾 Database** → **📊 Overview** tab:
- See counts for everything
- Check table schemas
- View database file size

### Option 3: Settings Page

Go to **⚙️ Settings** → **Tab 1: Current Settings**:
- See all active settings
- Check source (🌍 .env, 💾 Database, 📄 YAML)
- Verify API key status

### Option 4: Run System Test

```bash
python scripts/test_system.py
```

Shows detailed status of all components.

---

## 🗂️ View Data by Country

### In Database Viewer:

1. Go to **💾 Database** page
2. Select tab: **🕷️ Crawled Pages** or **📋 Visas**
3. Use **"Filter by Country"** dropdown
4. Select your country
5. Use pagination to browse

**Export:**
- Click "Export as JSON" button
- Download filtered data

---

## ⚙️ Configuration Sources

Settings load in this priority:

1. **🌍 .env file** (HIGHEST)
   - For API keys and secrets
   - Not committed to git

2. **💾 Database** (MEDIUM)
   - For user preferences
   - Editable via Settings UI

3. **📄 YAML files** (LOWEST)
   - For service defaults
   - Version controlled

**To see where each setting comes from:**
- Go to 💾 Database → Settings tab
- Check the "Source" column

---

## 🐛 Troubleshooting

### "No visas found in database"

**Cause:** You haven't run the Classifier yet

**Fix:**
1. Check you have crawled pages: Go to 💾 Database → Crawled Pages
2. If no pages: Run Crawler first
3. If have pages: Run Classifier (UI or CLI)

---

### "OpenRouter API key not found"

**Cause:** No API key configured

**Fix (Easy - Use UI):**
1. Go to ⚙️ Settings page
2. Tab 3: Environment (.env)
3. API Key Quick Setup section
4. Paste your OpenRouter key
5. Click Save
6. Restart app

**Fix (Manual - Use .env):**
```bash
echo "OPENROUTER_API_KEY=sk-or-your-key" >> .env
streamlit run app.py
```

Get FREE key: https://openrouter.ai/keys

---

### "AttributeError: 'DataStore' object has no attribute"

**Cause:** Old code trying to use JSON files instead of database

**Fix:** ✅ Already fixed! The classifier now uses Database.

If you still see this:
1. Pull latest code: `git pull`
2. Restart app

---

### Deprecation warning: "use_container_width"

**Fix:** ✅ Already fixed! Changed to `width='stretch'`

---

### "LLM features are disabled"

**Cause:** System working in fallback mode (no API key)

**What works without API key:**
- ✅ Crawler (web scraping)
- ✅ Pattern-based extraction (limited)
- ✅ Database viewing
- ✅ Settings management

**What needs API key:**
- ❌ LLM-powered visa extraction
- ❌ AI Assistant chat
- ❌ Intelligent requirement parsing

**Fix:** Add API key (see above)

---

## 📚 Useful Commands

### View Database:
```bash
# In UI
streamlit run app.py → 💾 Database page

# In CLI
python scripts/check_database.py
python scripts/query_database.py
```

### Export Data:
```bash
# In UI: 💾 Database page → Export buttons

# In CLI
python scripts/query_database.py
# Select option to export
```

### Test System:
```bash
python scripts/test_system.py
python test_config_lifecycle.py
```

### Check Semantic Search:
```bash
python scripts/search_semantic.py
```

### Verify API Key:
```bash
# Check if .env exists
cat .env | grep OPENROUTER_API_KEY

# Or check in UI
streamlit run app.py → ⚙️ Settings → Tab 1
```

---

## 🎨 UI Pages Overview

| Page | Icon | Purpose |
|------|------|---------|
| Home | 🌍 | Status overview, quick start |
| Crawler | 🕷️ | Scrape government websites |
| Classifier | 📊 | Extract visa data from pages |
| Matcher | 🔍 | Check eligibility (coming soon) |
| Assistant | 💬 | AI chat (coming soon) |
| Settings | ⚙️ | Configure API keys, models, etc. |
| **Database** | **💾** | **View all data (NEW!)** |

---

## 💡 Pro Tips

1. **Always check Database Viewer first** to see what data you have
2. **Use pagination** for large datasets (set to 10-20 items)
3. **Filter by country** to focus on specific data
4. **Export to JSON** before making big changes
5. **Check Settings → Tab 1** to see active configuration
6. **Use custom models** for better results (if you have access)
7. **Run embeddings after classification** for semantic search

---

## 🎯 Next Steps

1. **Set API key** (if not done)
2. **View Database** to see what you have
3. **Crawl pages** for countries you need
4. **Classify visas** to extract structured data
5. **Create embeddings** for semantic search
6. **Use Database Viewer** to explore results

---

## 📖 Documentation

- **Complete Guide:** `CONFIGURATION_LIFECYCLE.md`
- **Config Setup:** `CONFIG_GUIDE.md`
- **Scripts:** `scripts/README.md`
- **System Overview:** `SYSTEM.md`

---

## ✅ Summary

All issues fixed:
- ✅ Database visibility (new Database Viewer page)
- ✅ Custom models (Settings page)
- ✅ Classifier CLI (uses Database now)
- ✅ Streamlit warnings (deprecated params fixed)
- ✅ Clear error messages (actionable fixes)
- ✅ Paginated tables (5-50 items per page)
- ✅ Export functionality (JSON format)
- ✅ Config transparency (see sources)

**Everything is working! Start with the Database Viewer to see what you have! 💾**
