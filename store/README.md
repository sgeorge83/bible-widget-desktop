# Microsoft Store — Bible Widget Desktop

Publisher: **WordOnAir Labs**  
Homepage: https://wordonair.com  
Privacy policy URL for Partner Center:

https://sgeorge83.github.io/bible-widget-desktop/  
Repo: https://github.com/sgeorge83/bible-widget-desktop

## Product identity

| Field | Value |
|------|--------|
| App name | Bible Widget — Verse of the Day |
| Short name | Bible Widget |
| Package identity name | `WordOnAirLabs.BibleWidgetDesktop` (replace with Partner Center value) |
| Publisher display | WordOnAir Labs |
| Category | Lifestyle, or Books & reference |
| Age rating | Suitable for all ages (religious text, no ads) |
| Price | Free |

## Listing (en-US)

Copy from `store/listing/en-US/`.

## Privacy

See `store/privacy/`. Host the HTML on GitHub Pages, wordonair.com, or any public HTTPS URL, then paste that URL in Partner Center.

The app:
- Fetches the daily verse from `https://bible-widget-backend.vercel.app/api/morning`
- Stores the last verse and window position locally
- Does **not** require a Microsoft account
- Does **not** collect personal data for advertising
- Does **not** use advertising ID

## Package

Build from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_msix.ps1
```

Output:
- Payload: `dist\BibleWidgetDesktop\`
- MSIX (if Windows SDK is installed): `dist\BibleWidgetDesktop_1.0.0.0_x64.msix`

Before packing for Store, set **Identity Name** and **Publisher CN** from Partner Center → App identity (see `packaging/identity.env.example`).

Upload the `.msix` in Partner Center. Microsoft signs Store packages; you do not need a paid code-signing cert for Store submission.

## Screenshots (you capture these)

Partner Center needs at least one desktop screenshot. Recommended:

1. Widget on a Windows 11 desktop with wallpaper showing through (1920×1080)
2. Same widget resized larger, verse fully visible
3. Start menu / pinned tile (optional)

Do **not** include other companies’ widgets in the screenshot if you can avoid it.

## Notes

This is a **floating desktop widget** (closest match to the Android home-screen widget), packaged as a full-trust Win32 MSIX. A Windows 11 Widgets Board provider can be added later.
