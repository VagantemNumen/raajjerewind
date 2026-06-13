# Building Raajje Rewind as a native app (Capacitor)

The web app is wrapped with [Capacitor](https://capacitorjs.com/) to produce
native Android / iOS apps. Because every answer needs the FastAPI backend, the
native shell loads the **live HTTPS site** rather than running offline — so the
app updates instantly when you deploy, with no store resubmission.

Config lives in `capacitor.config.ts`. The generated `android/` and `ios/`
projects are gitignored; regenerate them with the `cap:add:*` scripts below.

## One-time setup

Point the shell at your deployed domain (otherwise its `/api` calls hit
localhost and fail). Set it in your shell before syncing:

```bash
# PowerShell
$env:CAP_SERVER_URL = "https://raajje-rewind.example.xyz"
# bash
export CAP_SERVER_URL="https://raajje-rewind.example.xyz"
```

Then add the platform(s) you want to build:

```bash
npm run cap:add:android   # needs Android Studio + SDK
npm run cap:add:ios       # needs macOS + Xcode
```

## Build / run

```bash
npm run cap:android   # build web, sync, open in Android Studio
npm run cap:ios       # build web, sync, open in Xcode (macOS only)
npm run cap:sync      # just rebuild web + copy into all native projects
```

From Android Studio you can run on a device/emulator or build a signed
`.aab` for the Play Store. From Xcode you archive and upload to App Store
Connect.

## Things to know

- **App ID** is `mv.raajjerewind.app` (in `capacitor.config.ts`). Change it
  before your first store submission — it's permanent per store listing.
- **iOS requires a Mac + Xcode** and an Apple Developer account
  (**$99/year, recurring**). Android needs a Play Console account
  (**$25, one-time**).
- A thin "website in a shell" app can be rejected under App Store guideline
  4.2 (minimum functionality). The installed PWA already covers most of the
  "it's an app" experience for free.
- App icons / splash: generate with
  [`@capacitor/assets`](https://github.com/ionic-team/capacitor-assets) from a
  source logo, then re-sync.
