"""Custom widgets for data entry and summary display."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGridLayout, QGroupBox, QSizePolicy, QVBoxLayout, QLabel, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .charts import build_scope_chart


class BannerLabel(QLabel):
    """A hero image that scales with its container without cropping or
    distorting the source pixmap (only its width/height ratio changes)."""

    def __init__(self, pixmap: QPixmap, max_height: int = 260, parent=None):
        super().__init__(parent)
        self._source = pixmap
        self._max_height = max_height
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def resizeEvent(self, event) -> None:
        if not self._source.isNull() and self.width() > 0:
            scaled = self._source.scaledToWidth(self.width(), Qt.SmoothTransformation)
            if scaled.height() > self._max_height:
                scaled = self._source.scaledToHeight(self._max_height, Qt.SmoothTransformation)
            # Fix the label's own height to the pixmap's so the layout can
            # never allot it less space than what it is about to paint,
            # which would otherwise silently clip the image.
            self.setFixedHeight(scaled.height())
            self.setPixmap(scaled)
        super().resizeEvent(event)


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

        self.total_title.setProperty("role", "summary-title")
        self.scope_1_title.setProperty("role", "summary-subtitle")
        self.scope_2_title.setProperty("role", "summary-subtitle")
        self.scope_3_title.setProperty("role", "summary-subtitle")
        self.total_label.setProperty("role", "summary-total")
        self.scope_1_label.setProperty("role", "summary-value")
        self.scope_2_label.setProperty("role", "summary-value")
        self.scope_3_label.setProperty("role", "summary-value")

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
