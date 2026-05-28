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

## Completed features

- a polished five-tab interface: General Information, Emission Factors, Data Activities, Settings, Dashboard
- menu bar and toolbar for quick actions
- report settings and export targets in Settings
- emission factor import from Excel/CSV and interactive factor browsing
- activity import from Excel/CSV with column mapping
- scope 1/2/3 CO2e computation pipeline
- interactive dashboard with styled summary cards and a scope chart
- JSON persistence for saved GHG data

## Run the application

Install dependencies:

```bash
python -m pip install PySide6 matplotlib pandas openpyxl
```

Start the GUI:

```bash
python -m ghg_manager.app
```

Use the toolbar to compute totals, save data, and export report summaries.

## Sample templates

There are sample import templates under `templates/`:

- `templates/emission_factors_template.xlsx`
- `templates/activity_data_template.xlsx`

Use these files to import emission factors and activity data via the Emission Factors and Data Activities tabs.
