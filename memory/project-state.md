# brew-parser Project State and Memory

## Project Context
- **Repository**: https://github.com/bluby/brew-parser
- **Current Version**: 0.2.0 (as of 2025-09-13)
- **Purpose**: Track changes in Homebrew formulas over time
- **Author**: Brian Luby (bluby)
- **License**: MIT

## Technical Stack
- **Language**: Python 3.8+ (tested with 3.13)
- **Key Libraries**: requests, rich
- **Testing**: pytest with >90% coverage
- **Code Quality**: black, flake8, mypy (strict mode)

## Recent Work Completed (v0.2.0)
1. **Code Quality Overhaul**
   - Removed unused click dependency
   - Added comprehensive type annotations
   - Fixed all flake8 warnings
   - Achieved mypy strict mode compliance
   - Applied black formatting

2. **Bug Fixes**
   - Fixed data format inconsistency between save/load operations
   - Data now stored as `{"formulas": [...]}` instead of raw array
   - Improved error handling with specific exception types

3. **Documentation Updates**
   - Updated README.md with correct GitHub URL
   - Enhanced CLAUDE.md with development guidance
   - Created CHANGELOG.md
   - Added code quality standards

## Current Architecture

### Data Flow
1. User runs `update` → Fetches from Homebrew API → Stores in ~/.brew-parser/
2. User runs `diff`/`new` → Loads stored data → Fetches current → Compares → Displays

### Key Design Decisions
- **Local Storage**: JSON files in ~/.brew-parser/ for simplicity
- **Data Wrapping**: Formulas wrapped in object for future extensibility
- **Hash-based Change Detection**: SHA256 to quickly detect if data changed
- **Rich Terminal Output**: Color-coded tables for better UX

## Known Issues and Limitations
1. **Date Filtering Non-functional**: `--days` parameter doesn't work (API limitation)
2. **Full Data Fetch**: Always downloads complete formula list (~5MB)
3. **No Progress Indicators**: Long operations appear frozen
4. **No Retry Logic**: Network failures fail immediately

## Future Development Priorities

### High Priority
1. **Progress Bars**: Add during fetch operations
2. **Retry Logic**: Handle transient network failures
3. **JSON Output**: Add `--json` flag for scripting
4. **Cask Support**: Track GUI applications too

### Medium Priority
1. **Delta Updates**: Only fetch changes since last update
2. **Search/Filter**: Find formulas by name/description
3. **History**: Keep multiple snapshots for trend analysis
4. **Brewfile Integration**: Auto-add formulas to Brewfile

### Architecture Improvements
1. **Plugin System**: Allow custom output formats
2. **Async Operations**: Speed up API calls
3. **Caching Strategy**: Smarter cache invalidation
4. **Config File**: User preferences in ~/.brew-parser/config.json

## Development Reminders

### Before Making Changes
1. Activate virtual environment: `source venv/bin/activate`
2. Pull latest changes
3. Run tests: `pytest`

### After Making Changes
1. Run formatters: `black *.py`
2. Check types: `mypy brew_parser.py --strict`
3. Lint: `flake8 *.py --max-line-length=88`
4. Test: `pytest -v`
5. Update CHANGELOG.md

### Common Pitfalls
- Remember data is wrapped: `{"formulas": [...]}`
- Always handle None from `load_stored_formulas()`
- Use specific exception types, not broad Exception
- Test data format changes thoroughly

## API Integration Notes
- **Base URL**: https://formulae.brew.sh/api/formula
- **Endpoints**: 
  - `/formula.json` - All formulas
  - `/formula/{name}.json` - Specific formula
- **User-Agent**: Must identify script
- **Rate Limits**: Unknown, be respectful

## Testing Reminders
- Mock all API calls in tests
- Test edge cases (empty data, network errors)
- Keep coverage above 90%
- Tests should be independent and fast

## User Feedback and Ideas
- "Would be nice to see trending formulas"
- "Integration with brew bundle would be useful"
- "Email notifications for favorite formula updates"
- "Show formula dependencies as a tree"

## Session Notes
- Fixed all code review issues from code-reviewer agent
- Data format change is breaking - consider migration in future
- Type annotations greatly improved code clarity
- Black formatting made code more consistent