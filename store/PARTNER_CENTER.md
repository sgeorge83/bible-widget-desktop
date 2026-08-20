# Microsoft Store submission guide

## 1. Partner Center app

1. Open https://partner.microsoft.com/dashboard
2. Create a new app: **Bible Widget — Verse of the Day**
3. Reserve the name
4. Publisher display name: **WordOnAir Labs**
5. Copy **Package/Identity Name** and **Publisher** from **App identity**
6. Put those values into `packaging/AppxManifest.xml` (or pass them to `build_msix.ps1`)

## 2. Host the privacy policy

Public URL (GitHub Pages, served from `docs/` on `main`):

**https://sgeorge83.github.io/bible-widget-desktop/**

Paste that URL in Partner Center → Properties. Source file: `docs/index.html`.

## 3. Build the Store package

On Windows (or via GitHub Actions):

```powershell
cd C:\Users\SharoonGeorge\Projects\BibleWidgetDesktop
powershell -ExecutionPolicy Bypass -File packaging\build_msix.ps1 `
  -IdentityName "YOUR_IDENTITY_NAME" `
  -Publisher "CN=YOUR_PUBLISHER_ID" `
  -Version 1.0.0.0
```

Upload `dist\BibleWidgetDesktop_1.0.0.0_x64.msix` under **Packages**.

## 4. Listing

Paste copy from `store/listing/en-US/`.

| Partner Center field | File |
|----------------------|------|
| Product name | `title.txt` |
| Short description | `short_description.txt` |
| Description | `full_description.txt` |
| Search terms | `search_terms.txt` |
| What’s new | `release_notes.txt` |

Category: **Lifestyle** (secondary: Books & reference).

## 5. Age rating / declarations

- Age rating questionnaire: general audience, religious/spiritual content, no violence, no sexual content, no ads
- This product does **not** use advertising ID
- Windows capabilities: **internetClient** + **runFullTrust** (Win32 desktop widget — required for unpackaged-style Python/WinForms)

When Partner Center asks why `runFullTrust` is needed: the app is a classic Win32 desktop widget (Python / Windows Forms), not a UWP app.

## 6. Certification tips

- ESV copyright is already in the widget footer
- Privacy policy URL must stay live
- Screenshots should show **this** widget clearly
- Test on Windows 10 1809+ / Windows 11 before submit

## 7. After approval

Link the Store listing from wordonair.com and the Android Play listing.
