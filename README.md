# brew-parser

A command-line tool to discover and explore new Homebrew formulas.

## Overview

This tool automates the workflow of discovering new packages in Homebrew by:
1. Tracking formula changes over time (new additions, updates, removals)
2. Fetching formula descriptions and homepages
3. Displaying information in clean, colorful tables and markdown format
4. Maintaining a local database for offline comparison

### Key Features

- **Change Tracking**: Compare current Homebrew formulas with your last update to see what's new, updated, or removed
- **Beautiful Output**: Color-coded tables for different types of changes
- **Fast Operations**: Local caching means instant comparisons without repeated API calls
- **Flexible Display**: Show all formulas or filter to just see what's new

## Installation

```bash
# Clone the repository
git clone https://github.com/bluby/brew-parser.git
cd brew-parser

# Create a virtual environment (required on macOS with Homebrew Python)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Note:** On macOS with Homebrew-installed Python, you must use a virtual environment due to [PEP 668](https://peps.python.org/pep-0668/). This prevents conflicts between system packages and project dependencies.

## Usage

### Quick Start (First Time)

```bash
# Activate the virtual environment
source venv/bin/activate

# Update local formula database (required for tracking changes)
python brew_parser.py update

# See what's new since your last update
python brew_parser.py new
```

### Daily Workflow

```bash
# Activate the virtual environment if not already active
source venv/bin/activate

# Update your local formula database with latest from Homebrew
python brew_parser.py update

# Show only newly added formulas
python brew_parser.py new

# Show all changes (added, removed, updated)
python brew_parser.py diff

# Browse all formulas (original functionality)
python brew_parser.py --limit 10

# Deactivate virtual environment when done
deactivate
```

### Command Reference

| Command | Description |
|---------|-------------|
| `brew_parser.py` | Show all formulas (alphabetically) |
| `brew_parser.py --limit N` | Show only first N formulas |
| `brew_parser.py update` | Download and store current formula data |
| `brew_parser.py diff` | Show all changes since last update |
| `brew_parser.py new` | Show only newly added formulas |
| `brew_parser.py new --limit N` | Show only N newest formulas |

**Note:** The `--days` parameter is currently a placeholder. Date filtering will be implemented in a future version.

## Data Storage

The tool stores formula data in `~/.brew-parser/`:
- `formulas.json` - Current snapshot of all Homebrew formulas (stored as `{"formulas": [...]}` for consistent parsing)
- `metadata.json` - Metadata including last update time and data hash

This local storage enables:
- Fast offline comparisons
- Historical tracking of formula changes
- No need to re-fetch data for multiple operations

## Development

```bash
# Activate virtual environment
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=brew_parser

# Format code
black brew_parser.py test_brew_parser.py

# Type checking (strict mode)
mypy brew_parser.py --strict

# Run linting
flake8 brew_parser.py test_brew_parser.py --max-line-length=88
```

## Troubleshooting

### "externally-managed-environment" Error
If you see this error when trying to install packages:
```
error: externally-managed-environment
```
This means you're trying to install packages system-wide on macOS with Homebrew Python. Always use a virtual environment as shown in the Installation section.

### Making the Script Executable
To run the script without typing `python`:
```bash
chmod +x brew_parser.py
./brew_parser.py --limit 5
```

## Future Features

- [x] Track new formula additions
- [x] Track formula updates (version changes)
- [x] Track formula removals
- [x] Local caching for offline operation
- [ ] Interactive TUI for browsing formulas
- [ ] Save/bookmark interesting formulas
- [ ] Auto-add selected formulas to Brewfile
- [ ] Category filtering
- [ ] Integration with brew analytics
- [ ] Historical tracking (show changes over multiple updates)
- [ ] Cask support (track GUI applications)
- [ ] Export changes to various formats (JSON, CSV)
- [ ] Web interface for browsing changes

## Recent Improvements (v0.2.1)

- **Contributor Guide**: Added AGENTS.md with project structure, dev commands, style, testing, and PR tips
- **Test Robustness**: Aligned tests with the stored JSON wrapper format (`{"formulas": [...]}`)
- **Tooling**: Verified black, flake8, mypy (strict), and pytest all pass locally

## License

MIT

## Contributing

See `AGENTS.md` for a concise contributor guide covering project layout, dev commands, coding style, testing, and PR expectations.
