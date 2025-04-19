# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-04-19

### Added
- Mock data generation feature
  - Support for various data types:
    - Basic types (string, integer, number, boolean)
    - Special types (email, phone, url, objectId)
    - Date formats
    - Arrays with type inference
  - Example JSON structure in UI
  - History of generated datasets
  - Export functionality
- Type definitions generation for:
  - Python
  - Golang
  - TypeScript
- CSV export functionality for Excel compatibility
- Smart type inference based on:
  - Field names
  - Example values
  - Common patterns

### Changed
- Improved UI with expandable sections
- Enhanced documentation
- Better error handling for data generation
- Updated internationalization strings

### Fixed
- Duplicate widget keys in Streamlit interface
- Type inference for array structures
- Session state management for history

## [0.0.1] - 2025-04-18

### Added
- Initial release
- JSON formatting with syntax highlighting
- AI-powered JSON analysis using Groq
- JSON comparison functionality
- Basic internationalization (English/Spanish)
- Session state management
