# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-07

### Changed
- **BREAKING**: Renamed package from `chromepy` to `chrome-extension-info`
- **BREAKING**: Renamed `ChromePyError` to `ChromeExtensionInfoError`
- Updated repository URL to https://github.com/karansbir/chrome-extension-info
- Updated package maintainer email

## [0.2.0] - 2024-12-07

### Added
- Chrome Web Store metadata fetching functionality
- ChromeWebStoreClient class for web scraping
- ExtensionMetadata and SearchResult data models
- Built-in caching with configurable TTL
- Rate limiting for respectful API usage
- Comprehensive error handling with custom exceptions
- Support for fetching by extension ID or Chrome Web Store URL
- HTML parsing and JSON data extraction from embedded JavaScript
- Full test suite with 18 tests

### Changed
- Complete refactor from local file parsing to web store fetching
- Updated package description and documentation
- Replaced manifest parsing with web store metadata extraction

### Removed
- Local file parsing functionality (parser.py, manifest.py, validator.py)
- Manifest validation for local files

## [0.1.0] - 2024-12-06

### Added
- Initial project structure
- Local Chrome extension manifest parsing
- Manifest validation functionality
- Support for Manifest V2 and V3
- Basic documentation and examples