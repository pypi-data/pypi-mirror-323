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

    @property
    def supports_vision(self) -> bool:
        """
        Check if the model supports vision tasks.
        """
        # List of Groq models that support vision
        vision_models = [
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision-preview"
        ]
        return self.model in vision_models

    def generate(self, prompt: str, context: Optional[List[Dict]] = None, memory: Optional[List[Dict]] = None) -> str:
        """
        Generate a response to a text-based prompt.
        """
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

    def generate_from_image(self, image_bytes: bytes, **kwargs) -> str:
        """
        Process an image and generate a response if the model supports vision.
        """
        if not self.supports_vision:
            raise ValueError(f"Model '{self.model}' does not support vision tasks.")

        try:
            # Call the Groq API with the image
            response = self.client.vision.completions.create(
                model=self.model,
                image=image_bytes,
                **kwargs,
            )
            return response.choices[0].text
        except Exception as e:
            raise ValueError(f"Error while processing image with Groq vision model: {e}")
