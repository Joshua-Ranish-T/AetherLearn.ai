/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))',
        },
        // Custom brand colors
        brand: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d7fe',
          300: '#a5bcfc',
          400: '#8098f9',
          500: '#6172f3',
          600: '#444fe8',
          700: '#3538cc',
          800: '#2d31a6',
          900: '#2d3282',
        },
        purple: {
          deep: '#1a1a2e',
          mid: '#16213e',
          accent: '#0f3460',
          hot: '#e94560',
        },
        'surface-container-low': '#FAFAFA', // Dr. White
        'inverse-surface': '#2d3748',
        'on-primary-container': '#1a202c',
        'outline': '#C1C2C1', // Stonewall Grey
        'surface-bright': '#EBEDEC', // Moonlit Snow
        'on-tertiary-fixed-variant': '#274774',
        'surface-container-highest': '#DBE5DD', // Aqua Squeeze
        'error-container': '#93000a',
        'secondary-fixed': '#dae1ff',
        'on-primary-fixed-variant': '#1a202c',
        'on-error': '#ffffff',
        'on-error-container': '#ffdad6',
        'on-background': '#1a202c',
        'primary-fixed': '#6ED987', // Jube Green
        'surface-container-lowest': '#ffffff',
        'secondary-fixed-dim': '#bbc5eb',
        'primary-container': '#d1f4d9',
        'on-secondary-container': '#1a202c',
        'tertiary': '#1BC237', // Green With Envy
        'on-primary-fixed': '#000000',
        'surface': '#FAFAFA', // Dr. White
        'surface-variant': '#EBEDEC', // Moonlit Snow
        'outline-variant': '#C1C2C1', // Stonewall Grey
        'surface-container': '#DBE5DD', // Aqua Squeeze
        'inverse-primary': '#1BC237',
        'on-secondary': '#ffffff',
        'inverse-on-surface': '#f8fafc',
        'on-tertiary-fixed': '#001b3c',
        'tertiary-fixed': '#d5e3ff',
        'surface-dim': '#EBEDEC',
        'primary-fixed-dim': '#1BC237', // Green With Envy
        'surface-tint': '#6ED987', // Jube Green
        'on-tertiary-container': '#1a202c',
        'on-tertiary': '#ffffff',
        'on-secondary-fixed-variant': '#3b4665',
        'on-primary': '#ffffff',
        'on-surface-variant': '#4a5568',
        'on-secondary-fixed': '#0f1a37',
        'secondary-container': '#e2e8f0',
        'on-surface': '#2d3748', // Dark text for light mode
        'surface-container-high': '#DBE5DD', // Aqua Squeeze
        'tertiary-container': '#c6f6d5',
        'tertiary-fixed-dim': '#6ED987' // Jube Green
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        'body-base': ['Inter', 'sans-serif'],
        'code-sm': ['JetBrains Mono', 'monospace'],
        'display-lg-mobile': ['Inter', 'sans-serif'],
        'label-caps': ['JetBrains Mono', 'monospace'],
        'display-lg': ['Inter', 'sans-serif'],
        'headline-md': ['Inter', 'sans-serif']
      },
      fontSize: {
        'body-base': ['16px', { lineHeight: '1.6', fontWeight: '400' }],
        'code-sm': ['14px', { lineHeight: '1.4', fontWeight: '500' }],
        'display-lg-mobile': ['32px', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '800' }],
        'label-caps': ['12px', { lineHeight: '1.0', letterSpacing: '0.1em', fontWeight: '700' }],
        'display-lg': ['48px', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '800' }],
        'headline-md': ['24px', { lineHeight: '1.3', fontWeight: '600' }]
      },
      spacing: {
        sm: '12px',
        xl: '80px',
        md: '24px',
        xs: '4px',
        base: '8px',
        gutter: '24px',
        lg: '48px',
        'container-max': '1440px'
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(99, 114, 243, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(99, 114, 243, 0.8)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'brand-gradient': 'linear-gradient(135deg, #6172f3 0%, #e94560 100%)',
        'dark-gradient': 'linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        'shimmer-gradient': 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%)',
      },
    },
  },
  plugins: [],
}
