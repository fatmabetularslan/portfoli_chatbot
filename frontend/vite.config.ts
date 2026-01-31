import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite dev server proxy:
// - `/api/*` -> FastAPI (127.0.0.1:8000)
// Not: `/assets/*` ve `/fonts/*` artık `frontend/public` içinden servis ediliyor.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Windows'ta `localhost` bazen ::1 (IPv6) çözülüp ECONNREFUSED verebiliyor.
      // 127.0.0.1 kullanarak IPv4'e sabitliyoruz.
      '/api': 'http://127.0.0.1:8000',
    },
  },
})

