from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WINDOW_STATE_PATH = PROJECT_ROOT / "config" / "window_state.json"
DEFAULT_WIDTH = 500
DEFAULT_HEIGHT = 700
MIN_WIDTH = 300
MIN_HEIGHT = 400
MAX_WIDTH = 1200
MAX_HEIGHT = 1400


@dataclass(frozen=True)
class WindowState:
    x: int = 120
    y: int = 120
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT


def load_window_state(path: Path = WINDOW_STATE_PATH) -> WindowState:
    if not path.exists():
        return WindowState()

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            raw: dict[str, Any] = json.load(file)
    except (OSError, json.JSONDecodeError):
        logging.getLogger(__name__).exception("Failed to load window state")
        return WindowState()

    return WindowState(
        x=_as_int(raw.get("x"), WindowState.x),
        y=_as_int(raw.get("y"), WindowState.y),
        width=_clamp(_as_int(raw.get("width"), WindowState.width), MIN_WIDTH, MAX_WIDTH),
        height=_clamp(_as_int(raw.get("height"), WindowState.height), MIN_HEIGHT, MAX_HEIGHT),
    )


def save_window_state(state: WindowState, path: Path = WINDOW_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "x": state.x,
        "y": state.y,
        "width": _clamp(state.width, MIN_WIDTH, MAX_WIDTH),
        "height": _clamp(state.height, MIN_HEIGHT, MAX_HEIGHT),
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _as_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))
