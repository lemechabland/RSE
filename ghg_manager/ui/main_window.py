"""Main window for the GHG Manager application."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .forms import ActivityForm, CompanyForm, EmissionFactorForm, SettingsForm
from .style_loader import apply_app_style
from .ui_builder import load_ui_module
from .widgets import ChartPanel, SummaryPanel
from ..models.activity import Activity
from ..models.company import Company
from ..models.emission_factor import EmissionFactor
from ..services.calculator import GHGCalculator
from ..services.data_store import DataStore


class MainWindow(QMainWindow):
    """Primary application shell and dashboard window."""

    def __init__(self):
        super().__init__()

        ui_module = load_ui_module(Path(__file__).resolve().with_name("main_window.ui"))
        self.ui = ui_module.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("GHG Manager")
        self.setMinimumSize(1100, 780)

        self.data_store = DataStore()
        self.calculator = GHGCalculator()
        self.company: Optional[Company] = None
        self.emission_factors: Dict[str, EmissionFactor] = {}
        self.activities: list[Activity] = []

        self.company_form = CompanyForm()
        self.factor_form = EmissionFactorForm()
        self.activity_form = ActivityForm()
        self.settings_form = SettingsForm()
        self.summary_panel = SummaryPanel()
        self.chart_panel = ChartPanel()
        self.last_totals: Dict[str, float] = {}

        self._setup_ui()
        self._load_saved_data()

    def _setup_ui(self) -> None:
        self._create_menu()
        self._create_toolbar()
        self.statusBar().showMessage("Ready")

        self.ui.tabWidget.addTab(self._build_general_tab(), "General Information")
        self.ui.tabWidget.addTab(self._build_factors_tab(), "Emission Factors")
        self.ui.tabWidget.addTab(self._build_activities_tab(), "Data Activities")
        self.ui.tabWidget.addTab(self._build_settings_tab(), "Settings")
        self.ui.tabWidget.addTab(self._build_dashboard_tab(), "Dashboard")
        self.ui.tabWidget.tabBar().hide()
        apply_app_style(self)

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(QAction("Load saved data", self, triggered=self._load_saved_data))
        file_menu.addAction(QAction("Save data", self, triggered=self.save_data))
        file_menu.addAction(QAction("Export report", self, triggered=self.export_report))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        self.menuBar().addAction(QAction("General Information", self, triggered=lambda: self.ui.tabWidget.setCurrentIndex(0)))
        self.menuBar().addAction(QAction("Emission Factor", self, triggered=lambda: self.ui.tabWidget.setCurrentIndex(1)))
        self.menuBar().addAction(QAction("Data Activities", self, triggered=lambda: self.ui.tabWidget.setCurrentIndex(2)))
        self.menuBar().addAction(QAction("Settings", self, triggered=lambda: self.ui.tabWidget.setCurrentIndex(3)))
        self.menuBar().addAction(QAction("Dashboard", self, triggered=lambda: self.ui.tabWidget.setCurrentIndex(4)))

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(QAction("About", self, triggered=self._show_about))

    def _create_toolbar(self) -> None:
        pass

    def _build_general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        intro = QLabel(
            "<h2>Welcome to GHG Manager</h2>"
            "<p>Use the tabs to provide company information, manage emission factors, import activity data, and review the dashboard.</p>"
        )
        intro.setWordWrap(True)
        intro.setMargin(8)
        self.validate_company_button = QPushButton("Validate and save company information")
        self.validate_company_button.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border-radius: 6px; padding: 8px 14px; }"
            "QPushButton:hover { background-color: #2ecc71; }"
        )
        self.validate_company_button.clicked.connect(self.save_company_info)

        layout.addWidget(intro)
        layout.addWidget(self.company_form)
        layout.addWidget(self.validate_company_button)
        layout.addStretch()
        return tab

    def _build_factors_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        description = QLabel(
            "<b>Emission Factors</b><br>Import your factor database from Excel or CSV, then review and edit values directly." 
        )
        description.setWordWrap(True)
        description.setMargin(8)
        layout.addWidget(description)
        layout.addWidget(self.factor_form)
        layout.addStretch()
        return tab

    def _build_activities_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        description = QLabel(
            "<b>Data Activities</b><br>Import activity records from Excel or CSV, then map columns to the activity fields."
        )
        description.setWordWrap(True)
        description.setMargin(8)
        layout.addWidget(description)
        layout.addWidget(self.activity_form)
        layout.addStretch()
        return tab

    def _build_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        description = QLabel(
            "<b>Settings</b><br>Choose report defaults and export targets for your generated GHG summaries."
        )
        description.setWordWrap(True)
        description.setMargin(8)
        layout.addWidget(description)
        layout.addWidget(self.settings_form)
        layout.addStretch()
        return tab

    def _build_dashboard_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        header = QHBoxLayout()
        header.addWidget(QLabel("<h3>Dashboard</h3>"))
        header.addStretch()
        compute_button = QPushButton("Compute emission")
        compute_button.setFixedHeight(42)
        compute_button.clicked.connect(self.compute_emission)
        header.addWidget(compute_button)

        summary_box = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_box)
        summary_layout.addWidget(self.summary_panel)

        chart_box = QGroupBox("Scope distribution")
        chart_layout = QVBoxLayout(chart_box)
        chart_layout.addWidget(self.chart_panel)

        layout.addLayout(header)
        layout.addWidget(summary_box)
        layout.addWidget(chart_box)
        layout.addStretch()
        return tab

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About GHG Manager",
            "GHG Manager\nA friendly GUI for emissions data, scope summaries, and visual reports.",
        )

    def _apply_styles(self) -> None:
        style_path = Path(__file__).resolve().parent / "style.qss"
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    def compute_emission(self) -> None:
        try:
            self.company = self.company_form.company()
        except Exception as error:
            QMessageBox.warning(self, "Input error", f"Failed to read company data: {error}")
            return

        self.emission_factors = self.factor_form.factors()
        self.activities = self.activity_form.activities()

        missing_keys = {
            activity.emission_factor_key for activity in self.activities
            if activity.emission_factor_key and activity.emission_factor_key not in self.emission_factors
        }
        if missing_keys:
            QMessageBox.warning(
                self,
                "Missing emission factor",
                f"The following emission factor keys are not defined: {', '.join(sorted(missing_keys))}",
            )
            return

        if not self.company.name:
            QMessageBox.warning(self, "Missing company", "Please fill in the company name before computing totals.")
            return

        totals = self.calculator.compute_report(self.activities, self.emission_factors)
        self.last_totals = totals
        self.summary_panel.update_summary(totals)
        self.chart_panel.plot_scope(totals)
        self.statusBar().showMessage("Computation completed", 5000)

    def export_report(self) -> None:
        if not self.last_totals:
            QMessageBox.warning(self, "No data", "Please compute totals before exporting the report.")
            return

        settings = self.settings_form.settings()
        folder = settings["export_folder"]
        if not folder:
            QMessageBox.warning(self, "No export folder", "Please choose an export folder in Settings.")
            return

        export_path = Path(folder)
        if not export_path.exists():
            QMessageBox.warning(self, "Invalid folder", "The selected export folder does not exist.")
            return

        report_name = settings["report_name"] or "ghg_report"
        file_stem = report_name.replace(" ", "_")
        report_data = [
            {"metric": "Total CO2e", "value": self.last_totals.get("total_co2e", 0)},
            {"metric": "Scope 1", "value": self.last_totals.get("scope_1", 0)},
            {"metric": "Scope 2", "value": self.last_totals.get("scope_2", 0)},
            {"metric": "Scope 3", "value": self.last_totals.get("scope_3", 0)},
        ]

        if settings["export_format"] == "excel":
            report_file = export_path / f"{file_stem}.xlsx"
            import pandas as pd
            pd.DataFrame(report_data).to_excel(report_file, index=False)
        else:
            report_file = export_path / f"{file_stem}.csv"
            with report_file.open("w", encoding="utf-8", newline="") as handle:
                handle.write("metric,value\n")
                for row in report_data:
                    handle.write(f"{row['metric']},{row['value']}\n")

        if settings["export_chart"]:
            chart_file = export_path / f"{file_stem}_chart.png"
            self.chart_panel.canvas.figure.savefig(chart_file)
        else:
            chart_file = None

        message = f"Report exported to {report_file}"
        if chart_file:
            message += f" and chart image to {chart_file}"
        QMessageBox.information(self, "Export complete", message)
        self.statusBar().showMessage("Report exported", 5000)

    def save_data(self) -> None:
        data = {
            "company": {
                "name": self.company.name if self.company else self.company_form.company().name,
                "industry": self.company.industry if self.company else self.company_form.company().industry,
                "location": self.company.location if self.company else self.company_form.company().location,
                "fiscal_year": self.company.fiscal_year if self.company else self.company_form.company().fiscal_year,
                "notes": self.company.notes if self.company else self.company_form.company().notes,
                "capital_amount": self.company.capital_amount if self.company else self.company_form.company().capital_amount,
            },
            "emission_factors": [
                {
                    "key": key,
                    "category": factor.category,
                    "source": factor.source,
                    "value": factor.value,
                    "unit": factor.unit,
                    "scope": factor.scope,
                }
                for key, factor in self.factor_form.factors().items()
            ],
            "activities": [
                {
                    "name": activity.name,
                    "activity_type": activity.activity_type,
                    "amount": activity.amount,
                    "unit": activity.unit,
                    "emission_factor_key": activity.emission_factor_key,
                    "scope": activity.scope,
                    "category": activity.category,
                }
                for activity in self.activity_form.activities()
            ],
            "saved_at": datetime.utcnow().isoformat() + "Z",
        }
        self.data_store.save(data)
        QMessageBox.information(self, "Saved", "GHG data has been saved successfully.")
        self.statusBar().showMessage("Data saved", 5000)

    def save_company_info(self) -> None:
        try:
            self.company = self.company_form.company()
        except Exception as error:
            QMessageBox.warning(self, "Input error", f"Failed to read company data: {error}")
            return

        if not self.company.name or not self.company.industry:
            QMessageBox.warning(self, "Missing company info", "Please fill in company name and industry before saving.")
            return

        self.save_data()

    def _load_saved_data(self) -> None:
        data = self.data_store.load()
        company_data = data.get("company") or {}
        if company_data:
            self.company_form.set_company(
                Company(
                    name=company_data.get("name", ""),
                    industry=company_data.get("industry", ""),
                    location=company_data.get("location", ""),
                    fiscal_year=company_data.get("fiscal_year", ""),
                    capital_amount=float(company_data.get("capital_amount", 0)),
                    notes=company_data.get("notes", ""),
                )
            )

        factors = {}
        for item in data.get("emission_factors", []):
            key = item.get("key")
            if not key:
                continue
            factors[key] = EmissionFactor(
                category=item.get("category", ""),
                source=item.get("source", ""),
                value=float(item.get("value", 0)),
                unit=item.get("unit", ""),
                scope=item.get("scope", "scope_1"),
            )
        self.factor_form.set_factors(factors)
        if not factors:
            self.factor_form.load_default_factors()

        activities = []
        for item in data.get("activities", []):
            activities.append(
                Activity(
                    name=item.get("name", ""),
                    activity_type=item.get("activity_type", ""),
                    amount=float(item.get("amount", 0)),
                    unit=item.get("unit", ""),
                    emission_factor_key=item.get("emission_factor_key", ""),
                    scope=item.get("scope", "scope_1"),
                    category=item.get("category", "General info"),
                )
            )
        self.activity_form.set_activities(activities)

        if data:
            self.statusBar().showMessage("Saved data loaded", 5000)
