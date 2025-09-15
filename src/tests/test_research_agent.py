"""
Comprehensive tests for the research agent using TestModel and FunctionModel patterns.
Follows examples/testing_examples/test_agent_patterns.py structure.
"""

import pytest
from unittest.mock import AsyncMock, patch
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel

from ..research_agent import research_agent, ResearchAgentDependencies


class TestAgentBasics:
    """Test basic agent functionality with TestModel."""

    def test_agent_with_test_model(self, test_dependencies):
        """Test agent responds to simple queries using TestModel."""
        test_model = TestModel()

        with research_agent.override(model=test_model):
            result = research_agent.run_sync(
                "Search for Python programming tutorials", deps=test_dependencies
            )

            # TestModel returns string by default (no result_type set)
            assert isinstance(result.output, str)
            assert len(result.output) > 0

    def test_agent_custom_test_model_output(self, test_dependencies):
        """Test agent with custom TestModel output."""
        test_model = TestModel(
            custom_output_text="Based on my search, here are Python tutorials I found..."
        )

        with research_agent.override(model=test_model):
            result = research_agent.run_sync(
                "Find Python learning resources", deps=test_dependencies
            )

            assert "Python tutorials" in result.output

    @pytest.mark.asyncio
    async def test_agent_async_with_test_model(self, test_dependencies):
        """Test async agent behavior with TestModel."""
        test_model = TestModel()

        with research_agent.override(model=test_model):
            result = await research_agent.run(
                "Research artificial intelligence", deps=test_dependencies
            )

            assert isinstance(result.output, str)
            assert len(result.output) > 0


class TestSearchTool:
    """Test the search_web tool functionality."""

    @pytest.mark.asyncio
    async def test_search_tool_success(self, test_dependencies, mock_brave_response):
        """Test search tool with mocked successful Brave API response."""
        test_model = TestModel(call_tools=["search_web"])

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock HTTP client
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_brave_response
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with research_agent.override(model=test_model):
                result = await research_agent.run(
                    "Search for Python tutorials", deps=test_dependencies
                )

                # Verify API was called
                mock_client.get.assert_called_once()
                call_args = mock_client.get.call_args
                assert "api.search.brave.com" in call_args[0][0]
                assert (
                    call_args[1]["headers"]["X-Subscription-Token"]
                    == "test_brave_api_key"
                )

                # Verify response format
                assert isinstance(result.output, str)
                assert "search_web" in result.output

    @pytest.mark.asyncio
    async def test_search_tool_empty_query(self, test_dependencies):
        """Test search tool with empty query."""
        test_model = TestModel(call_tools=["search_web"])

        with research_agent.override(model=test_model):
            result = await research_agent.run(
                "Search for: ''",  # Empty query
                deps=test_dependencies,
            )

            # Tool should handle empty query gracefully
            assert isinstance(result.output, str)

    @pytest.mark.asyncio
    async def test_search_tool_api_error_401(self, test_dependencies):
        """Test search tool handling 401 authentication error."""
        test_model = TestModel(call_tools=["search_web"])

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock HTTP client with 401 error
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with research_agent.override(model=test_model):
                result = await research_agent.run(
                    "Search for anything", deps=test_dependencies
                )

                # Tool should handle 401 error gracefully
                assert isinstance(result.output, str)

    @pytest.mark.asyncio
    async def test_search_tool_api_error_429(self, test_dependencies):
        """Test search tool handling 429 rate limit error."""
        test_model = TestModel(call_tools=["search_web"])

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock HTTP client with 429 error
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with research_agent.override(model=test_model):
                result = await research_agent.run(
                    "Search for test query", deps=test_dependencies
                )

                # Tool should handle 429 error gracefully
                assert isinstance(result.output, str)

    @pytest.mark.asyncio
    async def test_search_tool_invalid_api_key(self, error_dependencies):
        """Test search tool with invalid API key."""
        test_model = TestModel(call_tools=["search_web"])

        with research_agent.override(model=test_model):
            result = await research_agent.run(
                "Search for something",
                deps=error_dependencies,  # Has empty API key
            )

            # Tool should handle invalid API key gracefully
            assert isinstance(result.output, str)


class TestAgentWithFunctionModel:
    """Test agent behavior with FunctionModel for custom responses."""

    def test_function_model_custom_behavior(self, test_dependencies):
        """Test agent with FunctionModel for custom search behavior."""

        def custom_response_func(messages, tools):
            """Custom function to generate search-specific responses."""
            from pydantic_ai.models import ModelResponse
            from pydantic_ai.messages import TextPart

            # Extract content from the last message
            last_message = ""
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, "parts") and last_msg.parts:
                    # Get text content from message parts
                    for part in last_msg.parts:
                        if hasattr(part, "content"):
                            last_message += part.content
                        elif hasattr(part, "text"):
                            last_message += part.text

            if "python" in last_message.lower():
                response_text = "I found several excellent Python resources including tutorials, documentation, and community sites."
            elif "error" in last_message.lower():
                response_text = "I encountered an issue with the search. Let me try a different approach."
            else:
                response_text = "I've conducted a web search and found relevant information on your topic."

            return ModelResponse(parts=[TextPart(content=response_text)])

        function_model = FunctionModel(function=custom_response_func)

        with research_agent.override(model=function_model):
            # Test Python search
            result1 = research_agent.run_sync(
                "Search for Python tutorials", deps=test_dependencies
            )
            assert "Python resources" in result1.output

            # Test general search
            result2 = research_agent.run_sync(
                "Search for machine learning", deps=test_dependencies
            )
            assert "relevant information" in result2.output


class TestAgentErrorHandling:
    """Test agent error handling scenarios."""

    @pytest.mark.asyncio
    async def test_tool_network_error(self, test_dependencies):
        """Test agent behavior when search tool has network errors."""
        test_model = TestModel(call_tools=["search_web"])

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup mock HTTP client to raise network error
            mock_client = AsyncMock()
            mock_client.get.side_effect = Exception("Network connection failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with research_agent.override(model=test_model):
                result = await research_agent.run(
                    "Search for anything", deps=test_dependencies
                )

                # Agent should handle tool failures gracefully
                assert isinstance(result.output, str)

    def test_dependencies_validation(self):
        """Test that dependencies are properly validated."""
        # Test with valid dependencies
        valid_deps = ResearchAgentDependencies(
            brave_api_key="valid_key", session_id="test_session"
        )
        assert valid_deps.brave_api_key == "valid_key"
        assert valid_deps.session_id == "test_session"

        # Test with minimal required dependencies
        minimal_deps = ResearchAgentDependencies(brave_api_key="key")
        assert minimal_deps.brave_api_key == "key"
        assert minimal_deps.session_id is None


class TestAgentIntegration:
    """Integration tests for complete agent workflows."""

    @pytest.mark.asyncio
    async def test_complete_research_workflow(
        self, test_dependencies, mock_brave_response
    ):
        """Test complete research workflow with search tool."""
        test_model = TestModel(call_tools=["search_web"])

        with patch("httpx.AsyncClient") as mock_client_class:
            # Setup successful mock response
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_brave_response
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with research_agent.override(model=test_model):
                result = await research_agent.run(
                    "I need to research Python programming. Can you search for tutorials and documentation?",
                    deps=test_dependencies,
                )

                # Verify the workflow completed
                assert isinstance(result.output, str)
                assert len(result.output) > 0

                # Verify API was called with correct parameters
                mock_client.get.assert_called_once()
                call_args = mock_client.get.call_args
                assert call_args[1]["params"]["q"]  # Query parameter exists
                assert int(call_args[1]["params"]["count"]) <= 20  # Within API limits


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
