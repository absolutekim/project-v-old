<template>
  <!-- Most popular destinations container -->
  <div class="most-loved-container">
    <h1 class="page-title">Most Popular Destinations</h1>
    
    <!-- Loading state with spinner -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Fetching Popular Destinations...</p>
    </div>
    
    <!-- Empty state when no destinations found -->
    <div v-else-if="locations.length === 0" class="empty-state">
      <p>There are no destinations to display.</p>
    </div>
    
    <!-- Grid of popular destination cards -->
    <div v-else class="locations-grid">
      <div v-for="(location, index) in locations" :key="location.id" class="location-card">
        <!-- Ranking badge showing position -->
        <div class="rank-badge">{{ index + 1 }}</div>
        <router-link :to="`/destinations/${location.id}`" class="location-link">
          <!-- Destination image or placeholder -->
          <div class="location-image-container">
            <img v-if="location.image" :src="location.image" :alt="location.name" class="location-image">
            <div v-else class="placeholder-image">
              <i class="fas fa-image"></i>
            </div>
          </div>
          <!-- Destination information -->
          <div class="location-info">
            <h3 class="location-name">{{ location.name }}</h3>
            <p v-if="location.city || location.country" class="location-address">
              <i class="fas fa-map-marker-alt"></i>
              {{ getLocationString(location) }}
            </p>
            <!-- Likes count and rating -->
            <div class="location-meta">
              <div class="likes-count">
                <i class="fas fa-heart"></i>
                <span>{{ location.likes_count }}</span>
              </div>
              <div v-if="location.average_rating" class="rating">
                <i class="fas fa-star"></i>
                <span>{{ location.average_rating.toFixed(1) }}</span>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

/**
 * Most Popular Destinations View Component
 * Displays a ranked list of the most liked travel destinations
 * Features:
 * - Ranked display with position badges
 * - Image and location details
 * - Like counts and ratings
 */
export default {
  name: 'MostLoved',
  data() {
    return {
      locations: [], // List of popular locations
      isLoading: true // Loading state indicator
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  mounted() {
    this.fetchMostLovedLocations();
  },
  methods: {
    /**
     * Fetch the most liked destinations from the API
     * Orders destinations by number of likes
     */
    async fetchMostLovedLocations() {
      this.isLoading = true;
      try {
        const response = await axios.get('/api/destinations/most-loved/');
        this.locations = response.data;
      } catch (error) {
        console.error('Error loading popular destinations:', error);
        this.toast.error('Error loading popular destinations.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * Format location string from destination data
     * @param {Object} location - Location object with city and country data
     * @returns {string} Formatted location string (city, country)
     */
    getLocationString(location) {
      const parts = [];
      if (location.city) parts.push(location.city);
      if (location.country) parts.push(location.country);
      return parts.join(', ');
    }
  }
};
</script>

<style scoped>
/* Main container styling */
.most-loved-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Page title styling */
.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  color: #333;
}

/* Loading state container */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

/* Loading spinner animation */
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

/* Spinner animation keyframes */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty state message styling */
.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 2rem;
}

/* Grid layout for location cards */
.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

/* Individual location card styling */
.location-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: white;
}

/* Card hover effect animation */
.location-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

/* Ranking badge styling */
.rank-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 30px;
  height: 30px;
  background-color: #ff5722;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 1;
}

/* Link styling within location card */
.location-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

/* Image container within card */
.location-image-container {
  height: 180px;
  overflow: hidden;
}

/* Image styling with hover effect */
.location-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

/* Image zoom effect on hover */
.location-card:hover .location-image {
  transform: scale(1.05);
}

/* Placeholder for missing images */
.placeholder-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  color: #aaa;
  font-size: 2rem;
}

/* Location information section styling */
.location-info {
  padding: 1rem;
}

/* Location name styling */
.location-name {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
  color: #333;
}

/* Location address styling */
.location-address {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Meta information container (likes and rating) */
.location-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

/* Likes count and rating container styling */
.likes-count, .rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

/* Heart icon styling for likes */
.likes-count i {
  color: #e74c3c;
}

/* Star icon styling for ratings */
.rating i {
  color: #f1c40f;
}
</style> 