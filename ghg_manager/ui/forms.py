"""UI form components for GHG Manager data entry."""

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QHeaderView,
    QTextEdit,
)
from PySide6.QtCore import Qt

from ..models.activity import Activity
from ..models.company import Company
from ..models.emission_factor import EmissionFactor
from ..utils.excel_io import load_table, normalize_columns


SCOPE_OPTIONS = ["scope_1", "scope_2", "scope_3"]


class CompanyForm(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Company Information", parent)
        self.name_input = QLineEdit()
        self.industry_input = QLineEdit()
        self.location_input = QLineEdit()
        self.fiscal_year_input = QLineEdit()
        self.capital_amount_input = QDoubleSpinBox()
        self.capital_amount_input.setRange(0, 1e12)
        self.capital_amount_input.setDecimals(2)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional company or reporting notes")

        form_layout = QFormLayout()
        form_layout.addRow("Company name:", self.name_input)
        form_layout.addRow("Industry:", self.industry_input)
        form_layout.addRow("Location:", self.location_input)
        form_layout.addRow("Fiscal year:", self.fiscal_year_input)
        form_layout.addRow("Capital amount:", self.capital_amount_input)
        form_layout.addRow("Notes:", self.notes_input)
        self.setLayout(form_layout)

    def company(self) -> Company:
        return Company(
            name=self.name_input.text().strip(),
            industry=self.industry_input.text().strip(),
            location=self.location_input.text().strip() or None,
            fiscal_year=self.fiscal_year_input.text().strip() or None,
            capital_amount=float(self.capital_amount_input.value()),
            notes=self.notes_input.toPlainText().strip() or None,
        )

    def set_company(self, company: Company) -> None:
        self.name_input.setText(company.name)
        self.industry_input.setText(company.industry)
        self.location_input.setText(company.location or "")
        self.fiscal_year_input.setText(company.fiscal_year or "")
        self.capital_amount_input.setValue(company.capital_amount or 0)
        self.notes_input.setPlainText(company.notes or "")


class EmissionFactorForm(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Emission Factors", parent)
        self.factor_table = QTableWidget(0, 6)
        self.factor_table.setHorizontalHeaderLabels(
            ["Key", "Category", "Source", "Value", "Unit", "Scope"]
        )
        self.factor_table.horizontalHeader().setStretchLastSection(True)
        self.factor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.factor_table.verticalHeader().setVisible(False)
        self.factor_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.factor_key = QLineEdit()
        self.factor_category = QLineEdit()
        self.factor_source = QLineEdit()
        self.factor_value = QDoubleSpinBox()
        self.factor_value.setRange(0, 1e9)
        self.factor_value.setDecimals(6)
        self.factor_unit = QLineEdit()
        self.factor_scope = QComboBox()
        self.factor_scope.addItems(SCOPE_OPTIONS)

        self.add_button = QPushButton("Add factor")
        self.remove_button = QPushButton("Remove selected")
        self.load_button = QPushButton("Import factors from file")
        self.load_button.clicked.connect(self.import_factors)
        self.add_button.clicked.connect(self.add_factor)
        self.remove_button.clicked.connect(self.remove_selected)

        input_layout = QFormLayout()
        input_layout.addRow("Key:", self.factor_key)
        input_layout.addRow("Category:", self.factor_category)
        input_layout.addRow("Source:", self.factor_source)
        input_layout.addRow("Value:", self.factor_value)
        input_layout.addRow("Unit:", self.factor_unit)
        input_layout.addRow("Scope:", self.factor_scope)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        form_layout = QVBoxLayout()
        form_layout.addLayout(input_layout)
        form_layout.addLayout(button_layout)
        form_layout.addWidget(self.factor_table)
        self.setLayout(form_layout)
        self.load_default_factors()

    def import_factors(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open emission factor file",
            "",
            "Excel Files (*.xlsx *.xls *.xlsm *.xlsb);;CSV Files (*.csv);;All Files (*)",
        )
        if not file_path:
            return

        try:
            df = load_table(Path(file_path))
        except Exception as error:
            QMessageBox.warning(self, "Import error", f"Unable to import file: {error}")
            return

        self._load_factors_from_dataframe(df, replace_existing=True)

    def load_default_factors(self) -> None:
        template_path = Path(__file__).resolve().parents[2] / "templates" / "emission_factors_template.xlsx"
        if not template_path.exists():
            return

        try:
            df = load_table(template_path)
        except Exception:
            return

        self._load_factors_from_dataframe(df, replace_existing=False)

    def _load_factors_from_dataframe(self, df: pd.DataFrame, replace_existing: bool = True) -> None:
        expected_columns = ["key", "category", "source", "value", "unit", "scope"]
        columns = [str(col).strip().lower() for col in df.columns]
        if not all(column in columns for column in expected_columns):
            return

        if replace_existing:
            self.factor_table.setRowCount(0)
        elif self.factor_table.rowCount() > 0:
            return

        for _, row in df.iterrows():
            key = str(row.get("key", "")).strip()
            if not key:
                continue
            line = [
                key,
                str(row.get("category", "")).strip(),
                str(row.get("source", "")).strip(),
                f"{float(row.get('value', 0) or 0):.6f}",
                str(row.get("unit", "")).strip(),
                str(row.get("scope", "scope_1")).strip(),
            ]
            row_index = self.factor_table.rowCount()
            self.factor_table.insertRow(row_index)
            for column, value in enumerate(line):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.factor_table.setItem(row_index, column, item)

    def add_factor(self) -> None:
        key = self.factor_key.text().strip()
        if not key:
            return
        values = [
            key,
            self.factor_category.text().strip(),
            self.factor_source.text().strip(),
            f"{self.factor_value.value():.6f}",
            self.factor_unit.text().strip(),
            self.factor_scope.currentText(),
        ]
        row = self.factor_table.rowCount()
        self.factor_table.insertRow(row)
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.factor_table.setItem(row, column, item)
        self.clear_inputs()

    def remove_selected(self) -> None:
        for row in sorted({index.row() for index in self.factor_table.selectedIndexes()}, reverse=True):
            self.factor_table.removeRow(row)

    def factors(self) -> Dict[str, EmissionFactor]:
        result: Dict[str, EmissionFactor] = {}
        for row in range(self.factor_table.rowCount()):
            key = self._cell_text(row, 0)
            if not key:
                continue
            category = self._cell_text(row, 1)
            source = self._cell_text(row, 2)
            value = float(self._cell_text(row, 3) or 0)
            unit = self._cell_text(row, 4)
            scope = self._cell_text(row, 5)
            result[key] = EmissionFactor(
                category=category,
                source=source,
                value=value,
                unit=unit,
                scope=scope,
            )
        return result

    def set_factors(self, factors: Dict[str, EmissionFactor]) -> None:
        self.factor_table.setRowCount(0)
        for key, factor in factors.items():
            self.factor_table.insertRow(self.factor_table.rowCount())
            self.factor_table.setItem(self.factor_table.rowCount() - 1, 0, QTableWidgetItem(key))
            self.factor_table.setItem(self.factor_table.rowCount() - 1, 1, QTableWidgetItem(factor.category))
            self.factor_table.setItem(self.factor_table.rowCount() - 1, 2, QTableWidgetItem(factor.source))
            self.factor_table.setItem(self.factor_table.rowCount() - 1, 3, QTableWidgetItem(str(factor.value)))
            self.factor_table.setItem(self.factor_table.rowCount() - 1, 4, QTableWidgetItem(factor.unit))
            self.factor_table.setItem(self.factor_table.rowCount() - 1, 5, QTableWidgetItem(factor.scope))

    def clear_inputs(self) -> None:
        self.factor_key.clear()
        self.factor_category.clear()
        self.factor_source.clear()
        self.factor_value.setValue(0)
        self.factor_unit.clear()
        self.factor_scope.setCurrentIndex(0)

    def _cell_text(self, row: int, column: int) -> str:
        item = self.factor_table.item(row, column)
        return item.text().strip() if item is not None else ""


class CategoryActivityPanel(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.category = title
        self.activity_table = QTableWidget(0, 6)
        self.activity_table.setHorizontalHeaderLabels(
            ["Name", "Type", "Amount", "Unit", "Factor key", "Scope"]
        )
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.activity_name = QLineEdit()
        self.activity_type = QLineEdit()
        self.activity_amount = QDoubleSpinBox()
        self.activity_amount.setRange(0, 1e12)
        self.activity_amount.setDecimals(3)
        self.activity_unit = QLineEdit()
        self.activity_factor_key = QLineEdit()
        self.activity_scope = QComboBox()
        self.activity_scope.addItems(SCOPE_OPTIONS)

        self.map_name = QComboBox()
        self.map_type = QComboBox()
        self.map_amount = QComboBox()
        self.map_unit = QComboBox()
        self.map_factor_key = QComboBox()
        self.map_scope = QComboBox()
        self._initialize_mapping_dropdowns()

        self.load_button = QPushButton("Import activities from file")
        self.import_button = QPushButton("Add mapped rows")
        self.add_button = QPushButton("Add activity")
        self.remove_button = QPushButton("Remove selected")

        self.loaded_file_label = QLabel("No activity file loaded")

        self.load_button.clicked.connect(self.load_activity_file)
        self.import_button.clicked.connect(self.import_mapped_rows)
        self.add_button.clicked.connect(self.add_activity)
        self.remove_button.clicked.connect(self.remove_selected)

        input_layout = QFormLayout()
        input_layout.addRow("Name:", self.activity_name)
        input_layout.addRow("Type:", self.activity_type)
        input_layout.addRow("Amount:", self.activity_amount)
        input_layout.addRow("Unit:", self.activity_unit)
        input_layout.addRow("Emission factor key:", self.activity_factor_key)
        input_layout.addRow("Scope:", self.activity_scope)

        mapping_layout = QFormLayout()
        mapping_layout.addRow("Map name column:", self.map_name)
        mapping_layout.addRow("Map type column:", self.map_type)
        mapping_layout.addRow("Map amount column:", self.map_amount)
        mapping_layout.addRow("Map unit column:", self.map_unit)
        mapping_layout.addRow("Map factor key column:", self.map_factor_key)
        mapping_layout.addRow("Map scope column:", self.map_scope)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel(f"<b>{self.category}</b>"))
        form_layout.addLayout(input_layout)
        form_layout.addWidget(QLabel("Activity column mapping"))
        form_layout.addLayout(mapping_layout)
        form_layout.addWidget(self.loaded_file_label)
        form_layout.addLayout(button_layout)
        form_layout.addWidget(self.activity_table)
        self.setLayout(form_layout)

        self.loaded_data: Optional[pd.DataFrame] = None

    def _initialize_mapping_dropdowns(self) -> None:
        for dropdown in [
            self.map_name,
            self.map_type,
            self.map_amount,
            self.map_unit,
            self.map_factor_key,
            self.map_scope,
        ]:
            dropdown.clear()
            dropdown.addItem("-- select column --")

    def _populate_mapping_options(self, columns: list[str]) -> None:
        for dropdown in [
            self.map_name,
            self.map_type,
            self.map_amount,
            self.map_unit,
            self.map_factor_key,
            self.map_scope,
        ]:
            dropdown.clear()
            dropdown.addItems(["-- select column --"] + columns)

    def load_activity_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open activity import file",
            "",
            "Excel Files (*.xlsx *.xls *.xlsm *.xlsb);;CSV Files (*.csv);;All Files (*)",
        )
        if not file_path:
            return

        try:
            self.loaded_data = load_table(Path(file_path))
        except Exception as error:
            QMessageBox.warning(self, "Import error", f"Unable to import file: {error}")
            return

        columns = normalize_columns(self.loaded_data)
        self._populate_mapping_options(columns)
        self.loaded_file_label.setText(f"Loaded {Path(file_path).name} ({len(self.loaded_data)} rows)")

    def import_mapped_rows(self) -> None:
        if self.loaded_data is None:
            QMessageBox.warning(self, "No file", "Please import an activity file first.")
            return

        mapping = {
            "name": self.map_name.currentText(),
            "type": self.map_type.currentText(),
            "amount": self.map_amount.currentText(),
            "unit": self.map_unit.currentText(),
            "factor_key": self.map_factor_key.currentText(),
            "scope": self.map_scope.currentText(),
        }
        if any(value.startswith("-- select") for value in mapping.values()):
            QMessageBox.warning(self, "Incomplete mapping", "Please map every activity field before importing.")
            return

        for _, row in self.loaded_data.iterrows():
            values = [
                str(row.get(mapping["name"], "")).strip(),
                str(row.get(mapping["type"], "")).strip(),
                f"{float(row.get(mapping['amount'], 0) or 0):.3f}",
                str(row.get(mapping["unit"], "")).strip(),
                str(row.get(mapping["factor_key"], "")).strip(),
                str(row.get(mapping["scope"], "scope_1")).strip(),
            ]
            row_index = self.activity_table.rowCount()
            self.activity_table.insertRow(row_index)
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.activity_table.setItem(row_index, column, item)

        self.loaded_file_label.setText(f"Imported {len(self.loaded_data)} rows")
        self.loaded_data = None
        self._initialize_mapping_dropdowns()

    def add_activity(self) -> None:
        name = self.activity_name.text().strip()
        if not name:
            return
        values = [
            name,
            self.activity_type.text().strip(),
            f"{self.activity_amount.value():.3f}",
            self.activity_unit.text().strip(),
            self.activity_factor_key.text().strip(),
            self.activity_scope.currentText(),
        ]
        row = self.activity_table.rowCount()
        self.activity_table.insertRow(row)
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.activity_table.setItem(row, column, item)
        self.clear_inputs()

    def remove_selected(self) -> None:
        for row in sorted({index.row() for index in self.activity_table.selectedIndexes()}, reverse=True):
            self.activity_table.removeRow(row)

    def activities(self) -> List[Activity]:
        results: List[Activity] = []
        for row in range(self.activity_table.rowCount()):
            name = self._cell_text(row, 0)
            if not name:
                continue
            activity_type = self._cell_text(row, 1)
            amount = float(self._cell_text(row, 2) or 0)
            unit = self._cell_text(row, 3)
            factor_key = self._cell_text(row, 4)
            scope = self._cell_text(row, 5)
            results.append(
                Activity(
                    name=name,
                    activity_type=activity_type,
                    amount=amount,
                    unit=unit,
                    emission_factor_key=factor_key,
                    scope=scope,
                    category=self.category,
                )
            )
        return results

    def set_activities(self, activities: List[Activity]) -> None:
        self.activity_table.setRowCount(0)
        for activity in activities:
            row = self.activity_table.rowCount()
            self.activity_table.insertRow(row)
            self.activity_table.setItem(row, 0, QTableWidgetItem(activity.name))
            self.activity_table.setItem(row, 1, QTableWidgetItem(activity.activity_type))
            self.activity_table.setItem(row, 2, QTableWidgetItem(str(activity.amount)))
            self.activity_table.setItem(row, 3, QTableWidgetItem(activity.unit))
            self.activity_table.setItem(row, 4, QTableWidgetItem(activity.emission_factor_key))
            self.activity_table.setItem(row, 5, QTableWidgetItem(activity.scope))

    def add_activity_row(self, activity: Activity) -> None:
        row_index = self.activity_table.rowCount()
        self.activity_table.insertRow(row_index)
        self.activity_table.setItem(row_index, 0, QTableWidgetItem(activity.name))
        self.activity_table.setItem(row_index, 1, QTableWidgetItem(activity.activity_type))
        self.activity_table.setItem(row_index, 2, QTableWidgetItem(str(activity.amount)))
        self.activity_table.setItem(row_index, 3, QTableWidgetItem(activity.unit))
        self.activity_table.setItem(row_index, 4, QTableWidgetItem(activity.emission_factor_key))
        self.activity_table.setItem(row_index, 5, QTableWidgetItem(activity.scope))

    def clear_inputs(self) -> None:
        self.activity_name.clear()
        self.activity_type.clear()
        self.activity_amount.setValue(0)
        self.activity_unit.clear()
        self.activity_factor_key.clear()
        self.activity_scope.setCurrentIndex(0)

    def _cell_text(self, row: int, column: int) -> str:
        item = self.activity_table.item(row, column)
        return item.text().strip() if item is not None else ""


class ActivityForm(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Activities", parent)
        self.category_tabs = QTabWidget()
        self.general_panel = CategoryActivityPanel("General info")
        self.transport_panel = CategoryActivityPanel("Transports and professional moving")
        self.immobilisation_panel = CategoryActivityPanel("Immobilisation")

        self.category_tabs.addTab(self.general_panel, "General info")
        self.category_tabs.addTab(self.transport_panel, "Transports")
        self.category_tabs.addTab(self.immobilisation_panel, "Immobilisation")

        layout = QVBoxLayout()
        layout.addWidget(self.category_tabs)
        self.setLayout(layout)

    def activities(self) -> List[Activity]:
        return (
            self.general_panel.activities()
            + self.transport_panel.activities()
            + self.immobilisation_panel.activities()
        )

    def set_activities(self, activities: List[Activity]) -> None:
        self.general_panel.set_activities([a for a in activities if a.category is None or "general" in (a.category or "").lower()])
        self.transport_panel.set_activities([a for a in activities if "transport" in (a.category or "").lower()])
        self.immobilisation_panel.set_activities([a for a in activities if "immobil" in (a.category or "").lower()])

    def add_activity_row(self, activity: Activity) -> None:
        category = (activity.category or "general").lower()
        if "transport" in category:
            self.transport_panel.add_activity_row(activity)
        elif "immobil" in category:
            self.immobilisation_panel.add_activity_row(activity)
        else:
            self.general_panel.add_activity_row(activity)

    def clear_inputs(self) -> None:
        self.general_panel.clear_inputs()
        self.transport_panel.clear_inputs()
        self.immobilisation_panel.clear_inputs()


class SettingsForm(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Reporting Settings", parent)
        self.report_name = QLineEdit()
        self.report_name.setPlaceholderText("Quarterly GHG Report")
        self.fiscal_year = QLineEdit()
        self.fiscal_year.setPlaceholderText("2026")
        self.export_folder = QLineEdit()
        self.export_folder.setReadOnly(True)
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "Excel"])
        self.export_chart = QCheckBox("Export chart image")
        self.choose_folder_button = QPushButton("Choose folder")
        self.choose_folder_button.clicked.connect(self.choose_export_folder)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.export_folder)
        folder_layout.addWidget(self.choose_folder_button)

        self.preview_label = QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("color: #333333; padding: 6px; background: #f2f4f7; border: 1px solid #d7d7d7; border-radius: 6px;")

        self.folder_warning_label = QLabel("")
        self.folder_warning_label.setStyleSheet("color: #b00020; font-weight: bold;")

        form_layout = QFormLayout()
        form_layout.addRow("Report name:", self.report_name)
        form_layout.addRow("Fiscal year:", self.fiscal_year)
        form_layout.addRow("Export folder:", folder_layout)
        form_layout.addRow("", self.folder_warning_label)
        form_layout.addRow("Export format:", self.export_format)
        form_layout.addRow("", self.export_chart)
        form_layout.addRow("Preview:", self.preview_label)
        self.setLayout(form_layout)

        self.report_name.textChanged.connect(self.update_preview)
        self.fiscal_year.textChanged.connect(self.update_preview)
        self.export_format.currentIndexChanged.connect(self.update_preview)
        self.export_chart.toggled.connect(self.update_preview)
        self.export_folder.textChanged.connect(self.update_preview)
        self.update_preview()

    def choose_export_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select export folder")
        if folder:
            self.export_folder.setText(folder)

    def _safe_filename(self, text: str) -> str:
        sanitized = "_".join(str(text).strip().split())
        return sanitized if sanitized else "ghg_report"

    def _build_preview(self) -> str:
        export_folder = self.export_folder.text().strip()
        if not export_folder:
            return "Choose an export folder to preview report file locations."

        report_name = self._safe_filename(self.report_name.text() or "ghg_report")
        export_format = self.export_format.currentText().lower()
        report_file = Path(export_folder) / f"{report_name}.{ 'xlsx' if export_format == 'excel' else 'csv' }"
        chart_file = Path(export_folder) / f"{report_name}_chart.png" if self.export_chart.isChecked() else None

        preview_lines = [f"Report file: {report_file}"]
        if chart_file:
            preview_lines.append(f"Chart image: {chart_file}")
        return "\n".join(preview_lines)

    def _validate_folder(self) -> Optional[str]:
        folder = self.export_folder.text().strip()
        if not folder:
            return "Export folder is required."
        if not Path(folder).exists():
            return "The selected export folder does not exist."
        return None

    def update_preview(self) -> None:
        warning = self._validate_folder()
        self.folder_warning_label.setText(warning or "")
        self.preview_label.setText(self._build_preview())

    def settings(self) -> Dict[str, object]:
        return {
            "report_name": self.report_name.text().strip() or "ghg_report",
            "fiscal_year": self.fiscal_year.text().strip() or "",
            "export_folder": self.export_folder.text().strip(),
            "export_format": self.export_format.currentText().lower(),
            "export_chart": self.export_chart.isChecked(),
        }
