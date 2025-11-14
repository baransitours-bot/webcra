# 🏗️ Universal Immigration Crawler - Architecture

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Immigration Websites                     │
│  (Australia, Canada, UK, Germany, UAE, etc.)                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    CRAWLER LAYER                             │
│  • Scrapy Spiders (structured sites)                        │
│  • Playwright (JavaScript-heavy sites)                      │
│  • Rate limiting & robots.txt compliance                    │
│  • Multi-language support                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATA PROCESSING LAYER                        │
│  • Content extraction & cleaning                            │
│  • Metadata enrichment (country, visa type, tags)          │
│  • Breadcrumb & navigation analysis                         │
│  • PDF text extraction                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
│  • MongoDB (raw + processed data)                           │
│  • PostgreSQL (structured queries)                          │
│  • ElasticSearch (full-text search)                         │
│  • Vector DB (embeddings for semantic search)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM LAYER                               │
│  • Context builder (retrieve relevant pages)                │
│  • Prompt engineering (structured queries)                  │
│  • OpenAI / Anthropic / Local LLMs                          │
│  • Response validation & citation                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                           │
│  • REST API (Next.js API routes)                            │
│  • WebSocket (real-time chat)                               │
│  • Authentication & user sessions                           │
│  • Rate limiting & caching                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER                             │
│  • Next.js / React                                           │
│  • Search & filter interface                                │
│  • AI chatbot widget                                         │
│  • Visa comparison tools                                    │
│  • User profiles & saved searches                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Components

### 1. Universal Crawler

**Purpose**: Scrape immigration data from any government or official source

**Features**:
- **Multi-site support**: Works with any immigration website
- **Adaptive crawling**: Handles both static HTML and JavaScript-rendered sites
- **Smart filtering**: Keywords, URL patterns, content relevance
- **Recursive exploration**: Follows internal links with depth control
- **Rate limiting**: Respects server load and robots.txt
- **Error handling**: Retry logic, timeout management

**Technologies**:
- `Scrapy`: Core crawling framework
- `Playwright`: For JavaScript-heavy sites (Canada, UK)
- `BeautifulSoup`: HTML parsing
- `requests`: Simple HTTP requests

**Configuration**:
```yaml
seed_urls:
  - url: "https://immi.homeaffairs.gov.au/..."
    country: "Australia"
    language: "en"
    priority: 1

crawl_rules:
  max_depth: 4
  max_pages_per_site: 500
  delay_between_requests: 1
  respect_robots_txt: true

filters:
  keywords: ["visa", "immigration", "permit"]
  exclude_patterns: ["/news/", "/media/"]
  min_content_length: 200
```

---

### 2. Data Model

**Page Schema**:
```json
{
  "id": "uuid",
  "url": "string",
  "source": "string",
  "country": "string",
  "language": "string",
  "title": "string",
  "breadcrumbs": ["string"],
  "content_text": "string",
  "content_html": "string",
  "depth": "integer",
  "linked_urls": ["string"],
  "attachments": [
    {
      "type": "pdf|doc|xlsx",
      "url": "string",
      "title": "string",
      "extracted_text": "string"
    }
  ],
  "tags": ["string"],
  "visa_types": ["string"],
  "requirements": ["string"],
  "eligibility_criteria": {},
  "processing_time": "string",
  "fees": {},
  "timestamp": "datetime",
  "last_updated": "datetime",
  "version": "integer"
}
```

**Advantages**:
- Flexible schema for diverse sources
- Rich metadata for filtering and search
- Version tracking for change detection
- LLM-friendly format

---

### 3. LLM Integration Architecture

**Flow**:
```
User Query → Query Analysis → Context Retrieval → Prompt Building → LLM → Response
```

**Query Analysis**:
- Extract: country, visa type, user profile (age, education, profession)
- Identify intent: eligibility check, requirements, application process
- Determine language preference

**Context Retrieval**:
```python
def retrieve_context(query):
    # 1. Keyword search
    keyword_results = elasticsearch.search(query.keywords)
    
    # 2. Semantic search
    query_embedding = embed(query.text)
    semantic_results = vector_db.search(query_embedding, k=10)
    
    # 3. Hybrid ranking
    combined_results = rank_fusion(keyword_results, semantic_results)
    
    # 4. Build context
    context = build_context_from_pages(combined_results[:5])
    
    return context
```

**Prompt Template**:
```python
PROMPT = """You are an immigration visa expert. Answer based on official sources.

CONTEXT:
{context_from_crawled_pages}

USER PROFILE:
- Age: {age}
- Education: {education}
- Nationality: {nationality}
- Profession: {profession}

QUESTION:
{user_question}

INSTRUCTIONS:
1. Provide a clear, direct answer
2. Cite specific sources with URLs
3. List eligibility requirements
4. Mention application process if relevant
5. Note any restrictions or conditions
6. If unsure, say so explicitly

ANSWER:
"""
```

