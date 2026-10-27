<template>
  <!-- Main navigation bar component -->
  <v-toolbar color="#2c3e50" dark>
    <!-- Site title/logo that links to home page -->
    <v-toolbar-title class="text-h6 font-weight-bold">
      <span 
        @click="$router.push('/')" 
        class="title-text"
      >
        Travel Planner
      </span>
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <!-- Home navigation button -->
    <v-btn text to="/" class="mx-2 nav-btn">
      <v-icon left>mdi-home</v-icon>
      Home
    </v-btn>

    <!-- Navigation links for authenticated users -->
    <template v-if="isAuthenticated">
      <v-btn text to="/community" class="mx-2 nav-btn">
        <v-icon left>mdi-account-group</v-icon>
        Community
      </v-btn>

      <v-btn text to="/destinations" class="mx-2 nav-btn">
        <v-icon left>mdi-map-marker</v-icon>
        Destinations
      </v-btn>
      
      <v-btn text to="/most-loved" class="mx-2 nav-btn">
        <v-icon left>mdi-heart</v-icon>
        Popular
      </v-btn>

      <v-btn text to="/nearby" class="mx-2 nav-btn">
        <v-icon left>mdi-near-me</v-icon>
        Nearby
      </v-btn>

      <v-btn text to="/recommendations" class="mx-2 nav-btn">
        <v-icon left>mdi-star</v-icon>
        Recommendations
      </v-btn>

      <v-btn text to="/planner" class="mx-2 nav-btn">
        <v-icon left>mdi-calendar-check</v-icon>
        Planner
      </v-btn>

      <v-btn text to="/flights" class="mx-2 nav-btn">
        <v-icon left>mdi-airplane</v-icon>
        Flights
      </v-btn>

      <v-btn text to="/mypage" class="mx-2 nav-btn">
        <v-icon left>mdi-account</v-icon>
        My Page
      </v-btn>

      <v-btn text @click="logout" class="mx-2 nav-btn">
        <v-icon left>mdi-logout</v-icon>
        Logout
      </v-btn>
    </template>

    <!-- Navigation links for non-authenticated users -->
    <template v-else>
      

      <v-btn text to="/register" class="mx-2 nav-btn">
        <v-icon left>mdi-account-plus</v-icon>
        Register
      </v-btn>

      <v-btn text to="/login" class="mx-2 nav-btn">
        <v-icon left>mdi-login</v-icon>
        Login
      </v-btn>
    </template>

  </v-toolbar>
</template>


<script>
import axios from 'axios';

/**
 * Main navigation bar component
 * Displays different navigation options based on authentication status
 */
export default {
  name: 'AppNavbar',
  data() {
    return {
      isAuthenticated: !!localStorage.getItem('access_token'),
    };
  },
  methods: {
    /**
     * Check authentication status from localStorage
     * Updates the component state based on token presence
     */
    checkAuth() {
      this.isAuthenticated = !!localStorage.getItem('access_token');
    },
    
    /**
     * Handle user logout
     * Removes tokens from localStorage and redirects to login page
     */
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete axios.defaults.headers.common['Authorization'];

      alert("Successfully Logged Out.");
      this.isAuthenticated = false;
      this.$router.push('/login');
    }
  },
  mounted() {
    // Add event listeners to handle authentication changes
    window.addEventListener('storage', this.checkAuth);
    document.addEventListener('auth-changed', this.checkAuth);
  },
  beforeUnmount() {
    // Clean up event listeners
    window.removeEventListener('storage', this.checkAuth);
    document.removeEventListener('auth-changed', this.checkAuth);
  }
};
</script>

<style scoped>
/* Toolbar base styling */
.v-toolbar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Navigation button styling */
.nav-btn {
  text-transform: none;
  letter-spacing: 0.5px;
  font-weight: 400;
  opacity: 0.9;
  transition: opacity 0.2s;
}

/* Navigation button hover effect */
.nav-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1) !important;
}

/* Title text styling and interactions */
.title-text {
  color: white;
  cursor: pointer;
  transition: color 0.2s;
}

/* Active state for title click */
.title-text:active {
  color: #FF5252 !important;  /* Red color when clicked */
}

/* Hover effect for title */
.title-text:hover {
  opacity: 0.9;
}

/* Active route styling */
:deep(.router-link-active) {
  color: white !important;
}
</style>