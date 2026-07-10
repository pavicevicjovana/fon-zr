import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' // This is the package you just installed

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})