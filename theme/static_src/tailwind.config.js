module.exports = {
  content: [
    '../../../**/*.{html,py,js}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6', // Blue-500
        secondary: '#64748b', // Slate-500
        success: '#10b981', // Emerald-500
        danger: '#ef4444', // Red-500
        warning: '#f59e0b', // Amber-500
        info: '#06b6d4', // Cyan-500
        light: '#f1f5f9', // Slate-100
        dark: '#1e293b', // Slate-800
        'rose-50': 'hsl(20, 50%, 98%)',
        'rose-100': 'hsl(13, 31%, 94%)',
        'rose-300': 'hsl(14, 25%, 72%)',
        'rose-500': 'hsl(12, 20%, 44%)',
        'rose-900': 'hsl(14, 65%, 9%)'
      },
      fontFamily: {
        'body': ['Red Hat Text', 'sans-serif']
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'input': '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
      },
      borderRadius: {
        'card': '0.5rem'
      },
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
};