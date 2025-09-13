# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-09-13

### Added
- AGENTS.md contributor guide with structure, commands, style, and PR tips

### Fixed
- Tests aligned with stored JSON wrapper format ({"formulas": [...]})
- No functional changes; documentation and test expectations only

## [0.2.0] - 2025-09-13

### Added
- Comprehensive type annotations for all methods
- MyPy strict mode compliance
- Specific exception handling for different error types
- Consistent data storage format with wrapper dictionary
- Code quality standards documentation in CLAUDE.md

### Changed
- Improved error messages to be more specific about failure types
- User-Agent header now uses actual GitHub repository URL
- Data storage format now uses `{"formulas": [...]}` wrapper for consistency
- Updated shebang line to proper format with space after `#`

### Removed
- Unused `click` dependency from requirements
- Unused imports: `timedelta`, `Set`, `os`

### Fixed
- Type safety issues with API response handling
- Data format inconsistency between save and load operations
- Test compatibility with new data format
- Line length issues for flake8 compliance

### Developer Experience
- All code now formatted with Black (88-character line limit)
- Flake8 compliance with no warnings
- MyPy strict mode passes with no errors
- All 31 tests pass successfully

## [0.1.0] - Initial Release

### Added
- Basic formula fetching from Homebrew API
- Local caching of formula data
- Change tracking (new/updated/removed formulas)
- Beautiful terminal output with Rich library
- Comprehensive test suite
- Support for multiple commands: update, diff, new
- Debug mode for troubleshooting
