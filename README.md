# brew-parser

[Examples (v0.3.0): Markdown](https://github.com/brianluby/brew-parser/releases/download/v0.3.0/markdown-example.md) · [Table (text)](https://github.com/brianluby/brew-parser/releases/download/v0.3.0/table-example.txt) · [HTML](https://github.com/brianluby/brew-parser/releases/download/v0.3.0/table-example.html) · [JSON](https://github.com/brianluby/brew-parser/releases/download/v0.3.0/changes-example.json)

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

### Install with pipx (optional)

With the packaged CLI, you can install a global command `brew-parser`:

```bash
# From a local checkout
pipx install .

# Then run the CLI from anywhere
brew-parser --format table --limit 20
```

## Usage

### Quick Start (First Time)

```bash
# Activate the virtual environment
source venv/bin/activate

# Initialize baseline (first run) and show changes (none yet)
python brew_parser.py
```

### Daily Workflow

```bash
# Activate the virtual environment if not already active
source venv/bin/activate

# Show changes since your last run (default)
python brew_parser.py

# Show changes as a table instead of Markdown
python brew_parser.py --format table

# Show changes as JSON (for scripting)
python brew_parser.py --format json --limit 20

# Deactivate virtual environment when done
deactivate
```

### Command Reference

| Command | Description |
|---------|-------------|
| `brew_parser.py` | Show changes since last run (Markdown output) |
| `brew_parser.py --format table` | Show changes in a rich table |
| `brew_parser.py --format json` | Show changes as JSON |
| `brew_parser.py --limit N` | Limit items per category in the output |
| `brew_parser.py update` | Manually update local snapshot only |
| `brew_parser.py diff` | Show changes since last snapshot (does not save) |
| `brew_parser.py new` | Show only newly added formulas (legacy helper) |

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

## Recent Improvements (v0.3.0)

- **Default Flow**: Running `brew_parser.py` now shows changes since your last run and updates the snapshot on success
- **Formats**: `--format md|table|json` (default `md`) with `--limit N` per category
- **Faster Scan**: Summary prints before details in table output
- **pipx-ready**: Install a global CLI with `pipx install .` and run `brew-parser`

## License

MIT

## Contributing

See `AGENTS.md` for a concise contributor guide covering project layout, dev commands, coding style, testing, and PR expectations.

## Examples

Downloadable samples from the latest release (v0.3.0):

- Markdown: https://github.com/brianluby/brew-parser/releases/download/v0.3.0/markdown-example.md
- Table (text): https://github.com/brianluby/brew-parser/releases/download/v0.3.0/table-example.txt
- Table (HTML): https://github.com/brianluby/brew-parser/releases/download/v0.3.0/table-example.html
- JSON: https://github.com/brianluby/brew-parser/releases/download/v0.3.0/changes-example.json

Regenerate locally:

```bash
source venv/bin/activate
PYTHONPATH=. python scripts/generate_examples.py
# Outputs to examples/: changes-example.json, markdown-example.md, table-example.*
```
