import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  base: './',
  optimizeDeps: {
    exclude: ['electron']
  },
  build: {
    outDir: 'renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/renderer/index.html'),
      },
    },
    cssCodeSplit: true,
    minify: 'terser',
    sourcemap: true,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/renderer'),
      '@components': resolve(__dirname, 'src/renderer/components'),
      '@styles': resolve(__dirname, 'src/renderer/styles'),
      '@utils': resolve(__dirname, 'src/renderer/utils'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@styles/variables.scss";`,
      },
    },
  },
  define: {
    'process.env': process.env,
  },
  ssr: {
    noExternal: ['electron']
  },
});
