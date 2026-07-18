import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy /api và /audio về backend FastAPI (cổng 8000) trong lúc dev,
// nhờ đó frontend chỉ dùng đường dẫn tương đối (/api/..., /audio/...).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/audio': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
