import type { CapacitorConfig } from '@capacitor/cli'

// Raajje Rewind needs the FastAPI backend for every answer, so the native app
// can't run fully offline. The simplest, store-friendly setup is to load the
// live HTTPS site inside the native shell (like a TWA): set CAP_SERVER_URL to
// your deployed domain before running `cap sync`, e.g.
//
//   CAP_SERVER_URL=https://raajje-rewind.example.xyz npm run cap:sync
//
// With it set, the shell loads the deployed PWA and updates instantly without
// resubmitting to the stores. Without it, the bundled dist/ loads but its /api
// calls hit localhost and fail — so set it for any real build.
const serverUrl = process.env.CAP_SERVER_URL

const config: CapacitorConfig = {
  appId: 'mv.raajjerewind.app',
  appName: 'Raajje Rewind',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    ...(serverUrl ? { url: serverUrl, cleartext: false } : {}),
  },
}

export default config
