"""
Flexible provider configuration for LLM models.
Based on examples/main_agent_reference/providers.py pattern.
"""

from typing import Optional
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel
from .settings import settings


def get_llm_model(model_choice: Optional[str] = None) -> OpenAIChatModel:
    """
    Get LLM model configuration based on environment variables.

    Args:
        model_choice: Optional override for model choice

    Returns:
        Configured OpenAI-compatible model
    """
    llm_choice = model_choice or settings.llm_model
    base_url = settings.llm_base_url
    api_key = settings.llm_api_key

    # Create provider based on configuration
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)

    return OpenAIChatModel(llm_choice, provider=provider)


def get_model_info() -> dict:
    """
    Get information about current model configuration.

    Returns:
        Dictionary with model configuration info
    """
    return {
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
    }


def validate_llm_configuration() -> bool:
    """
    Validate that LLM configuration is properly set.

    Returns:
        True if configuration is valid
    """
    try:
        # Check if we can create a model instance
        get_llm_model()
        return True
    except Exception as e:
        print(f"LLM configuration validation failed: {e}")
        return False
