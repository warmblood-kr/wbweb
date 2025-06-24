# wbgpt Cleanup Plan

## Overview
After successful Phase 4 integration of wbweb framework into wbgpt, we can now remove duplicated code that has been replaced by wbweb imports.

**Goal**: Remove ~350+ lines of duplicated framework code while preserving business-specific logic.

## Analysis Results

### Files to REMOVE (Complete Duplicates)

✅ **Database Package (180 LOC)**
- `wbgpt/core/database/managers.py` (127 LOC) - Django-style ORM managers
- `wbgpt/core/database/base.py` (29 LOC) - Base model with metaclass  
- `wbgpt/core/database/config.py` (48 LOC) - Database configuration
- `wbgpt/core/database/__init__.py` - Package exports

✅ **Templates Package (177 LOC)**
- `wbgpt/core/templates/hiccup.py` (126 LOC) - HiccupRenderer implementation
- `wbgpt/core/templates/renderers.py` (51 LOC) - Base renderer classes
- `wbgpt/core/templates/__init__.py` - Package exports

✅ **Web Package (Partial)**
- `wbgpt/core/web/decorators.py` - content_negotiation decorator (now in wbweb)
- `wbgpt/core/web/negotiation.py` - ContentNegotiator class (now in wbweb)

### Files to KEEP (Business Logic)

❌ **Business-Specific Components**
- `wbgpt/core/web/exceptions.py` - Business exception handlers (still in use)
- `wbgpt/core/settings.py` - wbgpt-specific settings and configuration

## Cleanup Execution Plan

### Phase 1: Remove Complete Duplicate Directories

**Step 1: Remove Database Package**
```bash
cd /path/to/wbgpt
rm -rf wbgpt/core/database/
```

**Step 2: Remove Templates Package**
```bash
rm -rf wbgpt/core/templates/
```

### Phase 2: Partial Web Package Cleanup

**Step 3: Remove Duplicated Web Files**
```bash
rm wbgpt/core/web/decorators.py    # content_negotiation decorator
rm wbgpt/core/web/negotiation.py   # ContentNegotiator class
```

**Step 4: Update Web Package Exports**
Edit `wbgpt/core/web/__init__.py`:
```python
# Keep only business-specific exports
from .exceptions import (
    conversation_not_found_handler,
    server_error_handler, 
    validation_error_handler
)
```

### Phase 3: Verification

**Step 5: Test All Functionality**
```bash
cd /path/to/wbgpt
pytest tests/ -v
# Should maintain 19/19 framework tests passing
```

**Step 6: Verify Import Structure**
Ensure `wbgpt/web/app.py` still imports correctly:
```python
from wbgpt.core.web import (
    conversation_not_found_handler,
    server_error_handler, 
    validation_error_handler
)
```

## Expected Results

### Before Cleanup
```
wbgpt/core/
├── __init__.py
├── database/           # 180 LOC - DUPLICATE
│   ├── __init__.py
│   ├── managers.py
│   ├── base.py
│   └── config.py
├── templates/          # 177 LOC - DUPLICATE  
│   ├── __init__.py
│   ├── hiccup.py
│   └── renderers.py
├── web/               # Partially duplicate
│   ├── __init__.py
│   ├── decorators.py   # DUPLICATE
│   ├── negotiation.py  # DUPLICATE
│   └── exceptions.py   # BUSINESS LOGIC
└── settings.py        # BUSINESS LOGIC
```

### After Cleanup
```
wbgpt/core/
├── __init__.py
├── web/               # Business handlers only
│   ├── __init__.py
│   └── exceptions.py  # Business exception handlers
└── settings.py        # Business-specific settings
```

## Risk Assessment

- **Risk Level**: Zero
- **Breaking Changes**: None expected
- **Test Coverage**: 19/19 framework tests must pass
- **Rollback Plan**: Git history allows complete rollback if needed

## Success Criteria

1. ✅ All duplicate framework code removed (~350+ LOC)
2. ✅ Business logic preserved and functional
3. ✅ All tests continue to pass (19/19)
4. ✅ Clean separation: framework (wbweb) vs business (wbgpt)
5. ✅ Import structure remains functional

## Notes

- This cleanup is only possible because Phase 4 integration is 100% complete
- All framework functionality is now provided by wbweb package
- Business-specific handlers remain in wbgpt for domain logic
- Integration work validated zero breaking changes before cleanup