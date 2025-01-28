# image_to_text.py
from .base_tool import BaseTool
from PIL import Image
import pytesseract
import requests
import io
import os
from typing import Dict, Any, List, Union

class ImageToTextTool(BaseTool):
    def __init__(self, **kwargs):
        super().__init__(
            name="ImageToTextTool",
            description="Extract text from images using OCR. Supports both URLs and local file paths.",
            **kwargs
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text from one or more images using OCR.

        Args:
            input_data (Dict[str, Any]): Input data containing either:
                - "image_url": A single image URL or a list of image URLs.
                - "image_path": A single local file path or a list of file paths.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted text or an error message.
        """
        try:
            # Check if the input contains image URLs or local file paths
            image_urls = input_data.get("image_url", [])
            image_paths = input_data.get("image_path", [])

            # Ensure inputs are lists
            if isinstance(image_urls, str):
                image_urls = [image_urls]
            if isinstance(image_paths, str):
                image_paths = [image_paths]

            # Combine all image sources
            all_images = image_urls + image_paths

            if not all_images:
                return {"error": "No image URLs or file paths provided."}

            results = {}

            for image_source in all_images:
                try:
                    # Load the image
                    if image_source.startswith(("http://", "https://")):
                        # Load image from URL
                        response = requests.get(image_source)
                        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
                        image_bytes = response.content
                        image = Image.open(io.BytesIO(image_bytes))
                    else:
                        # Load image from local file path
                        if not os.path.exists(image_source):
                            results[image_source] = {"error": f"File not found: {image_source}"}
                            continue
                        image = Image.open(image_source)

                    # Extract text using OCR
                    extracted_text = pytesseract.image_to_string(image)

                    # Store the result
                    results[image_source] = {"extracted_text": extracted_text}

                except Exception as e:
                    results[image_source] = {"error": str(e)}

            return results

        except Exception as e:
            return {"error": str(e)}