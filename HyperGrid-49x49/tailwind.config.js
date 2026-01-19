/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#020617', // Slate-950
          900: '#0f172a',
          800: '#1e293b',
        },
        accent: {
          amber: '#f59e0b',
          emerald: '#10b981',
          neon: '#8b5cf6',
        }
      },
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
      gridTemplateColumns: {
        '49': 'repeat(49, minmax(0, 1fr))',
        '7': 'repeat(7, minmax(0, 1fr))',
      },
      gridTemplateRows: {
        '7': 'repeat(7, minmax(0, 1fr))',
      },
    },
  },
  plugins: [],
}
