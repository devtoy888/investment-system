/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#0a0e1a',
          card: 'rgba(17,24,39,0.8)',
          accent: '#f59e0b',
          up: '#22c55e',
          down: '#ef4444',
          muted: '#6b7280',
          'muted-foreground': '#9ca3af',
        }
      }
    },
  },
  plugins: [],
}
