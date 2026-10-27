<template>
  <v-footer color="#2c3e50" dark class="mt-5">
    <v-container>
      <!-- Company information section -->
      <v-row>
        <v-col cols="12" md="4">
          <div class="text-h6 mb-3 footer-title">Travel Planner</div>
          <div class="text-body-2 footer-text">
            Make your travel smarter
          </div>
        </v-col>
        
        <!-- Contact information section -->
        <v-col cols="12" md="4">
          <div class="text-h6 mb-3 footer-title">Contact</div>
          <div class="text-body-2 footer-text">
            <v-icon small class="mr-2">mdi-email</v-icon>
            contact@travelplanner.com
          </div>
          <div class="text-body-2 footer-text">
            <v-icon small class="mr-2">mdi-phone</v-icon>
            02-1234-5678
          </div>
        </v-col>
        
        <!-- Social media links section -->
        <v-col cols="12" md="4">
          <div class="text-h6 mb-3 footer-title">Follow Us</div>
          <div class="d-flex">
            <v-btn icon class="mr-2 social-btn">
              <v-icon>mdi-facebook</v-icon>
            </v-btn>
            <v-btn icon class="mr-2 social-btn">
              <v-icon>mdi-instagram</v-icon>
            </v-btn>
            <v-btn icon class="mr-2 social-btn">
              <v-icon>mdi-twitter</v-icon>
            </v-btn>
          </div>
        </v-col>
      </v-row>
      
      <v-divider class="my-4" color="rgba(255, 255, 255, 0.1)"></v-divider>
      
      <!-- Copyright information -->
      <div class="text-center text-body-2 copyright">
        © {{ new Date().getFullYear() }} Travel Planner. All rights reserved.
      </div>
    </v-container>
  </v-footer>
</template>

<script>
/**
 * Footer component displayed at the bottom of all pages
 * Contains company information, contact details, and social media links
 */
export default {
  name: 'AppFooter'
};
</script>

<style scoped>
/* Position footer at the bottom of the page */
.v-footer {
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Title styling for each footer section */
.footer-title {
  color: #ecf0f1;
  font-weight: 500;
}

/* Text styling with hover effect */
.footer-text {
  color: #bdc3c7;
  transition: color 0.2s;
}

.footer-text:hover {
  color: #ecf0f1;
}

/* Social media buttons with hover animation */
.social-btn {
  opacity: 0.9;
  transition: opacity 0.2s;
}

.social-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1) !important;
}

/* Copyright text styling */
.copyright {
  color: #95a5a6;
}
</style> 