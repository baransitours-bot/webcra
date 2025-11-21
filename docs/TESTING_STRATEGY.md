# Testing Strategy - Immigration Assistant System

## 🎯 Testing Philosophy

**Purpose**: Validate that this CONTEXT GENERATION SYSTEM properly feeds the LLM with relevant, accurate immigration information for tourism office operations.

**Critical Success Factors**:
1. **Data Quality**: Context must be accurate and current
2. **Retrieval Accuracy**: System finds relevant information for queries
3. **LLM Integration**: Context properly formatted for LLM consumption
4. **Architecture Compliance**: Engine/Fuel pattern followed correctly
5. **User Experience**: Tourism office staff can use the system effectively

---

## 📋 Testing Levels

### Level 1: Unit Tests (Code Quality)
**Goal**: Verify individual components work correctly in isolation

**Coverage**:
- ✅ Repository layer (database access)
- ✅ Engine layer (business logic)
- ✅ Interface layer (service + controller)
- ✅ Data models (from_db_row, to_dict)
- ✅ Configuration management
- ✅ Logging system

**Tools**: pytest with logging

### Level 2: Integration Tests (Data Flow)
**Goal**: Verify services work together correctly

**Coverage**:
- ✅ Crawler → Database (pages saved correctly)
- ✅ Classifier → Database (visas + general content extracted)
- ✅ Database → Assistant (retrieval works)
- ✅ Assistant → LLM (context formatting)
- ✅ Configuration cascade (global → service → runtime)

**Tools**: pytest with database fixtures

### Level 3: End-to-End Tests (User Workflows)
**Goal**: Verify complete user journeys work

**Coverage**:
- ✅ New tourism office staff onboarding
- ✅ Client visa inquiry workflow
- ✅ Multi-country comparison workflow
- ✅ General immigration question workflow (Phase 4)

**Tools**: pytest + manual testing

### Level 4: Manual Tests (Real-World Usage)
**Goal**: Validate system in actual tourism office scenarios

**Coverage**:
- ✅ Browser crawler bypasses bot detection
- ✅ LLM answers are accurate and helpful
- ✅ Sources are traceable to government websites
- ✅ UI is intuitive for non-technical staff

**Tools**: Streamlit UI + test scenarios

---

## 🔍 Testing Phases

### Phase A: Architecture Validation ✅ COMPLETE
**Status**: PASSED - All services follow Engine/Fuel pattern

