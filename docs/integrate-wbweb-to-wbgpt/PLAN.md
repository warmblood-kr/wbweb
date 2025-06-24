# Integration Plan: wbweb → wbgpt

**Branch**: `integrate-wbweb-to-wbgpt`  
**Objective**: Integrate wbweb framework back into wbgpt and remove duplicated code

## Phase 4: Integration Strategy

### Preconditions ✅
- [x] wbweb framework is complete and production-ready
- [x] All 89 wbweb tests passing
- [x] wbwpt directory accessible and test structure verified
- [x] Can run pytest on wbgpt from wbweb directory
- [x] wbgpt has existing core components that duplicate wbweb functionality

### Current wbgpt Status
**Test Collection Results:**
- 22 tests found across 10 test files
- 6 errors due to missing dependencies (httpx, aiosqlite, html2image)
- Core tests working: hiccup_renderer, renderers, components, settings, llm_service

**Components in wbgpt/core/ to Replace:**
- `database/` (managers.py, base.py, config.py) → Replace with wbweb imports
- `templates/` (hiccup.py, renderers.py) → Replace with wbweb imports  
- `web/` (negotiation.py, decorators.py) → Replace with wbweb imports
- `settings.py` → Business-specific, keep but may need updates

### Integration Steps

#### Step 1: Dependency Setup
- [ ] Add wbweb as dependency to wbgpt/pyproject.toml
- [ ] Install wbweb in wbgpt environment
- [ ] Verify wbweb imports work in wbgpt context

#### Step 2: Component-by-Component Replacement
- [ ] **Templates**: Replace `wbgpt.core.templates` imports with `wbweb` imports
- [ ] **Database**: Replace `wbgpt.core.database` imports with `wbweb` imports  
- [ ] **Web**: Replace `wbgpt.core.web` imports with `wbweb` imports
- [ ] Update business logic to use wbweb configuration patterns

#### Step 3: Testing & Validation
- [ ] Run wbgpt test suite after each component replacement
- [ ] Fix any import errors or compatibility issues
- [ ] Ensure all business functionality preserved
- [ ] Verify no breaking changes to wbgpt API

#### Step 4: Cleanup
- [ ] Remove duplicated core components from wbgpt
- [ ] Update import statements throughout wbgpt codebase
- [ ] Clean up any unused dependencies
- [ ] Update documentation

### Success Criteria
- [ ] All wbgpt tests pass with wbweb integration
- [ ] wbgpt uses wbweb for all framework functionality
- [ ] No duplicated code between wbgpt and wbweb
- [ ] wbgpt functionality unchanged from user perspective
- [ ] Clean separation: wbweb = framework, wbgpt = business logic

### Risk Mitigation
- Work on feature branch to preserve working main branch
- Replace components incrementally, not all at once
- Test after each component replacement
- Keep detailed rollback plan if issues arise

## Notes
- wbgpt has missing dependencies (httpx, aiosqlite) that need installation
- Some tests may need environment setup (DATABASE_URL, etc.)
- Configuration patterns may need adjustment for wbweb compatibility