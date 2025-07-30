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

## Additional Development Principles (Lessons Learned)

### 1. **Naming Audit During Refactoring**
**Rule**: After removing/changing core components, audit all related naming for accuracy.

**Implementation**:
- Ask: "Does this name still describe what it does?"
- Consider user perspective: "What would I expect this to be called?"
- Update names to match current reality, not legacy context

**Example**: After removing `ContentNegotiator`, `@content_negotiation` became misleading. `@renderer` better describes wiring views to renderers.

### 2. **Standard Deprecation Practices**
**Rule**: Use `warnings.warn()` with `DeprecationWarning` instead of simple aliases.

```python
# ❌ BAD: Silent alias
old_function = new_function

# ✅ GOOD: Educational deprecation
def old_function(*args, **kwargs):
    warnings.warn("Use new_function instead.", DeprecationWarning, stacklevel=2)
    return new_function(*args, **kwargs)
```

**Benefits**: Users get migration guidance, follows Python standards, enables future removal.

### 3. **Documentation as Implementation**
**Rule**: Update documentation immediately as part of implementation, not as afterthoughts.

**Implementation**:
- Update README examples in same PR as code changes
- Keep package structure docs current with code
- Update all examples to use new preferred patterns

**Why**: Users need immediate guidance on new patterns; documentation drift blocks adoption.

### 4. **Dependency Injection Over Mock Patching**
**Rule**: Prefer dependency injection for testability rather than complex mock patching.

**Implementation**:
```python
# ❌ BAD: Complex mock patching
@patch('module.get_session_maker')
@patch('module.engine_factory.create_engine') 
@patch('sqlalchemy.ext.asyncio.async_sessionmaker')
async def test_method(self, mock_session, mock_engine, mock_get_session):
    # Complex setup...

# ✅ GOOD: Simple dependency injection
async def test_method(self):
    mock_session = create_mock_session()
    await service.method(..., session=mock_session)
```

**Benefits**: Simpler tests, clearer interfaces, easier maintenance, better separation of concerns.

### 5. **Cross-Repository Security Awareness**
**Rule**: Consider repository visibility and information sensitivity when planning and documenting.

**Implementation**:
- **Private repos**: Can contain internal details, Korean language, sensitive architecture info
- **Public repos**: English only, generic technical specs, no proprietary information
- **Cross-linking**: Link public issues to private planning, but sanitize public content

**Example**: Internal planning in private repo issue, clean technical specs in public repo issue.

### 6. **GitHub Issues for Project Planning**
**Rule**: Use GitHub issues for planning rather than repository files for collaborative projects.

**Implementation**:
- **Large project planning**: Create comprehensive GitHub issues with implementation details
- **Cross-repository coordination**: Link related issues across repositories  
- **Phase-based execution**: Break large projects into phases with separate issues
- **Progress tracking**: Use issue checkboxes for progress visibility

**Benefits**: Team collaboration, clean repositories, discoverable planning, progress tracking.

## Universal Collaboration Principles

These principles transcend technology and apply to any complex problem-solving collaboration across industries and domains.

### 1. **Question the Foundation, Not Just the Surface**
**Principle**: When facing a problem, look for existing patterns that already solve similar challenges rather than inventing new mechanisms.

**Example**: "Why do we need reset methods? Doesn't ConfigurableBackendProxy already solve this?"

**Universal Application**: In any field - medicine, business, education - often the solution pattern already exists elsewhere in your system. Look for analogous problems that have been solved before building from scratch.

### 2. **Correct Course Early When You Spot Misalignment**
**Principle**: Speak up immediately when you see something going off-track, rather than letting it continue and fixing later.

**Example**: "Don't we use the global settings object?" "Don't inherit defaults, fallback handles it"

**Universal Application**: Leadership, teaching, relationships, project management - early course correction prevents bigger problems. The cost of change increases exponentially with time.

### 3. **Prefer Systematic Understanding Over Memorization**
**Principle**: Learn the underlying principles so you can apply them in new contexts, rather than just following recipes or copying implementations.

**Example**: Understanding Django's centralized settings pattern's essence, not just copying implementation details.

**Universal Application**: Any expertise development - cooking, sports, management, parenting. Principles transfer; specific techniques don't always apply.

### 4. **Integration is Often Harder Than Creation**
**Principle**: The challenge isn't in building individual pieces, it's in making them work together harmoniously.

**Example**: Building config system and proxy system separately was straightforward; integrating them revealed the real architectural complexity.

**Universal Application**: Team building, manufacturing, education systems, family dynamics. Systems thinking is often more valuable than component optimization.

### 5. **Test Your Assumptions Early and Often**
**Principle**: Get feedback on your thinking before investing heavily in a direction. Small step → immediate validation → course correct if needed.

**Example**: Each small architectural change was immediately tested and validated before proceeding to the next step.

**Universal Application**: Product development, relationships, career decisions, creative projects. Rapid feedback loops prevent costly mistakes and enable adaptive problem-solving.

### 6. **Align on Principles Before Diving Into Implementation**
**Principle**: Establish shared understanding of the fundamental approach before getting into detailed execution.

**Example**: Agreeing on "Django-style config" concept before implementing specific classes and methods.

**Universal Application**: Any collaborative work - strategy sessions, creative projects, family decisions. Misaligned foundations lead to misaligned outcomes.
