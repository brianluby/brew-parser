# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

brew-parser is a Python command-line tool that tracks changes in Homebrew formulas over time. It maintains a local database of formula information and compares it with the current state to show what's new, updated, or removed. The project emphasizes clean code with comprehensive inline comments and test coverage.

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
mypy brew_parser.py

# Linting
flake8 brew_parser.py test_brew_parser.py
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
  - `formulas.json`: Complete formula data snapshot
  - `metadata.json`: Update timestamp and hash

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

5. **API Etiquette**: Custom User-Agent header identifies our script to Homebrew's servers.

6. **Efficient Comparison**: Uses set operations and dictionary lookups for O(n) comparison performance.

7. **Error Handling**: All commands handle missing data gracefully and provide helpful error messages.

## Design Decisions

1. **Local Storage**: Chose `~/.brew-parser/` to follow Unix conventions for user-specific application data.

2. **JSON Format**: Human-readable format allows users to inspect data if needed.

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