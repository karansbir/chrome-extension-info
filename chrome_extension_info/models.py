"""Data models for Chrome Web Store extension metadata."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ExtensionMetadata:
    """Metadata for a Chrome extension from the Chrome Web Store."""

    # Basic information
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None

    # Developer information
    developer: Optional[str] = None
    developer_website: Optional[str] = None
    support_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None

    # Store statistics
    user_count: Optional[int] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None

    # Categories and classification
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Technical details
    size: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    manifest_version: Optional[int] = None

    # Dates
    last_updated: Optional[str] = None
    published_date: Optional[str] = None

    # Visual assets
    icon_url: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)

    # Permissions (if available)
    permissions: List[str] = field(default_factory=list)
    host_permissions: List[str] = field(default_factory=list)

    # Additional metadata
    featured: bool = False
    is_theme: bool = False
    is_app: bool = False
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "developer": self.developer,
            "developer_website": self.developer_website,
            "support_url": self.support_url,
            "privacy_policy_url": self.privacy_policy_url,
            "user_count": self.user_count,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "category": self.category,
            "tags": self.tags,
            "size": self.size,
            "languages": self.languages,
            "manifest_version": self.manifest_version,
            "last_updated": self.last_updated,
            "published_date": self.published_date,
            "icon_url": self.icon_url,
            "screenshots": self.screenshots,
            "permissions": self.permissions,
            "host_permissions": self.host_permissions,
            "featured": self.featured,
            "is_theme": self.is_theme,
            "is_app": self.is_app,
            "additional_data": self.additional_data,
        }

    def __str__(self) -> str:
        """String representation of the extension metadata."""
        parts = [f"{self.name or 'Unknown'} ({self.id})"]
        if self.version:
            parts.append(f"v{self.version}")
        if self.user_count:
            parts.append(f"{self.user_count:,} users")
        if self.rating:
            parts.append(f"★{self.rating:.1f}")
        return " - ".join(parts)


@dataclass
class SearchResult:
    """Result from a Chrome Web Store search."""

    extensions: List[ExtensionMetadata]
    total_results: Optional[int] = None
    query: Optional[str] = None

    def __len__(self) -> int:
        """Return the number of extensions in the result."""
        return len(self.extensions)

    def __iter__(self):
        """Iterate over the extensions."""
        return iter(self.extensions)

    def __getitem__(self, index: int) -> ExtensionMetadata:
        """Get an extension by index."""
        return self.extensions[index]
