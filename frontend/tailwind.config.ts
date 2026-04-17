import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        heading: ['Outfit', 'Inter', 'ui-sans-serif', 'sans-serif'],
        mono:    ['JetBrains Mono', 'Fira Code', 'ui-monospace', 'monospace'],
      },
      colors: {
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        secondary: {
          400: '#f472b6',
          500: '#ec4899',
          600: '#db2777',
        },
        dark: '#0f172a',
        'surface': {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
        }
      },
      boxShadow: {
        'glow':       '0 0 0 1px rgba(99, 102, 241, 0.15), 0 4px 24px rgba(99, 102, 241, 0.35)',
        'glow-sm':    '0 0 0 1px rgba(99, 102, 241, 0.1), 0 2px 12px rgba(99, 102, 241, 0.2)',
        'glow-pink':  '0 0 0 1px rgba(236, 72, 153, 0.15), 0 4px 24px rgba(236, 72, 153, 0.3)',
        'glow-green': '0 0 0 1px rgba(16, 185, 129, 0.15), 0 4px 24px rgba(16, 185, 129, 0.3)',
        'soft':       '0 20px 40px -15px rgba(0,0,0,0.05)',
        'lift':       '0 4px 12px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04)',
        'card':       '0 1px 3px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)',
        'dropdown':   '0 4px 6px -1px rgba(0,0,0,0.04), 0 10px 40px -4px rgba(0,0,0,0.1)',
        'navbar':     '0 1px 0 0 rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.04)',
      },
      animation: {
        'float':        'float 6s ease-in-out infinite',
        'float-slow':   'float 10s ease-in-out infinite',
        'pulse-slow':   'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':    'spin 8s linear infinite',
        'shimmer':      'shimmer 2s linear infinite',
        'fade-in':      'fadeIn 0.35s ease-out both',
        'fade-in-up':   'fadeInUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both',
        'fade-in-down': 'fadeInDown 0.4s cubic-bezier(0.16, 1, 0.3, 1) both',
        'scale-in':     'scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) both',
        'slide-right':  'slideInRight 0.4s cubic-bezier(0.16, 1, 0.3, 1) both',
        'slide-left':   'slideInLeft 0.4s cubic-bezier(0.16, 1, 0.3, 1) both',
        'ping-slow':    'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'bounce-sm':    'bounceSm 1s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':       { transform: 'translateY(-12px)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-400% 0' },
          '100%': { backgroundPosition: '400% 0' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          from: { opacity: '0', transform: 'translateY(-20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.92)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        slideInRight: {
          from: { opacity: '0', transform: 'translateX(24px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        slideInLeft: {
          from: { opacity: '0', transform: 'translateX(-24px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        bounceSm: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':       { transform: 'translateY(-4px)' },
        },
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':  'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'mesh-indigo':     'radial-gradient(at 40% 20%, hsla(250,100%,76%,0.4) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(210,100%,76%,0.3) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(280,100%,76%,0.35) 0px, transparent 50%)',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'bounce-in': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      backdropBlur: {
        xs: '2px',
      },
      blur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

export default config
