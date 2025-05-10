// plugins/vuetify.js

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// Vuetify setup with custom theme
export default createVuetify({
  theme: {
    defaultTheme: 'noToxicTheme',
    themes: {
      noToxicTheme: {
        dark: true,
        colors: {
          primary: '#134B66',     // Indigo dye - main background, navbar, footer
          secondary: '#8B85C1',   // Tropical indigo - button hovers, accents
          accent: '#D4CDF4',      // Periwinkle - light highlights, text accents
          error: '#DA2C38',       // Poppy - toxic messages
          success: '#149911',     // Forest green - non-toxic messages
          background: '#134B66',  // General background color
          surface: '#1F2F3F',     // Cards, dialogs, input boxes
        },
      },
    },
  },
})
