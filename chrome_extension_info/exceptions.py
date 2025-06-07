"""Custom exceptions for ChromePy."""


class ChromeExtensionInfoError(Exception):
    """Base exception for all ChromePy errors."""

    pass


class ExtensionNotFoundError(ChromeExtensionInfoError):
    """Raised when an extension is not found in the Chrome Web Store."""

    pass


class NetworkError(ChromeExtensionInfoError):
    """Raised when a network request fails."""

    pass


class RateLimitError(ChromeExtensionInfoError):
    """Raised when rate limiting is exceeded."""

    pass


class ParseError(ChromeExtensionInfoError):
    """Raised when parsing response data fails."""

    pass
