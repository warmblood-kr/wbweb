# wbweb

A lightweight, FaaS-optimized web framework with Hiccup-style HTML rendering and Django-style ORM patterns.

**By Warmblood Co., Ltd.**

## Why wbweb?

While FastAPI excels at building JSON APIs, wbweb is designed for **HTML-first web applications** that need to be lightweight and FaaS-friendly. Here's our philosophy:

### 🚀 **FaaS-Optimized & Lightweight**
- Built on **Starlette only** (no Pydantic overhead)
- Minimal dependencies for faster cold starts
- Perfect for serverless deployments (AWS Lambda, Google Cloud Functions, etc.)
- Quick startup times and small memory footprint

### 🎯 **HTML-First, Not JSON-First**
- Designed for building **interactive web applications**, not just APIs
- Excellent **HTMX integration** for dynamic, responsive UIs
- Still supports XML/JSON APIs when needed
- Content negotiation handles both HTML and API responses automatically

### 📝 **Hiccup-Style HTML Generation**
Inspired by Clojure's Hiccup, we use **Python data structures** to represent HTML:

```python
# Instead of parsing HTML templates like Jinja2...
component = ['div', {'class': 'card'}, 
    ['h1', {}, 'Welcome!'],
    ['p', {}, 'This is more efficient than string parsing']
]
```

**Why Hiccup over traditional templates?**
- **More efficient**: No string parsing or template compilation
- **More flexible**: Full Python power for logic and data transformation
- **S-expression friendly**: Natural for developers with Lisp/functional programming backgrounds
- **HTMX perfect match**: Dynamic component generation aligns perfectly with HTMX patterns

### 🗄️ **Django-Style ORM Patterns**
Familiar Active Record patterns for SQLAlchemy:

```python
# Django-style manager usage
user = await User.objects.create(name='John', email='john@example.com')
users = await User.objects.filter(active=True).all()
```

## Core Features

- **🎨 Hiccup HTML Rendering**: Python data structures → HTML
- **🔄 Content Negotiation**: Automatic API/UI client detection  
- **📊 Django-Style ORM**: Familiar SQLAlchemy patterns with async support
- **⚙️ Configurable**: Environment-aware configuration system
- **📦 Minimal Dependencies**: Only Starlette + SQLAlchemy
- **⚡ HTMX Ready**: Perfect for building interactive web applications

## Installation

```bash
pip install wbweb
```

## Quick Start

```python
from starlette.applications import Starlette
from starlette.routing import Route
from wbweb import content_negotiation, DefaultRenderer, configure_database

# Configure database
configure_database(\"sqlite:///app.db\")

# Create a renderer
class HomeRenderer(DefaultRenderer):
    def render_ui(self, **kwargs):
        return ['html', {},
            ['head', {}, ['title', {}, 'wbweb App']],
            ['body', {},
                ['h1', {}, f\"Welcome {kwargs.get('name', 'Guest')}!\"],
                ['p', {}, 'Built with wbweb framework']
            ]
        ]
    
    def render_api(self, **kwargs):
        return {'message': f\"Welcome {kwargs.get('name', 'Guest')}!\"}

# Create endpoint with content negotiation
@content_negotiation(HomeRenderer)
async def home(request):
    return {'name': 'Developer'}

# Set up Starlette app
app = Starlette(routes=[
    Route('/', home),
])
```

## Package Structure

```
wbweb/
├── core/
│   ├── templates/          # Hiccup rendering system
│   │   ├── hiccup.py      # Core HTML renderer
│   │   └── renderers.py   # Content negotiation renderers
│   ├── web/               # Web framework components  
│   │   ├── negotiation.py # Client detection
│   │   └── decorators.py  # Content negotiation decorator
│   └── database/          # Django-style ORM
│       ├── managers.py    # Active Record patterns
│       ├── base.py        # Model base classes
│       └── config.py      # Database configuration
```

## HTMX Integration

wbweb's Hiccup-style HTML generation provides **powerful Python-native HTMX integration**. Since HTML is generated from Python data structures, you can use Python variables and functions directly in `hx-` attributes:

```python
from starlette.routing import Route

# URL generation functions
def get_user_url(user_id): return f'/users/{user_id}'
def get_api_url(endpoint): return f'/api/{endpoint}'

class UserRenderer(DefaultRenderer):
    def render_ui(self, **kwargs):
        user_id = kwargs.get('user_id', 1)
        current_tab = kwargs.get('tab', 'profile')
        
        # Python variables used directly in hx- attributes!
        return ['div', {'class': 'user-dashboard'},
            # Dynamic URL generation - no separate template logic needed
            ['button', {
                'hx-get': get_user_url(user_id),  # Python function call!
                'hx-target': '#user-content',
                'hx-swap': 'innerHTML',
                'class': 'btn-primary'
            }, f'Load User {user_id}'],
            
            # Dynamic attributes based on Python logic
            ['div', {'id': 'tabs'},
                *[self._render_tab(tab, current_tab, user_id) 
                  for tab in ['profile', 'settings', 'history']]
            ],
            
            # Conditional attributes
            ['div', {
                'id': 'user-content',
                'hx-indicator': '#loading' if kwargs.get('show_loading') else None,
                'data-user': str(user_id)
            }]
        ]
    
    def _render_tab(self, tab_name, current_tab, user_id):
        # Dynamic CSS classes and hx- attributes
        is_active = tab_name == current_tab
        return ['button', {
            'class': f'tab {"active" if is_active else ""}',
            'hx-get': f'/users/{user_id}/{tab_name}',  # String interpolation
            'hx-target': '#user-content',
            'hx-push-url': f'/users/{user_id}?tab={tab_name}',
            'disabled': is_active  # Conditional attributes
        }, tab_name.title()]

# Routes can reference Python functions directly
routes = [
    Route('/users/{user_id:int}', user_detail_view),
    Route(get_api_url('users'), api_users_view),  # URL function used in routing too!
]
```

**Why this is powerful:**
- **No template syntax**: Pure Python for logic and URL generation
- **DRY principle**: Same URL functions used in routing and templates  
- **Dynamic attributes**: Full Python expressions in any attribute
- **Type safety**: Python tooling works throughout your templates
- **Refactoring friendly**: Change URL patterns in one place

## Database Usage

```python
from wbweb import Base, Manager, configure_database
from sqlalchemy import Column, Integer, String

# Configure database connection
configure_database(\"postgresql://user:pass@localhost/db\")

# Define models with Django-style managers
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    
    # Custom manager
    active_users = Manager()  # Custom manager for active users

# Use Django-style ORM
user = await User.objects.create(name='John', email='john@example.com')
users = await User.objects.filter(active=True).all()
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install dependencies
uv install

# Install development dependencies
uv install --dev

# Run tests
uv run pytest

# Run with test coverage
uv run pytest --cov=wbweb
```

## Philosophy

wbweb fills the gap between heavyweight frameworks and lightweight libraries:

- **Not FastAPI**: We're HTML-first, not JSON-first
- **Not Flask**: We provide opinionated patterns for modern web development  
- **Not Django**: We're lightweight and FaaS-optimized
- **Not Jinja2**: We use efficient data structures instead of string templates

Perfect for developers who want:
- 🏗️ **Structured patterns** without heavyweight frameworks
- ⚡ **Fast startup times** for serverless deployments
- 🎨 **Flexible HTML generation** with full Python power
- 📱 **HTMX-ready** interactive applications
- 🗄️ **Familiar ORM patterns** from the Django ecosystem

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see our contributing guidelines.

---

**Built with ❤️ by Warmblood Co., Ltd.**