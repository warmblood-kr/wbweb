# Documentation Organization Principles

## Core Principle: Timeless vs Temporal Documentation

### Timeless Documents (Long-term, Persistent)
Documents that remain relevant across the entire project lifecycle:
- **Architecture** - Design decisions, patterns, principles
- **API Documentation** - Public interfaces and usage
- **Development Guidelines** - Code standards, practices
- **Core Concepts** - Fundamental ideas and philosophy

**Location**: `/docs/` (root docs directory)

### Temporal Documents (Task-specific, Branch-specific)
Documents tied to specific tasks, features, or time periods:
- **Task Plans** - Specific goal roadmaps
- **Progress Tracking** - Session-by-session updates
- **Migration Plans** - One-time transformation tasks
- **Feature Specifications** - Specific implementation details

**Location**: `/docs/{branch-name}/` (task-specific subdirectories)

## Branch-Document Matching Principle

### Git Branch ↔ Documentation Directory Mapping
- **Branch name**: `task/extract-wbgpt-core`
- **Docs directory**: `/docs/task-extract-wbgpt-core/`

### Branch Naming Convention
Use standard Git flow prefixes:
- `feature/{description}` - New features or capabilities
- `task/{description}` - General tasks, refactoring, extraction work
- `bug/{description}` - Bug fixes
- `refactor/{description}` - Code restructuring without behavior change
- `docs/{description}` - Documentation-only changes

### Documentation Directory Mapping
- Branch: `{prefix}/{description}` → Docs: `/docs/{prefix}-{description}/`
- Examples:
  - Branch: `feature/user-auth` → Docs: `/docs/feature-user-auth/`
  - Branch: `task/extract-wbgpt-core` → Docs: `/docs/task-extract-wbgpt-core/`
  - Branch: `refactor/database-layer` → Docs: `/docs/refactor-database-layer/`
  - Branch: `bug/fix-content-negotiation` → Docs: `/docs/bug-fix-content-negotiation/`

### Workflow
1. **Before starting task**: Create git branch for the task
2. **Create docs subdirectory**: Match branch name format
3. **Document task-specific work**: In the branch-specific directory
4. **Update timeless docs**: When architectural decisions are made
5. **Archive on completion**: Move temporal docs to `/docs/archive/` when task complete

## Document Types by Category

### Timeless Documents (`/docs/`)
- `ARCHITECTURE.md` - System design and patterns
- `API.md` - Public interfaces and usage
- `DEVELOPMENT.md` - Development practices and guidelines
- `CONCEPTS.md` - Core ideas and philosophy
- `DOCUMENTATION_PRINCIPLES.md` - This file

### Temporal Documents (`/docs/{branch-name}/`)
- `PLAN.md` - Task-specific roadmap and strategy
- `PROGRESS.md` - Session-by-session tracking
- `COMPONENTS.md` - Task-specific component mapping
- `DECISIONS.md` - Task-specific technical decisions
- `TESTING.md` - Task-specific testing approaches

## Benefits

1. **Context Preservation** - Task-specific context doesn't pollute long-term docs
2. **Easy Navigation** - Branch name directly maps to documentation location
3. **Clean History** - Temporal documents can be archived after task completion
4. **Parallel Work** - Multiple tasks can document independently
5. **Future Reference** - Completed task documentation provides implementation history

## Implementation

### Starting a New Task
```bash
# Create branch with appropriate prefix
git checkout -b task/extract-wbgpt-core

# Create corresponding docs directory
mkdir -p docs/task-extract-wbgpt-core

# Create initial task documentation
touch docs/task-extract-wbgpt-core/PLAN.md
touch docs/task-extract-wbgpt-core/PROGRESS.md
```

### Completing a Task
```bash
# Merge task branch
git checkout main
git merge task/extract-wbgpt-core

# Archive temporal documentation
mkdir -p docs/archive/task-extract-wbgpt-core
mv docs/task-extract-wbgpt-core/* docs/archive/task-extract-wbgpt-core/

# Update timeless documentation with any architectural changes
# (if applicable)
```

This principle ensures our documentation scales cleanly with project complexity while maintaining clear separation between persistent knowledge and task-specific work.