# Bible Widget Desktop — Verse of the Day

Floating always-on-top Windows desktop widget that shows today's ESV verse, matching the Android [Bible Widget](https://github.com/sgeorge83/BibleWidgetApp) structure and **WordOnAir** branding from [wordonair.com](https://wordonair.com).

Built by **WordOnAir Labs**.

---

## Features

| Feature | Detail |
|--------|--------|
| Floating widget | Frameless, draggable, always-on-top (toggle with pin) |
| Same API as Android | `https://bible-widget-backend.vercel.app/api/morning` |
| Daily refresh | Targets **9:30 AM Asia/Dubai** (same as Android) |
| Local cache | Keeps last verse if offline |
| WordOnAir colors | Deep navy `#060B14`, light text `#F4F7FB`, gold accent `#D4A853` |
| Structure | Title · verse · reference · insight · meaning · brand · ESV disclaimer |

---

## Run locally (Windows)

Requirements: **Python 3.11+**, [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/) (usually already installed on Windows 10/11).

```powershell
cd BibleWidgetDesktop
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

---

## Build a standalone `.exe`

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --clean bible-widget-desktop.spec
```

Output: `dist\BibleWidgetDesktop\BibleWidgetDesktop.exe`

---

## Microsoft Store

See [`store/`](store/) for listing copy, privacy notes, and a packaging / Partner Center checklist.

High-level path:

1. Build the desktop app (PyInstaller or later WinUI packaging).
2. Package as **MSIX** (e.g. with the Windows App Packaging tools / Partner Center).
3. Submit via [Partner Center](https://partner.microsoft.com/dashboard).

---

## Project layout

```
app.py                 # Floating WebView2 window (pywebview)
widget/
  index.html           # Widget chrome (matches Android layout)
  widget.css           # WordOnAir palette
  widget.js            # Fetch / cache / daily refresh
store/                 # Store listing helpers
.github/workflows/     # CI checks on GitHub
```

---

## Scripture copyright

Scripture quotations are from the **ESV® Bible** (The Holy Bible, English Standard Version®), copyright © Crossway. Used in accordance with ESV API terms.

---

## License & author

© **WordOnAir Labs** — [sgeorge83](https://github.com/sgeorge83)
