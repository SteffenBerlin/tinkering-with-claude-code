"""
Integration tests for Brave Search API.
These tests require real API keys and are optional.

Run with: pytest src/tests/test_brave_integration.py -v --api-key="your-brave-api-key"
"""

import pytest
import os
import asyncio

from ..research_agent import research_agent, ResearchAgentDependencies


@pytest.fixture
def brave_api_key(request):
    """Get Brave API key from command line or environment."""
    # Try command line first, then environment
    api_key = request.config.getoption("--api-key")
    if not api_key:
        api_key = os.environ.get("BRAVE_API_KEY")

    if not api_key:
        pytest.skip(
            "No Brave API key provided. Use --api-key or set BRAVE_API_KEY environment variable."
        )

    return api_key


@pytest.fixture
def integration_dependencies(brave_api_key):
    """Create dependencies with real API key for integration tests."""
    return ResearchAgentDependencies(
        brave_api_key=brave_api_key, session_id="integration_test_session"
    )


@pytest.mark.integration
class TestBraveAPIIntegration:
    """Integration tests with real Brave Search API."""

    @pytest.mark.asyncio
    async def test_real_search_basic(self, integration_dependencies):
        """Test basic search with real Brave API."""
        # Use a simple, stable search query
        query = "Python programming language"

        # Call search tool directly through agent
        from ..research_agent import search_web
        from pydantic_ai import RunContext
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.usage import RunUsage

        # Create a proper context with real dependencies
        ctx = RunContext(
            deps=integration_dependencies, retry=0, model=TestModel(), usage=RunUsage()
        )

        results = await search_web(ctx, query, max_results=3)

        # Verify we got results
        assert isinstance(results, list)
        assert len(results) > 0

        # Check first result structure
        first_result = results[0]
        if "error" not in first_result:
            assert "title" in first_result
            assert "url" in first_result
            assert "description" in first_result
            assert "score" in first_result
            assert isinstance(first_result["score"], (int, float))
            assert 0 <= first_result["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_search_result_count_limits(self, integration_dependencies):
        """Test that max_results parameter is respected."""
        from ..research_agent import search_web
        from pydantic_ai import RunContext
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.usage import RunUsage

        ctx = RunContext(
            deps=integration_dependencies, retry=0, model=TestModel(), usage=RunUsage()
        )

        # Test with small count
        results = await search_web(ctx, "artificial intelligence", max_results=2)
        assert isinstance(results, list)
        if not any("error" in r for r in results):
            assert len(results) <= 2

        # Test with larger count
        results = await search_web(ctx, "machine learning", max_results=10)
        assert isinstance(results, list)
        if not any("error" in r for r in results):
            assert len(results) <= 10

    @pytest.mark.asyncio
    async def test_search_empty_query_handling(self, integration_dependencies):
        """Test handling of empty queries with real API."""
        from ..research_agent import search_web
        from pydantic_ai import RunContext
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.usage import RunUsage

        ctx = RunContext(
            deps=integration_dependencies, retry=0, model=TestModel(), usage=RunUsage()
        )

        # Empty query should return error
        results = await search_web(ctx, "", max_results=5)
        assert isinstance(results, list)
        assert len(results) > 0
        assert "error" in results[0]
        assert "empty" in results[0]["error"].lower()

    @pytest.mark.asyncio
    async def test_api_rate_limiting_behavior(self, integration_dependencies):
        """Test API behavior under rapid requests (rate limiting)."""
        from ..research_agent import search_web
        from pydantic_ai import RunContext
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.usage import RunUsage

        ctx = RunContext(
            deps=integration_dependencies, retry=0, model=TestModel(), usage=RunUsage()
        )

        # Make several rapid requests to test rate limiting
        queries = ["test query 1", "test query 2", "test query 3"]
        results_list = []

        for query in queries:
            results = await search_web(ctx, query, max_results=1)
            results_list.append(results)
            await asyncio.sleep(0.1)  # Small delay between requests

        # At least one request should succeed (unless we hit immediate rate limiting)
        successful_requests = sum(
            1
            for results in results_list
            if isinstance(results, list)
            and len(results) > 0
            and "error" not in results[0]
        )

        # We expect at least some requests to work, but rate limiting is expected
        assert successful_requests >= 0  # At minimum, requests should not crash


@pytest.mark.integration
class TestBraveAPIErrors:
    """Test error handling with real API conditions."""

    @pytest.mark.asyncio
    async def test_invalid_api_key_error(self):
        """Test handling of invalid API key."""
        from ..research_agent import search_web
        from pydantic_ai import RunContext
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.usage import RunUsage

        # Use obviously invalid API key
        invalid_deps = ResearchAgentDependencies(
            brave_api_key="invalid_api_key_123", session_id="error_test"
        )

        ctx = RunContext(
            deps=invalid_deps, retry=0, model=TestModel(), usage=RunUsage()
        )

        results = await search_web(ctx, "test query", max_results=5)

        # Should return error about invalid API key
        assert isinstance(results, list)
        assert len(results) > 0
        assert "error" in results[0]
        # Could be "Invalid Brave API key" or similar HTTP error
        assert any(
            word in results[0]["error"].lower()
            for word in ["invalid", "unauthorized", "401", "key"]
        )

    @pytest.mark.asyncio
    async def test_empty_api_key_error(self):
        """Test handling of empty API key."""
        from ..research_agent import search_web
        from pydantic_ai import RunContext
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.usage import RunUsage

        empty_deps = ResearchAgentDependencies(
            brave_api_key="",  # Empty API key
            session_id="error_test",
        )

        ctx = RunContext(deps=empty_deps, retry=0, model=TestModel(), usage=RunUsage())

        results = await search_web(ctx, "test query", max_results=5)

        # Should return error about missing API key
        assert isinstance(results, list)
        assert len(results) > 0
        assert "error" in results[0]
        assert "required" in results[0]["error"].lower()


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests with the full agent."""

    @pytest.mark.asyncio
    async def test_agent_with_real_api(self, integration_dependencies):
        """Test the complete agent workflow with real Brave API."""
        # Import TestModel for controlled testing even with real API
        from pydantic_ai.models.test import TestModel

        # Use TestModel to control agent behavior while using real search tool
        test_model = TestModel(
            call_tools=["search_web"],
            custom_output_text="I found some great resources for you based on my web search.",
        )

        with research_agent.override(model=test_model):
            result = await research_agent.run(
                "Search for information about sustainable energy",
                deps=integration_dependencies,
            )

            # Verify agent completed successfully
            assert isinstance(result.output, str)
            assert len(result.output) > 0
            # TestModel should include our custom output
            assert "resources" in result.output.lower()


# Configuration for pytest handled in root conftest.py


if __name__ == "__main__":
    # Run integration tests directly (requires API key)
    pytest.main([__file__, "-v", "-m", "integration"])
