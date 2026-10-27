<template>
  <!-- Destination detail page container -->
  <v-container class="destination-detail-container" fluid>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="10">
        <v-card class="destination-detail-card" elevation="4">
          <!-- Loading state -->
          <v-card v-if="loading" class="text-center pa-6">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <div class="mt-4">🔄 Loading data...</div>
          </v-card>

          <!-- Error state -->
          <v-alert v-else-if="error" type="error" class="text-center">
            🚨 Error: {{ error }}
          </v-alert>

          <!-- Data display -->
          <template v-else>
            <!-- Header image -->
            <v-img
              v-if="destination.image"
              :src="destination.image"
              height="300"
              cover
              class="destination-detail-image"
            ></v-img>

            <!-- Title section -->
            <v-card-title class="text-h4 font-weight-bold d-flex align-center flex-wrap">
              {{ destination.name }}
              <v-chip
                color="info"
                variant="outlined"
                class="ml-2"
              >
                {{ destination.country }}
              </v-chip>
            </v-card-title>

            <!-- Like button section -->
            <div class="like-button-container px-4 d-flex align-center">
              <like-button 
                :location-id="Number(destination.id)" 
                :initial-liked="destination.user_has_liked"
                @like-changed="onLikeChanged"
              />
              <v-chip
                v-if="destination.likes_count !== undefined"
                color="pink-lighten-4"
                class="ml-3"
                prepend-icon="mdi-heart"
              >
                {{ destination.likes_count }} {{ destination.likes_count === 1 ? 'Like' : 'Likes' }}
              </v-chip>
            </div>

            <v-card-text>
              <!-- Basic information -->
              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-3">Basic Information</h3>
                  <v-chip
                    color="primary"
                    variant="outlined"
                    class="mr-2 mb-2"
                  >
                    {{ destination.type }}
                  </v-chip>
                  
                  <div v-if="destination.subcategories" class="my-2">
                    <v-chip
                      v-for="(subcat, index) in destination.subcategories"
                      :key="index"
                      color="secondary"
                      variant="outlined"
                      class="mr-2 mb-2"
                    >
                      {{ subcat }}
                    </v-chip>
                  </div>

                  <div v-if="destination.subtypes" class="my-2">
                    <v-chip
                      v-for="(subtype, index) in destination.subtypes"
                      :key="index"
                      color="success"
                      variant="outlined"
                      class="mr-2 mb-2"
                    >
                      {{ subtype }}
                    </v-chip>
                  </div>

                  <div v-if="destination.description" class="mt-4 text-body-1">
                    {{ destination.description }}
                  </div>
                </v-col>

                <!-- Address information -->
                <v-col cols="12" md="6">
                  <h3 class="text-h6 mb-3">Address Information</h3>
                  <v-list>
                    <v-list-item v-if="destination.address">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-map-marker</v-icon>
                      </template>
                      <v-list-item-title>Address</v-list-item-title>
                      <v-list-item-subtitle>{{ destination.address }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.local_address">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-map-marker-outline</v-icon>
                      </template>
                      <v-list-item-title>Local Address</v-list-item-title>
                      <v-list-item-subtitle>{{ destination.local_address }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.city || destination.state">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-city</v-icon>
                      </template>
                      <v-list-item-title>City/State</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ [destination.city, destination.state].filter(Boolean).join(', ') }}
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.postal_code">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-post</v-icon>
                      </template>
                      <v-list-item-title>Postal Code</v-list-item-title>
                      <v-list-item-subtitle>{{ destination.postal_code }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.street1 || destination.street2">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-road-variant</v-icon>
                      </template>
                      <v-list-item-title>Street Address</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ [destination.street1, destination.street2].filter(Boolean).join(' ') }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>

                <!-- Contact and location information -->
                <v-col cols="12" md="6">
                  <h3 class="text-h6 mb-3">Additional Information</h3>
                  <v-list>
                    <v-list-item v-if="destination.website">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-web</v-icon>
                      </template>
                      <v-list-item-title>Website</v-list-item-title>
                      <v-list-item-subtitle>
                        <a :href="destination.website" target="_blank">{{ destination.website }}</a>
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.email">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-email</v-icon>
                      </template>
                      <v-list-item-title>Email</v-list-item-title>
                      <v-list-item-subtitle>
                        <a :href="`mailto:${destination.email}`">{{ destination.email }}</a>
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.latitude && destination.longitude">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-crosshairs-gps</v-icon>
                      </template>
                      <v-list-item-title>Coordinates</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ destination.latitude }}, {{ destination.longitude }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
              </v-row>

              <!-- Map Container -->
              <v-row v-if="destination.latitude && destination.longitude" class="mt-4">
                <v-col cols="12">
                  <h3 class="text-h6 mb-3">Location Map</h3>
                  <v-alert v-if="mapError" type="warning" class="mb-3">
                    {{ mapError }}
                  </v-alert>
                  <div
                    id="map"
                    ref="mapContainer"
                    style="width: 100%; height: 400px; border-radius: 8px;"
                  ></div>
                </v-col>
              </v-row>

              <!-- Reviews section -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <h3 class="text-h6 mb-3">Reviews</h3>
                  
                  <!-- Login prompt for unauthenticated users -->
                  <v-alert
                    v-if="!isAuthenticated"
                    color="info"
                    icon="mdi-information"
                    class="mb-4"
                  >
                    Please <router-link to="/login">log in</router-link> to leave a review.
                  </v-alert>
                  
                  <!-- Already reviewed message -->
                  <v-alert
                    v-else-if="hasUserReview"
                    color="success"
                    icon="mdi-check-circle"
                    class="mb-4"
                  >
                    You have already submitted a review for this destination. You can edit your review below.
                  </v-alert>
                  
                  <!-- Review form for creating new reviews -->
                  <div v-if="isAuthenticated && !isEditingReview && !hasUserReview">
                    <review-form 
                      :location-id="Number(destination.id)" 
                      @review-submitted="onReviewSubmitted"
                      ref="reviewForm"
                    />
                  </div>
                  
                  <!-- Review form for editing existing reviews -->
                  <div v-if="isEditingReview">
                    <review-form 
                      :location-id="Number(destination.id)" 
                      :existing-review="currentEditingReview"
                      @review-submitted="onReviewUpdated"
                      @cancel="cancelEditReview"
                      ref="editReviewForm"
                    />
                  </div>
                  
                  <!-- Reviews list -->
                  <review-list 
                    :location-id="Number(destination.id)" 
                    @edit-review="startEditReview"
                    @reviews-loaded="checkUserReview"
                    ref="reviewList"
                  />
                </v-col>
              </v-row>
            </v-card-text>

            <!-- Back button -->
            <v-card-actions class="pa-4">
              <v-btn
                color="primary"
                variant="outlined"
                block
                @click="$router.push('/destinations')"
              >
                <v-icon left>mdi-arrow-left</v-icon>
                Back to List
              </v-btn>
            </v-card-actions>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
/* eslint-disable no-undef */
import axios from 'axios';
import LikeButton from '@/components/LikeButton.vue';
import ReviewForm from '@/components/ReviewForm.vue';
import ReviewList from '@/components/ReviewList.vue';

/**
 * Destination Detail View
 * Displays comprehensive information about a specific travel destination
 * Includes basic info, address details, contact info, and user reviews
 */
export default {
  components: {
    LikeButton,
    ReviewForm,
    ReviewList
  },
  data() {
    return {
      destination: {},
      loading: true,
      error: null,
      isEditingReview: false,
      currentEditingReview: null,
      map: null,
      mapLoaded: false,
      mapError: null,
      mapInitRetries: 0, // Number of retries for map initialization
      coordinatesText: '',
      routeCoordinates: [],
      routeMarkers: [],
      routePolyline: null,
      routeInfoWindows: [],
      exampleCoordinates: '71.16983 25.783571 70.97685 25.97946 70.66463 23.680859 69.94744 23.187012 69.93274 23.270948 69.88493 23.25117',
      handleWindowResize: null,
      hasUserReview: false
    };
  },
  computed: {
    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  },
  created() {
    try {
      // Add authentication token to headers if available
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      // Start loading data
      this.loading = true;
      
      // Get destination data asynchronously
      axios.get(`http://localhost:8000/api/destinations/${this.$route.params.id}/`, {
        headers
      }).then(response => {
        this.destination = response.data;
        
        // Add to recently viewed destinations
        this.addToRecentlyViewed(this.destination);
      }).catch(err => {
        this.error = err.message;
        console.error("Failed to load data:", err);
      }).finally(() => {
        // Set loading complete flag
        this.loading = false;
      });
    } catch (err) {
      this.error = err.message;
      console.error("Failed to load data:", err);
      this.loading = false;
    }
  },
  methods: {
    /**
     * Handle like status change event from like button
     * @param {boolean} isLiked - New like status
     */
    onLikeChanged(isLiked) {
      this.destination.user_has_liked = isLiked;
      
      // Update likes_count
      if (this.destination.likes_count !== undefined) {
        if (isLiked) {
          // Add like
          this.destination.likes_count += 1;
        } else {
          // Remove like
          this.destination.likes_count = Math.max(0, this.destination.likes_count - 1);
        }
      }
    },
    
    /**
     * Handle new review submission
     */
    onReviewSubmitted() {
      // Refresh reviews list
      if (this.$refs.reviewList) {
        this.$refs.reviewList.fetchReviews();
      }
    },
    
    /**
     * Start editing an existing review
     * @param {Object} review - Review to edit
     */
    startEditReview(review) {
      this.isEditingReview = true;
      this.currentEditingReview = review;
    },
    
    /**
     * Cancel review editing mode
     */
    cancelEditReview() {
      this.isEditingReview = false;
      this.currentEditingReview = null;
    },
    
    /**
     * Handle review update completion
     */
    onReviewUpdated() {
      // Refresh reviews list
      if (this.$refs.reviewList) {
        this.$refs.reviewList.fetchReviews();
      }
      this.isEditingReview = false;
      this.currentEditingReview = null;
    },
    
    /**
     * Add destination to recently viewed list in localStorage
     * Stores limited information for quick access later
     * @param {Object} destination - Destination to save to recently viewed
     */
    addToRecentlyViewed(destination) {
      if (!destination || !destination.id) return;
      
      try {
        // Get recently viewed destinations from localStorage
        let recentlyViewed = JSON.parse(localStorage.getItem('recentlyViewed') || '[]');
        
        // Remove if already exists (to update with latest info)
        recentlyViewed = recentlyViewed.filter(item => item.id !== destination.id);
        
        // Create viewed info object with essential details
        const viewedInfo = {
          id: destination.id,
          name: destination.name,
          country: destination.country,
          subcategories: destination.subcategories,
          subtypes: destination.subtypes,
          timestamp: new Date().toISOString()
        };
        
        // Add to the beginning of the array
        recentlyViewed.unshift(viewedInfo);
        
        // Keep only the 10 most recent
        if (recentlyViewed.length > 10) {
          recentlyViewed = recentlyViewed.slice(0, 10);
        }
        
        // Save to localStorage
        localStorage.setItem('recentlyViewed', JSON.stringify(recentlyViewed));
      } catch (error) {
        console.error('Error saving to recently viewed:', error);
      }
    },
    
    /**
     * Load Google Maps API script
     */
    loadGoogleMapsScript() {
      // Check if it's already loaded
      if (window.google && window.google.maps) {
        // Execute after DOM is fully updated
        this.$nextTick(() => {
          this.initMap();
        });
        return;
      }
      
      // Check if the script is already added (prevent duplicate loading)
      if (document.querySelector('script[src*="maps.googleapis.com/maps/api/js"]')) {
        
        // Check every 5 seconds until loaded
        const checkInterval = setInterval(() => {
          if (window.google && window.google.maps) {
            clearInterval(checkInterval);
            this.initMap();
          }
        }, 5000);
        
        // Timeout after 30 seconds
        setTimeout(() => {
          clearInterval(checkInterval);
          if (!window.google || !window.google.maps) {
            console.error('Google Maps API load timeout');
            this.mapError = "Google Maps API load timeout";
            this.mapLoaded = true;
          }
        }, 30000);
        
        return;
      }
      
      const API_KEY = 'AIzaSyAnJWxpGIPrDueHMNX_1xkopRALQXCeZOE';
      
      // Change to direct script loading method
      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&v=weekly`;
      script.async = true;
      script.defer = true;
      
      // Script load complete event
      script.onload = () => {
        
        // Additional verification and delay processing
        setTimeout(() => {
          if (window.google && window.google.maps) {
            this.initMap();
          } else {
            console.error('Google Maps API loaded but object not found');
            this.mapError = "Failed to initialize Google Maps";
            this.mapLoaded = true;
          }
        }, 1000);
      };
      
      // Script load error handling
      script.onerror = (error) => {
        console.error('Google Maps API script load failed:', error);
        this.mapError = "Failed to load Google Maps API";
        this.mapLoaded = true;
      };
      
      // Add script to DOM
      document.head.appendChild(script);
    },
    
    /**
     * Initialize Google Map with given location coordinates
     */
    initMap() {
      if (!this.destination || !this.destination.latitude || !this.destination.longitude) {
        this.mapError = "No coordinates information";
        this.mapLoaded = true;
        return;
      }
      
      try {
        const lat = parseFloat(this.destination.latitude);
        const lng = parseFloat(this.destination.longitude);
        
        if (isNaN(lat) || isNaN(lng)) {
          this.mapError = "Invalid coordinates";
          this.mapLoaded = true;
          return;
        }
        
        // Check map container
        const mapElement = this.$refs.mapContainer || document.getElementById('map');
        if (!mapElement) {
          
          // Check maximum retry count
          if (this.mapInitRetries >= 3) {
            console.error('Map initialization maximum retries exceeded');
            this.mapError = "can't find map element";
            this.mapLoaded = true;
            return;
          }
          
          this.mapInitRetries++;
          // Delay and retry
          setTimeout(() => {
            this.initMap();
          }, 1000);
          return;
        }
        
        // Check if map element is not visible or has zero size
        if (mapElement.offsetWidth === 0 || mapElement.offsetHeight === 0) {
          
          if (this.mapInitRetries >= 3) {
            console.error('Map initialization maximum retries exceeded');
            this.mapError = "Map element size is 0";
            this.mapLoaded = true;
            return;
          }
          
          this.mapInitRetries++;
          setTimeout(() => {
            this.initMap();
          }, 1000);
          return;
        }
        
        // Check Google Maps API
        if (!window.google || !window.google.maps) {
          console.error('Google Maps API not loaded');
          
          if (this.mapInitRetries >= 3) {
            this.mapError = "Google Maps API not loaded";
            this.mapLoaded = true;
            return;
          }
          
          this.mapInitRetries++;
          this.loadGoogleMapsScript();
          return;
        }
        
        // Remove existing map before creating new one (prevent duplicate creation)
        if (this.map) {
          this.map = null;
        }
        
        // Set map options
        const mapOptions = {
          zoom: 15,
          center: { lat, lng },
          mapTypeControl: true,
          fullscreenControl: true,
          streetViewControl: true,
          mapTypeId: window.google.maps.MapTypeId.ROADMAP
        };
        
        // Create map
        this.map = new window.google.maps.Map(mapElement, mapOptions);
        
        // Check map creation
        if (!this.map) {
          console.error('Map object creation failed');
          this.mapError = "Failed to create map object";
          this.mapLoaded = true;
          return;
        }
        
        // Create marker
        this.createMarker(lat, lng);
        
        this.mapLoaded = true;
        
      } catch (error) {
        console.error('Map initialization error:', error);
        this.mapError = "Failed to load map";
        this.mapLoaded = true;
      }
    },
    
    /**
     * Create marker on map
     */
    createMarker(lat, lng) {
      try {
        if (!this.map || !window.google || !window.google.maps) {
          console.error('Marker creation failed: Map or Google Maps API not found');
          return;
        }
        
        const position = { lat, lng };
        
        // Create marker
        const marker = new window.google.maps.Marker({
          position: position,
          map: this.map,
          title: this.destination.name || 'Location',
          // Remove animation (prevent errors)
        });
        
        // Info window content
        const infoContent = `
          <div style="padding: 8px; max-width: 200px;">
            <h3 style="margin-top: 0; font-size: 16px;">${this.destination.name || 'Location'}</h3>
            ${this.destination.address ? `<p style="margin-bottom: 5px; font-size: 14px;">${this.destination.address}</p>` : ''}
            <p style="margin-bottom: 0; font-size: 12px; color: #666;">Coordinates: ${lat.toFixed(6)}, ${lng.toFixed(6)}</p>
          </div>
        `;
        
        // Create info window
        const infoWindow = new window.google.maps.InfoWindow({
          content: infoContent
        });
        
        // Marker click event
        marker.addListener('click', () => {
          infoWindow.open(this.map, marker);
        });
        
        // Display info window initially
        setTimeout(() => {
          infoWindow.open(this.map, marker);
        }, 500);
        
      } catch (error) {
        console.error('Marker creation error:', error);
        // Marker errors do not affect map display, so ignore
      }
    },

    showRouteExample() {
    },

    /**
     * Check if user already has a review for this destination
     * @param {Array} reviews - List of reviews for the destination
     */
    checkUserReview(reviews) {
      const userId = this.getUserId();
      this.hasUserReview = reviews.some(review => review.author_id === userId);
    },
    
    /**
     * Get current user ID from localStorage token
     * @returns {number|null} User ID or null if not logged in
     */
    getUserId() {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return null;
        
        // Decode JWT token content (second part is payload)
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        
        // Return user_id if it exists
        return decoded.user_id || null;
      } catch (error) {
        console.error('Error getting user ID:', error);
        return null;
      }
    },
  },
  mounted() {
    // Window resize event handler
    this.handleWindowResize = () => {
      if (this.map && window.google && window.google.maps) {
        window.google.maps.event.trigger(this.map, 'resize');
        
        // Reset map center
        if (this.destination?.latitude && this.destination?.longitude) {
          const lat = parseFloat(this.destination.latitude);
          const lng = parseFloat(this.destination.longitude);
          const center = new window.google.maps.LatLng(lat, lng);
          this.map.setCenter(center);
        }
      }
    };
    
    // Map initialization function (simplified version)
    const ensureMapInitialization = () => {
      // Execute after DOM is fully rendered
      this.$nextTick(() => {
        // Check if loading is complete and location info exists
        if (!this.loading && this.destination?.latitude && this.destination?.longitude) {
          // Start map API loading
          setTimeout(() => {
            this.loadGoogleMapsScript();
          }, 1000);
        }
      });
    };
    
    // Watch loading state changes
    this.$watch('loading', (newValue) => {
      if (newValue === false) {
        this.mapInitRetries = 0;
        this.mapError = null;
        ensureMapInitialization();
      }
    });
    
    // Try to initialize map after component is mounted (if already loaded)
    if (!this.loading && this.destination?.latitude && this.destination?.longitude) {
      this.mapInitRetries = 0; 
      ensureMapInitialization();
    }
    
    // Window resize event listener
    window.addEventListener('resize', this.handleWindowResize);
  },
  
  beforeUnmount() {
    // Clean up event listeners
    window.removeEventListener('resize', this.handleWindowResize);
    
    // Clean up Google Maps related resources
    if (this.map && window.google && window.google.maps) {
      // Remove map object reference
      this.map = null;
    }
  },
};
</script>

<style scoped>
/* Container styling */
.destination-detail-container {
  background-image: url('@/assets/destback.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  min-height: 100vh;
  padding: 20px;
  margin: 0;
  width: 100%;
  max-width: 100%;
}

/* Card styling */
.destination-detail-card {
  border-radius: 12px;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.95);
}

/* Header image styling */
.destination-detail-image {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

/* Card title styling */
.v-card-title {
  padding: 1.5rem;
  background-color: white;
}

/* Card content styling */
.v-card-text {
  padding: 1.5rem;
}

/* Like button container styling */
.like-button-container {
  margin-bottom: 12px;
}

/* Link styling */
a {
  color: #1976d2;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .destination-detail-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
}
</style> 