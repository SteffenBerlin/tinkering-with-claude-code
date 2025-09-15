"""
Configuration management using pydantic-settings.
Simplified version focusing on research agent requirements.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # LLM Configuration
    llm_api_key: str = Field(...)
    llm_model: str = Field(default="gpt-4")
    llm_base_url: Optional[str] = Field(default="https://api.openai.com/v1")

    # Brave Search Configuration
    brave_api_key: str = Field(...)

    @field_validator("llm_api_key", "brave_api_key")
    @classmethod
    def validate_api_keys(cls, v):
        """Ensure API keys are not empty."""
        if not v or v.strip() == "":
            raise ValueError("API key cannot be empty")
        return v


# Global settings instance
try:
    # Attempt to create settings from environment variables
    settings = Settings(_env_file=".env")  # type: ignore
except Exception:
    # For testing, create settings with dummy values
    import os

    os.environ.setdefault("LLM_API_KEY", "test_key")
    os.environ.setdefault("BRAVE_API_KEY", "test_key")
    settings = Settings(llm_api_key="test_key", brave_api_key="test_key")
