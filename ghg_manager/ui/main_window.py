"""Main window for the GHG Manager application."""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel


class MainWindow(QMainWindow):
    """Primary application shell."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GHG Manager")
        self.setMinimumSize(1024, 720)
        self._setup_ui()

    def _setup_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Welcome to the GHG Manager"))
        layout.addWidget(QLabel("Use the menus to load company data, emissions factors, and see computed scope summaries."))
        container.setLayout(layout)
        self.setCentralWidget(container)
