<template>
  <div class="nearby-container">
    <h2 class="section-title">My Nearby Locations</h2>
    
    <!-- Location controls section with geolocation button and radius selector -->
    <div class="location-controls">
      <button @click="getUserLocation" :disabled="isLoading" class="location-button">
        <i class="fas fa-location-arrow"></i>
        {{ isLoading ? 'Checking location...' : 'Find My Location' }}
      </button>
      
      <div class="radius-selector">
        <label>Search Boundary:</label>
        <select v-model="searchRadius" @change="searchRadius && userLocation && fetchNearbyLocations()">
          <option value="5">5km</option>
          <option value="10">10km</option>
          <option value="25">25km</option>
          <option value="50">50km</option>
          <option value="100">100km</option>
        </select>
      </div>
    </div>
    
    <!-- Error message display -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    
    <!-- User location information display -->
    <div v-if="userLocation" class="user-location-info">
      <p>Current Location: Latitude {{ userLocation.latitude.toFixed(4) }}, Longitude {{ userLocation.longitude.toFixed(4) }}</p>
    </div>
    
    <!-- Loading indicator -->
    <div v-if="isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Finding nearby locations...</p>
    </div>
    
    <!-- No results message -->
    <div v-else-if="nearbyLocations.length === 0 && !errorMessage && userLocation" class="no-results">
      <p>There are no locations within {{ searchRadius }}km of your current location.</p>
    </div>
    
    <!-- Grid display of nearby locations -->
    <div v-else-if="nearbyLocations.length > 0" class="location-grid">
      <div v-for="location in nearbyLocations" :key="location.id" class="location-card">
        <div class="location-image">
          <img :src="location.image || defaultImage" :alt="location.name">
        </div>
        <div class="location-details">
          <h3>{{ location.name }}</h3>
          <p class="location-place">
            <i class="fas fa-map-marker-alt"></i>
            {{ getLocationString(location) }}
          </p>
          <p class="location-distance">
            <i class="fas fa-route"></i>
            {{ formatDistance(location.distance) }} away
          </p>
          <p v-if="location.description" class="location-description">
            {{ truncateText(location.description, 100) }}
          </p>
          <div class="card-actions">
            <button @click="viewDetails(location.id)" class="view-button">
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

/**
 * Component to display nearby travel destinations based on user's geolocation
 * Allows users to find destinations within a specified radius
 */
export default {
  name: 'NearbyLocations',
  data() {
    return {
      userLocation: null,         // Stores user's coordinates
      nearbyLocations: [],        // Array of nearby destinations
      isLoading: false,           // Loading state indicator
      errorMessage: null,         // Error message if geolocation fails
      searchRadius: 50,           // Default search radius in km
      defaultImage: 'https://via.placeholder.com/300x200?text=No+Image' // Fallback image
    };
  },
  methods: {
    /**
     * Get user's current geolocation
     * Uses browser's geolocation API to determine coordinates
     */
    getUserLocation() {
      this.isLoading = true;
      this.errorMessage = null;
      
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            this.userLocation = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            };
            this.fetchNearbyLocations();
          },
          (error) => {
            this.isLoading = false;
            switch(error.code) {
              case error.PERMISSION_DENIED:
                this.errorMessage = "Location permission denied";
                break;
              case error.POSITION_UNAVAILABLE:
                this.errorMessage = "Location information unavailable";
                break;
              case error.TIMEOUT:
                this.errorMessage = "Location request timed out";
                break;
              default:
                this.errorMessage = "Error getting location";
            }
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
          }
        );
      } else {
        this.isLoading = false;
        this.errorMessage = "This browser does not support location information";
      }
    },
    
    /**
     * Fetch nearby locations from the API
     * Uses user's coordinates and search radius to find destinations
     */
    async fetchNearbyLocations() {
      if (!this.userLocation) return;
      
      try {
        const response = await axios.post('http://localhost:8000/api/destinations/nearby/', {
          latitude: this.userLocation.latitude,
          longitude: this.userLocation.longitude,
          radius: parseFloat(this.searchRadius)
        });
        
        this.nearbyLocations = response.data;
        this.isLoading = false;
      } catch (error) {
        this.isLoading = false;
        this.errorMessage = "Failed to fetch nearby locations";
        console.error('API Error:', error);
      }
    },
    
    /**
     * Format distance to friendly string with appropriate units
     * @param {number} distance - Distance in kilometers
     * @returns {string} Formatted distance
     */
    formatDistance(distance) {
      if (distance < 1) {
        return `${Math.round(distance * 1000)}m`;
      }
      return `${distance.toFixed(1)}km`;
    },
    
    /**
     * Get formatted location string from location object
     * @param {Object} location - Location object
     * @returns {string} Formatted location string (city, country)
     */
    getLocationString(location) {
      const parts = [];
      if (location.city) parts.push(location.city);
      if (location.country) parts.push(location.country);
      return parts.join(', ') || 'No location information';
    },
    
    /**
     * Truncate text to specified length with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} length - Maximum length
     * @returns {string} Truncated text
     */
    truncateText(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    },
    
    /**
     * Navigate to location details page
     * @param {number} locationId - ID of the location
     */
    viewDetails(locationId) {
      this.$router.push(`/destinations/${locationId}`);
    }
  }
};
</script>

<style scoped>
/* Main container styling */
.nearby-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Section title styling */
.section-title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

/* Controls layout */
.location-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

/* Location button styling */
.location-button {
  padding: 10px 20px;
  background-color: #1976D2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s;
}

/* Button hover effect */
.location-button:hover {
  background-color: #1565C0;
}

/* Button disabled state */
.location-button:disabled {
  background-color: #B0BEC5;
  cursor: not-allowed;
}

/* Radius selector styling */
.radius-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.radius-selector select {
  padding: 8px 15px;
  border-radius: 5px;
  border: 1px solid #ddd;
  background-color: white;
}

/* Error message styling */
.error-message {
  color: #D32F2F;
  text-align: center;
  padding: 15px;
  border-radius: 5px;
  background-color: #FFEBEE;
  margin-bottom: 20px;
}

/* User location info styling */
.user-location-info {
  text-align: center;
  padding: 10px;
  border-radius: 5px;
  background-color: #E3F2FD;
  margin-bottom: 20px;
}

/* Loading spinner container */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 50px 0;
}

/* Spinner animation */
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #ddd;
  border-top: 5px solid #1976D2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* No results message styling */
.no-results {
  text-align: center;
  margin: 50px 0;
  color: #757575;
  font-size: 1.2rem;
}

/* Location grid layout */
.location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

/* Location card styling */
.location-card {
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  background-color: white;
}

/* Card hover animation */
.location-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Image container */
.location-image {
  height: 200px;
  overflow: hidden;
}

/* Image styling and zoom effect */
.location-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.location-card:hover .location-image img {
  transform: scale(1.05);
}

/* Card details container */
.location-details {
  padding: 15px;
}

/* Location title */
.location-details h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 1.3rem;
}

/* Location place and distance info */
.location-place, .location-distance {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #666;
}

.location-distance {
  color: #1976D2;
  font-weight: bold;
}

/* Location description */
.location-description {
  margin-top: 10px;
  color: #555;
  line-height: 1.4;
}

/* Card action buttons container */
.card-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

/* View details button */
.view-button {
  padding: 8px 16px;
  background-color: #1976D2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.view-button:hover {
  background-color: #1565C0;
}

/* Responsive layout */
@media (max-width: 768px) {
  .location-grid {
    grid-template-columns: 1fr;
  }
  
  .location-controls {
    flex-direction: column;
  }
}
</style> 