# System Map

Visual representation of the entire system architecture.

---

## High-Level System Flow

```
┌─────────────┐
│    USER     │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────┐
│              STREAMLIT UI (app.py)                  │
│  ┌────────┬────────┬────────┬────────┬────────┐   │
│  │Crawler │Classify│Matcher │Assistan│Settings│   │
│  │        │        │        │   t    │        │   │
│  └────────┴────────┴────────┴────────┴────────┘   │
└─────────────────────────────────────────────────────┘
       │        │        │        │        │
       ↓        ↓        ↓        ↓        ↓
┌─────────────────────────────────────────────────────┐
│                  CONTROLLERS                         │
│  (Exterior Interfaces - UI Friendly)                │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Crawler    │  │  Classifier   │               │
│  │  Controller  │  │  Controller   │  ...          │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
       │                     │
       ↓                     ↓
┌─────────────────────────────────────────────────────┐
│                   SERVICES                           │
│  (Interior Interfaces - Python API)                 │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Crawler    │  │  Classifier   │               │
│  │   Service    │  │   Service     │  ...          │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
       │                     │
       ↓                     ↓
┌─────────────────────────────────────────────────────┐
│                   ENGINES                            │
│  (Business Logic - Pure Functions)                  │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Crawler    │  │  Classifier   │               │
│  │    Engine    │  │    Engine     │  ...          │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
       │                     │
       ↓                     ↓
┌─────────────────────────────────────────────────────┐
│                 REPOSITORIES                         │
│  (Data Access - CRUD Operations)                    │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Crawler    │  │  Classifier   │               │
│  │  Repository  │  │  Repository   │  ...          │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
       │                     │
       ↓                     ↓
┌─────────────────────────────────────────────────────┐
│              DATABASE & MODELS                       │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Database   │  │    Models     │               │
│  │   (SQLite)   │  │ (Dataclasses) │               │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────┐
│           PERSISTENT STORAGE                         │
│            data/immigration.db                       │
└─────────────────────────────────────────────────────┘
```

---

## Data Flow by Service

### 1. Crawler Service

```
UI (Streamlit)
    │
    ↓ [Select countries, click "Start Crawl"]
CrawlerController
    │ .crawl_with_progress(countries, callbacks)
    ↓
CrawlerService
    │ .crawl_country(name, urls)
    ↓
CrawlerEngine
    │ .crawl_country(name, urls)
    │     ├─ Fetch URLs
    │     ├─ Parse HTML
    │     ├─ Extract data
    │     └─ Create CrawledPage model
    ↓
CrawlerRepository
    │ .save_page(page)
    ↓
Database
    │ .save_crawled_page(...)
    ↓
SQLite (immigration.db)
    └─ crawled_pages table
```

### 2. Classifier Service

```
UI (Streamlit)
    │
    ↓ [Click "Classify Pages"]
ClassifierController
    │ .classify_with_progress(callbacks)
    ↓
ClassifierService
    │ .classify_country(country)
    ↓
ClassifierEngine
    │ .classify_pages(country)
    │     ├─ Get pages from repo
    │     ├─ Extract visa info (LLM)
    │     ├─ Create Visa model
    │     └─ Save via repo
    ↓
ClassifierRepository
    │ .get_pages(country)
    │ .save_visa(visa)
    ↓
Database
    │ .get_pages() → CrawledPage models
    │ .save_visa(...) → Visa record
    ↓
SQLite (immigration.db)
    ├─ crawled_pages table (read)
    └─ visas table (write)
```

### 3. Matcher Service

```
UI (Streamlit)
    │
    ↓ [Enter profile, click "Match"]
MatcherController
    │ .match_with_progress(profile, callbacks)
    ↓
MatcherService
    │ .match_user(profile)
    ↓
MatcherEngine
    │ .match_user_to_visas(profile)
    │     ├─ Get visas from repo
    │     ├─ Calculate scores
    │     ├─ Identify gaps
    │     └─ Rank results
    ↓
MatcherRepository
    │ .get_visas()
    ↓
Database
    │ .get_visas() → Visa models
    ↓
SQLite (immigration.db)
    └─ visas table (read)
```

### 4. Assistant Service

```
UI (Streamlit)
    │
    ↓ [Ask question]
AssistantController
    │ .chat(question, callbacks)
    ↓
AssistantService
    │ .ask(question, profile)
    ↓
AssistantEngine
    │ .ask(question, profile)
    │     ├─ Retrieve relevant visas
    │     ├─ Format context
    │     ├─ Call LLM
    │     └─ Return answer
    ↓
AssistantRepository
    │ .get_visas()
    ↓
Database
    │ .get_visas() → Visa models
    ↓
SQLite (immigration.db)
    └─ visas table (read)
```

