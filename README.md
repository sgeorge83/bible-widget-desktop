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
| WordOnAir colors | Transparent light-navy glass (wallpaper shows through), gold `#D4A853`, teal `#5EC4CF` |
| Structure | Title · verse · reference · insight · meaning · brand · ESV disclaimer |

---

## Run locally (Windows)

Requirements: **Python 3.11+** on Windows.

```powershell
cd C:\Users\SharoonGeorge\Projects\BibleWidgetDesktop
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks `Activate.ps1`, skip the venv script and run `python app.py` directly. Drag the widget to move it; resize from the edges.

---

## Build a standalone `.exe`

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --clean bible-widget-desktop.spec
```

Output: `dist\BibleWidgetDesktop\BibleWidgetDesktop.exe`

---

## Microsoft Store

Full listing copy, privacy policy, and Partner Center steps: [`store/`](store/)

Build a Store package:

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_msix.ps1
```

Then submit `dist\BibleWidgetDesktop_1.0.0.0_x64.msix` at [Partner Center](https://partner.microsoft.com/dashboard). Replace the Publisher CN in `packaging/AppxManifest.xml` with your Partner Center identity first.

---

## Project layout

```
app.py                 # Floating WinForms widget
verse.py               # API fetch + cache
packaging/             # AppxManifest, Store logos, MSIX build
store/                 # Listing copy + privacy policy
.github/workflows/     # CI: API check, exe, MSIX payload
```

---

## Scripture copyright

Scripture quotations are from the **ESV® Bible** (The Holy Bible, English Standard Version®), copyright © Crossway. Used in accordance with ESV API terms.

---

## License & author

© **WordOnAir Labs** — [sgeorge83](https://github.com/sgeorge83)
