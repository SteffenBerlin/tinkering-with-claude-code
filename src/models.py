"""
Core data models for the simple research agent.
Follows main_agent_reference patterns with focus on research functionality.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BraveSearchResult(BaseModel):
    """Individual search result from Brave API"""

    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    description: str = Field(..., description="Result snippet")
    score: float = Field(0.0, ge=0.0, le=1.0, description="Relevance score")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "title": "Understanding AI Safety",
                "url": "https://example.com/ai-safety",
                "description": "A comprehensive guide to AI safety principles...",
                "score": 0.95,
            }
        }


class ResearchQuery(BaseModel):
    """Research request model"""

    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(5, ge=1, le=20, description="Max results")
    include_summary: bool = Field(False, description="Generate AI summary")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "query": "artificial intelligence safety research",
                "max_results": 10,
                "include_summary": True,
            }
        }


class ResearchResponse(BaseModel):
    """Research response model"""

    query: str = Field(..., description="Original research query")
    results: List[BraveSearchResult] = Field(..., description="Search results")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    total_results: int = Field(..., description="Total number of results found")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Query timestamp"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "query": "artificial intelligence safety",
                "results": [
                    {
                        "title": "AI Safety Research",
                        "url": "https://example.com/ai-safety",
                        "description": "Latest research on AI safety...",
                        "score": 0.95,
                    }
                ],
                "summary": "Current AI safety research focuses on...",
                "total_results": 1,
                "timestamp": "2024-01-01T12:00:00",
            }
        }
