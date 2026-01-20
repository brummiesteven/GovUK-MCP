import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { readdirSync, existsSync } from 'fs'

// Get all widget directories that have an index.html file
const widgetsDir = resolve(__dirname, 'src/widgets')
let widgetEntries: Record<string, string> = {}

try {
  const widgets = readdirSync(widgetsDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .filter(dirent => existsSync(resolve(widgetsDir, dirent.name, 'index.html')))
    .map(dirent => dirent.name)

  widgetEntries = Object.fromEntries(
    widgets.map(widget => [widget, resolve(widgetsDir, widget, 'index.html')])
  )
} catch {
  // Widgets directory might not exist yet
}

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: widgetEntries,
      output: {
        entryFileNames: '[name]/index.js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: '[name]/[name][extname]'
      }
    },
    outDir: 'dist',
    emptyDirBeforeWrite: true
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})
