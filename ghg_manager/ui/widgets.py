"""Custom widgets for data entry and summary display."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SummaryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Total CO2e: 0"))
        layout.addWidget(QLabel("Scope 1: 0"))
        layout.addWidget(QLabel("Scope 2: 0"))
        layout.addWidget(QLabel("Scope 3: 0"))
        self.setLayout(layout)
