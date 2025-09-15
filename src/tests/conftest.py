"""
Pytest configuration and fixtures for research agent tests.
Follows examples/testing_examples patterns for TestModel and FunctionModel testing.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock

from ..research_agent import ResearchAgentDependencies


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_dependencies():
    """Create basic test dependencies with test API key."""
    return ResearchAgentDependencies(
        brave_api_key="test_brave_api_key", session_id="test_session_123"
    )


@pytest.fixture
def mock_brave_response():
    """Mock successful Brave API response."""
    return {
        "web": {
            "results": [
                {
                    "title": "Python Programming Tutorial",
                    "url": "https://example.com/python-tutorial",
                    "description": "Learn Python programming from basics to advanced topics.",
                },
                {
                    "title": "Python Documentation",
                    "url": "https://docs.python.org/3/",
                    "description": "Official Python documentation and reference.",
                },
                {
                    "title": "Real Python",
                    "url": "https://realpython.com/",
                    "description": "Real Python tutorials and articles for Python developers.",
                },
            ]
        }
    }


@pytest.fixture
def expected_search_results():
    """Expected formatted search results for testing."""
    return [
        {
            "title": "Python Programming Tutorial",
            "url": "https://example.com/python-tutorial",
            "description": "Learn Python programming from basics to advanced topics.",
            "score": 1.0,
        },
        {
            "title": "Python Documentation",
            "url": "https://docs.python.org/3/",
            "description": "Official Python documentation and reference.",
            "score": 0.95,
        },
        {
            "title": "Real Python",
            "url": "https://realpython.com/",
            "description": "Real Python tutorials and articles for Python developers.",
            "score": 0.9,
        },
    ]


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing API calls."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "web": {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com/test",
                    "description": "Test description",
                }
            ]
        }
    }
    mock_client.get.return_value = mock_response
    return mock_client


@pytest.fixture
def error_dependencies():
    """Create dependencies with invalid API key for error testing."""
    return ResearchAgentDependencies(
        brave_api_key="",  # Invalid empty API key
        session_id="error_test_session",
    )
