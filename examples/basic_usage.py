#!/usr/bin/env python3
"""Basic usage examples for Chrome Extension Info."""

from chrome_extension_info import ChromeWebStoreClient, ExtensionNotFoundError, ChromeExtensionInfoError


def main():
    """Run basic usage examples."""
    # Create a client
    client = ChromeWebStoreClient()

    print("Chrome Extension Info - Chrome Extension Metadata Fetcher")
    print("=" * 50)
    print()

    # Example 1: Fetch extension by ID
    print("Example 1: Fetching extension by ID")
    print("-" * 30)

    # Google Translate extension ID
    extension_id = "aapbdbdomjkkjkaonfhkkikfgjllcleb"

    try:
        extension = client.get_extension(extension_id)
        print(f"ID: {extension.id}")
        print(f"Name: {extension.name}")
        print(f"Version: {extension.version}")
        print(f"Developer: {extension.developer}")
        print(
            f"Users: {extension.user_count:,}"
            if extension.user_count
            else "Users: Unknown"
        )
        print(
            f"Rating: ★{extension.rating:.1f}"
            if extension.rating
            else "Rating: Not available"
        )
        print(f"Category: {extension.category}")
        print(f"Last Updated: {extension.last_updated}")
        print()
    except ExtensionNotFoundError:
        print(f"Extension '{extension_id}' not found!")
    except ChromeExtensionInfoError as e:
        print(f"Error: {e}")

    # Example 2: Fetch extension by URL
    print("\nExample 2: Fetching extension by URL")
    print("-" * 30)

    url = "https://chromewebstore.google.com/detail/google-translate/aapbdbdomjkkjkaonfhkkikfgjllcleb"

    try:
        extension = client.get_extension_by_url(url)
        print(f"Extension: {extension}")
        print(
            f"Description: {extension.description[:100]}..."
            if extension.description
            else "No description"
        )
        print()
    except ChromeExtensionInfoError as e:
        print(f"Error: {e}")

    # Example 3: Using cache
    print("\nExample 3: Demonstrating cache behavior")
    print("-" * 30)

    print("First request (will fetch from web)...")
    extension1 = client.get_extension("aapbdbdomjkkjkaonfhkkikfgjllcleb")
    print(f"Got: {extension1.name}")

    print("Second request (should use cache)...")
    extension2 = client.get_extension("aapbdbdomjkkjkaonfhkkikfgjllcleb")
    print(f"Got: {extension2.name}")
    print("(Both requests returned the same data)")
    print()

    # Example 4: Error handling
    print("\nExample 4: Error handling")
    print("-" * 30)

    try:
        client.get_extension("invalid-extension-id-12345")
    except ExtensionNotFoundError:
        print("✓ Correctly caught ExtensionNotFoundError")

    # Example 5: Getting full metadata
    print("\nExample 5: Full metadata as dictionary")
    print("-" * 30)

    extension = client.get_extension("aapbdbdomjkkjkaonfhkkikfgjllcleb")
    metadata = extension.to_dict()

    # Print some interesting fields
    print("Available metadata fields:")
    for key in sorted(metadata.keys()):
        value = metadata[key]
        if (
            value
            and not isinstance(value, (list, dict))
            or (isinstance(value, list) and value)
        ):
            print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()
