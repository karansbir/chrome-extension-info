"""Chrome Web Store client for fetching extension metadata."""

import re
import json
import time
from typing import Dict, Optional, Any
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

from .exceptions import ChromeExtensionInfoError, ExtensionNotFoundError
from .models import ExtensionMetadata


class ChromeWebStoreClient:
    """Client for fetching Chrome extension metadata from the Chrome Web Store."""

    BASE_URL = "https://chrome.google.com/webstore/detail/"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self, cache_ttl: int = 3600, rate_limit_delay: float = 1.0):
        """Initialize the Chrome Web Store client.

        Args:
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
            rate_limit_delay: Delay between requests in seconds (default 1 second)
        """
        self.cache_ttl = cache_ttl
        self.rate_limit_delay = rate_limit_delay
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
        )

    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        self._last_request_time = time.time()

    def _get_from_cache(self, extension_id: str) -> Optional[Dict[str, Any]]:
        """Get extension data from cache if available and not expired."""
        if extension_id in self._cache:
            cached_data = self._cache[extension_id]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["data"]
        return None

    def _save_to_cache(self, extension_id: str, data: Dict[str, Any]):
        """Save extension data to cache."""
        self._cache[extension_id] = {"data": data, "timestamp": time.time()}

    def _extract_json_data(self, html: str) -> Dict[str, Any]:
        """Extract JSON data embedded in the Chrome Web Store page."""
        # Look for the specific AF_initDataCallback line with ds:0 data
        pattern = r'AF_initDataCallback\(\{key:\s*[\'"]ds:0[\'"][^}]*data:\s*(\[\[[^\]]*(?:\[[^\]]*\][^\]]*)*\])'
        match = re.search(pattern, html, re.DOTALL)

        if match:
            try:
                data_str = match.group(1)
                # The data is a nested array, we want the first element
                data = json.loads(data_str)
                if data and len(data) > 0 and isinstance(data[0], list):
                    return self._parse_af_data(data[0])
            except (json.JSONDecodeError, IndexError):
                pass

        # Alternative approach: find the line directly
        for line in html.split("\n"):
            if "AF_initDataCallback" in line and "ds:0" in line and "data:" in line:
                # Extract the data array part
                start = line.find("data:")
                if start != -1:
                    start = line.find("[[", start)
                    if start != -1:
                        # Find the end of the data array
                        bracket_count = 0
                        end = start
                        for i, char in enumerate(line[start:]):
                            if char == "[":
                                bracket_count += 1
                            elif char == "]":
                                bracket_count -= 1
                                if bracket_count == 0:
                                    end = start + i + 1
                                    break

                        if end > start:
                            try:
                                data_str = line[start:end]
                                data = json.loads(data_str)
                                if data and len(data) > 0 and isinstance(data[0], list):
                                    return self._parse_af_data(data[0])
                            except (json.JSONDecodeError, IndexError):
                                pass

        return {}

    def _parse_af_data(self, data: list) -> Dict[str, Any]:
        """Parse the AF_initDataCallback data array."""
        parsed = {}

        try:
            # Based on the actual data structure from Chrome Web Store:
            # data[0] = extension_id
            # data[1] = icon_url
            # data[2] = name
            # data[3] = rating (float)
            # data[4] = rating_count (int)
            # data[5] = null
            # data[6] = description
            # data[7-11] = various nulls and other data
            # data[12] = category info (array like ["productivity/workflow", null, 4])
            # data[13] = some flag
            # data[14] = some flag
            # data[15] = user_count (int)
            # data[18] = manifest string (if available)
            # data[25] = version string

            if len(data) > 0 and data[0]:
                parsed["id"] = data[0]
            if len(data) > 1 and data[1]:
                parsed["icon_url"] = data[1]
            if len(data) > 2 and data[2]:
                parsed["name"] = data[2]
            if len(data) > 3 and isinstance(data[3], (int, float)):
                parsed["rating"] = float(data[3])
            if len(data) > 4 and isinstance(data[4], (int, float)):
                parsed["rating_count"] = int(data[4])
            if len(data) > 6 and data[6]:
                parsed["description"] = data[6]
            if (
                len(data) > 12
                and data[12]
                and isinstance(data[12], list)
                and len(data[12]) > 0
            ):
                # Category is often nested: ["productivity/workflow", null, 4]
                category_data = data[12][0] if data[12][0] else ""
                if isinstance(category_data, str):
                    # Clean up category (remove subcategory)
                    category_parts = category_data.split("/")
                    parsed["category"] = (
                        category_parts[0].title() if category_parts else category_data
                    )
            if len(data) > 15 and isinstance(data[15], (int, float)):
                parsed["user_count"] = int(data[15])

            # Try to extract version from position 25 first, then from manifest
            if len(data) > 25 and data[25] and isinstance(data[25], str):
                if re.match(r"\d+\.\d+", data[25]):
                    parsed["version"] = data[25]
            elif len(data) > 18 and data[18] and isinstance(data[18], str):
                # Try to extract version from manifest JSON
                try:
                    manifest = json.loads(data[18])
                    if "version" in manifest:
                        parsed["version"] = manifest["version"]
                except (json.JSONDecodeError, TypeError):
                    pass

        except (IndexError, TypeError, ValueError):
            pass

        return parsed

    def _parse_user_count(self, user_count_str: str) -> int:
        """Parse user count string to integer."""
        if not user_count_str:
            return 0

        # Remove commas and plus signs
        clean_str = user_count_str.replace(",", "").replace("+", "").strip()

        # Extract number
        match = re.search(r"(\d+)", clean_str)
        if match:
            return int(match.group(1))
        return 0

    def _extract_metadata_from_html(
        self, html: str, extension_id: str
    ) -> Dict[str, Any]:
        """Extract metadata from the HTML page."""
        soup = BeautifulSoup(html, "html.parser")
        metadata = {"id": extension_id}

        # Extract title from h1 tags
        h1_elements = soup.find_all("h1")
        if h1_elements:
            metadata["name"] = h1_elements[0].get_text().strip()

        # Extract description from meta tag
        desc_meta = soup.find("meta", attrs={"name": "description"})
        if desc_meta and desc_meta.get("content"):
            metadata["description"] = desc_meta["content"].strip()

        # Extract rating from aria-label
        rating_elements = soup.find_all(
            attrs={"aria-label": re.compile(r".*out of.*star.*", re.I)}
        )
        if rating_elements:
            # Take the first rating (should be the main extension rating)
            aria_label = rating_elements[0].get("aria-label", "")
            rating_match = re.search(r"(\d+\.?\d*)\s*out of", aria_label)
            if rating_match:
                metadata["rating"] = float(rating_match.group(1))

            # Extract rating count
            count_match = re.search(
                r"(\d+(?:,\d+)*(?:\.\d+)?)\s*[KMB]?\s*rating", aria_label, re.I
            )
            if count_match:
                count_str = count_match.group(1).replace(",", "")
                # Handle K, M, B suffixes
                if "K" in aria_label.upper():
                    metadata["rating_count"] = int(float(count_str) * 1000)
                elif "M" in aria_label.upper():
                    metadata["rating_count"] = int(float(count_str) * 1000000)
                elif "B" in aria_label.upper():
                    metadata["rating_count"] = int(float(count_str) * 1000000000)
                else:
                    metadata["rating_count"] = int(float(count_str))

        # Extract user count from page text
        all_text = soup.get_text()
        user_patterns = [r"(\d+(?:,\d+)*)\s*users?", r"(\d+(?:,\d+)*)\s*installs?"]

        for pattern in user_patterns:
            matches = re.findall(pattern, all_text, re.I)
            if matches:
                # Take the largest number found (likely the main user count)
                user_counts = [int(match.replace(",", "")) for match in matches]
                metadata["user_count"] = max(user_counts)
                break

        # Extract developer from links
        dev_links = soup.find_all("a", href=re.compile(r"/developer/"))
        if dev_links:
            metadata["developer"] = dev_links[0].get_text().strip()

        return metadata

    def get_extension(self, extension_id: str) -> ExtensionMetadata:
        """Fetch metadata for a Chrome extension.

        Args:
            extension_id: The Chrome Web Store extension ID

        Returns:
            ExtensionMetadata object with all available information

        Raises:
            ExtensionNotFoundError: If the extension is not found
            ChromeExtensionInfoError: If there's an error fetching or parsing data
        """
        # Check cache first
        cached_data = self._get_from_cache(extension_id)
        if cached_data:
            return ExtensionMetadata(**cached_data)

        # Enforce rate limiting
        self._enforce_rate_limit()

        # Build URL
        url = f"{self.BASE_URL}{extension_id}"

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 404:
                raise ExtensionNotFoundError(f"Extension '{extension_id}' not found")
            response.raise_for_status()
        except ExtensionNotFoundError:
            raise  # Re-raise our custom exception
        except Exception as e:
            raise ChromeExtensionInfoError(f"Error fetching extension data: {str(e)}")

        # Extract metadata
        try:
            # Start with HTML data
            metadata_dict = self._extract_metadata_from_html(
                response.text, extension_id
            )

            # Try to get additional data from embedded JSON
            try:
                json_data = self._extract_json_data(response.text)
                # Merge JSON data, giving priority to JSON data when available
                for key, value in json_data.items():
                    if value is not None:  # Only override if JSON has actual data
                        metadata_dict[key] = value
            except Exception:
                # If we can't extract JSON, continue with HTML data only
                pass

            # Save to cache
            self._save_to_cache(extension_id, metadata_dict)

            return ExtensionMetadata(**metadata_dict)

        except Exception as e:
            raise ChromeExtensionInfoError(f"Error parsing extension data: {str(e)}")

    def search_extensions(
        self, query: str, max_results: int = 10
    ) -> list[ExtensionMetadata]:
        """Search for extensions in the Chrome Web Store.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of ExtensionMetadata objects
        """
        # This would require implementing search functionality
        # For now, this is a placeholder
        raise NotImplementedError("Search functionality not yet implemented")

    def get_extension_by_url(self, url: str) -> ExtensionMetadata:
        """Fetch extension metadata from a Chrome Web Store URL.

        Args:
            url: Full Chrome Web Store URL

        Returns:
            ExtensionMetadata object
        """
        # Extract extension ID from URL
        # Handle both old and new Chrome Web Store URL formats
        patterns = [
            r"/detail/[^/]+/([a-z]{32})",  # /detail/extension-name/id
            r"/detail/([a-z]{32})",  # /detail/id
            r"[?&]id=([a-z]{32})",  # ?id=extension_id
            r"/([a-z]{32})(?:[/?]|$)",  # Just the ID at end of path
        ]

        match = None
        for pattern in patterns:
            match = re.search(pattern, url, re.I)
            if match:
                break

        if not match:
            raise ChromeExtensionInfoError("Invalid Chrome Web Store URL")

        extension_id = match.group(1)
        return self.get_extension(extension_id)
