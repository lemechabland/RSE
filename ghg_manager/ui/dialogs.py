"""Reusable dialog widgets for importing and editing data."""

from PySide6.QtWidgets import QDialog


class ImportDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Data")


class NewActivityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Activity")
