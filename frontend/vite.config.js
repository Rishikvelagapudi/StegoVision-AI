import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development the dev server proxies /api to the local FastAPI backend, so no
// VITE_API_BASE_URL is needed locally. In production set VITE_API_BASE_URL (see .env.example).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://127.0.0.1:8000", changeOrigin: true } },
  },
});
