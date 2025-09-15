name: "Simple Research Agent with Brave API - Comprehensive Implementation PRP"
description: |

## Purpose
Implement a simple, focused research agent using Pydantic AI and the Brave Search API, following the established patterns from the main_agent_reference and keeping it simple per the YAGNI principle.

## Core Principles
1. **Context is King**: All necessary documentation, examples, and caveats included
2. **Validation Loops**: Executable tests/lints for iterative refinement
3. **Information Dense**: Uses existing patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Follow all rules in CLAUDE.md (UV package management, 500 line files, KISS principle)

---

## Goal
Build a simple research agent that can search topics using the Brave Search API, returning structured results with summaries. The agent should be lightweight, follow existing patterns, and be production-ready with proper error handling and testing.

## Why
- Provide a focused research capability without the complexity of the multi-agent system
- Demonstrate clean Pydantic AI patterns for future agent development
- Enable users to get current information on topics through structured search
- Serve as a template for building other simple, single-purpose agents

## What
A standalone research agent that:
- Accepts research queries as input
- Uses Brave Search API to find relevant results
- Returns structured results with titles, URLs, descriptions, and relevance scores
- Provides optional AI-generated summaries of findings
- Handles errors gracefully and provides clear feedback
- Follows the established patterns from examples/main_agent_reference

### Success Criteria
- [ ] Agent accepts string queries and returns structured research results
- [ ] Brave API integration works with proper error handling (401, 429, timeouts)
- [ ] All validation gates pass (ruff, mypy, pytest)
- [ ] Follows existing patterns from main_agent_reference
- [ ] Under 500 lines per file following CLAUDE.md guidelines
- [ ] Environment variable configuration working
- [ ] Comprehensive test coverage using TestModel and FunctionModel patterns

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://ai.pydantic.dev/agents/
  why: Core agent creation patterns and tool integration
  
- url: https://ai.pydantic.dev/tools/
  why: Tool registration and RunContext usage patterns
  
- url: https://ai.pydantic.dev/testing/
  why: TestModel and FunctionModel testing patterns
  
- url: https://search.brave.com/help/api
  why: Brave Search API documentation, rate limits, authentication
  
- file: examples/main_agent_reference/research_agent.py
  why: Follow agent structure, tools pattern, dependency injection
  
- file: examples/main_agent_reference/settings.py
  why: Environment variable configuration with pydantic-settings
  
- file: examples/main_agent_reference/providers.py
  why: LLM model configuration and provider setup
  
- file: examples/main_agent_reference/tools.py
  why: Brave Search API implementation pattern - CRITICAL reference
  
- file: examples/testing_examples/test_agent_patterns.py
  why: Complete testing patterns with TestModel, FunctionModel, mocks
  
- file: examples/tool_enabled_agent/agent.py
  why: Simple agent with tools pattern, string output (no result_type)
  
- file: examples/main_agent_reference/.env.example
  why: Environment variable naming conventions
```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase
```bash
.
├── examples
│   ├── basic_chat_agent
│   │   └── agent.py
│   ├── main_agent_reference
│   │   ├── .env.example
│   │   ├── cli.py
│   │   ├── models.py
│   │   ├── providers.py
│   │   ├── research_agent.py
│   │   ├── settings.py
│   │   └── tools.py
│   ├── structured_output_agent
│   │   └── agent.py
│   ├── testing_examples
│   │   ├── pytest.ini
│   │   └── test_agent_patterns.py
│   └── tool_enabled_agent
│       └── agent.py
└── PRPs
    ├── INITIAL.md
    └── templates
        └── prp_base.md
```

### Desired Codebase tree with files to be added and responsibility of file
```bash
src/
├── __init__.py                    # Package initialization
├── research_agent.py              # Main agent implementation with Brave search tool
├── settings.py                    # Environment configuration (mirrors main_agent_reference)
├── providers.py                   # LLM provider configuration (mirrors main_agent_reference)
├── models.py                      # Pydantic models for requests/responses
└── tests/
    ├── __init__.py                # Test package initialization
    ├── conftest.py                # Pytest fixtures and configuration
    ├── test_research_agent.py     # Agent testing with TestModel/FunctionModel patterns
    └── test_brave_integration.py  # Integration tests for Brave API
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: Pydantic AI requires specific patterns
# - Use @dataclass for dependencies, not BaseModel
# - RunContext[DependencyType] for tool context
# - Agent tools must be registered with @agent.tool decorator

# CRITICAL: Brave Search API specifics
# - Rate limit: Check API quota limits (usually 1000/month free)
# - Authentication: X-Subscription-Token header (not Authorization)
# - Response format: web.results array, not direct results
# - Count parameter: 1-20 max, default to reasonable number (5-10)
# - Handle 429 (rate limit), 401 (auth), timeouts gracefully

