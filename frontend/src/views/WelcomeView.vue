<template>
  <!-- Welcome page container with background image -->
  <div class="welcome-container">
    <v-container>
      <v-row justify="center" align="center" class="fill-height">
        <v-col cols="12" md="8" class="text-center">
          <!-- Welcome page content with animation -->
          <div data-aos="fade-up" class="welcome-content">
            <h1 class="text-h2 font-weight-bold white--text mb-6">
              Welcome to Travel Planner
            </h1>
            <p class="text-h5 white--text mb-8">
              The Best Choice for Your Perfect Journey
            </p>
            <!-- Buttons for non-authenticated users -->
            <div v-if="!isAuthenticated">
              <v-btn
                to="/login"
                x-large
                color="info"
                elevation="4"
                class="mr-4 mb-4"
                data-aos="fade-up"
                data-aos-delay="200"
              >
                <v-icon left>mdi-login</v-icon>
                Login
              </v-btn>
              <v-btn
                to="/register"
                x-large
                color="secondary"
                elevation="4"
                class="mb-4"
                data-aos="fade-up"
                data-aos-delay="300"
              >
                <v-icon left>mdi-account-plus</v-icon>
                Register
              </v-btn>
            </div>
            
            <!-- Buttons for authenticated users -->
            <div v-else>
              <v-btn
                to="/flights"
                x-large
                color="primary"
                elevation="4"
                class="mr-4 mb-4"
                data-aos="fade-up"
                data-aos-delay="200"
              >
                <v-icon left>mdi-airplane</v-icon>
                Flight Search
              </v-btn>
              <v-btn
                to="/planner"
                x-large
                color="info"
                elevation="4"
                class="mr-4 mb-4"
                data-aos="fade-up"
                data-aos-delay="300"
              >
                <v-icon left>mdi-map-marker-path</v-icon>
                Travel Planner
              </v-btn>
              <v-btn
                to="/recommendations"
                x-large
                color="secondary"
                elevation="4"
                class="mb-4"
                data-aos="fade-up"
                data-aos-delay="400"
              >
                <v-icon left>mdi-star</v-icon>
                Recommendations
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import AOS from 'aos';
import 'aos/dist/aos.css';

/**
 * Welcome View Component
 * Landing page that serves as the entry point to the application
 * Features:
 * - Attractive hero section with background image
 * - Different navigation options based on authentication state
 * - Animated entrance effects for UI elements
 */
export default {
  name: 'WelcomeView',
  mounted() {
    // Initialize animation library with configuration
    AOS.init({
      duration: 1000,
      once: true
    });
  },
  computed: {
    /**
     * Check if user is authenticated
     * @returns {boolean} True if access token exists in localStorage
     */
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  }
};
</script>

<style scoped>
/* Main container with background image */
.welcome-container {
  min-height: 100vh;
  background-image: url('@/assets/back.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  display: flex;
  align-items: center;
  position: relative;
}

/* Dark overlay for better text readability */
.welcome-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

/* Content positioning above the overlay */
.welcome-content {
  position: relative;
  z-index: 1;
}

/* Full height container */
.fill-height {
  min-height: 100vh;
}
</style>
