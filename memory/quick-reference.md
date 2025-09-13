# Quick Reference for brew-parser Development

## Environment Setup
```bash
cd ~/personal-repos/brew-parser
source venv/bin/activate
```

## Common Commands

### Development Workflow
```bash
# Make changes
black brew_parser.py test_brew_parser.py
mypy brew_parser.py --strict
flake8 brew_parser.py test_brew_parser.py --max-line-length=88
pytest -v

# Quick test of functionality
python brew_parser.py update
python brew_parser.py diff
python brew_parser.py new --limit 5
```

### Git Workflow
```bash
# Check what changed
git status
git diff

# Commit with conventional message
git add -A
git commit -m "type: description

Detailed explanation if needed

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Key File Locations
- Main script: `brew_parser.py`
- Tests: `test_brew_parser.py`
- User data: `~/.brew-parser/`
- Docs: `README.md`, `CLAUDE.md`, `CHANGELOG.md`

## Type Hints Cheat Sheet
```python
# Common patterns used in project
List[Dict[str, Any]]  # For formula lists
Optional[List[Dict[str, Any]]]  # For methods that might return None
Tuple[bool, str]  # For status returns
Dict[str, List[Dict[str, Any]]]  # For diff results
```

## Error Handling Pattern
```python
try:
    # Network operations
except requests.RequestException as e:
    logger.error(f"Network error: {e}")
except (IOError, OSError) as e:
    logger.error(f"File error: {e}")
except json.JSONDecodeError as e:
    logger.error(f"JSON error: {e}")
```

## Testing Patterns
```python
# Mock API responses
with patch("requests.get") as mock_get:
    mock_response = Mock()
    mock_response.json.return_value = [{"name": "tool"}]
    mock_get.return_value = mock_response
    
# Mock file operations
parser.stored_formulas_path = tmp_path / "formulas.json"
```

## Data Format
```json
{
  "formulas": [
    {
      "name": "tool-name",
      "desc": "Description",
      "homepage": "https://...",
      "versions": {"stable": "1.0.0"}
    }
  ]
}
```

## Debug Mode
Add `--debug` to any command for verbose logging:
```bash
python brew_parser.py update --debug
python brew_parser.py diff --debug
```