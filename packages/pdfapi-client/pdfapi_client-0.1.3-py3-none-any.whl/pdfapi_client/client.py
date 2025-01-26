import time
import logging
from typing import Dict, Optional, Union, BinaryIO, TextIO
import requests
from urllib.parse import urljoin
from pathlib import Path
from .models import ConversionConfig, Margin, PageFormat

logger = logging.getLogger(__name__)

class ConversionError(Exception):
    """Raised when conversion fails."""
    pass

class PDFApiClient:
    """Client for the PDF API service."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.pdfapi.dev"):
        """Initialize the client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the API (optional)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Api-Key": api_key
        })

    def convert_html(
        self,
        html: Union[str, TextIO, Path],
        assets: Optional[Dict[str, Union[str, bytes, BinaryIO, Path]]] = None,
        config: Optional[ConversionConfig] = None,
        max_retries: int = 10,
        retry_delay: float = 1.0
    ) -> bytes:
        """Convert HTML to PDF.
        
        Args:
            html: HTML content as string, file-like object, or Path to file
            assets: Dictionary mapping filenames to their content (as string, bytes, file-like object, or Path)
            config: Configuration for the conversion (format, margins, scale, etc.)
            max_retries: Maximum number of retries when polling for results
            retry_delay: Delay between retries in seconds
            
        Returns:
            bytes: The generated PDF file content
            
        Raises:
            ConversionError: If conversion fails
        """
        if config is None:
            config = ConversionConfig()

        # Initialize conversion
        conversion_id = self._initialize_conversion(config)
        logger.info(f"Initialized conversion with ID: {conversion_id}")

        try:
            # Upload header and footer files if provided
            additional_assets = config.get_additional_assets()
            if additional_assets:
                logger.info(f"Uploading header/footer files: {list(additional_assets.keys())}")
                for filename, content in additional_assets.items():
                    self._attach_asset(conversion_id, filename, content)

            # Upload regular assets if provided
            if assets:
                logger.info(f"Uploading assets: {list(assets.keys())}")
                for filename, content in assets.items():
                    self._attach_asset(conversion_id, filename, content)

            # Perform conversion
            logger.info("Starting conversion")
            self._perform_conversion(conversion_id, html)

            # Get result with retries
            logger.info("Fetching conversion result")
            return self._get_result(conversion_id, max_retries, retry_delay)
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise ConversionError(f"Conversion failed: {str(e)}") from e

    def _initialize_conversion(self, config: ConversionConfig) -> str:
        """Initialize a new conversion."""
        url = urljoin(self.base_url, "/api/conversions")
        data = config.to_dict()
        logger.debug(f"Initializing conversion at {url} with config: {data}")
        
        try:
            # Add Content-Type header only for JSON request
            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["id"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initialize conversion: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text}")
            raise

    def _read_content(self, content: Union[str, bytes, TextIO, BinaryIO, Path]) -> Union[str, bytes]:
        """Read content from various input types."""
        if isinstance(content, (str, bytes)):
            return content
        elif isinstance(content, Path):
            return content.read_text() if isinstance(content, TextIO) else content.read_bytes()
        elif hasattr(content, 'read'):
            return content.read()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def _attach_asset(self, conversion_id: str, filename: str, content: Union[str, bytes, BinaryIO, Path]) -> None:
        """Attach an asset to the conversion."""
        url = urljoin(self.base_url, f"/api/conversions/{conversion_id}/assets")
        logger.debug(f"Attaching asset {filename} to conversion {conversion_id}")
        
        # Remove Content-Type header for multipart requests
        headers = self.session.headers.copy()
        headers.pop('Content-Type', None)
        
        asset_content = self._read_content(content)
        if isinstance(asset_content, str):
            asset_content = asset_content.encode('utf-8')
            
        # Create multipart form-data with 'asset' as the part name
        files = {
            'asset': (filename, asset_content, 'application/octet-stream')
        }
        try:
            response = self.session.post(url, files=files, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to attach asset {filename}: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text}")
            raise

    def _perform_conversion(self, conversion_id: str, html: Union[str, TextIO, Path]) -> None:
        """Perform the conversion with the provided HTML."""
        url = urljoin(self.base_url, f"/api/conversions/{conversion_id}/convert")
        logger.debug(f"Performing conversion for {conversion_id}")
        
        # Remove Content-Type header for multipart requests
        headers = self.session.headers.copy()
        headers.pop('Content-Type', None)
        
        html_content = self._read_content(html)
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8')

        # Create multipart form-data with 'index' as the part name
        files = {
            'index': ('index.html', html_content.encode('utf-8'), 'text/html')
        }
        try:
            response = self.session.post(url, files=files, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to perform conversion: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text}")
            raise

    def _get_result(self, conversion_id: str, max_retries: int, retry_delay: float) -> bytes:
        """Get the conversion result with retries."""
        url = urljoin(self.base_url, f"/api/conversions/{conversion_id}")
        logger.debug(f"Fetching result for conversion {conversion_id}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, stream=True)
                
                if response.status_code == 200:
                    logger.info(f"Successfully fetched result after {attempt + 1} attempts")
                    return response.content
                elif response.status_code == 204:
                    logger.debug(f"Result not ready yet (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch result: {str(e)}")
                if hasattr(e.response, 'text'):
                    logger.error(f"Response content: {e.response.text}")
                raise

        raise ConversionError("Maximum retries exceeded while waiting for conversion result") 