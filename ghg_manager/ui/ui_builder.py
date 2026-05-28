from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import Optional


def _pyside6_uic_path() -> Optional[str]:
    return which("pyside6-uic")


def compile_ui_file(ui_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    uic_exe = _pyside6_uic_path()
    if uic_exe is None:
        raise RuntimeError("Could not find pyside6-uic in PATH. Install PySide6 and ensure pyside6-uic is available.")

    completed = subprocess.run(
        [uic_exe, "-o", str(output_path), str(ui_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"UI compilation failed for {ui_path}: {completed.stderr or completed.stdout}"
        )


def load_ui_module(ui_path: Path):
    ui_path = ui_path.resolve()
    target = ui_path.parent / "generated" / f"{ui_path.stem}_ui.py"
    if not target.exists() or ui_path.stat().st_mtime > target.stat().st_mtime:
        compile_ui_file(ui_path, target)

    module_name = f"ghg_manager.ui.generated.{ui_path.stem}_ui"
    spec = importlib.util.spec_from_file_location(module_name, str(target))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to create import spec for {target}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
