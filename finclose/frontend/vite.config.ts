import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // 상위 저장소의 PostCSS 설정을 상속하지 않도록 격리
  css: { postcss: { plugins: [] } },
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  build: { outDir: "dist", sourcemap: false },
});
