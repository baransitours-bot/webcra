# Configuration Lifecycle - SOLVED ✅

## ❌ The Problem You Identified

You were absolutely right - the old system had **no proper lifecycle**:

```
User starts app
  ↓
Page loads
  ↓
User clicks button
  ↓
Service tries to load config from YAML
  ↓
❌ ERROR: API key not found!
  ↓
Falls into error loop
```

**Issues:**
- Config loaded **AFTER** services needed it
- Each service loaded config independently (inefficient)
- YAML files checked first (wrong priority)
- No centralized config management
- Error messages didn't tell users what to do

---

## ✅ The Solution - Proper Lifecycle

Now the system has a **proper initialization lifecycle**:

```
App starts (app.py)
  ↓
@st.cache_resource init_app()  ← RUNS ONCE
  ↓
1. Initialize Database (creates settings table)
  ↓
2. Load ConfigManager (.env > Database > YAML)
  ↓
3. Cache config for entire app session
  ↓
Services auto-use global ConfigManager
  ↓
✅ Everything works!
```

---

## 🔄 Configuration Flow

### Priority Order (Highest to Lowest):

1. **🌍 .env file** (Environment Variables)
   - For API keys and secrets
   - Not committed to git
   - Highest priority

2. **💾 Database** (Settings Table)
   - For user preferences
   - Editable via Settings UI
   - Persists across sessions

3. **📄 YAML files** (Service Defaults)
   - For service configuration
   - Version controlled
   - Lowest priority (fallback)

### Example Lookup:

```python
config.get('llm.provider')

Step 1: Check .env for LLM_PROVIDER
        → Not found

Step 2: Check database settings table
        → Found: "openrouter"
        → RETURN "openrouter" ✅
```

---

## 📂 Where Configuration Lives

### Storage Locations:

| Setting Type | Storage | Managed By | Use Case |
|--------------|---------|------------|----------|
| **API Keys** | `.env` file | User manually edits | Secrets (never commit!) |
| **User Prefs** | Database `settings` table | Settings UI | Personalization |
| **Defaults** | `services/*/config.yaml` | Developers | Service configuration |

### Priority Example:

```bash
# .env file (HIGHEST)
OPENROUTER_API_KEY=sk-or-abc123

# Database settings table (MEDIUM)
llm.provider = openrouter
llm.model = google/gemini-2.0-flash-001:free

# YAML file (LOWEST)
llm:
  provider: openai  # ← IGNORED! Database has it
  model: gpt-4      # ← IGNORED! Database has it
```

Result: Uses **OpenRouter** with **Gemini** and API key from `.env`

---

## 🚀 App Initialization Sequence

### What Happens at Startup:

```python
# app.py

@st.cache_resource  # ← Runs ONCE per session
def init_app():
    # 1. Initialize database
    db = Database()
    # Creates all tables including settings
    # Auto-populates default settings

    # 2. Load configuration
    config = get_config()
    # Reads from: .env > Database > YAML
    # Caches internally

    return {"db": db, "config": config}

# Initialize (cached)
app_state = init_app()
config = app_state["config"]

# Services can now use config
api_key_configured = config.get_api_key() is not None
```

**Benefits:**
- ✅ Runs **once** at app startup (cached)
- ✅ Config ready **before** any service loads
- ✅ No redundant config loading
- ✅ Fast subsequent page loads

---

## 🔧 Service Integration

### Old Way (BROKEN):

```python
# Classifier page
with open('services/classifier/config.yaml', 'r') as f:
    config = yaml.safe_load(f)  # ❌ Manual loading

extractor = VisaExtractor(config)  # ❌ Passing config around
# ERROR: No API key in YAML!
```

### New Way (CORRECT):

```python
# Classifier page
extractor = VisaExtractor()  # ✅ Auto-uses ConfigManager

# Inside VisaExtractor
class VisaExtractor:
    def __init__(self):
        self.llm_client = LLMClient()  # ✅ Auto-uses ConfigManager

# Inside LLMClient
class LLMClient:
    def __init__(self, config=None):
        if config is None:
            config = get_config()  # ✅ Uses global ConfigManager

        api_key = config.get_api_key()  # ✅ Loads from .env/DB
```

**No manual config passing! Services auto-connect to ConfigManager.**

---

## 🛡️ Graceful Error Handling

### Without API Key:

```python
try:
    llm = LLMClient()
except ValueError as e:
    # Clear, actionable error message:
    """
    Openrouter API key not found!

    Quick fix:
    1. Go to Settings page (⚙️) in the UI
    2. Tab 3 → API Key Quick Setup
    3. Paste your openrouter API key and save

    Or create .env file:
       OPENROUTER_API_KEY=your-key-here

    Get FREE OpenRouter key: https://openrouter.ai/keys
    """
```

### Fallback Strategy:

```python
# VisaExtractor
self.llm_client = None
try:
    self.llm_client = LLMClient()  # Try LLM
except ValueError:
    logger.warning("LLM not available, using pattern extraction")

# Later
if self.llm_client:
    result = self._extract_with_llm(text)  # AI-powered
else:
    result = self._extract_with_patterns(text)  # Rule-based fallback
```

