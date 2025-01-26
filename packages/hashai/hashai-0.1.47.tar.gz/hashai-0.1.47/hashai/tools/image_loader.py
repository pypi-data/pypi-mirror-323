from .base_tool import BaseTool
from PIL import Image
import requests
import io
from typing import Dict, Any

class ImageLoaderTool(BaseTool):
    def __init__(self, **kwargs):
        super().__init__(
            name="ImageLoaderTool",
            description="Load images from URLs and return them as PIL Image objects.",
            **kwargs
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load an image from a URL and return it as a PIL Image object.

        Args:
            input_data (Dict[str, Any]): Input data containing the image URL.

        Returns:
            Dict[str, Any]: A dictionary containing the PIL Image object or an error message.
        """
        try:
            image_url = input_data.get("image_url")
            if not image_url:
                return {"error": "No image URL provided."}

            # Fetch the image from the URL
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            image_bytes = response.content

            # Convert the image bytes to a PIL Image object
            image = Image.open(io.BytesIO(image_bytes))

            return {"image": image}
        except Exception as e:
            return {"error": str(e)}