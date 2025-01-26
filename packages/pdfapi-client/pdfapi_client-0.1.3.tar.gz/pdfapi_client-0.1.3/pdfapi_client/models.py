from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, BinaryIO, Dict
from pathlib import Path

# Constants for header/footer filenames
HEADER_FILENAME = "header.html"
FOOTER_FILENAME = "footer.html"

class PageFormat(str, Enum):
    """Available page formats for PDF conversion."""
    LETTER = "Letter"
    LEGAL = "Legal"
    TABLOID = "Tabloid"
    LEDGER = "Ledger"
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    A6 = "A6"

@dataclass
class Margin:
    """Page margins in pixels."""
    top: int = 0
    bottom: int = 0
    left: int = 0
    right: int = 0

@dataclass
class ConversionConfig:
    """Configuration for PDF conversion."""
    scale: float = 1.0
    margin: Margin = field(default_factory=Margin)
    format: Optional[PageFormat] = None
    landscape: bool = False
    header_file: Optional[Union[str, bytes, BinaryIO, Path]] = None
    footer_file: Optional[Union[str, bytes, BinaryIO, Path]] = None

    def to_dict(self) -> dict:
        """Convert config to dictionary for API request."""
        data = {
            "scale": self.scale,
            "margin": {
                "top": self.margin.top,
                "bottom": self.margin.bottom,
                "left": self.margin.left,
                "right": self.margin.right
            },
            "landscape": self.landscape
        }
        if self.format:
            data["format"] = self.format.value
        if self.header_file:
            data["headerFile"] = HEADER_FILENAME
        if self.footer_file:
            data["footerFile"] = FOOTER_FILENAME
        return data

    def get_additional_assets(self) -> Dict[str, Union[str, bytes, BinaryIO, Path]]:
        """Get header and footer files as assets."""
        assets = {}
        if self.header_file:
            assets[HEADER_FILENAME] = self.header_file
        if self.footer_file:
            assets[FOOTER_FILENAME] = self.footer_file
        return assets 