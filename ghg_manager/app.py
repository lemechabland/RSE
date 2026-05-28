"""Entry point for the GHG Manager application."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

if __package__ is None and __name__ == "__main__":
    package_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(package_root))

try:
    from .ui.main_window import MainWindow
    from .utils.logging import configure_logging
except ImportError:
    from ghg_manager.ui.main_window import MainWindow
    from ghg_manager.utils.logging import configure_logging


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
