import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// U1 백엔드(FastAPI, uvicorn 기본 :8000)로 API 프록시 → 브라우저 CORS 우회.
// 백엔드 라우트는 프리픽스 없이 /intent, /advise, /feedback.
const BACKEND = process.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/intent': { target: BACKEND, changeOrigin: true },
      '/advise': { target: BACKEND, changeOrigin: true },
      '/feedback': { target: BACKEND, changeOrigin: true },
    },
  },
})