---

## Service Interaction Map

```
┌─────────────────────────────────────────────────────┐
│                   SERVICES                           │
│                                                      │
│  ┌──────────┐    ┌───────────┐                     │
│  │ Crawler  │───→│Classifier │                     │
│  │          │    │           │                     │
│  │ Collects │    │ Extracts  │                     │
│  │  pages   │    │   visas   │                     │
│  └──────────┘    └─────┬─────┘                     │
│                        │                            │
│                        ↓                            │
│                   ┌─────────┐                       │
│                   │ Matcher │                       │
│                   │         │                       │
│                   │ Matches │                       │
│                   │  users  │                       │
│                   └────┬────┘                       │
│                        │                            │
│                        ↓                            │
│                  ┌───────────┐                      │
│                  │ Assistant │                      │
│                  │           │                      │
│                  │  Answers  │                      │
│                  │ questions │                      │
│                  └───────────┘                      │
└─────────────────────────────────────────────────────┘

Pipeline Flow:
1. Crawler → collects pages
2. Classifier → extracts visas from pages
3. Matcher → matches visas to users
4. Assistant → answers questions about visas
```

---

## File Structure Map

```
immigration-crawler-demo/
│
├── app.py                       ← Main entry point
│
├── pages/                       ← UI Pages (Streamlit)
│   ├── 1_Crawler.py            ← Uses CrawlerController
│   ├── 2_Classifier.py         ← Uses ClassifierController
│   ├── 3_Matcher.py            ← Uses MatcherController
│   ├── 4_Assistant.py          ← Uses AssistantController
│   ├── 5_Settings.py
│   ├── 6_Database.py
│   └── 7_Global_Config.py
│
├── services/                    ← Backend Services
│   │
│   ├── crawler/
│   │   ├── repository.py       ← Data access
│   │   ├── engine.py           ← Business logic
│   │   ├── interface.py        ← Service + Controller
│   │   ├── config.yaml         ← Configuration
│   │   └── components/         ← UI components
│   │
│   ├── classifier/
│   │   ├── repository.py       ← Data access
│   │   ├── engine.py           ← LLM extraction
│   │   ├── interface.py        ← Service + Controller
│   │   ├── extractor.py        ← Pattern fallback
│   │   └── config.yaml
│   │
│   ├── matcher/
│   │   ├── repository.py       ← Data access
│   │   ├── engine.py           ← Matching logic
│   │   ├── interface.py        ← Service + Controller
│   │   ├── scorer.py           ← Scoring helper
│   │   ├── ranker.py           ← Ranking helper
│   │   └── config.yaml
│   │
│   └── assistant/
│       ├── repository.py       ← Data access
│       ├── engine.py           ← Q&A logic
│       ├── interface.py        ← Service + Controller
│       ├── retriever.py        ← Context retrieval
│       ├── enhanced_retriever.py
│       ├── llm_client.py       ← LLM communication
│       └── config.yaml
│
├── shared/                      ← Common Utilities
│   ├── models.py               ← Data structures (Visa, Page, etc.)
│   ├── database.py             ← SQLite operations
│   ├── config_manager.py       ← Configuration
│   ├── logger.py               ← Logging
│   └── components.py           ← Shared UI components
│
├── data/
│   └── immigration.db          ← SQLite database
│
├── legacy/                      ← Old code (reference)
│   ├── README.md
│   ├── crawler/
│   ├── classifier/
│   ├── matcher/
│   └── assistant/
│
└── docs/
    ├── SYSTEM_DEVELOPMENT_GUIDE.md  ← How to build features
    ├── SYSTEM_MAP.md                ← This file
    ├── SERVICE_ARCHITECTURE.md      ← Architecture details
    ├── STRUCTURE.md                 ← Project structure
    └── REFACTORING_COMPLETE.md      ← What was done
```

---

## Database Schema Map

```
immigration.db
│
├── crawled_pages               ← Raw scraped content
│   ├── id (PK)
│   ├── url
│   ├── country
│   ├── title
│   ├── content
│   ├── metadata (JSON)
│   ├── crawled_at
│   ├── version
│   └── is_latest
│
├── visas                       ← Structured visa data
│   ├── id (PK)
│   ├── visa_type
│   ├── country
│   ├── category
│   ├── requirements (JSON)
│   ├── fees (JSON)
│   ├── processing_time
│   ├── documents_required (JSON)
│   ├── source_urls (JSON)
│   ├── version
│   ├── is_latest
│   └── created_at
│
├── clients                     ← User profiles
│   ├── id (PK)
│   ├── name
│   ├── email
│   ├── nationality
│   ├── profile (JSON)
│   └── created_at
│
├── eligibility_checks          ← Audit trail
│   ├── id (PK)
│   ├── client_id (FK)
│   ├── visa_id (FK)
│   ├── score
│   ├── eligible
│   ├── gaps (JSON)
│   └── check_date
│
├── embeddings                  ← For semantic search
│   ├── id (PK)
│   ├── visa_id (FK)
│   ├── embedding (BLOB)
│   ├── model_name
│   └── indexed_at
│
└── settings                    ← Configuration
    ├── key (PK)
    ├── value
    ├── type
    └── updated_at
```

