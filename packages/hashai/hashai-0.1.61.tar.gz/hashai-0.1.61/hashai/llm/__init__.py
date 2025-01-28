from .openai import OpenAILlm
from .anthropic import AnthropicLlm
# from .llama import LlamaLlm
from .groq import GroqLlm

def get_llm(provider: str, **kwargs):
    provider = provider.lower()  # Convert provider name to lowercase
    if provider == "openai":
        return OpenAILlm(**kwargs)
    elif provider == "anthropic":
        return AnthropicLlm(**kwargs)
    # elif provider == "llama":
    #     return LlamaLlm(**kwargs)
    elif provider == "groq":
        return GroqLlm(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")