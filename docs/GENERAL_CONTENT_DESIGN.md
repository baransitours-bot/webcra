# General Immigration Content Extraction - Design Document

## Problem Statement

Currently, the system only extracts **structured visa data** (visa types, requirements, fees). But immigration websites contain much more valuable information:
- **Process guides** ("How to apply for immigration")
- **Step-by-step instructions** ("Getting started with Express Entry")
- **General requirements** ("Documents you need")
- **FAQs** ("Can I bring my family?")
- **Timeline information** ("How long does it take?")
- **Eligibility overviews** ("Am I eligible for immigration?")

**The Goal:** Extract and store this general immigration knowledge so the Assistant can answer broader questions like:
- "How do I start immigrating to Canada?"
- "What documents do I need to prepare?"
- "What are the general steps for UK immigration?"
- "Can I work while my application is being processed?"

## Proposed Solution

### 1. New Database Table: `general_content`

```sql
CREATE TABLE general_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,  -- guide, faq, process, requirements, timeline, overview
    summary TEXT,                 -- LLM-generated summary
    key_points JSON,              -- List of main points
    content TEXT,                 -- Full content
    source_url TEXT,
    metadata JSON,                -- {audience: "skilled_workers", difficulty: "beginner", etc.}

    -- Versioning
    version INTEGER DEFAULT 1,
    is_latest INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 2. New Model: `GeneralContent`

```python
@dataclass
class GeneralContent:
    """General immigration information (not visa-specific)"""
    country: str
    title: str
    content_type: str  # guide, faq, process, requirements, timeline, overview
    summary: str
    key_points: List[str]
    content: str
    source_url: str
    metadata: Dict = field(default_factory=dict)

    # Database fields
    id: Optional[int] = None
    version: int = 1
    created_at: Optional[str] = None
```

### 3. Enhanced Classifier: Dual-Mode Extraction

The Classifier will detect page type and extract accordingly:

**Mode 1: Visa Page** (current behavior)
- Extracts structured visa data
- Saves to `visas` table

**Mode 2: General Content Page** (NEW)
- Extracts general immigration information
- Saves to `general_content` table

**Detection Logic:**
```python
if page_contains_specific_visa_info():
    extract_visa_data()  # Current behavior
elif page_contains_general_immigration_info():
    extract_general_content()  # NEW behavior
else:
    skip_page()  # Not relevant
```

### 4. General Content Extraction Schema

```yaml
general_content_extraction:
  title: "Extract page title"
  content_type: "Classify as: guide|faq|process|requirements|timeline|overview"
  summary: "200-word summary of main information"
  key_points:
    - "Extract 5-10 key takeaways"
    - "Actionable information"
    - "Important facts or requirements"
  audience: "Who is this for? (skilled_workers, students, families, etc.)"
  difficulty: "beginner|intermediate|advanced"
  topics:
    - "Tags: visa, work_permit, study, pr, citizenship, etc."
```

### 5. LLM Prompt Example

```
Page Title: {title}
Country: {country}
Content: {content_sample}

This appears to be a GENERAL IMMIGRATION PAGE (not a specific visa).

Extract the following:

1. content_type: What type of content is this?
   - guide: How-to guide or instruction
   - faq: Frequently asked questions
   - process: Application or procedural steps
   - requirements: General document/eligibility requirements
   - timeline: Time expectations and deadlines
   - overview: General information or introduction

2. summary: Write a 200-word summary of the key information

3. key_points: List 5-10 main takeaways (bulleted format)
   - Focus on actionable information
   - Include important facts, deadlines, requirements
   - What would someone need to know?

4. audience: Who is this content for? (skilled_workers, students, families, general)

5. difficulty: beginner|intermediate|advanced

6. topics: Relevant tags (select from: immigration, visa, work_permit, study, pr, citizenship, family, business)

Return as JSON.
```

### 6. Workflow Changes

**Current Flow:**
```
Crawler → Classifier → Visas Table
```

**Enhanced Flow:**
```
Crawler → Enhanced Classifier → {
    If visa page    → Visas Table (structured data)
    If general page → General Content Table (guides, FAQs)
    If neither      → Skip
}
```

### 7. UI Changes

#### Classifier Page
- Add "General Content" metric showing how many general pages were extracted
- Add filter to show "Visa Pages" vs "General Pages" in Database View

#### New Tab in Classifier Results
```
Results Tab:
  - 💾 Database View
    - 📋 Visas (current)
    - 📖 General Content (NEW)
  - 🔄 Current Run
```

#### Assistant Service Enhancement
The Assistant will now have access to:
- **Visa data** (structured requirements, fees)
- **General content** (guides, FAQs, process information)

This creates a **comprehensive knowledge base** for answering all immigration questions.

### 8. Benefits

✅ **Richer context** for the Assistant
✅ **Answer broader questions** ("How do I start?" not just "What are visa requirements?")
✅ **Capture all valuable content** from government websites
✅ **Structured knowledge base** for immigration guidance
✅ **Better user experience** - one-stop information source

### 9. Example Use Cases

**Question:** "How do I immigrate to Canada?"

**Without General Content:**
- Assistant can only show visa options
- No guidance on process or steps

**With General Content:**
- Shows overview guide "Getting Started with Canadian Immigration"
- Lists step-by-step process
- Provides document checklist
- Explains timelines
- THEN shows relevant visa options

## Implementation Plan

### Phase 1: Database & Models
- [ ] Create `general_content` table
- [ ] Add `GeneralContent` model to `shared/models.py`
- [ ] Add database methods: `save_general_content()`, `get_general_content()`

### Phase 2: Classifier Enhancement
- [ ] Create general content extraction schema
- [ ] Modify Classifier engine to detect page type
- [ ] Implement dual-mode extraction (visa vs general)
- [ ] Test with sample pages

### Phase 3: UI Updates
- [ ] Add General Content view to Classifier Results
- [ ] Add general content metrics
- [ ] Add filtering/viewing capabilities

### Phase 4: Assistant Integration
- [ ] Modify Assistant to query both visas AND general content
- [ ] Enhance context building for LLM
- [ ] Test question answering with richer context

## Questions for You

1. **Content Types:** Are the 6 types (guide, faq, process, requirements, timeline, overview) sufficient? Any others?

2. **Priority:** Should we extract general content for ALL crawled pages, or only specific types?

3. **Workflow:** Should this be:
   - **Automatic** (Classifier does both visa + general in one pass)
   - **Separate** (Run Classifier twice: once for visas, once for general content)
   - **Optional** (Toggle to enable/disable general content extraction)

4. **Storage:** Is the proposed schema good, or would you prefer different fields?

Let me know your thoughts and I'll implement this system!
