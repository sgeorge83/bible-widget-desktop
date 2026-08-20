# Microsoft Store — Bible Widget Desktop

Publisher: **WordOnAir Labs**  
Homepage: https://wordonair.com  
Repo: https://github.com/sgeorge83/bible-widget-desktop

## Product identity

| Field | Value |
|------|--------|
| App name | Bible Widget — Verse of the Day |
| Short name | Bible Widget |
| Publisher display | WordOnAir Labs |
| Category | Lifestyle / Books & reference |
| Age rating | Suitable for all ages (religious text) |

## Listing (en-US)

### Title
Bible Widget — Verse of the Day

### Short description
Daily ESV verse on your Windows desktop — same WordOnAir widget you know from Android.

### Full description
Bible Widget places today's English Standard Version (ESV) verse on your Windows desktop as a floating, always-on-top widget.

Features:
• Verse of the Day with reference
• Short Verse Insight / simplified meaning
• Updates each morning (Asia/Dubai schedule, same as the Android widget)
• Works offline with the last cached verse
• WordOnAir Labs branding and colors from wordonair.com

Scripture quotations are from the ESV® Bible (The Holy Bible, English Standard Version®), copyright © Crossway.

Published by WordOnAir Labs. Learn more at https://wordonair.com

## Privacy

This app:
- Fetches the daily verse from `https://bible-widget-backend.vercel.app/api/morning`
- Stores the last verse and window position locally on the device
- Does **not** require a Microsoft account
- Does **not** collect personal data for advertising
- Does **not** use advertising ID

Host a privacy policy URL (you can reuse the Android policy under BibleWidgetApp `store/privacy/` if it covers this desktop client).

## Packaging checklist

- [ ] Build `BibleWidgetDesktop.exe` via PyInstaller (CI artifact on GitHub Actions)
- [ ] Create MSIX package (Visual Studio Packaging Project, or `MakeAppx` / Partner Center)
- [ ] Add Store logos (44×44, 150×150, 310×150, Store logo)
- [ ] Screenshots of the floating widget on a Windows 11 desktop
- [ ] Partner Center listing + age rating questionnaire
- [ ] Submit for certification

## Notes

True Windows 11 **Widgets Board** pins require a WinUI / Widget Provider package. This release is a **floating desktop widget** (closest match to the Android home-screen widget). A Widgets Board provider can be added later as a second package if needed.
