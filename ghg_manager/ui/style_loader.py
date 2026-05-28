from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

try:
    import sass
except ImportError:  # pragma: no cover
    sass = None


def _theme_path() -> Path:
    return Path(__file__).resolve().parents[2] / "styles" / "theme.json"


def _scss_path() -> Path:
    return Path(__file__).resolve().parents[2] / "styles" / "style.scss"


def _output_path() -> Path:
    return Path(__file__).resolve().parent / "style.qss"


def load_theme() -> Dict[str, str]:
    theme_path = _theme_path()
    with theme_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    return {key: str(value) for key, value in raw.items()}


def _render_scss(scss_text: str, variables: Dict[str, str]) -> str:
    variable_block = "\n".join(f"${key}: {value};" for key, value in variables.items())
    source = f"{variable_block}\n{scss_text}"

    if sass is not None:
        return sass.compile(string=source)

    rendered = source
    rendered = re.sub(r"^\s*\$[a-zA-Z0-9_-]+:.*$", "", rendered, flags=re.MULTILINE)

    def replace(match: re.Match) -> str:
        name = match.group(1)
        return variables.get(name, match.group(0))

    return re.sub(r"\$([a-zA-Z0-9_-]+)", replace, rendered)


def compile_style_sheet(force: bool = False) -> Path:
    qss_path = _output_path()
    scss_path = _scss_path()
    theme = load_theme()

    theme_path = _theme_path()
    if qss_path.exists() and not force:
        if qss_path.stat().st_mtime >= max(scss_path.stat().st_mtime, theme_path.stat().st_mtime):
            return qss_path

    scss_text = scss_path.read_text(encoding="utf-8")
    qss_text = _render_scss(scss_text, theme)
    qss_path.write_text(qss_text, encoding="utf-8")
    return qss_path


def apply_app_style(app) -> None:
    qss_path = compile_style_sheet()
    app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
