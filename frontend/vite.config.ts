import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

  // Allow LAN tunnels (ngrok / cloudflare quick tunnels) by default for phone
  // PWA testing over HTTPS. Add comma-separated extras via VITE_ALLOWED_HOSTS.
  const allowedHosts = [
    '.ngrok-free.app',
    '.ngrok.app',
    '.trycloudflare.com',
    ...(env.VITE_ALLOWED_HOSTS?.split(',').map((h) => h.trim()).filter(Boolean) ?? []),
  ]

  return {
    plugins: [
      vue(),
      tailwindcss(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
        workbox: {
          runtimeCaching: [
            {
              urlPattern: /\.woff2$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'fonts',
                expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 },
              },
            },
          ],
        },
        manifest: {
          name: 'Raajje Rewind',
          short_name: 'Raajje Rewind',
          description: 'Ask questions about Maldives and its history.',
          theme_color: '#0f172a',
          background_color: '#0f172a',
          display: 'standalone',
          start_url: '/',
          icons: [
            { src: 'pwa-192.png', sizes: '192x192', type: 'image/png' },
            { src: 'pwa-512.png', sizes: '512x512', type: 'image/png' },
            { src: 'pwa-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
          ],
        },
      }),
    ],
    server: {
      allowedHosts,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    preview: {
      allowedHosts,
    },
  }
})
