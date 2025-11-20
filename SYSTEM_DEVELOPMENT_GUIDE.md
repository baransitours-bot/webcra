# System Development Guide

Complete instructions for building features in this system.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Principles](#development-principles)
3. [How to Build a Feature](#how-to-build-a-feature)
4. [Layer-by-Layer Guide](#layer-by-layer-guide)
5. [Common Patterns](#common-patterns)
6. [Testing Strategy](#testing-strategy)
7. [Code Standards](#code-standards)
8. [Examples](#examples)

---

## Architecture Overview

### The Engine/Fuel Pattern

```
┌─────────────────────────────────────────────────────┐
│  LAYER 4: INTERFACES                                │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │  EXTERIOR       │  │  INTERIOR       │          │
│  │  (Controller)   │  │  (Service)      │          │
│  │  - UI callbacks │  │  - Python API   │          │
│  │  - Validation   │  │  - Simple calls │          │
│  └─────────────────┘  └─────────────────┘          │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  LAYER 3: ENGINE (Business Logic)                   │
│  - Pure functions                                    │
│  - No database imports                               │
│  - No UI knowledge                                   │
│  - Uses repository for data                          │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  LAYER 2: REPOSITORY (Fuel Transport)               │
│  - Database operations                               │
│  - Model conversions                                 │
│  - No business logic                                 │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│  LAYER 1: DATA (Fuel)                               │
│  - Models (shared/models.py)                         │
│  - Database (shared/database.py)                     │
│  - Configuration                                     │
└─────────────────────────────────────────────────────┘
```

### Why This Pattern?

| Benefit | Description |
|---------|-------------|
| **Testability** | Each layer can be tested independently |
| **Maintainability** | Change one layer without affecting others |
| **Reusability** | Same engine, multiple interfaces |
| **Clarity** | Each file has one clear purpose |

---

## Development Principles

### 1. Separation of Concerns

**DO:**
- One responsibility per file
- Engine = logic only
- Repository = data only
- Interface = API only

**DON'T:**
- Mix database calls with business logic
- Put UI code in engine
- Put business logic in repository

### 2. Dependency Direction

Always flows DOWN the layers:

```
Interface → Engine → Repository → Database
```

**NEVER:**
```
Repository → Engine  ❌
Engine → Interface   ❌
```

### 3. Data Flow

```
1. Interface receives request
2. Interface calls Engine method
3. Engine uses Repository to get data
4. Engine processes data
5. Engine uses Repository to save results
6. Engine returns results to Interface
7. Interface formats for user
```

---

## How to Build a Feature

### Step-by-Step Process

#### 1. Define the Data (FUEL)

Start with `shared/models.py`:

```python
@dataclass
class MyNewModel:
    """Clear description"""
    # Required fields
    field1: str
    field2: int

    # Optional fields
    field3: str = ""

    @classmethod
    def from_db_row(cls, row: dict) -> 'MyNewModel':
        """Convert database row to model"""
        return cls(
            field1=row['field1'],
            field2=row['field2']
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'field1': self.field1,
            'field2': self.field2
        }
```

**Checklist:**
- [ ] Add to `shared/models.py`
- [ ] Include docstrings
- [ ] Add `from_db_row()` method
- [ ] Add `to_dict()` method
- [ ] Add helper properties if needed

#### 2. Update Database (FUEL STORAGE)

Update `shared/database.py`:

```python
def save_my_data(self, data: MyNewModel) -> int:
    """Save data with versioning"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO my_table (field1, field2)
            VALUES (?, ?)
        """, (data.field1, data.field2))
        return cursor.lastrowid

def get_my_data(self) -> List[MyNewModel]:
    """Get data as models"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM my_table")
        rows = [dict(row) for row in cursor.fetchall()]
        return [MyNewModel.from_db_row(r) for r in rows]
```

**Checklist:**
- [ ] Create table if needed
- [ ] Add save method
- [ ] Add get method
- [ ] Use versioning if applicable
- [ ] Return model objects

#### 3. Create Repository (FUEL TRANSPORT)

Create `services/myservice/repository.py`:

```python
"""
MyService Repository - FUEL TRANSPORT LAYER

Handles data flow for myservice.
"""

from typing import List, Optional
from shared.database import Database
from shared.models import MyNewModel


class MyServiceRepository:
    """
    Data access layer for myservice.

    Responsibilities:
    - Fetch data from database
    - Save results to database
    - Convert between DB and models
    """

    def __init__(self):
        self.db = Database()

    def get_data(self, filter_param: Optional[str] = None) -> List[MyNewModel]:
        """
        Get data from database.

        Args:
            filter_param: Optional filter

        Returns:
            List of MyNewModel objects
        """
        # Use database methods
        data = self.db.get_my_data()

        # Apply filters if needed
        if filter_param:
            data = [d for d in data if d.field1 == filter_param]

        return data

    def save_result(self, result: MyNewModel) -> int:
        """Save result to database"""
        return self.db.save_my_data(result)
```

**Checklist:**
- [ ] Import Database and Models
- [ ] Only data access code
- [ ] No business logic
- [ ] Clear docstrings
- [ ] Type hints
- [ ] Return models, not dicts

#### 4. Create Engine (BUSINESS LOGIC)

Create `services/myservice/engine.py`:

```python
"""
MyService Engine - CORE LOGIC LAYER

Core business logic for myservice.
Pure logic - no database access.
"""

from typing import List, Dict
from shared.models import MyNewModel
from shared.logger import setup_logger
from services.myservice.repository import MyServiceRepository


class MyServiceEngine:
    """
    Core business logic.

    Responsibilities:
    - Process data
    - Apply algorithms
    - Coordinate operations

    Does NOT:
    - Access database directly
    - Know about UI
    - Handle configuration loading
    """

    def __init__(self, config: dict, repository: MyServiceRepository):
        """
        Initialize engine.

        Args:
            config: Service configuration
            repository: Data access layer
        """
        self.config = config
        self.repo = repository
        self.logger = setup_logger('myservice_engine')

    def process_data(self, input_param: str) -> Dict:
        """
        Main processing method.

        Args:
            input_param: Input parameter

        Returns:
            Processing results
        """
        # Step 1: Get data via repository
        data = self.repo.get_data(input_param)

        if not data:
            self.logger.warning("No data found")
            return {'status': 'no_data'}

        # Step 2: Process (business logic)
        results = []
        for item in data:
            processed = self._process_single_item(item)
            results.append(processed)

            # Save via repository
            self.repo.save_result(processed)

        # Step 3: Return results
        return {
            'status': 'success',
            'processed': len(results)
        }

    def _process_single_item(self, item: MyNewModel) -> MyNewModel:
        """
        Process a single item.

        Private method - internal logic.
        """
        # Your business logic here
        item.field2 = item.field2 * 2
        return item
```

**Checklist:**
- [ ] Import repository and models
- [ ] NO database imports
- [ ] Use repository for all data access
- [ ] Pure business logic
- [ ] Clear method names
- [ ] Docstrings explain what, not how
- [ ] Private methods start with `_`

#### 5. Create Interfaces (APIs)

Create `services/myservice/interface.py`:

```python
"""
MyService Interface - INTERACTION LAYER

INTERIOR: Python API for service-to-service
EXTERIOR: UI Controller with callbacks
"""

import yaml
from typing import List, Dict, Callable, Optional
from pathlib import Path

from services.myservice.engine import MyServiceEngine
from services.myservice.repository import MyServiceRepository
from shared.logger import setup_logger


class MyService:
    """
    INTERIOR Interface: Service-to-Service API

    Clean Python API for other services.
    """

    def __init__(self, config_path: str = 'services/myservice/config.yaml'):
        """Initialize service"""
        self.logger = setup_logger('myservice')

        # Load config
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()

        # Initialize layers
        self.repo = MyServiceRepository()
        self.engine = MyServiceEngine(self.config, self.repo)

    def process(self, input_param: str) -> Dict:
        """
        Process data.

        Args:
            input_param: Input parameter

        Returns:
            Results dictionary
        """
        return self.engine.process_data(input_param)

    def get_statistics(self) -> Dict:
        """Get statistics"""
        data = self.repo.get_data()
        return {
            'total': len(data)
        }

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'setting1': 'value1',
            'setting2': 42
        }


class MyServiceController:
    """
    EXTERIOR Interface: UI Controller

    User-friendly API with callbacks for UI.
    """

    def __init__(self, config_path: str = 'services/myservice/config.yaml'):
        """Initialize controller"""
        self.service = MyService(config_path)
        self.logger = setup_logger('myservice_controller')

    def process_with_progress(
        self,
        input_param: str,
        on_start: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> Dict:
        """
        Process with progress callbacks.

        Args:
            input_param: Input parameter
            on_start: Called when starting
            on_progress: Called during processing (current, total)
            on_complete: Called when complete (results)
            on_error: Called on error (error_message)

        Returns:
            Results dictionary
        """
        try:
            # Notify start
            if on_start:
                on_start()

            # Process
            result = self.service.process(input_param)

            # Notify complete
            if on_complete:
                on_complete(result)

            return result

        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            if on_error:
                on_error(str(e))
            raise

    def validate_input(self, input_param: str) -> Dict:
        """
        Validate input.

        Returns validation result with errors.
        """
        errors = []

        if not input_param:
            errors.append("Input parameter is required")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


# Convenience functions
def process(input_param: str) -> Dict:
    """Quick function to process data"""
    service = MyService()
    return service.process(input_param)
```

**Checklist:**
- [ ] Two classes: Service + Controller
- [ ] Service = simple API
- [ ] Controller = UI-friendly with callbacks
- [ ] Both use engine + repository
- [ ] Convenience functions at bottom
- [ ] Error handling
- [ ] Validation in Controller

#### 6. Create Configuration

Create `services/myservice/config.yaml`:

```yaml
# MyService Configuration

# Feature settings
feature:
  enabled: true
  max_items: 100

# Processing settings
processing:
  batch_size: 10
  timeout: 30

# Thresholds
thresholds:
  min_score: 0.5
  max_errors: 5
```

**Checklist:**
- [ ] YAML format
- [ ] Clear sections
- [ ] Comments explain purpose
- [ ] Default values that work

#### 7. Create UI Page

Create `pages/X_MyService.py`:

```python
"""
MyService Page
"""

import streamlit as st
from services.myservice.interface import MyServiceController

st.set_page_config(
    page_title="MyService",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 MyService")
st.markdown("Description of what this service does")

# Input
input_param = st.text_input("Enter parameter")

# Process button
if st.button("▶️ Process", type="primary"):
    if not input_param:
        st.error("Please enter a parameter")
    else:
        controller = MyServiceController()

        # Progress UI
        progress = st.progress(0)
        status = st.empty()

        # Callbacks
        def on_start():
            status.text("Starting...")

        def on_complete(result):
            st.success(f"✅ Complete: {result['status']}")

        def on_error(error):
            st.error(f"❌ Error: {error}")

        # Process
        result = controller.process_with_progress(
            input_param,
            on_start=on_start,
            on_complete=on_complete,
            on_error=on_error
        )
```

**Checklist:**
- [ ] Use Controller (not Service)
- [ ] Use callbacks for progress
- [ ] Show errors clearly
- [ ] Validate input
- [ ] Clear UI feedback

---

## Layer-by-Layer Guide

### Layer 1: Models (FUEL)

**Purpose:** Define data structures

**File:** `shared/models.py`

**Rules:**
- Dataclasses only
- No business logic
- Include `from_db_row()` and `to_dict()`
- Clear field names
- Type hints always

**Example:**
```python
@dataclass
class VisaApplication:
    applicant_name: str
    visa_type: str
    status: str = "pending"
    submitted_at: Optional[str] = None
```

### Layer 2: Repository (FUEL TRANSPORT)

**Purpose:** Move data between DB and Engine

**File:** `services/<service>/repository.py`

**Rules:**
- Database access ONLY
- No business logic
- Return models, not dicts
- Clear method names
- Handle DB errors

**Example:**
```python
class ApplicationRepository:
    def get_pending_applications(self) -> List[VisaApplication]:
        apps = self.db.get_applications(status='pending')
        return [VisaApplication.from_db_row(a) for a in apps]
```

### Layer 3: Engine (CORE LOGIC)

**Purpose:** Business logic

**File:** `services/<service>/engine.py`

**Rules:**
- NO database imports
- Use repository for ALL data
- Pure functions when possible
- Log important steps
- Return simple types

**Example:**
```python
class ApplicationEngine:
    def process_application(self, app_id: int) -> Dict:
        app = self.repo.get_application(app_id)

        if self._is_valid(app):
            app.status = "approved"
            self.repo.save_application(app)
            return {'status': 'approved'}

        return {'status': 'rejected'}
```

### Layer 4a: Service (INTERIOR)

**Purpose:** Clean Python API

**File:** `services/<service>/interface.py`

**Rules:**
- Simple method signatures
- Setup engine + repository
- Load configuration
- No callbacks
- Return data

**Example:**
```python
class ApplicationService:
    def __init__(self):
        self.repo = ApplicationRepository()
        self.engine = ApplicationEngine(config, self.repo)

    def process_application(self, app_id: int) -> Dict:
        return self.engine.process_application(app_id)
```

### Layer 4b: Controller (EXTERIOR)

**Purpose:** UI-friendly API

**File:** `services/<service>/interface.py`

**Rules:**
- Use callbacks for progress
- Validate input
- User-friendly errors
- Uses Service internally
- Format output for UI

**Example:**
```python
class ApplicationController:
    def process_with_progress(self, app_id, on_complete=None):
        result = self.service.process_application(app_id)
        if on_complete:
            on_complete(result)
        return result
```

---

## Common Patterns

### Pattern 1: Batch Processing

```python
# Engine
def process_batch(self, items: List[Item]) -> Dict:
    results = []
    errors = 0

    for item in items:
        try:
            result = self._process_single(item)
            self.repo.save_result(result)
            results.append(result)
        except Exception as e:
            self.logger.error(f"Failed: {e}")
            errors += 1

    return {
        'processed': len(results),
        'errors': errors
    }
```

### Pattern 2: Validation

```python
# Controller
def validate_input(self, data: Dict) -> Dict:
    errors = []

    if not data.get('required_field'):
        errors.append("Missing required field")

    if data.get('number_field', 0) < 0:
        errors.append("Number must be positive")

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
```

### Pattern 3: Progress Tracking

```python
# Controller
def process_with_progress(self, items, on_progress=None):
    total = len(items)

    for i, item in enumerate(items, 1):
        result = self.service.process_item(item)

        if on_progress:
            on_progress(i, total, item.name)

    return {'completed': total}
```

### Pattern 4: Error Handling

```python
# Engine
def process(self, data):
    try:
        result = self._do_processing(data)
        return {'status': 'success', 'result': result}
    except ValueError as e:
        self.logger.error(f"Validation error: {e}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        return {'status': 'error', 'message': 'Processing failed'}
```

---

## Testing Strategy

### Test Each Layer Independently

#### Test Repository (with real DB)

```python
def test_repository_save():
    repo = MyServiceRepository()
    model = MyNewModel(field1="test", field2=42)

    id = repo.save_result(model)

    assert id > 0
    retrieved = repo.get_data()
    assert len(retrieved) == 1
    assert retrieved[0].field1 == "test"
```

#### Test Engine (with mock repo)

```python
class MockRepository:
    def get_data(self):
        return [MyNewModel("test", 42)]

    def save_result(self, result):
        return 1

def test_engine_process():
    engine = MyServiceEngine(config, MockRepository())
    result = engine.process_data("test")

    assert result['status'] == 'success'
    assert result['processed'] == 1
```

#### Test Service (integration)

```python
def test_service_process():
    service = MyService()
    result = service.process("test")

    assert 'status' in result
    assert result['status'] in ['success', 'no_data']
```

---

## Code Standards

### Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Classes | PascalCase | `VisaProcessor` |
| Functions | snake_case | `process_visa()` |
| Private methods | `_snake_case` | `_validate_input()` |
| Constants | UPPER_CASE | `MAX_RETRIES` |
| Files | snake_case | `visa_processor.py` |

### Documentation

**Every module:**
```python
"""
Module Name - Purpose

Brief description of what this module does.
"""
```

**Every class:**
```python
class MyClass:
    """
    Brief description.

    Responsibilities:
    - What it does
    - What it manages

    Does NOT:
    - What it doesn't do
    """
```

**Every public method:**
```python
def my_method(self, param: str) -> Dict:
    """
    Brief description.

    Args:
        param: Description

    Returns:
        Description of return value
    """
```

### Type Hints

ALWAYS use type hints:

```python
def process_data(
    input: str,
    options: Dict = None
) -> List[Result]:
    pass
```

---

## Examples

See:
- `services/crawler/` - Complete example
- `services/classifier/` - LLM integration
- `services/matcher/` - Scoring/ranking
- `services/assistant/` - Chat/retrieval

All follow the exact same pattern!

---

## Quick Checklist

When adding a new feature:

- [ ] Define model in `shared/models.py`
- [ ] Add database methods in `shared/database.py`
- [ ] Create `repository.py` (data access only)
- [ ] Create `engine.py` (business logic only)
- [ ] Create `interface.py` (Service + Controller)
- [ ] Create `config.yaml`
- [ ] Create UI page using Controller
- [ ] Add tests for each layer
- [ ] Update documentation

---

## Summary

**Remember:**

1. **Layers flow down** - Interface → Engine → Repository → Database
2. **Each layer has ONE job** - Don't mix concerns
3. **Engine is pure** - No DB, no UI
4. **Repository is simple** - Just data access
5. **Two interfaces** - Service (simple) + Controller (UI)

This pattern makes code:
- Easy to test
- Easy to modify
- Easy to understand
- Consistent throughout

Follow this guide for ALL new features!
