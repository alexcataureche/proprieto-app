/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors
        primary: {
          DEFAULT: '#2563EB',
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#2563EB',
          600: '#1D4ED8',
          700: '#1E40AF',
        },
        // Navy (for titles, sidebar, text)
        navy: {
          DEFAULT: '#1E293B',
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
        },
        // App background
        'app-bg': '#F8FAFC',
        // Surface (cards, table background)
        surface: '#FFFFFF',
        // Semantic badges
        success: {
          bg: '#D1FAE5',
          text: '#065F46',
        },
        warning: {
          bg: '#FEF3C7',
          text: '#92400E',
        },
        danger: {
          bg: '#FEE2E2',
          text: '#991B1B',
        },
      },
      borderColor: {
        DEFAULT: '#E2E8F0',
      },
    },
  },
  plugins: [],
}
