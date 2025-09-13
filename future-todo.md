# Future TODOs

- Add `--show` filter to select categories: `new`, `updated`, `removed`, `all`.
- Track `first_seen` and (optionally) `last_seen` per formula in metadata for richer history.
- Support `diff --since YYYY-MM-DD` using local history (no extra API calls).
- Provide a small TUI to browse changes interactively.
- Add HTTP caching (ETag/If-None-Match) to avoid downloading unchanged data.
- Offer a `console_scripts` entry point (`brew-parser`) for pipx installs.
- Optional: compress local snapshot (gzip) to reduce disk footprint.
