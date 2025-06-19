# wbweb Extraction Plan

**Objective**: Extract generic web framework components from wbgpt to create a reusable web framework for Warmblood Co., Ltd.

## High-Level Strategy

### Phase 1: Analysis & Planning ✅
- [x] Analyze wbgpt.core components
- [x] Identify generic vs business-specific logic
- [x] Design wbweb package structure
- [x] Plan extraction approach

### Phase 2: Structure & Design 🔄
- [ ] Define clean wbweb package structure
- [ ] Design public API interfaces
- [ ] Plan component dependencies
- [ ] Create migration strategy

### Phase 3: Extraction 📋
- [ ] Clean up wbgpt-specific logic from core components
- [ ] Extract core web facilities
- [ ] Implement wbweb package structure
- [ ] Create proper imports/exports

### Phase 4: Integration 📋
- [ ] Update wbgpt to use wbweb as dependency
- [ ] Test integration thoroughly
- [ ] Handle any breaking changes
- [ ] Document migration path

## Components to Extract

### Generic Components (Extract to wbweb)
1. **Web Layer** (`wbgpt/core/web/`)
   - Content negotiation decorators
   - ContentNegotiator class
   - Generic error handling

2. **Template System** (`wbgpt/core/templates/`)
   - HiccupRenderer
   - Base renderer classes (DefaultRenderer, UIRenderer, ApiRenderer)

3. **Database Layer** (`wbgpt/core/database/`)
   - Django-style SQLAlchemy managers
   - Base model classes
   - Database configuration

4. **Settings System** (`wbgpt/core/settings.py`)
   - Generic configuration management
   - Environment variable handling

### Business Components (Keep in wbgpt)
1. Domain models (Conversation, Message)
2. Business services (ChatService, LLMService)
3. Domain-specific renderers
4. Application routes and endpoints

## Success Criteria
- [ ] wbweb can be installed as independent package
- [ ] wbgpt successfully uses wbweb as dependency
- [ ] All existing wbgpt functionality preserved
- [ ] No breaking changes to wbgpt API
- [ ] Clean separation of concerns achieved