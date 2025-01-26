# qrcode.py
from .base_tool import BaseTool
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SquareGradiantColorMask
from typing import Dict, Any, Optional
import os
from datetime import datetime

class QRCodeGenerator(BaseTool):
    def __init__(
        self,
        default_format: str = "png",  # Default output format
        enable_custom_design: bool = True,  # Enable custom QR code designs
        enable_error_correction: bool = True,  # Enable error correction levels
        enable_dynamic_naming: bool = True,  # Enable dynamic file naming
    ):
        """
        Initialize the QRCodeGenerator tool with customizable options.

        Args:
            default_format (str): Default output format (e.g., "png", "svg").
            enable_custom_design (bool): Enable custom QR code designs (e.g., colors, shapes).
            enable_error_correction (bool): Enable error correction levels.
            enable_dynamic_naming (bool): Enable dynamic file naming.
        """
        super().__init__(
            name="QRCodeGenerator",
            description="Generate customizable QR codes for a given text or URL."
        )
        self.default_format = default_format
        self.enable_custom_design = enable_custom_design
        self.enable_error_correction = enable_error_correction
        self.enable_dynamic_naming = enable_dynamic_naming

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a QR code based on the provided input.

        Args:
            input_data (Dict[str, Any]): Input data containing the text/URL and optional parameters.

        Returns:
            Dict[str, Any]: Status and file path of the generated QR code.
        """
        data = input_data.get("data")
        if not data:
            return {"error": "No data provided for QR code generation."}

        # Customize QR code design
        qr = qrcode.QRCode(
            version=1,
            error_correction=self._get_error_correction(input_data.get("error_correction")),
            box_size=input_data.get("box_size", 10),
            border=input_data.get("border", 4),
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Generate QR code image
        img = self._generate_image(qr, input_data)

        # Save QR code to file
        file_path = self._get_file_path(input_data.get("file_name"), input_data.get("format"))
        img.save(file_path)

        return {"status": "QR code generated successfully.", "file_path": file_path}

    def _get_error_correction(self, level: Optional[str]) -> int:
        """
        Get the error correction level for the QR code.

        Args:
            level (Optional[str]): Error correction level (e.g., "L", "M", "Q", "H").

        Returns:
            int: Error correction level code.
        """
        if not self.enable_error_correction:
            return qrcode.constants.ERROR_CORRECT_L  # Default to low error correction

        levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,  # 7% error correction
            "M": qrcode.constants.ERROR_CORRECT_M,  # 15% error correction
            "Q": qrcode.constants.ERROR_CORRECT_Q,  # 25% error correction
            "H": qrcode.constants.ERROR_CORRECT_H,  # 30% error correction
        }
        return levels.get(level, qrcode.constants.ERROR_CORRECT_L)

    def _generate_image(self, qr: qrcode.QRCode, input_data: Dict[str, Any]) -> Any:
        """
        Generate the QR code image with optional custom design.

        Args:
            qr (qrcode.QRCode): The QR code object.
            input_data (Dict[str, Any]): Input data containing design options.

        Returns:
            Any: The generated QR code image.
        """
        if not self.enable_custom_design:
            return qr.make_image(fill_color="black", back_color="white")

        # Custom design options
        fill_color = input_data.get("fill_color", "black")
        back_color = input_data.get("back_color", "white")
        module_drawer = self._get_module_drawer(input_data.get("module_shape"))
        color_mask = self._get_color_mask(input_data.get("color_style"))

        return qr.make_image(
            image_factory=StyledPilImage,
            fill_color=fill_color,
            back_color=back_color,
            module_drawer=module_drawer,
            color_mask=color_mask,
        )

    def _get_module_drawer(self, shape: Optional[str]) -> Any:
        """
        Get the module drawer for custom QR code shapes.

        Args:
            shape (Optional[str]): Module shape (e.g., "circle", "square").

        Returns:
            Any: The module drawer object.
        """
        shapes = {
            "circle": CircleModuleDrawer(),
            "square": SquareModuleDrawer(),
        }
        return shapes.get(shape, SquareModuleDrawer())  # Default to square

    def _get_color_mask(self, style: Optional[str]) -> Any:
        """
        Get the color mask for custom QR code styles.

        Args:
            style (Optional[str]): Color style (e.g., "radial", "square").

        Returns:
            Any: The color mask object.
        """
        styles = {
            "radial": RadialGradiantColorMask(),
            "square": SquareGradiantColorMask(),
        }
        return styles.get(style, None)  # Default to no color mask

    def _get_file_path(self, file_name: Optional[str], format: Optional[str]) -> str:
        """
        Generate a file path for the QR code image.

        Args:
            file_name (Optional[str]): Custom file name.
            format (Optional[str]): File format (e.g., "png", "svg").

        Returns:
            str: The file path.
        """
        if not self.enable_dynamic_naming:
            return "qrcode.png"  # Default file name

        # Generate a dynamic file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = file_name or f"qrcode_{timestamp}"
        format = format or self.default_format
        return f"{file_name}.{format}"