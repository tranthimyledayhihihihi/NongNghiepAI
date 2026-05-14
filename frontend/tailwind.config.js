/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Be Vietnam Pro'", '-apple-system', 'BlinkMacSystemFont', "'Segoe UI'", 'sans-serif'],
        mono: ["'JetBrains Mono'", 'Menlo', 'Monaco', 'Consolas', "'Courier New'", 'monospace'],
      },
      colors: {
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        }
      },
      fontSize: {
        'xs':   ['0.75rem',  { lineHeight: '1.5' }],
        'sm':   ['0.875rem', { lineHeight: '1.6' }],
        'base': ['0.9375rem',{ lineHeight: '1.6' }],
        'lg':   ['1.0625rem',{ lineHeight: '1.5' }],
        'xl':   ['1.1875rem',{ lineHeight: '1.4' }],
        '2xl':  ['1.375rem', { lineHeight: '1.35'}],
        '3xl':  ['1.75rem',  { lineHeight: '1.3' }],
        '4xl':  ['2.125rem', { lineHeight: '1.25'}],
      },
    },
  },
  plugins: [],
}
