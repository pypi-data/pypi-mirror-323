"""
pdfapi.dev - Python client for pdfapi.dev HTML to PDF conversion service
"""

from .client import PDFApiClient
from .models import ConversionConfig, Margin, PageFormat

__version__ = "0.1.0"
__all__ = ["PDFApiClient", "ConversionConfig", "Margin", "PageFormat"] 