# CRITICAL: Environment variables
# - Use pydantic-settings BaseSettings for validation
# - Follow CLAUDE.md: Use UV for package management
# - API keys must be validated (not empty/None)
# - Provide test fallbacks for missing env vars

# CRITICAL: Testing patterns from examples/testing_examples
# - TestModel for development validation
# - FunctionModel for custom behavior testing
# - AsyncMock for async dependencies
# - Use agent.override(model=test_model) for test isolation

# CRITICAL: File size limits from CLAUDE.md
# - Never create a file longer than 500 lines of code
# - Functions should be under 50 lines
# - Classes should be under 100 lines
```

## Implementation Blueprint

### Data models and structure

Create the core data models first to ensure type safety and consistency.
```python
# models.py - Follow examples/main_agent_reference/models.py patterns
class BraveSearchResult(BaseModel):
    """Individual search result from Brave API"""
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")  
    description: str = Field(..., description="Result snippet")
    score: float = Field(0.0, ge=0.0, le=1.0, description="Relevance score")

class ResearchQuery(BaseModel):
    """Research request model"""
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(5, ge=1, le=20, description="Max results")
    include_summary: bool = Field(False, description="Generate AI summary")

class ResearchResponse(BaseModel):
    """Research response model"""
    query: str
    results: List[BraveSearchResult]
    summary: Optional[str] = None
    total_results: int
    timestamp: datetime = Field(default_factory=datetime.now)
```

### List of tasks to be completed to fulfill the PRP in the order they should be completed

```yaml
Task 1:
CREATE src/__init__.py:
  - Empty init file for package structure

CREATE src/settings.py:
  - MIRROR pattern from: examples/main_agent_reference/settings.py
  - MODIFY to include only: llm_api_key, brave_api_key, llm_model, llm_base_url
  - KEEP pydantic-settings BaseSettings pattern identical
  - ADD brave_api_key validation (not empty)

Task 2:
CREATE src/providers.py:
  - MIRROR pattern from: examples/main_agent_reference/providers.py  
  - KEEP get_llm_model() function identical
  - PRESERVE OpenAI provider configuration pattern

Task 3:
CREATE src/models.py:
  - MIRROR pattern from: examples/main_agent_reference/models.py
  - CREATE BraveSearchResult, ResearchQuery, ResearchResponse models
  - FOLLOW Field validation patterns from existing models
  - KEEP Config class patterns for JSON schema examples

Task 4:
CREATE src/research_agent.py:
  - MIRROR structure from: examples/main_agent_reference/research_agent.py
  - SIMPLIFY: Remove email agent integration
  - KEEP: Agent initialization, dependency pattern, tool registration
  - MODIFY: Single search_web tool using Brave API
  - PRESERVE: Error handling, logging patterns
  - FOLLOW: examples/main_agent_reference/tools.py for Brave API implementation

Task 5:
CREATE src/tests/__init__.py:
  - Empty init file for test package

CREATE src/tests/conftest.py:
  - MIRROR pattern from: examples/testing_examples/test_agent_patterns.py
  - CREATE pytest fixtures for test dependencies
  - KEEP AsyncMock patterns for HTTP client mocking

Task 6:
CREATE src/tests/test_research_agent.py:
  - MIRROR patterns from: examples/testing_examples/test_agent_patterns.py
  - IMPLEMENT TestModel and FunctionModel test classes
  - TEST agent with mocked Brave API responses
  - PRESERVE async testing patterns with pytest.mark.asyncio

Task 7:
CREATE src/tests/test_brave_integration.py:
  - INTEGRATION tests for actual Brave API (optional, env-dependent)
  - ERROR handling tests (401, 429, timeout scenarios)
  - RATE limiting behavior validation
```

### Per task pseudocode as needed added to each task

```python
# Task 4 - research_agent.py critical implementation details
@dataclass
class ResearchAgentDependencies:
    """Dependencies - CRITICAL: Use @dataclass, not BaseModel"""
    brave_api_key: str
    session_id: Optional[str] = None

research_agent = Agent(
    get_llm_model(),  # From providers.py
    deps_type=ResearchAgentDependencies,
    # IMPORTANT: No result_type = defaults to string output (keep simple)
    system_prompt=RESEARCH_SYSTEM_PROMPT
)

