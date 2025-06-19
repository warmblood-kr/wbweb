# Development Principles

Core principles guiding the wbweb development process, discovered and refined through practice.

## Principle 1: No Ad-Hoc Code Execution

**Rule**: Never run ad-hoc test code directly. Always create permanent test files.

### Why This Matters
- **Regression Testing**: Ad-hoc code is lost, permanent tests can be rerun
- **Documentation**: Test files serve as living documentation of expected behavior
- **Collaboration**: Other developers can understand and verify functionality
- **Quality Assurance**: Systematic testing prevents future breakage

### Implementation
```python
# ❌ BAD: Ad-hoc testing
# Running: python -c "from wbweb import HiccupRenderer; print(renderer.render(...))"

# ✅ GOOD: Permanent test file
# File: tests/test_extraction_verification.py
class TestHiccupRendererExtraction:
    def test_basic_functionality(self):
        from wbweb import HiccupRenderer
        renderer = HiccupRenderer()
        result = renderer.render(["p", {}, "Hello"])
        assert result == "<p>Hello</p>"
```

### Examples in Practice
- **Structure Analysis**: Created `analysis/structure_analyzer.py` instead of manual exploration
- **Extraction Verification**: Created `tests/test_extraction_verification.py` instead of ad-hoc import tests
- **Functionality Testing**: Permanent test suites over temporary validation scripts

## Principle 2: Structure-Preserving Transformations

**Rule**: Make changes that strengthen existing patterns rather than imposing new ones.

### Core Concepts
- **Preserve Existing Centers**: Identify and strengthen the vital structures already present
- **Small Incremental Steps**: Transform gradually to maintain system wholeness
- **Follow Natural Flow**: Let the solution emerge from the problem domain
- **Validate Continuously**: Verify each step preserves functionality

### Implementation Pattern
1. **Observe**: Understand existing structure and patterns
2. **Transform**: Make minimal changes that respect existing design
3. **Validate**: Verify the transformation preserves wholeness
4. **Iterate**: Build on successful transformations

### Examples in Practice
- **HiccupRenderer Extraction**: Zero code changes needed - structure was already perfect
- **Package Organization**: Followed existing wbgpt structure patterns
- **Test Structure**: Preserved original test patterns while adding verification

## Principle 3: Tool Creation Over Manual Work

**Rule**: When facing repetitive or complex analysis, create reusable tools instead of manual processes.

### Why This Matters
- **Scalability**: Tools can be reused across sessions and projects
- **Accuracy**: Automated analysis reduces human error
- **Documentation**: Tools serve as executable documentation of processes
- **Efficiency**: Amortize effort across multiple uses

### Examples in Practice
- **Structure Analyzer**: Created `analysis/structure_analyzer.py` for systematic codebase analysis
- **Verification Framework**: Built `tests/test_extraction_verification.py` for validating extractions
- **Progress Tracking**: File-based documentation system for multi-session work

## Principle 4: Data-Driven Decision Making

**Rule**: Base decisions on systematic analysis rather than assumptions or intuition.

### Implementation
- **Coupling Analysis**: Use dependency graphs to determine extraction order
- **Complexity Metrics**: Lines of code, dependency counts, business logic detection
- **Validation Results**: Test outcomes guide next steps

### Examples in Practice
- **Extraction Order**: Used coupling scores to identify `templates.hiccup` as optimal first target
- **Business Logic Detection**: Keyword-based analysis to identify components needing cleanup
- **Success Metrics**: Test pass rates validate extraction success

## Principle 5: Incremental Validation

**Rule**: Validate each step immediately rather than building up unverified complexity.

### Why This Matters
- **Early Error Detection**: Catch problems when they're easy to fix
- **Confidence Building**: Each validated step increases confidence in approach
- **Rollback Capability**: Small steps make it easy to backtrack when needed

### Implementation Pattern
1. **Make Small Change**: 5-15 lines of code or single concept
2. **Immediate Validation**: Run tests, verify behavior
3. **Document Results**: Update progress, commit working state
4. **Plan Next Step**: Based on validation results

### Examples in Practice
- **HiccupRenderer Extraction**: Validated imports, then functionality, then complete test suite
- **Package Structure**: Set up structure, then implementation, then tests
- **Each Session**: Commit working state before proceeding

## Principle 6: Living Documentation

**Rule**: Documentation should evolve with the codebase and serve multiple purposes.

### Characteristics of Living Documentation
- **Executable**: Tests and analysis scripts that document by running
- **Evolving**: Updated as understanding deepens
- **Multi-Purpose**: Serves both human readers and automated processes
- **Discoverable**: Organized for easy navigation and reference

### Examples in Practice
- **Structure Analyzer**: Documents codebase while providing analysis
- **Verification Tests**: Document expected behavior while ensuring correctness
- **Progress Tracking**: Records decisions and reasoning for future reference

## Principle 7: Separation of Concerns in Documentation

**Rule**: Distinguish between timeless architectural knowledge and temporal task-specific information.

### Implementation
- **Timeless Docs** (`/docs/`): Architecture, principles, API documentation
- **Temporal Docs** (`/docs/{branch-name}/`): Task plans, progress, decisions
- **Archive on Completion**: Move temporal docs to archive after task completion

## Principle Integration

These principles work together to create a sustainable development process:

1. **Tool Creation** provides the infrastructure
2. **Data-Driven Decisions** guide the direction  
3. **Structure-Preserving Transformations** maintain quality
4. **Incremental Validation** ensures each step works
5. **No Ad-Hoc Code** preserves knowledge
6. **Living Documentation** captures the process
7. **Separation of Concerns** organizes knowledge properly

The result is a development process that scales, preserves knowledge, and maintains system quality over time.