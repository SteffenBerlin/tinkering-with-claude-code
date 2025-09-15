"""
Simple Research Agent using Brave Search and Pydantic AI.
Follows main_agent_reference patterns with focus on research functionality.
"""

import logging
import httpx
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from .providers import get_llm_model

logger = logging.getLogger(__name__)


RESEARCH_SYSTEM_PROMPT = """
You are an expert research assistant with web search capabilities. Your primary goal is to help users find relevant, current information on any topic through intelligent web searches.

Your capabilities:
1. **Web Search**: Use Brave Search to find current, relevant information on any topic
2. **Analysis**: Analyze search results for relevance and credibility
3. **Synthesis**: Synthesize information from multiple sources into clear summaries

When conducting research:
- Use specific, targeted search queries
- Focus on high-quality, credible sources
- Provide clear, well-organized information
- Include source URLs for reference
- Be concise but thorough in your responses

Always strive to provide accurate, helpful, and actionable information based on the search results.
"""


@dataclass
class ResearchAgentDependencies:
    """Dependencies for the research agent - only configuration needed."""

    brave_api_key: str
    session_id: Optional[str] = None


# Initialize the research agent
research_agent = Agent(
    get_llm_model(),
    deps_type=ResearchAgentDependencies,
    system_prompt=RESEARCH_SYSTEM_PROMPT,
)


@research_agent.tool
async def search_web(
    ctx: RunContext[ResearchAgentDependencies], query: str, max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search the web using Brave Search API.

    Args:
        query: Search query
        max_results: Maximum number of results to return (1-20)

    Returns:
        List of search results with title, URL, description, and score
    """
    try:
        # Input validation
        if not query or not query.strip():
            return [{"error": "Query cannot be empty"}]

        # Ensure max_results is within valid range
        max_results = min(max(max_results, 1), 20)

        if not ctx.deps.brave_api_key or not ctx.deps.brave_api_key.strip():
            return [{"error": "Brave API key is required"}]

        headers = {
            "X-Subscription-Token": ctx.deps.brave_api_key,
            "Accept": "application/json",
        }

        params = {"q": query, "count": str(max_results)}

        logger.info(f"Searching Brave for: {query}")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=30.0,
            )

            # Handle rate limiting
            if response.status_code == 429:
                return [{"error": "Rate limit exceeded. Check your Brave API quota."}]

            # Handle authentication errors
            if response.status_code == 401:
                return [{"error": "Invalid Brave API key"}]

            # Handle other errors
            if response.status_code != 200:
                return [
                    {
                        "error": f"Brave API returned {response.status_code}: {response.text}"
                    }
                ]

            data = response.json()

            # Extract web results
            web_results = data.get("web", {}).get("results", [])

            # Convert to our format
            results = []
            for idx, result in enumerate(web_results):
                # Calculate a simple relevance score based on position
                score = 1.0 - (idx * 0.05)  # Decrease by 0.05 for each position
                score = max(score, 0.1)  # Minimum score of 0.1

                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", ""),
                        "score": score,
                    }
                )

            logger.info(f"Found {len(results)} results for query: {query}")
            return results

    except httpx.RequestError as e:
        logger.error(f"Request error during Brave search: {e}")
        return [{"error": f"Request failed: {str(e)}"}]
    except Exception as e:
        logger.error(f"Error during Brave search: {e}")
        return [{"error": f"Search failed: {str(e)}"}]


# Convenience function to create research agent with dependencies
def create_research_agent(
    brave_api_key: str, session_id: Optional[str] = None
) -> Agent[ResearchAgentDependencies, str]:
    """
    Create a research agent with specified dependencies.

    Args:
        brave_api_key: Brave Search API key
        session_id: Optional session identifier

    Returns:
        Configured research agent
    """
    return research_agent