---

## Configuration Hierarchy

```
┌─────────────────────────────────────────┐
│  1. Environment Variables (.env)         │
│     - API_KEY=xxx                        │
│     - LLM_MODEL=xxx                      │
└───────────────┬─────────────────────────┘
                │ Override ↓
┌─────────────────────────────────────────┐
│  2. Database Settings                    │
│     - settings table                     │
│     - UI editable                        │
└───────────────┬─────────────────────────┘
                │ Override ↓
┌─────────────────────────────────────────┐
│  3. Service Configs (YAML)               │
│     - services/*/config.yaml             │
│     - Service-specific settings          │
└───────────────┬─────────────────────────┘
                │ Override ↓
┌─────────────────────────────────────────┐
│  4. Runtime Parameters                   │
│     - UI inputs                          │
│     - Function arguments                 │
└─────────────────────────────────────────┘

Priority: 4 > 3 > 2 > 1
(Runtime overrides everything)
```

---

## Component Dependency Graph

```
┌─────────────────────────────────────────────────────┐
│                   UI Pages                           │
└────────┬───────────────────────────────────┬────────┘
         │                                   │
         ↓                                   ↓
┌──────────────────┐              ┌──────────────────┐
│   Controllers    │              │   Services       │
└────────┬─────────┘              └────────┬─────────┘
         │                                  │
         └───────────────┬──────────────────┘
                         ↓
                ┌──────────────────┐
                │     Engines      │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │   Repositories   │
                └────────┬─────────┘
                         ↓
         ┌───────────────┴───────────────┐
         │                               │
         ↓                               ↓
┌──────────────────┐          ┌──────────────────┐
│    Database      │          │     Models       │
└──────────────────┘          └──────────────────┘
         │
         ↓
┌──────────────────┐
│  immigration.db  │
└──────────────────┘
```

---

## Request Flow Example

### Example: User Asks "What are Australia work visa requirements?"

```
1. User types question in Assistant UI
   └─→ pages/4_Assistant.py

2. UI calls AssistantController
   └─→ controller.chat(question, callbacks)

3. Controller validates and calls Service
   └─→ service.ask(question)

4. Service calls Engine
   └─→ engine.ask(question)

5. Engine calls Retriever to get context
   └─→ retriever.retrieve_relevant_visas("Australia work visa")

6. Retriever calls Repository
   └─→ repo.get_visas_as_dicts(country="Australia")

7. Repository calls Database
   └─→ db.get_visas(country="Australia")

8. Database queries SQLite
   └─→ SELECT * FROM visas WHERE country='Australia'

9. Data flows back up:
   SQLite → Database → Repository → Retriever → Engine

10. Engine formats context and calls LLM
    └─→ llm_client.chat([...])

11. LLM returns answer

12. Answer flows back:
    Engine → Service → Controller → UI

13. UI displays answer to user
```

---

## Summary

### Key Points

1. **Layered Architecture** - Each layer has specific responsibility
2. **Data Flows Down** - UI → Controller → Service → Engine → Repository → Database
3. **Results Flow Up** - Database → Repository → Engine → Service → Controller → UI
4. **Single Source of Truth** - SQLite database (immigration.db)
5. **Consistent Pattern** - All services follow same structure

### Navigation Tips

- **Want to add feature?** → Start with SYSTEM_DEVELOPMENT_GUIDE.md
- **Want to understand flow?** → Use this SYSTEM_MAP.md
- **Want to see code?** → Look at services/crawler/ (complete example)
- **Want architecture details?** → Read SERVICE_ARCHITECTURE.md
- **Want file locations?** → Check STRUCTURE.md

### Quick Reference

| Question | Answer |
|----------|--------|
| Where is business logic? | `services/*/engine.py` |
| Where is data access? | `services/*/repository.py` |
| Where are APIs? | `services/*/interface.py` |
| Where are data models? | `shared/models.py` |
| Where is database code? | `shared/database.py` |
| Where is UI? | `pages/*.py` |
| Where is old code? | `legacy/` (don't use) |

---

This map shows the complete system architecture and data flows. Use it as reference when building new features or debugging issues.
