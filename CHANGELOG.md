# Changelog

## [migrate-v16] - ERPNext v16 / Python 3.14

### Changed
- `pyproject.toml`: `requires-python` bumped to `>=3.14`; `frappe` dependency
  range changed to `>=16.0.0,<17.0.0`.
- `hooks.py`: `app_license` set to `gpl-3.0` (matches `license.txt`).
- Removed legacy hooks not supported in v16 (`jenv`, `jenv_customizations`,
  `get_translated_dict`) and version checks (`is_frappe_above_v12/v13/v14`).

### Added
- `CHANGELOG.md`.

### Notes
- Backward compatibility with Frappe/ERPNext v13/v14/v15 has been dropped.
