from .base_tool import BaseTool
from .image_loader import ImageLoaderTool
import pytesseract
from typing import Dict, Any

class TextExtractorTool(BaseTool):
    def __init__(self, image_loader_tool: ImageLoaderTool, **kwargs):
        super().__init__(
            name="TextExtractorTool",
            description="Extract text from images using OCR.",
            **kwargs
        )
        self.image_loader_tool = image_loader_tool

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text from an image using OCR.

        Args:
            input_data (Dict[str, Any]): Input data containing the image URL.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted text or an error message.
        """
        try:
            # Load the image using the ImageLoaderTool
            image_response = self.image_loader_tool.execute(input_data)
            if "error" in image_response:
                return image_response  # Return the error if image loading failed

            # Extract text using OCR
            image = image_response["image"]
            extracted_text = pytesseract.image_to_string(image)

            return {"extracted_text": extracted_text}
        except Exception as e:
            return {"error": str(e)}