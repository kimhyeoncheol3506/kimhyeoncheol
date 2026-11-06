import { defineConfig } from 'vite';

export default defineConfig({
  server: { port: +(process.env.PORT || 5173), strictPort: true, fs: { strict: false } },
  build: { target: 'es2022', chunkSizeWarningLimit: 4000 },
});
