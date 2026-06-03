/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        brand: {
          50:  '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          primary: '#6366f1',
          'primary-hover': '#4f46e5',
          'primary-soft': '#818cf8',
          canvas: {
            light: '#ffffff',
            dark: '#09090b',
          },
          'canvas-soft': {
            light: '#f6f9fc',
            dark: '#18181b',
          },
          ink: {
            light: '#0d253d',
            dark: '#fafafa',
          },
          'ink-mute': {
            light: '#64748d',
            dark: '#a1a1aa',
          },
          hairline: {
            light: '#e3e8ee',
            dark: '#27272a',
          }
        },
      },
      borderRadius: {
        'stripe-card': '12px',
        'stripe-input': '6px',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'stripe-1': 'rgba(0, 55, 112, 0.08) 0px 1px 3px',
        'stripe-2': 'rgba(0, 55, 112, 0.08) 0px 8px 24px, rgba(0, 55, 112, 0.04) 0px 2px 6px',
      }
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
