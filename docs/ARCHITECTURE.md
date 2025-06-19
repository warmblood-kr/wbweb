# wbweb Architecture

## Design Principles

1. **Minimal Dependencies**: Built on Starlette + SQLAlchemy core
2. **Clean Separation**: Generic framework vs business logic
3. **Django-inspired**: Familiar patterns for Python developers
4. **Modern Async**: Full async/await support
5. **Content Negotiation**: Automatic API/UI client handling

## Proposed Package Structure

```
wbweb/
├── __init__.py              # Public API exports
├── core/
│   ├── __init__.py
│   ├── web/
│   │   ├── __init__.py
│   │   ├── decorators.py    # @content_negotiation decorator
│   │   ├── negotiation.py   # ContentNegotiator class
│   │   └── exceptions.py    # Generic error handling
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── hiccup.py        # HiccupRenderer main class
│   │   └── renderers.py     # Base renderer strategy classes
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py          # Base model with manager metaclass
│   │   ├── managers.py      # Django-style Manager class
│   │   └── config.py        # Database configuration
│   └── settings.py          # Generic settings system
└── tests/
    ├── test_web/
    ├── test_templates/
    ├── test_database/
    └── test_settings/
```

## Core Components

### Web Layer
- **ContentNegotiator**: Detects API vs UI clients via Accept headers
- **@content_negotiation**: Decorator for automatic response formatting
- **Generic exceptions**: Error handling with content negotiation support

### Template System
- **HiccupRenderer**: Converts Python data structures to HTML
- **Renderer Strategy**: Base classes for different output formats (UI, API, etc.)

### Database Layer
- **Django-style Managers**: Familiar `.objects.create()`, `.get()`, `.filter()` patterns
- **Base Model**: SQLAlchemy model with manager metaclass
- **Async Support**: Full async/await compatibility

### Settings System
- **Environment Variables**: Automatic env var loading
- **External Config**: JSON/YAML configuration file support
- **AWS Parameter Store**: Cloud configuration integration

## Migration Strategy

### Phase 1: Extract Template System (Least Coupled)
- HiccupRenderer has zero dependencies on business logic
- Can be extracted and tested independently
- Provides immediate value for other projects

### Phase 2: Extract Database Layer
- Manager pattern is generic and reusable
- Minimal cleanup needed for wbgpt-specific references
- Critical for most web applications

### Phase 3: Extract Web Layer
- Content negotiation is framework core
- Some minor cleanup needed for business exceptions
- Enables full framework functionality

### Phase 4: Extract Settings System
- Generic configuration management
- May need some wbgpt-specific setting removal
- Completes the framework foundation

## Public API Design

```python
# Main imports users will use
from wbweb import HiccupRenderer, ContentNegotiator
from wbweb.core.web import content_negotiation
from wbweb.core.database import BaseModel, Manager
from wbweb.core.settings import Settings

# Framework integration
from wbweb import create_app  # Future: full app factory
```

## Dependencies

### Required
- `starlette` - Web framework base
- `sqlalchemy[asyncio]` - ORM with async support
- `aiosqlite` - Async SQLite driver

### Optional
- `alembic` - Database migrations
- `httpx` - HTTP client for external integrations