module.exports = {
  content: [
    './app/**/*.{ts,tsx}',
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#1a1a1a',
        foreground: '#ffffff',
        primary: {
          DEFAULT: '#f4d03f',
          foreground: '#1a1a1a',
        },
        secondary: {
          DEFAULT: '#f8b4d9',
          foreground: '#1a1a1a',
        },
        accent: {
          DEFAULT: '#e8c39e',
          foreground: '#1a1a1a',
        },
        muted: {
          DEFAULT: '#2a2a2a',
          foreground: '#a0a0a0',
        },
        border: '#333333',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
