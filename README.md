# ChromePy

A Python package for fetching Chrome extension metadata from the Chrome Web Store.

## Features

- 🔍 **Fetch extension metadata** - Get detailed information about any Chrome extension
- 📊 **Rich metadata** - Ratings, user count, version, permissions, and more
- 🚀 **Simple API** - Easy to use with just an extension ID or URL
- 💾 **Built-in caching** - Reduces requests and improves performance
- ⏱️ **Rate limiting** - Respectful of Chrome Web Store servers
- 🐍 **Type hints** - Full type annotations for better IDE support

## Installation

```bash
pip install chromepy
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from chrome_extension_info import ChromeWebStoreClient

# Create a client
client = ChromeWebStoreClient()

# Fetch extension metadata by ID
extension = client.get_extension("aapbdbdomjkkjkaonfhkkikfgjllcleb")
print(f"{extension.name} - {extension.user_count:,} users, ★{extension.rating}")

# Or fetch by Chrome Web Store URL
url = "https://chrome.google.com/webstore/detail/google-translate/aapbdbdomjkkjkaonfhkkikfgjllcleb"
extension = client.get_extension_by_url(url)
print(extension.to_dict())
```

## Available Metadata

ChromePy can fetch the following information about extensions:

- **Basic Info**: Name, description, version, extension ID
- **Developer**: Developer name, website, support URL, privacy policy
- **Stats**: User count, rating, number of ratings
- **Technical**: Size, languages, manifest version, permissions
- **Store Info**: Category, last updated date, featured status
- **Assets**: Icon URL, screenshot URLs

## API Reference

### ChromeWebStoreClient

The main client for interacting with the Chrome Web Store.

```python
client = ChromeWebStoreClient(
    cache_ttl=3600,        # Cache duration in seconds (default: 1 hour)
    rate_limit_delay=1.0   # Delay between requests in seconds (default: 1 second)
)
```

#### Methods

- `get_extension(extension_id: str) -> ExtensionMetadata`: Fetch metadata for an extension
- `get_extension_by_url(url: str) -> ExtensionMetadata`: Fetch metadata from a Chrome Web Store URL
- `search_extensions(query: str, max_results: int = 10) -> List[ExtensionMetadata]`: Search for extensions (not yet implemented)

### ExtensionMetadata

The data model containing all extension information.

```python
@dataclass
class ExtensionMetadata:
    id: str
    name: Optional[str]
    description: Optional[str]
    version: Optional[str]
    developer: Optional[str]
    user_count: Optional[int]
    rating: Optional[float]
    # ... and many more fields
```

## Examples

### Get detailed information about an extension

```python
from chrome_extension_info import ChromeWebStoreClient

client = ChromeWebStoreClient()

# Google Translate
extension = client.get_extension("aapbdbdomjkkjkaonfhkkikfgjllcleb")

print(f"Name: {extension.name}")
print(f"Version: {extension.version}")
print(f"Users: {extension.user_count:,}")
print(f"Rating: {extension.rating} ({extension.rating_count} reviews)")
print(f"Category: {extension.category}")
print(f"Last Updated: {extension.last_updated}")
print(f"Size: {extension.size}")
```

### Cache behavior

```python
# First call fetches from Chrome Web Store
extension1 = client.get_extension("extension-id")  # Network request

# Second call within cache TTL returns cached data
extension2 = client.get_extension("extension-id")  # From cache, no network request
```

### Error handling

```python
from chrome_extension_info import ChromeWebStoreClient, ExtensionNotFoundError, ChromeExtensionInfoError

client = ChromeWebStoreClient()

try:
    extension = client.get_extension("invalid-extension-id")
except ExtensionNotFoundError:
    print("Extension not found in Chrome Web Store")
except ChromeExtensionInfoError as e:
    print(f"An error occurred: {e}")
```

## Exceptions

- `ChromeExtensionInfoError`: Base exception for all ChromePy errors
- `ExtensionNotFoundError`: Extension not found in the Chrome Web Store
- `NetworkError`: Network request failed
- `RateLimitError`: Rate limiting exceeded
- `ParseError`: Failed to parse response data

## Development

### Setup

```bash
git clone https://github.com/karansbir/chromepy.git
cd chromepy
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black chromepy tests
```

### Type Checking

```bash
mypy chromepy
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.