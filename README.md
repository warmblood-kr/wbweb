# wbweb

A general-purpose web framework for Warmblood Co., Ltd.

## Project Goal

wbweb is designed to be a lightweight, modern web framework that provides:

- **Hiccup-style HTML rendering** - Python data structures to HTML conversion
- **Content negotiation** - Automatic API/UI client detection and response formatting
- **Django-style SQLAlchemy managers** - Familiar ORM patterns with async support
- **Generic configuration system** - Environment-aware settings management
- **Minimal dependencies** - Built on Starlette and SQLAlchemy core

## Current Status

This project is in active development, with core components being extracted and refined from the wbgpt codebase to create a reusable web framework.

## Development

This project uses uv for package management:

```bash
uv install          # Install dependencies
uv run python main.py  # Run application
```