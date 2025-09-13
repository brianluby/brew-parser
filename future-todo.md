# Future TODOs

- Add `--show` filter to select categories: `new`, `updated`, `removed`, `all`.
- Track `first_seen` and (optionally) `last_seen` per formula in metadata for richer history.
- Support `diff --since YYYY-MM-DD` using local history (no extra API calls).
- Provide a small TUI to browse changes interactively.
- Add HTTP caching (ETag/If-None-Match) to avoid downloading unchanged data.
- Optional: compress local snapshot (gzip) to reduce disk footprint.

Next steps
- Config defaults file (e.g., `~/.brew-parser/config.toml`) for `format`, `limit`, and default category filters.
- JSON output schema: include a `schema_version` and document fields for stability.
- Snapshot rotation: keep last N snapshots; add command to diff arbitrary snapshots.
- Offline mode improvements: on network failure, show timestamp of last snapshot and proceed with local-only messaging.
- CI: GitHub Actions workflow to run black, flake8, mypy (strict), and pytest.
- Packaging readiness (no publish yet): build sdist/wheel, ensure entry point metadata and long description render on PyPI.
- Filters: add tap/category filters and simple search (name/desc contains).
- Cask support and (optional) brew analytics integration for popularity insights.
- Export options: CSV in addition to JSON/Markdown for spreadsheets.
- CLI flags: `--quiet` (suppress tables/markdown; summary only) and `--verbose` (more details per row).
- Tests: golden tests for Markdown/table output and JSON schema; basic E2E CLI smoke test.
- Deprecation plan: mark `update/diff/new` as legacy in help; consider removal after 1–2 releases.
