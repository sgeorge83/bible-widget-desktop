"""Bible Widget Desktop — floating Verse of the Day widget for Windows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import webview

APP_NAME = "Bible Widget — Verse of the Day"
DEFAULT_WIDTH = 380
DEFAULT_HEIGHT = 520
MIN_WIDTH = 300
MIN_HEIGHT = 360
CONFIG_FILE = Path.home() / ".bible-widget-desktop" / "config.json"


class WidgetApi:
    """JS bridge: window.pywebview.api.*"""

    def __init__(self) -> None:
        self._window: webview.Window | None = None
        self._on_top = True

    def attach(self, window: webview.Window, on_top: bool) -> None:
        self._window = window
        self._on_top = on_top

    def toggle_on_top(self) -> bool:
        if self._window is None:
            return self._on_top
        self._on_top = not self._on_top
        self._window.on_top = self._on_top
        return self._on_top

    def close(self) -> None:
        if self._window is not None:
            self._window.destroy()


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def widget_url() -> str:
    widget_dir = Path(__file__).resolve().parent / "widget"
    index = widget_dir / "index.html"
    if not index.exists():
        raise FileNotFoundError(f"Widget UI not found: {index}")
    return index.as_uri()


def main() -> int:
    config = load_config()
    on_top = bool(config.get("on_top", True))
    api = WidgetApi()

    window = webview.create_window(
        title=APP_NAME,
        url=widget_url(),
        width=int(config.get("width", DEFAULT_WIDTH)),
        height=int(config.get("height", DEFAULT_HEIGHT)),
        x=config.get("x"),
        y=config.get("y"),
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        resizable=True,
        frameless=True,
        easy_drag=True,
        on_top=on_top,
        background_color="#060B14",
        text_select=False,
        js_api=api,
    )
    api.attach(window, on_top)

    def on_closing() -> None:
        try:
            save_config(
                {
                    "x": window.x,
                    "y": window.y,
                    "width": window.width,
                    "height": window.height,
                    "on_top": api._on_top,
                }
            )
        except OSError:
            pass

    window.events.closing += on_closing
    webview.start(debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
