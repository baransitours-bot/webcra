# Utility Scripts

All utility scripts organized in one place.

## 📋 Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_system.py` | **Test all operations** | `python scripts/test_system.py` |
| `add_settings_table.py` | Add settings table (upgrade) | `python scripts/add_settings_table.py` |
| `migrate_database.py` | Migrate JSON → Database | `python scripts/migrate_database.py` |
| `check_database.py` | Quick database overview | `python scripts/check_database.py` |
| `query_database.py` | Interactive SQL queries | `python scripts/query_database.py` |
| `index_embeddings.py` | Create semantic embeddings | `python scripts/index_embeddings.py` |
| `search_semantic.py` | Test semantic search | `python scripts/search_semantic.py` |

---

## 🧪 test_system.py

**Comprehensive system test - validates all components**

Tests:
- ✅ Config sources (YAML vs environment variables)
- ✅ Database structure and connectivity
- ✅ Crawler components
- ✅ Classifier components
- ✅ Matcher components
- ✅ Embeddings/semantic search
- ✅ Assistant components
- ✅ File structure

**Run this first to validate your setup!**

```bash
python scripts/test_system.py
```

---

## ⚙️ add_settings_table.py

**Database upgrade - adds settings table for centralized config**

Run this ONCE if you have an existing database without settings table:

```bash
python scripts/add_settings_table.py
```

Adds:
- Settings table with 10 default settings
- Support for .env integration
- Centralized config management

**Note:** New databases auto-create this table. Only needed for upgrading old databases.

---

## 🗄️ migrate_database.py

**One-time migration from JSON files to SQLite database**

Migrates:
- `data/raw/*.json` → `crawled_pages` table
- `data/processed/visas.json` → `visas` table

Preserves original files (backup).

```bash
python scripts/migrate_database.py
```

---

## 👀 check_database.py

**Quick database overview**

Shows:
- Overall statistics
- Pages by country
- Visas by country
- Version tracking status
- Sample records

```bash
python scripts/check_database.py
```

---

## 🔍 query_database.py

**Interactive database query tool**

Features:
- View pages/visas by country
- Check visa version history
- Run custom SQL queries
- Database statistics

```bash
python scripts/query_database.py
```

Menu-driven interface.

---

## 🧠 index_embeddings.py

**Create semantic embeddings for all visas**

Creates 384-dimensional vectors for semantic search.

**Run after adding new visas!**

```bash
python scripts/index_embeddings.py
```

Takes ~1 minute for 100 visas.

---

## 🔎 search_semantic.py

**Test semantic search**

Interactive natural language search:
- "work visa for software engineers"
- "student visa for master degree"
- "family visa for spouse"

```bash
python scripts/search_semantic.py
```

---

## 📁 app_old_backup.py

Backup of old monolithic app.py (before multi-page refactor).

Keep for reference.

---

## 🎯 Quick Start Workflow

**1. First time setup:**
```bash
# Test everything
python scripts/test_system.py

# If you have old JSON data, migrate it
python scripts/migrate_database.py

# Create embeddings
python scripts/index_embeddings.py
```

**2. Check system status:**
```bash
python scripts/check_database.py
```

**3. Query data:**
```bash
python scripts/query_database.py
```

**4. Test semantic search:**
```bash
python scripts/search_semantic.py
```

---

## 📝 Notes

- All scripts can be run from project root: `python scripts/script_name.py`
- Scripts automatically add project root to Python path
- Database location: `data/immigration.db`
- Logs location: `logs/`
