from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ghg_manager.ui.style_loader import compile_style_sheet
from ghg_manager.ui.ui_builder import compile_ui_file


def build_ui_modules() -> None:
    ui_folder = ROOT / "ghg_manager" / "ui"
    generated_folder = ui_folder / "generated"
    generated_folder.mkdir(parents=True, exist_ok=True)
    for ui_file in sorted(ui_folder.glob("*.ui")):
        output_file = generated_folder / f"{ui_file.stem}_ui.py"
        compile_ui_file(ui_file, output_file)
        print(f"Compiled {ui_file.name} -> {output_file.name}")


def build_style_sheet() -> None:
    qss_path = compile_style_sheet(force=True)
    print(f"Compiled style sheet to {qss_path}")


if __name__ == "__main__":
    build_ui_modules()
    build_style_sheet()
