# Repository Guidelines

## Project Structure & Module Organization
- Root script: `brew_parser.py` (CLI entrypoint and core logic)
- Tests: `test_brew_parser.py` (pytest)
- Config: `pyproject.toml` (mypy, black, pytest), `requirements*.txt`
- Data/assets: `formula.json` (sample data), cache dirs like `.pytest_cache/`, `.mypy_cache/`
- Virtual env (local): `venv/` (do not commit)

## Build, Test, and Development Commands
- Setup venv: `python3 -m venv venv && source venv/bin/activate`
- Install deps: `pip install -r requirements.txt` (add `-r requirements-dev.txt` for dev)
- Run CLI: `python brew_parser.py [update|diff|new|--limit N]`
- Test (quiet): `pytest` or `pytest -q`
- Coverage: `pytest --cov=brew_parser` (optional)
- Format: `black brew_parser.py test_brew_parser.py`
- Lint: `flake8 brew_parser.py test_brew_parser.py --max-line-length=88`
- Type-check: `mypy brew_parser.py --strict`

## Coding Style & Naming Conventions
- Python 3.8+; 4-space indentation; max line length 88 (black/pylint)
- Use type hints everywhere (project runs mypy in strict mode)
- Naming: modules/functions `snake_case`, classes `CapWords`, constants `UPPER_SNAKE`
- Prefer small, pure functions; handle network/file I/O errors explicitly
- Keep user-visible CLI output stable; update tests if output format changes

## Testing Guidelines
- Framework: pytest (configured via `pyproject.toml` with `-ra -q --strict-markers`)
- Tests live in `test_brew_parser.py`; add new tests as `test_*.py` if needed
- Write tests for parsing, change-diff logic, and error paths
- Aim for meaningful coverage on core behaviors; use `pytest --cov` locally

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise, scoped (e.g., "Add diff table rendering")
- Reference issues in the body when applicable (e.g., "Fixes #12")
- PRs: include a clear description, rationale, sample CLI output (before/after), and steps to test
- Keep diffs focused; include screenshots or text snippets of CLI tables when helpful

## Security & Configuration Tips
- Never commit secrets; this tool only uses public Homebrew data
- Local data is stored under `~/.brew-parser/` (e.g., `formulas.json`, `metadata.json`)
- Use a venv on macOS (PEP 668) to avoid "externally-managed-environment" errors
