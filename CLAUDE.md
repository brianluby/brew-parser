# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

brew-parser is a Python command-line tool that tracks changes in Homebrew formulas over time. It maintains a local database of formula information and compares it with the current state to show what's new, updated, or removed. The project emphasizes clean code with comprehensive inline comments and test coverage.

### Project Status
- **Current Version**: 0.2.0
- **Python Version**: 3.8+ (tested with 3.13)
- **License**: MIT
- **Repository**: https://github.com/bluby/brew-parser

## Key Commands

### Development Setup
```bash
# Always work in a virtual environment (required on macOS with Homebrew Python)
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### Running the Application
```bash
# First time setup - establish baseline
python brew_parser.py update

# Show newly added formulas only
python brew_parser.py new

# Show all changes (added/removed/updated)
python brew_parser.py diff

# Browse all formulas (original functionality)
python brew_parser.py --limit 10

# Debug mode for any command
python brew_parser.py update --debug
python brew_parser.py diff --debug
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=brew_parser

# Run specific test
pytest test_brew_parser.py::TestBrewParser::test_fetch_all_formulas_success -v

# Run tests matching a pattern
pytest -k "test_format" -v
```

### Code Quality
```bash
# Format code (automatically fixes formatting)
black brew_parser.py test_brew_parser.py

# Type checking (strict mode configured in pyproject.toml)
mypy brew_parser.py --strict

# Linting (88 character line limit for black compatibility)
flake8 brew_parser.py test_brew_parser.py --max-line-length=88
```

## Architecture

The project follows a modular architecture with clear separation of concerns:

### Core Components

- **BrewParser Class**: Main class handling all formula operations
  - `fetch_all_formulas()`: Retrieves complete formula list from Homebrew API
  - `get_formula_details()`: Fetches detailed info for specific formulas
  - `update_stored_formulas()`: Downloads and stores current formula state with hash-based change detection
  - `load_stored_formulas()`: Loads previously stored formula data from local cache
  - `compare_formulas()`: Performs three-way comparison (added/removed/updated)
  - `format_as_markdown()`: Converts data to rich markdown output
  - `format_diff_as_table()`: Creates color-coded tables for changes
  - `calculate_file_hash()`: SHA256 hashing for efficient change detection

### Command Handlers

- `handle_update_command()`: Updates local formula database
- `handle_diff_command()`: Shows all changes since last update
- `handle_new_command()`: Shows only newly added formulas
- `main()`: Router that dispatches to appropriate handlers based on subcommand

### Data Storage

- **Location**: `~/.brew-parser/`
- **Files**:
  - `formulas.json`: Complete formula data snapshot stored as `{"formulas": [...]}` wrapper object
  - `metadata.json`: Update timestamp, formula count, and SHA256 hash
- **Format Decision**: Data is wrapped in a dictionary to allow future extensibility (e.g., adding version info, source metadata)

### Testing Strategy

- Comprehensive unit tests with mocked API responses
- Mock context managers for Console.status
- Tests for all new methods and command handlers
- Edge case testing (empty lists, missing data, errors)

## Important Implementation Notes

1. **Change Detection**: Uses SHA256 file hashing to quickly detect if formula data has changed without parsing JSON.

2. **Date Filtering**: The `--days` parameter is a placeholder. Homebrew's API doesn't provide formula creation dates directly.

3. **Virtual Environment**: macOS with Homebrew Python requires virtual environments due to PEP 668. All pip commands must be run inside the activated venv.

4. **Rich Output**: Uses the Rich library for beautiful terminal output with color-coded tables and markdown rendering.

5. **API Etiquette**: Custom User-Agent header identifies our script to Homebrew's servers as `brew-parser/1.0 (https://github.com/bluby/brew-parser)`.

6. **Efficient Comparison**: Uses set operations and dictionary lookups for O(n) comparison performance.

7. **Error Handling**: All commands handle missing data gracefully with specific exception types:
   - `requests.RequestException` for network errors
   - `IOError`/`OSError` for file system errors
   - `json.JSONDecodeError` for parsing errors
   - `ValueError` for data validation errors

## Design Decisions

1. **Local Storage**: Chose `~/.brew-parser/` to follow Unix conventions for user-specific application data.

2. **JSON Format**: Human-readable format with 2-space indentation. Data is wrapped in a dictionary with a "formulas" key for consistent parsing between save and load operations.

3. **Subcommands**: Used argparse subparsers for clear command separation and future extensibility.

4. **Color Coding**: Green=new, Red=removed, Yellow=updated follows common UI conventions.

## Future Enhancements

Completed:
- ✅ Local caching to reduce API calls
- ✅ Change tracking (new/removed/updated)

Planned:
- Interactive TUI for browsing formulas
- Historical tracking (multiple snapshots)
- Cask support for GUI applications
- Integration with brew analytics for popularity data
- Auto-adding formulas to user's Brewfile
- Export functionality (JSON, CSV)

## Recent Changes (v0.2.0)

### Fixed Issues
1. Removed unused click dependency
2. Fixed type annotations for API response methods
3. Removed unused imports (timedelta, Set, os)
4. Updated User-Agent to use actual GitHub URL
5. Made exception handling more specific
6. Fixed data format consistency between save/load
7. Applied black formatting
8. Achieved flake8 and mypy strict compliance

### Data Format Change
**Important**: The storage format changed in v0.2.0. Old data files will cause errors. Users should run `brew_parser.py update` after upgrading.

## Code Quality Standards

### Type Annotations
- All methods have complete type annotations
- Use `Dict[str, Any]` for API responses
- Return types explicitly defined for all functions
- MyPy strict mode compliance required

### Code Formatting
- Black formatter with 88-character line limit
- Consistent import ordering (handled by black)
- No trailing whitespace
- Proper shebang format: `#! /usr/bin/env python3`

### Testing Requirements
- All new features must have corresponding tests
- Mock external API calls
- Test edge cases (empty data, errors, missing fields)
- Maintain >90% code coverage

### Dependencies
- Core: requests, rich
- Development: pytest, pytest-cov, pytest-mock, black, flake8, mypy, types-requests
- No unused dependencies (removed click in v0.2.0)
- Use pip-compile for consistent dependency management

## Common Development Tasks

### Adding a New Command
1. Add subparser in `main()` function
2. Create handler function following pattern: `handle_<command>_command(args)`
3. Add tests in `TestSubcommands` class
4. Update README.md command reference table

### Modifying Data Format
1. Update both `update_stored_formulas()` and `load_stored_formulas()`
2. Consider backward compatibility or migration
3. Update tests that create test data
4. Document change in CHANGELOG.md

### API Changes
1. Update type annotations
2. Add error handling for new failure modes
3. Update mock responses in tests
4. Consider rate limiting implications

## Known Limitations

1. **Date Filtering**: The `--days` parameter is non-functional because Homebrew API doesn't provide formula creation dates
2. **Rate Limiting**: No explicit rate limiting implemented (relies on good citizenship)
3. **Large Dataset**: Formula list is ~5MB and growing; future optimization may be needed
4. **No Incremental Updates**: Always fetches full formula list (potential for delta updates)

## Future Development Notes

### High Priority
- Add progress bars for long operations
- Implement connection retry logic
- Add `--json` output format option
- Support for Homebrew casks (GUI applications)

### Medium Priority  
- Delta updates (only fetch changes)
- Multiple snapshot history
- Search/filter functionality
- Integration with user's Brewfile

### Low Priority
- Web UI for browsing changes
- Analytics integration
- Formula popularity metrics
- Automated notifications for favorite formulas