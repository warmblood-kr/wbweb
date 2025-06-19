# Component Mapping: wbgpt → wbweb

This document maps specific files and classes from wbgpt to their new locations in wbweb.

## File Mapping

### Template System
| wbgpt Location | wbweb Location | Status | Notes |
|---------------|----------------|--------|-------|
| `wbgpt/core/templates/hiccup.py` | `wbweb/core/templates/hiccup.py` | 📋 Pending | Clean extraction - no business logic |
| `wbgpt/core/templates/renderers.py` | `wbweb/core/templates/renderers.py` | 📋 Pending | Strategy pattern base classes |

### Web Layer
| wbgpt Location | wbweb Location | Status | Notes |
|---------------|----------------|--------|-------|
| `wbgpt/core/web/decorators.py` | `wbweb/core/web/decorators.py` | 📋 Pending | Generic content negotiation decorator |
| `wbgpt/core/web/negotiation.py` | `wbweb/core/web/negotiation.py` | 📋 Pending | ContentNegotiator class |
| `wbgpt/core/web/exceptions.py` | `wbweb/core/web/exceptions.py` | 🔧 Needs Cleanup | Remove business-specific exceptions |

### Database Layer
| wbgpt Location | wbweb Location | Status | Notes |
|---------------|----------------|--------|-------|
| `wbgpt/core/database/base.py` | `wbweb/core/database/base.py` | 📋 Pending | Generic SQLAlchemy base with managers |
| `wbgpt/core/database/managers.py` | `wbweb/core/database/managers.py` | 📋 Pending | Django-style Manager class |
| `wbgpt/core/database/config.py` | `wbweb/core/database/config.py` | 🔧 Needs Cleanup | Remove wbgpt-specific settings |

### Settings System
| wbgpt Location | wbweb Location | Status | Notes |
|---------------|----------------|--------|-------|
| `wbgpt/core/settings.py` | `wbweb/core/settings.py` | 🔧 Needs Cleanup | Remove wbgpt-specific configuration |

## Class/Function Mapping

### Template System
- `HiccupRenderer` → `wbweb.core.templates.HiccupRenderer`
- `DefaultRenderer` → `wbweb.core.templates.DefaultRenderer`
- `UIRenderer` → `wbweb.core.templates.UIRenderer`
- `ApiRenderer` → `wbweb.core.templates.ApiRenderer`

### Web Layer
- `ContentNegotiator` → `wbweb.core.web.ContentNegotiator`
- `@content_negotiation` → `wbweb.core.web.content_negotiation`

### Database Layer
- `BaseModel` → `wbweb.core.database.BaseModel`
- `Manager` → `wbweb.core.database.Manager`
- `DatabaseConfig` → `wbweb.core.database.DatabaseConfig`

### Settings System
- `Settings` → `wbweb.core.settings.Settings`

## Import Changes Required in wbgpt

After extraction, wbgpt will need these import changes:

### Before (Current)
```python
from wbgpt.core.templates.hiccup import HiccupRenderer
from wbgpt.core.web.decorators import content_negotiation
from wbgpt.core.web.negotiation import ContentNegotiator
from wbgpt.core.database.base import BaseModel
from wbgpt.core.database.managers import Manager
from wbgpt.core.settings import Settings
```

### After (Using wbweb)
```python
from wbweb.core.templates import HiccupRenderer
from wbweb.core.web import content_negotiation, ContentNegotiator
from wbweb.core.database import BaseModel, Manager
from wbweb.core.settings import Settings
```

## Cleanup Tasks

### wbgpt/core/web/exceptions.py
- Remove: `ConversationNotFound` and other domain-specific exceptions
- Keep: Generic `APIError`, `ValidationError` base classes

### wbgpt/core/database/config.py
- Remove: wbgpt-specific database settings references
- Keep: Generic database configuration patterns

### wbgpt/core/settings.py
- Remove: Chat-specific configuration keys
- Keep: Generic settings loading mechanism

## Test Migration

### Tests to Extract
- `test_content_negotiation.py` → Move to wbweb test suite
- `test_hiccup_renderer.py` → Move to wbweb test suite
- Generic database manager tests → Move to wbweb test suite

### Tests to Keep in wbgpt
- Domain-specific integration tests
- Business logic tests
- Application-level tests

## Dependencies After Extraction

### wbweb Dependencies
```toml
dependencies = [
    "starlette",
    "sqlalchemy[asyncio]",
    "aiosqlite",
]
```

### wbgpt Dependencies (Updated)
```toml
dependencies = [
    "wbweb",
    "httpx",           # For LLM API calls
    "python-multipart", # Form handling
    "alembic",         # Database migrations
]
```