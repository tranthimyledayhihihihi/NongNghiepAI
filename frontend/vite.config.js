import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendProxyUrl = process.env.VITE_BACKEND_PROXY_URL || env.VITE_BACKEND_PROXY_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      watch: {
        usePolling: true
      },
      proxy: {
        '/api': {
          target: backendProxyUrl,
          changeOrigin: true
        },
        '/health': {
          target: backendProxyUrl,
          changeOrigin: true
        },
        '/db-test': {
          target: backendProxyUrl,
          changeOrigin: true
        }
      }
    }
  }
})
