from typing import List, Dict, Optional
from .base_llm import BaseLLM
import anthropic
import os

class AnthropicLlm(BaseLLM):
    def __init__(
        self,
        model: str = "claude-2.1",  # Default Anthropic model
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass it explicitly.")
        self.client = anthropic.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        memory: Optional[List[Dict]] = None,
    ) -> str:
        # Prepare messages for the Anthropic API
        messages = []
        if memory:
            messages.extend(memory)
        if context:
            messages.append({"role": "system", "content": "Context: " + str(context)})
        messages.append({"role": "user", "content": prompt})

        # Call Anthropic API
        response = self.client.completion(
            model=self.model,
            messages=messages,
        )

        # Extract and return the response
        return response.choices[0].message.content