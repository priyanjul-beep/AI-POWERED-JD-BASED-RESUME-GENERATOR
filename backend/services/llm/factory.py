from django.conf import settings
from .base import BaseLLMProvider
from .gemini_provider import GeminiProvider

def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """
    Factory function to obtain the configured LLM provider.
    Enables zero-touch switching between Gemini and future providers (OpenAI, Anthropic, etc.).
    """
    name = (provider_name or getattr(settings, 'LLM_PROVIDER', 'gemini')).lower()

    if name == 'gemini':
        return GeminiProvider(
            api_key=getattr(settings, 'GEMINI_API_KEY', ''),
            model_name=getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash'),
            max_retries=getattr(settings, 'GEMINI_MAX_RETRIES', 3),
            timeout=getattr(settings, 'GEMINI_TIMEOUT_SECONDS', 60)
        )
    else:
        raise ValueError(f"Unsupported LLM provider: '{name}'. Supported options: 'gemini'.")
