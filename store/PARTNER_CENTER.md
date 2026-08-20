# Microsoft Store submission guide

## 1. Partner Center

1. Open https://partner.microsoft.com/dashboard
2. Create a new app: **Bible Widget — Verse of the Day**
3. Reserve the name if available
4. Publisher: WordOnAir Labs

## 2. Build the app

On a Windows machine (or via GitHub Actions artifact):

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --clean bible-widget-desktop.spec
```

Artifact folder: `dist\BibleWidgetDesktop\`

## 3. Package as MSIX (recommended path)

Options:

1. **Visual Studio** — Windows Application Packaging Project targeting the PyInstaller output folder
2. **MSIX Packaging Tool** from the Microsoft Store
3. **Partner Center** — upload unpackaged build only if you use a supported Desktop Bridge flow

Minimum package identity example:

- Name: `WordOnAirLabs.BibleWidgetDesktop`
- Publisher: your Partner Center publisher CN=
- Version: `1.0.0.0`

## 4. Capabilities

Declare only what you need:

- Internet (Client) — daily verse fetch
- No microphone / camera / contacts

## 5. Certification tips

- Include ESV copyright text in-app (already in the widget footer)
- Privacy policy URL must be public HTTPS
- Screenshots should clearly show the floating widget, not only the Store logo
- Age rating: religious content, no mature themes

## 6. After approval

Link the Store listing from wordonair.com and the Android Play listing for cross-promotion.