**System works even without API key (limited features)!**

---

## 📊 Configuration Status Visibility

### Home Page Banner:

**Without API Key:**
```
⚠️ API Key Not Configured - LLM features are disabled

To enable AI-powered features:
1. Go to ⚙️ Settings page (in sidebar)
2. Tab 3 → API Key Quick Setup
3. Paste your API key and save

Get FREE OpenRouter key: https://openrouter.ai/keys
```

**With API Key:**
```
✅ System Ready - Using Openrouter (google/gemini-2.0-flash-001:free)
```

Users **immediately know** if system is configured!

---

## ✅ Testing the Lifecycle

### Run the Test:

```bash
python test_config_lifecycle.py
```

### Expected Output:

```
================================================================================
TESTING CONFIGURATION LIFECYCLE
================================================================================

1. Testing Database Initialization...
   ✅ Database initialized

2. Testing ConfigManager Initialization...
   ✅ ConfigManager initialized

3. Testing Config Loading...
   ✅ Provider: openrouter
   ✅ Model: google/gemini-2.0-flash-001:free

4. Testing API Key Check...
   ⚠️  API Key NOT configured (expected if .env not set)

5. Testing LLMClient Initialization...
   ⚠️  LLMClient failed (expected without API key)

6. Testing VisaExtractor Initialization (with fallback)...
   ✅ VisaExtractor with pattern-based fallback (no LLM)

================================================================================
CONFIGURATION LIFECYCLE TEST COMPLETE
================================================================================
```

---

## 🎯 Quick Setup Guide

### Option 1: Use .env File (Recommended for API Keys)

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit and add your API key
nano .env

# Add this line:
OPENROUTER_API_KEY=sk-or-your-key-here

# 3. Restart app
streamlit run app.py
```

### Option 2: Use Settings UI (Easier)

```bash
# 1. Start app
streamlit run app.py

# 2. Go to ⚙️ Settings page

# 3. Tab 3 → API Key Quick Setup

# 4. Paste key and click "Save"

# 5. App restarts automatically with new config
```

---

## 🔍 How to Verify Configuration

### Method 1: Check Home Page

- ✅ Green banner = Configured
- ⚠️ Yellow banner = Not configured

### Method 2: Run System Test

```bash
python scripts/test_system.py
```

Look for:
```
CONFIG MANAGER TEST
✅ ConfigManager imported successfully
✅ .env file found  # or ⚠️ No .env file
✅ API Key: sk-or-ab... (configured)
```

### Method 3: Check Settings Page

- Go to ⚙️ Settings
- Tab 1: Current Settings
- See "Source" column for each setting

---

## 🎨 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         APP STARTUP                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  app.py → @st.cache_resource init_app()                    │
│            │                                                │
│            ├─ Database()      → Creates settings table     │
│            │                                                │
│            └─ get_config()    → Loads ConfigManager        │
│                     │                                       │
│                     ├─ Load .env file (if exists)          │
│                     ├─ Cache database settings             │
│                     └─ Load YAML defaults                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    GLOBAL CONFIG READY                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  All services use: get_config()                            │
│                                                             │
│  VisaExtractor → LLMClient → ConfigManager                 │
│  EligibilityMatcher → ConfigManager                        │
│  Assistant → LLMClient → ConfigManager                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Improvements

### Before:
- ❌ No lifecycle - config loaded on-demand
- ❌ Each service loaded own config
- ❌ YAML priority was wrong
- ❌ No .env support
- ❌ Error loops
- ❌ No status visibility

### After:
- ✅ Proper lifecycle - config loads at startup
- ✅ Single ConfigManager (cached)
- ✅ Correct priority (.env > DB > YAML)
- ✅ Full .env integration
- ✅ Graceful fallback
- ✅ Clear status indicators
- ✅ Actionable error messages
- ✅ Backward compatible

---

## 📚 Related Files

- **Core Config:** `shared/config_manager.py`
- **Database:** `shared/database.py` (settings table)
- **LLM Client:** `services/assistant/llm_client.py`
- **App Init:** `app.py` (initialization)
- **Settings UI:** `pages/5_⚙️_Settings.py`
- **Test:** `test_config_lifecycle.py`
- **Guide:** `CONFIG_GUIDE.md`
- **Example:** `.env.example`

---

## 🎉 Summary

**You identified the critical problem:**
> "we do not have a lifecycle"

**We fixed it:**
1. ✅ Config loads **BEFORE** app starts (proper lifecycle)
2. ✅ Stored in Database **AND** .env (as you wanted)
3. ✅ Single source of truth (ConfigManager)
4. ✅ No more error loops
5. ✅ Graceful fallback
6. ✅ Clear user guidance

**The system now has a proper architecture with:**
- Initialization phase
- Configuration loading
- Service initialization
- Error handling
- Status visibility

**No more configuration chaos! 🎯**
