"""Custom widgets for data entry and summary display."""

from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .charts import build_scope_chart


from PySide6.QtWidgets import QGridLayout, QGroupBox, QVBoxLayout, QLabel, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .charts import build_scope_chart


class SummaryPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("GHG Summary", parent)
        self.total_label = QLabel("0")
        self.scope_1_label = QLabel("0")
        self.scope_2_label = QLabel("0")
        self.scope_3_label = QLabel("0")

        self.total_title = QLabel("Total CO2e")
        self.scope_1_title = QLabel("Scope 1")
        self.scope_2_title = QLabel("Scope 2")
        self.scope_3_title = QLabel("Scope 3")

        for label in [
            self.total_title,
            self.scope_1_title,
            self.scope_2_title,
            self.scope_3_title,
            self.total_label,
            self.scope_1_label,
            self.scope_2_label,
            self.scope_3_label,
        ]:
            label.setWordWrap(True)

        self.total_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.scope_1_title.setStyleSheet("font-weight: bold;")
        self.scope_2_title.setStyleSheet("font-weight: bold;")
        self.scope_3_title.setStyleSheet("font-weight: bold;")
        self.total_label.setStyleSheet("font-size: 22px; color: #2a6f97;")
        self.scope_1_label.setStyleSheet("font-size: 16px;")
        self.scope_2_label.setStyleSheet("font-size: 16px;")
        self.scope_3_label.setStyleSheet("font-size: 16px;")

        grid = QGridLayout()
        grid.addWidget(self.total_title, 0, 0)
        grid.addWidget(self.total_label, 1, 0)
        grid.addWidget(self.scope_1_title, 0, 1)
        grid.addWidget(self.scope_1_label, 1, 1)
        grid.addWidget(self.scope_2_title, 2, 0)
        grid.addWidget(self.scope_2_label, 3, 0)
        grid.addWidget(self.scope_3_title, 2, 1)
        grid.addWidget(self.scope_3_label, 3, 1)
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(30)

        self.setLayout(grid)
        self.setStyleSheet(
            "QGroupBox { background: #fdfdfd; border: 1px solid #dcdcdc; border-radius: 8px; margin-top: 10px; }"
            "QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 5px; }"
        )

    def update_summary(self, totals: dict) -> None:
        self.total_label.setText(f"{totals.get('total_co2e', 0):.3f}")
        self.scope_1_label.setText(f"{totals.get('scope_1', 0):.3f}")
        self.scope_2_label.setText(f"{totals.get('scope_2', 0):.3f}")
        self.scope_3_label.setText(f"{totals.get('scope_3', 0):.3f}")


class ChartPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_scope(self, totals: dict) -> None:
        figure = build_scope_chart(totals)
        self.canvas.figure = figure
        self.canvas.draw_idle()
