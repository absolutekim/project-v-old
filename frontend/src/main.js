/**
 * Main application entry point
 * Configures Vue application with plugins and global settings
 */
import { createApp } from 'vue';
import App from './App.vue';
import { createVuetify } from 'vuetify';
import 'vuetify/styles'; // Import Vuetify styles
import * as components from 'vuetify/components'; // Register Vuetify components
import * as directives from 'vuetify/directives'; // Register Vuetify directives
import router from './router';
import axios from 'axios';
import '@mdi/font/css/materialdesignicons.css'; // Import icon styles
import 'aos/dist/aos.css'; // Import AOS animation styles
import AOS from 'aos';


/**
 * Vuetify configuration
 * Sets up theme, components, directives and icons
 */
const vuetify = createVuetify({
  components, // Add components
  directives, // Add directives
  theme: {
    defaultTheme: 'light', // Set default theme
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#1976D2',  // Can be customized
          // secondary: '#424242',
          // accent: '#82B1FF',
          // error: '#FF5252',
          // info: '#2196F3',
          // success: '#4CAF50',
          // warning: '#FFC107',
        },
      },
    },
  },
  icons: {
    defaultSet: 'mdi', // Set default icon set
  },
});

/**
 * Create and configure Vue application instance
 */
const app = createApp(App);
app.use(vuetify); // Apply Vuetify plugin (must be before router)
app.use(router);


/**
 * Axios global configuration
 * Set base URL and authentication headers
 */
axios.defaults.baseURL = 'http://localhost:8000';

// Set Authorization header if JWT token exists
const token = localStorage.getItem('access_token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  console.log("✅ JWT token found:", token);
} else {
  console.warn("⚠️ No JWT token found in localStorage!");
}

/**
 * Event listener for authentication changes
 * Updates Authorization header when authentication state changes
 */
document.addEventListener('auth-changed', () => {
  const newToken = localStorage.getItem('access_token');
  if (newToken) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    console.log("✅ Token updated:", newToken);
  } else {
    delete axios.defaults.headers.common['Authorization'];
    console.warn("⚠️ Token removed!");
  }
});

/**
 * Axios interceptor for handling token refresh
 * Automatically refreshes expired JWT tokens and retries failed requests
 */
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Prevent infinite loop for retry attempts
    if (originalRequest._retry) {
      return Promise.reject(error);
    }
    
    // Try to refresh token on 401 errors (authentication failure)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        console.warn("⚠️ No refresh token found!");
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
        router.push('/login');
        return Promise.reject(error);
      }

      try {
        console.log("🔄 Attempting to refresh token...");
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken
        });
        
        if (response.data.access) {
          console.log("✅ Token refreshed successfully!");
          localStorage.setItem('access_token', response.data.access);
          
          // Update header with new token
          axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
          
          // Retry original request with new token
          originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;
          return axios(originalRequest);
        } else {
          console.error("❌ Token refresh failed: No access token in response");
          throw new Error("Token refresh failed");
        }
      } catch (refreshError) {
        console.error("❌ Token refresh error:", refreshError);
        
        // Logout on token refresh failure
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
        
        // Redirect to login page
        router.push('/login');
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

// Mount Vue application to DOM
app.mount('#app');

// Initialize AOS animation library
AOS.init({ duration: 1200 });
