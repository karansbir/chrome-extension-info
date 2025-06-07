"""Chrome Extension Info - A Python package for fetching Chrome extension metadata from the Chrome Web Store."""

__version__ = "0.2.1"

from .client import ChromeWebStoreClient
from .models import ExtensionMetadata, SearchResult
from .exceptions import (
    ChromeExtensionInfoError,
    ExtensionNotFoundError,
    NetworkError,
    RateLimitError,
    ParseError,
)

__all__ = [
    "ChromeWebStoreClient",
    "ExtensionMetadata",
    "SearchResult",
    "ChromeExtensionInfoError",
    "ExtensionNotFoundError",
    "NetworkError",
    "RateLimitError",
    "ParseError",
]
