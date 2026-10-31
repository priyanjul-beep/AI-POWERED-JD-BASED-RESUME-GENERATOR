from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass

class LLMRateLimitError(LLMProviderError):
    """Raised when rate limit or quota is exceeded."""
    pass

class LLMAuthenticationError(LLMProviderError):
    """Raised when API key is missing or invalid."""
    pass

class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Decouples business logic from specific AI model vendors (Gemini, OpenAI, Anthropic, etc.).
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name (e.g., 'gemini', 'openai')."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_instruction: str = "",
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generates a structured JSON response conforming to a given Pydantic schema or returns a dict.
        Must handle retries, rate-limits, and response parsing.
        """
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3
    ) -> str:
        """
        Generates unstructured or markdown text.
        """
        pass