**Tests**:
- [x] Layer 1 (DATA) structure
- [x] Layer 2-4 (Services) structure
- [x] No layer violations (engines don't import Database)
- [x] UI structure complete
- [x] Logging implemented

**Result**: 4/4 services compliant, 0 violations

### Phase B: Context Generation Testing ⏳ IN PROGRESS
**Goal**: Verify we can collect and structure context for LLM

**Tests**:
1. **Crawler Tests**:
   - [ ] Simple crawler extracts relevant pages
   - [ ] Browser crawler bypasses bot detection (403 errors)
   - [ ] Keyword filtering works correctly
   - [ ] Link extraction follows same-domain rule
   - [ ] Rate limiting prevents server overload

2. **Classifier Tests**:
   - [ ] Visa extraction works for all countries
   - [ ] General content extraction works (Phase 4)
   - [ ] Dual extraction doesn't interfere
   - [ ] LLM extraction prompts are country-agnostic
   - [ ] Structured data is valid (all required fields)

3. **Database Tests**:
   - [ ] Versioning works (is_latest flag)
   - [ ] Models serialize/deserialize correctly
   - [ ] Repository returns models, not dicts
   - [ ] Counts are accurate

### Phase C: Context Retrieval Testing ⏳ NEXT
**Goal**: Verify we can find relevant context for queries

**Tests**:
1. **Retrieval Tests**:
   - [ ] Keyword matching finds relevant visas
   - [ ] Keyword matching finds relevant general content
   - [ ] retrieve_all_context returns both types
   - [ ] Context scoring ranks by relevance
   - [ ] Max limits are respected (max_visas, max_general_content)

2. **Context Formatting Tests**:
   - [ ] format_context_for_llm includes both sections
   - [ ] Visa section properly formatted
   - [ ] General content section properly formatted
   - [ ] Source URLs preserved
   - [ ] Country information included

### Phase D: LLM Integration Testing ⏳ PENDING
**Goal**: Verify LLM receives context and generates quality answers

**Tests**:
1. **LLM Client Tests**:
   - [ ] API key loads correctly (.env → database → config)
   - [ ] OpenRouter client works
   - [ ] OpenAI client works (if configured)
   - [ ] Error handling for API failures
   - [ ] Token limit handling

2. **Assistant Tests**:
   - [ ] Visa queries get relevant answers
   - [ ] General content queries get relevant answers
   - [ ] Mixed queries use both context types
   - [ ] Sources are properly extracted
   - [ ] Source types are labeled (visa vs general)

3. **Answer Quality Tests** (Manual):
   - [ ] Answers are factually accurate
   - [ ] Answers reference provided context
   - [ ] Answers don't hallucinate information
   - [ ] Answers are appropriate for tourism office staff

### Phase E: End-to-End Workflow Testing ⏳ PENDING
**Goal**: Verify complete user workflows work correctly

**Tests**:
1. **Tourism Office Workflows**:
   - [ ] Staff member asks about work visas → Gets comprehensive answer
   - [ ] Staff member asks about healthcare → Gets general content answer
   - [ ] Staff member asks about specific country → Gets country-filtered context
   - [ ] Staff member views sources → Can trace to government sites

2. **Data Refresh Workflows**:
   - [ ] Monthly re-crawl updates context
   - [ ] Versioning preserves history
   - [ ] Classifier re-extraction updates structured data
   - [ ] Assistant uses latest data (is_latest=1)

---

## 🔧 Testing Infrastructure

### Enhanced Test Runner with Logging

**Features**:
1. **Structured logging** - All test output logged to file
2. **Test classification** - Unit/Integration/E2E/Manual
3. **Failure tracking** - Failed tests logged with stack traces
4. **Performance metrics** - Test execution time
5. **Coverage reports** - Which services/layers tested

**Usage**:
```bash
# Run all automated tests with logging
python run_tests.py --all --log-level DEBUG

# Run specific test suite
python run_tests.py --suite unit --log-level INFO

# Run with coverage report
python run_tests.py --all --coverage

# Run manual test scenarios
python run_tests.py --manual --scenario "tourism-office-workflow"
```

### Test Database

**Approach**: Use separate test database to avoid polluting production data

```python
# In test setup:
import os
os.environ['DATABASE_PATH'] = 'data/test_immigration.db'

from shared.database import Database
db = Database()

# In test teardown:
# Clean up test database or restore from backup
```

### Logging Configuration

**Test logging setup**:
```python
from shared.logger import setup_logger

# Create test logger with file output
test_logger = setup_logger(
    'test_runner',
    log_file='logs/test_run_{timestamp}.log',
    level='DEBUG'
)

# Log test start
test_logger.info("=" * 60)
test_logger.info(f"Starting test: {test_name}")
test_logger.info("=" * 60)

# Log test result
test_logger.info(f"Test {test_name}: {'PASS' if passed else 'FAIL'}")
if not passed:
    test_logger.error(f"Error: {error_message}")
    test_logger.error(f"Stack trace: {stack_trace}")
```

---

## 📝 Manual Testing Scenarios

### Scenario 1: New Tourism Office Staff Onboarding
**Goal**: Verify system is usable by non-technical staff

**Steps**:
1. Open Streamlit UI (`streamlit run app.py`)
2. Navigate to Assistant page (page 4)
3. Check system status (should show "Ready" with visa/general content counts)
4. Ask question: "What work visas are available for Canada?"
5. Verify answer quality:
   - [ ] Answer is comprehensive
   - [ ] Answer cites both visas and general content
   - [ ] Sources are provided with URLs
   - [ ] Answer is in plain language (not technical)
6. Click on source URLs:
   - [ ] URLs go to government websites
   - [ ] URLs are not broken
7. Try follow-up question: "What are the requirements?"
8. Verify answer builds on context

**Success Criteria**: Staff member can get useful answers without technical knowledge

### Scenario 2: Data Collection with Browser Crawler
**Goal**: Verify browser crawler bypasses bot detection

**Steps**:
1. Navigate to Crawler page (page 1)
2. Select "Browser (Playwright)" mode
3. Select a country known to block bots (e.g., Canada, Australia)
4. Set max pages to 10
5. Click "Start Crawling"
6. Monitor progress:
   - [ ] Browser engine launches
   - [ ] Pages are crawled (not 403 errors)
   - [ ] Content is saved to database
   - [ ] Progress shows in real-time
7. Navigate to Database page (page 6)
8. Verify crawled pages are stored

**Success Criteria**: Browser crawler successfully collects pages from blocked sites

### Scenario 3: Dual Content Extraction
**Goal**: Verify classifier extracts both visas and general content

**Steps**:
1. Ensure crawled pages exist (from Scenario 2)
2. Navigate to Classifier page (page 2)
3. Select country to classify
4. Click "Start Classification"
5. Monitor extraction:
   - [ ] Both visas and general content extracted
   - [ ] Statistics show counts for both types
   - [ ] No errors during extraction
6. Navigate to Database page
7. View extracted visas tab:
   - [ ] Visas are structured correctly
8. View general content tab:
   - [ ] General content has proper categories (employment, healthcare, benefits, education)

**Success Criteria**: Both content types extracted and stored correctly

### Scenario 4: Comprehensive Question Answering
**Goal**: Verify Assistant uses both content types

**Steps**:
1. Navigate to Assistant page (page 4)
2. Test visa-specific question: "What are the age requirements for skilled worker visas?"
   - [ ] Answer includes visa information
   - [ ] Sources show "🎫 Visa" badge
3. Test general content question: "What healthcare services are available for immigrants?"
   - [ ] Answer includes general content information
   - [ ] Sources show "📄 Guide" badge
4. Test mixed question: "What work opportunities and support services are available in Canada?"
   - [ ] Answer includes both visas and general content
   - [ ] Sources show both badge types
   - [ ] Answer is comprehensive

**Success Criteria**: Assistant successfully uses both context types for comprehensive answers

### Scenario 5: Multi-Country Comparison
**Goal**: Verify system can compare across countries

**Steps**:
1. Ensure multiple countries have data
2. Ask: "Compare work visa options between Canada and Australia"
3. Verify:
   - [ ] Answer discusses both countries
   - [ ] Sources include both countries
   - [ ] Comparison is balanced
4. Ask: "Which country has better healthcare for new immigrants?"
5. Verify:
   - [ ] Uses general content from both countries
   - [ ] Provides factual comparison

**Success Criteria**: System provides useful multi-country comparisons

---

## 📊 Success Metrics

### Automated Test Metrics
- **Code coverage**: Target 80%+ for core services
- **Test pass rate**: Target 100% for all automated tests
- **Test execution time**: < 5 minutes for full suite
- **Zero layer violations**: Architecture compliance

### Manual Test Metrics
- **Answer accuracy**: 90%+ factually correct (verified against sources)
- **Source traceability**: 100% of sources lead to valid URLs
- **Staff usability**: Non-technical staff can use system without training
- **Crawler success rate**: 90%+ pages successfully crawled (with browser mode)

### Production Readiness Checklist
- [ ] All automated tests pass
- [ ] All manual scenarios pass
- [ ] Architecture validation passes
- [ ] LLM integration works
- [ ] Browser crawler bypasses bot detection
- [ ] Both content types (visa + general) work
- [ ] Logging captures all important events
- [ ] Error handling prevents system crashes
- [ ] Documentation is complete

---

## 🚀 Next Steps

1. **Immediate** (Phase B):
   - Run enhanced test suite for context generation
   - Fix any failures in crawler/classifier
   - Verify browser engine works for blocked sites

2. **Short-term** (Phase C):
   - Test retrieval accuracy
   - Verify context formatting
   - Validate dual content retrieval (Phase 4)

3. **Medium-term** (Phase D):
   - Test LLM integration end-to-end
   - Manually validate answer quality
   - Optimize retrieval for better answers

4. **Long-term** (Phase E):
   - Run full E2E workflows
   - Test with real tourism office staff
   - Collect feedback and iterate
   - Prepare for production deployment

---

## 📚 References

- **Architecture**: `docs/claude-references/SERVICE_ARCHITECTURE.md`
- **Development Guide**: `docs/claude-references/SYSTEM_DEVELOPMENT_GUIDE.md`
- **Quick Reference**: `docs/claude-references/QUICK_REFERENCE.md`
- **System Context**: `CLAUDE.md`
- **Architecture Validation**: `validate_architecture.py`

---

**Remember**: This is a CONTEXT GENERATION SYSTEM for LLM. Test success means: Can the tourism office staff get accurate, helpful immigration information for their clients? Everything else is just the fuel.
