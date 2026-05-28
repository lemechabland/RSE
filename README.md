# RSE
A graphic user interface application in python to manage GHG.

## Project Architecture

The repository is organized for a clean separation of concerns:

- `ghg_manager/`
  - `app.py` - application entry point and Qt startup logic
  - `config.py` - global paths and application constants
  - `models/` - domain entities such as company details, emission factors, activities, and reports
  - `services/` - business logic for calculations, persistence, and input validation
  - `ui/` - user interface components, dialogs, and chart helpers
  - `utils/` - reusable helpers for logging, file IO, and CSV import/export
- `tests/` - unit tests for key business logic and data handling
- `pyproject.toml` - package metadata and dependencies
- `.gitignore` - ignored build, environment, and cache files

## Goals

This architecture supports:

- easy extension for additional GHG scopes and reporting rules
- a clear service layer for calculation and persistence
- a UI layer decoupled from business logic
- testable components for validation and computation

## Next steps

- implement data entry forms for company, activity, and emission factor data
- connect the calculator service to the UI
- add real charts and reporting export options
- build sample datasets and import templates