**Response Structure**:
```json
{
  "answer": "string",
  "eligibility": "eligible|not_eligible|uncertain",
  "confidence": 0.95,
  "sources": [
    {
      "url": "string",
      "title": "string",
      "relevance": 0.8
    }
  ],
  "requirements": ["string"],
  "next_steps": ["string"],
  "warnings": ["string"]
}
```

---

### 4. Indexing & Search

**ElasticSearch Schema**:
```json
{
  "mappings": {
    "properties": {
      "content": {"type": "text", "analyzer": "english"},
      "title": {"type": "text", "boost": 2.0},
      "country": {"type": "keyword"},
      "visa_types": {"type": "keyword"},
      "tags": {"type": "keyword"},
      "language": {"type": "keyword"},
      "timestamp": {"type": "date"}
    }
  }
}
```

**Vector Database** (Pinecone / Weaviate):
- Store embeddings of page content
- Enable semantic search
- Support similarity queries
- Use for: "Find visas similar to Australia Skilled 189"

---

### 5. Change Detection

**Strategy**:
1. Crawl sites on schedule (daily/weekly)
2. Compare with previous version
3. Detect changes in:
   - Requirements
   - Processing times
   - Fees
   - Eligibility criteria
4. Notify users with active searches
5. Update LLM knowledge base

**Implementation**:
```python
def detect_changes(old_page, new_page):
    changes = {
        'title_changed': old_page.title != new_page.title,
        'content_diff': compute_diff(old_page.content, new_page.content),
        'requirements_changed': set(old_page.requirements) != set(new_page.requirements),
        'fees_changed': old_page.fees != new_page.fees
    }
    
    if any(changes.values()):
        notify_affected_users(old_page, changes)
        update_vector_embeddings(new_page)
    
    return changes
```

---

### 6. Public Portal Features

**Core Pages**:
- `/` - Home with country selector
- `/countries/[country]` - Country overview
- `/visas/[country]/[visa-type]` - Detailed visa page
- `/eligibility-checker` - AI-powered eligibility tool
- `/compare` - Compare visa options
- `/chat` - AI assistant

**AI Chatbot**:
- Embedded on every page
- Context-aware (knows current page)
- Maintains conversation history
- Provides citations
- Suggests related visas

**User Features**:
- Save favorite visas
- Track applications
- Get change notifications
- Export reports

---

## 🔧 Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
└───────────┬─────────────────────────────────────────────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼────┐      ┌───▼────┐
│ Web    │      │ Web    │
│ Server │      │ Server │
│ (Next) │      │ (Next) │
└───┬────┘      └───┬────┘
    │               │
    └───────┬───────┘
            │
    ┌───────▼───────────────────────────────┐
    │          API Gateway                   │
    └───┬────────────────────────────────────┘
        │
    ┌───┴──────────────────┬──────────────┐
    │                      │              │
┌───▼────┐          ┌──────▼────┐   ┌────▼─────┐
│ Crawler │          │ LLM API   │   │ Search   │
│ Service │          │ Service   │   │ Service  │
└───┬────┘          └──────┬────┘   └────┬─────┘
    │                      │              │
    └──────────────┬───────┴──────────────┘
                   │
    ┌──────────────▼──────────────────────────┐
    │           Data Layer                     │
    │  • PostgreSQL (structured)              │
    │  • MongoDB (documents)                  │
    │  • ElasticSearch (search)               │
    │  • Pinecone (vectors)                   │
    └─────────────────────────────────────────┘
```

---

## 📊 Scalability Considerations

**Crawler**:
- Distributed crawling with Scrapy Cluster
- Queue-based job distribution (Redis/RabbitMQ)
- Horizontal scaling for multiple countries

**Storage**:
- Sharding by country for MongoDB
- Read replicas for PostgreSQL
- ElasticSearch cluster for high availability

**LLM**:
- Cache frequent queries
- Rate limiting per user
- Fallback to smaller models for simple queries
- Self-hosted models for cost optimization

**Frontend**:
- CDN for static assets
- Edge caching for country pages
- Serverless functions for API routes

---

## 🔒 Security & Privacy

- No PII collected during crawling
- GDPR compliance for user data
- API rate limiting
- Input sanitization
- Source attribution and copyright respect

---

## 📈 Monitoring & Analytics

**Metrics**:
- Crawl success rate
- Pages crawled per day
- Query response time
- LLM accuracy (via user feedback)
- User engagement

**Tools**:
- Prometheus + Grafana
- Sentry for error tracking
- PostHog for analytics

---

## 🚀 Future Enhancements

1. **Multi-language support**: Translate content on-the-fly
2. **Visual document analysis**: OCR for complex forms
3. **Personalized recommendations**: ML-based visa suggestions
4. **Community features**: User reviews, success stories
5. **Agent assistance**: Find immigration lawyers/consultants
6. **Document preparation**: Auto-fill forms based on user profile
