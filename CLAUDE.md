# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**wbweb** is a general-purpose web framework for Warmblood Co., Ltd. The project is in active development, with core components being extracted from the wbgpt codebase to create a reusable framework.

**Key Features:**
- Hiccup-style HTML rendering (Python data structures → HTML)
- Content negotiation (automatic API/UI client detection) 
- Django-style SQLAlchemy managers with async support
- Generic configuration system
- Minimal dependencies (Starlette + SQLAlchemy)

## Development Commands

### Package Management
- `uv install` - Install dependencies from pyproject.toml
- `uv add <package>` - Add a new dependency  
- `uv add --dev <package>` - Add a development dependency
- `uv remove <package>` - Remove a dependency

### Running the Application
- `uv run python main.py` - Run the main application
- `uv run python -m wbweb` - Run as module (when configured)

### Development Environment
- Python version: 3.11 (specified in .python-version)
- Package manager: uv
- Virtual environment is automatically managed by uv

## Project Structure

### Core Files
- `main.py` - Entry point with main() function
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Lock file for reproducible installations
- `.python-version` - Python version specification

### Documentation Structure
The `/docs/` directory contains our project knowledge base:

- `ARCHITECTURE.md` - Design decisions and package structure
- `DEVELOPMENT_PRINCIPLES.md` - Core development principles including:
- `DOCUMENTATION_PRINCIPLES.md` - Documentation organization:

## Development Principles

This project follows systematic development principles refined through practice. **Always read the key principles documents**:

### Essential Reading
- **`/docs/DEVELOPMENT_PRINCIPLES.md`** - Core development principles including:
  - No ad-hoc code execution (always create test files)  
  - Structure-preserving transformations
  - Tool creation over manual work
  - Data-driven decision making
  - Incremental validation with immediate feedback

- **`/docs/DOCUMENTATION_PRINCIPLES.md`** - Documentation organization:
  - **Timeless docs** (in `/docs/`) - Architecture, API, development guidelines
  - **Temporal docs** (in `/docs/{branch-name}/`) - Task-specific plans and progress
  - **Branch-document matching** - Git branch names map to documentation directories

## Long-term Project Context

This is an **ongoing multi-session extraction project**. The goal is to extract generic web framework components from the wbgpt codebase while keeping business-specific logic in wbgpt.

**Always check the documentation files** to understand:
- **Current task status**: Check `/docs/{current-branch}/` for task-specific progress
- **Architecture decisions**: Check `/docs/ARCHITECTURE.md` for design patterns
- **Component mapping**: Check task-specific docs for extraction details

The extraction follows a phased approach focusing on minimal dependencies and clean separation of concerns.
