// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // Import path module

// Backend CNAME (ensure http or https is correct)
const targetBackend = 'http://ai-news-analyzer-env.eba-nysdsd77vj8c.us-east-1.elasticbeanstalk.com/analyze';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Tell Vite that the source code and index.html are in the 'src' directory
  root: 'src',
  // Configure build output directory relative to project root
  build: {
    outDir: '../dist', // Output to 'dist' at the project root level
    emptyOutDir: true, // Clean the dist folder before building
  },
  // Adjust server options if needed (e.g., ensure port 3000)
  server: {
    port: 3000,
  },
  // Configure path aliases (optional, but good practice based on your tsconfig)
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})

