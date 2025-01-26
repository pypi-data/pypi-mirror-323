from typing import List, Dict, Optional
from .base_llm import BaseLLM
import openai
import os

class OpenAILlm(BaseLLM):
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it explicitly.")
        openai.api_key = self.api_key

    def generate(self, prompt: str, context: Optional[List[Dict]] = None, memory: Optional[List[Dict]] = None) -> str:
        messages = []
        if memory:
            messages.extend(memory)
        if context:
            messages.append({"role": "system", "content": "Context: " + str(context)})
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message["content"]