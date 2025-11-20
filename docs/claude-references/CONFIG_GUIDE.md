# Configuration Guide

## ✅ Integrated Configuration System

Your settings and configuration are now **fully integrated** with:
- ✅ **Database** (settings table)
- ✅ **.env file** (environment variables)
- ✅ **YAML files** (service defaults)

---

## 🎯 Configuration Priority

Settings are loaded in this order (highest to lowest priority):

1. **🌍 .env file** (Environment variables) - **HIGHEST PRIORITY**
2. **💾 Database** (Settings saved via UI)
3. **📄 YAML files** (Default configs in `services/`) - **LOWEST PRIORITY**

**Example:**
- If `OPENROUTER_API_KEY` is in `.env` → Uses that value
- If not in `.env` but saved in database → Uses database value
- If not in database → Uses YAML default (or empty)

---

## 🚀 Quick Setup

### Option 1: Use the Settings UI (Recommended)

1. **Run the app:**
   ```bash
   streamlit run app.py
   ```

2. **Go to Settings page** (⚙️ in sidebar)

3. **Set your API key:**
   - Scroll to "API Key Quick Setup"
   - Choose OpenRouter (FREE) or OpenAI (Paid)
   - Paste your API key
   - Click "Save"

4. **Edit other settings** as needed

### Option 2: Use .env file (Manual)

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   nano .env  # or use any text editor
   ```

3. **Add your API key:**
   ```bash
   OPENROUTER_API_KEY=sk-or-your-key-here
   ```

4. **Save and restart the app**

---

## 📋 Available Settings

### LLM Settings
- `llm.provider` - Provider: `openrouter` or `openai`
- `llm.model` - Model name (e.g., `google/gemini-2.0-flash-001:free`)
- `llm.temperature` - Temperature (0.0-1.0)
- `llm.max_tokens` - Max tokens per request

### Crawler Settings
- `crawler.delay` - Delay between requests (seconds)
- `crawler.max_pages` - Max pages per country
- `crawler.max_depth` - Max crawl depth

### Embeddings
- `embeddings.model` - Model for semantic search (default: `all-MiniLM-L6-v2`)

### Application
- `app.log_level` - Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `app.default_country` - Default country in UI

---

## 🔑 API Keys

### Where to Get FREE API Keys

**OpenRouter (Recommended - 100% FREE models available):**
1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up / Login
3. Get your API key from dashboard
4. Use FREE models:
   - `google/gemini-2.0-flash-001:free`
   - `meta-llama/llama-3.2-3b-instruct:free`

**OpenAI (Paid):**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account / Add payment
3. Go to API Keys section
4. Create new key

---

## 🛠️ Using ConfigManager in Code

```python
from shared.config_manager import get_config

config = get_config()

# Get a setting
provider = config.get('llm.provider', 'openrouter')
model = config.get('llm.model')

# Get API key
api_key = config.get_api_key()

# Get complete LLM config
llm_config = config.get_llm_config()

# Save a setting to database
config.set('llm.temperature', 0.5)

# Get all settings for a category
llm_settings = config.get_all('llm')
```

---

## 📊 Database Settings Table

The database now has a `settings` table:

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,          -- Setting key (e.g., 'llm.provider')
    value TEXT NOT NULL,           -- Setting value
    type TEXT NOT NULL,            -- Type: string, integer, float, boolean
    category TEXT,                 -- Category: llm, crawler, app, etc.
    description TEXT,              -- Human-readable description
    updated_at TIMESTAMP           -- Last update timestamp
);
```

**Default settings are auto-created** on first run!

---

## 🔄 Migration

If you have an **existing database** without the settings table:

```bash
python scripts/add_settings_table.py
```

**New databases automatically include the settings table.**

---

## ✅ Verify Your Setup

Run the system test:

```bash
python scripts/test_system.py
```

Look for:
- ✅ **CONFIG MANAGER TEST** section
- ✅ **Settings table** in database
- ✅ **API Key status**

---

## 💡 Tips

1. **API Keys** → Store in `.env` file (secure, not committed to git)
2. **User Preferences** → Store in database (editable via UI)
3. **Service Defaults** → Keep in YAML files (version controlled)

4. **Edit settings via UI** → Changes saved to database
5. **Edit .env file** → Restart app to apply
6. **Edit YAML files** → No restart needed (lowest priority)

---

## 🎨 Settings UI Features

The **⚙️ Settings** page provides:

### Tab 1: Current Settings
- View all active settings
- See where each setting comes from (🌍 .env, 💾 Database, 📄 YAML)
- Check API key status

### Tab 2: Edit Settings
- Edit LLM configuration (provider, model, temperature)
- Edit crawler settings (delay, max pages, depth)
- Edit app settings (log level, default country)
- Changes save to database

### Tab 3: Environment (.env)
- Create `.env` from template
- Edit `.env` file directly (with API key masking)
- Quick API key setup for OpenRouter/OpenAI
- Shows configuration priority

---

## 🚨 Troubleshooting

**Problem:** API key not working

**Solution:**
1. Check `.env` file exists and has correct key
2. Verify key format starts with `sk-` (OpenAI) or `sk-or-` (OpenRouter)
3. Restart Streamlit app after editing `.env`
4. Check Settings UI → Tab 1 → API Key status

**Problem:** Settings not saving

**Solution:**
1. Verify database exists: `data/immigration.db`
2. Check settings table: `python scripts/check_database.py`
3. Run migration if needed: `python scripts/add_settings_table.py`

**Problem:** Config shows wrong values

**Solution:**
1. Remember priority: `.env` > Database > YAML
2. Check `.env` file first (highest priority)
3. Use Settings UI → Tab 1 to see active values

---

## 📚 Additional Resources

- **Full system test:** `python scripts/test_system.py`
- **Check database:** `python scripts/check_database.py`
- **Script documentation:** `scripts/README.md`
- **.env template:** `.env.example`