@research_agent.tool
async def search_web(
    ctx: RunContext[ResearchAgentDependencies],
    query: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    CRITICAL: Mirror examples/main_agent_reference/tools.py search_web_tool
    - Use ctx.deps.brave_api_key for authentication
    - Handle httpx.AsyncClient() pattern
    - Return List[Dict] format for compatibility
    - Error handling: 429, 401, timeouts, connection errors
    """
    # PATTERN: Input validation first
    if not query or not query.strip():
        return [{"error": "Query cannot be empty"}]
    
    max_results = min(max(max_results, 1), 20)  # Brave API limits
    
    # PATTERN: HTTP client with proper headers
    headers = {
        "X-Subscription-Token": ctx.deps.brave_api_key,  # CRITICAL: Not Authorization
        "Accept": "application/json"
    }
    
    # GOTCHA: Brave API specific URL and parameters
    async with httpx.AsyncClient() as client:
        # CRITICAL: Handle rate limiting (429), auth (401), timeouts
        # RETURN: List[{"title": ..., "url": ..., "description": ..., "score": ...}]
```

### Integration Points
```yaml
ENVIRONMENT:
  - add to: .env file (copy from examples/main_agent_reference/.env.example)
  - pattern: "BRAVE_API_KEY=your-brave-api-key-here"
  - pattern: "LLM_API_KEY=your-openai-api-key-here" 
  
DEPENDENCIES:
  - use UV package management per CLAUDE.md
  - required: pydantic-ai, pydantic-settings, httpx, python-dotenv
  - testing: pytest, pytest-asyncio
  
PROJECT:
  - create at: src/ directory (new package)
  - follow: vertical slice architecture per CLAUDE.md
  - tests: next to code they test
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check src/ --fix        # Auto-fix what's possible  
uv run ruff format src/             # Format code
uv run mypy src/                    # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns
```python
# CREATE test_research_agent.py with these test cases:
def test_agent_basic_functionality():
    """Test agent responds to simple queries using TestModel"""
    test_model = TestModel()
    with research_agent.override(model=test_model):
        result = research_agent.run_sync(
            "Search for Python programming tutorials",
            deps=ResearchAgentDependencies(brave_api_key="test_key")
        )
        assert isinstance(result.data, str)
        assert len(result.data) > 0

@pytest.mark.asyncio
async def test_search_tool_success():
    """Test search tool with mocked successful Brave API response"""
    # Mock successful Brave API response
    mock_response = {
        "web": {
            "results": [
                {
                    "title": "Python Tutorial",
                    "url": "https://example.com/python",
                    "description": "Learn Python programming basics"
                }
            ]
        }
    }
    
    test_model = TestModel(call_tools=['search_web'])
    with research_agent.override(model=test_model):
        # Test tool execution with mocked HTTP response
        # Verify search_web tool returns expected format

@pytest.mark.asyncio 
async def test_api_error_handling():
    """Test graceful handling of Brave API errors"""
    # Test 401, 429, timeout scenarios
    # Verify error messages are user-friendly
    # Ensure agent doesn't crash on API failures
```

```bash
# Run and iterate until passing:
uv run pytest src/tests/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Test with real environment (optional - requires API keys)
# Create .env file with real API keys for manual testing:
echo "BRAVE_API_KEY=your-real-api-key" > .env
echo "LLM_API_KEY=your-openai-key" >> .env

# Test basic functionality:
python -c "
from src.research_agent import research_agent, ResearchAgentDependencies
from src.settings import settings

deps = ResearchAgentDependencies(brave_api_key=settings.brave_api_key)
result = research_agent.run_sync('Python tutorials', deps=deps)
print(result.data)
"

# Expected: Successful search results or clear error message
```

## Final validation Checklist
- [ ] All tests pass: `uv run pytest src/tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Manual test successful with real API key
- [ ] Error cases handled gracefully (no crashes on API failures)
- [ ] Logs are informative but not verbose
- [ ] Environment variable configuration working
- [ ] File sizes under 500 lines per CLAUDE.md

---

## Anti-Patterns to Avoid
- ❌ Don't create complex multi-agent system (keep it simple - YAGNI)
- ❌ Don't skip validation because "it should work"  
- ❌ Don't ignore failing tests - fix them
- ❌ Don't hardcode API keys - use environment variables
- ❌ Don't catch all exceptions - be specific (401, 429, timeout)
- ❌ Don't exceed 500 lines per file (CLAUDE.md requirement)
- ❌ Don't assume Brave API works like other search APIs
- ❌ Don't use Authorization header (Brave uses X-Subscription-Token)
- ❌ Don't ignore rate limiting - handle 429 responses properly

## Expected Brave API Response Format
```json
{
  "web": {
    "results": [
      {
        "title": "Example Title",
        "url": "https://example.com",
        "description": "Example description",
        "published": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

## Key Success Factors
1. **Follow existing patterns exactly** - Don't reinvent established patterns
2. **Test thoroughly** - Use TestModel and FunctionModel for comprehensive testing  
3. **Handle errors gracefully** - Brave API has specific error codes and rate limits
4. **Keep it simple** - Single purpose agent, no unnecessary complexity
5. **Environment first** - Proper configuration management with validation
6. **Validation loops** - Run tests early and often during development

**PRP Confidence Score: 9/10** 

This PRP provides comprehensive context from the existing codebase, specific implementation patterns to follow, detailed validation gates, and addresses all critical gotchas. The high score reflects:
- Complete reference to existing working patterns
- Specific API documentation and error handling guidance  
- Executable validation gates with clear expected outcomes
- Detailed gotchas and anti-patterns to avoid
- Progressive implementation approach with clear task breakdown