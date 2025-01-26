from typing import List, Dict, Optional
from .base_llm import BaseLLM
import groq
import os

class GroqLlm(BaseLLM):
    def __init__(
        self,
        model: str = "mixtral-8x7b-32768",  # Default Groq model
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass it explicitly.")
        self.client = groq.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        memory: Optional[List[Dict]] = None,
    ) -> str:
        # Prepare messages for the Groq API
        messages = []
        if memory:
            messages.extend(memory)
        if context:
            messages.append({"role": "system", "content": "Context: " + str(context)})
        messages.append({"role": "user", "content": prompt})

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        # Extract and return the response
        return response.choices[0].message.content