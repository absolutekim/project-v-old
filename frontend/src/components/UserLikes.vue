<template>
  <!-- Component for displaying user's liked destinations -->
  <div class="user-likes-container">
    <h2 class="section-title">My Liked Destinations</h2>
    
    <!-- Loading indicator -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading liked destinations...</p>
    </div>
    
    <!-- Empty state message -->
    <div v-else-if="likes.length === 0" class="empty-state">
      <p>You haven't liked any destinations yet.</p>
      <router-link to="/destinations" class="browse-link">Browse Destinations</router-link>
    </div>
    
    <!-- Grid display of liked destinations -->
    <div v-else class="likes-grid">
      <div v-for="like in likes" :key="like.id" class="like-card">
        <div class="card-image" :style="{ backgroundImage: `url(${like.location.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }">
          <button @click="unlikeDestination(like.id, like.location.id)" class="unlike-button">
            <i class="fas fa-heart"></i>
          </button>
        </div>
        <div class="card-content">
          <h3 class="destination-name">{{ like.location.name }}</h3>
          <p v-if="like.location.city || like.location.country" class="destination-location">
            <i class="fas fa-map-marker-alt"></i>
            {{ [like.location.city, like.location.country].filter(Boolean).join(', ') }}
          </p>
          <p class="destination-description">{{ truncateText(like.location.description, 100) }}</p>
          <div class="card-footer">
            <span class="liked-date">{{ formatDate(like.created_at) }}</span>
            <router-link :to="`/destinations/${like.location.id}`" class="view-button">View Details</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Load more button for pagination -->
    <div v-if="hasMore" class="load-more">
      <button @click="loadMore" :disabled="isLoadingMore" class="load-more-button">
        {{ isLoadingMore ? 'Loading...' : 'Load More' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

/**
 * Component for displaying all destinations a user has liked
 * Provides functionality to unlike destinations and view details
 */
export default {
  name: 'UserLikes',
  data() {
    return {
      likes: [],
      isLoading: true,
      isLoadingMore: false,
      page: 1,
      hasMore: false
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  mounted() {
    this.fetchLikes();
  },
  methods: {
    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    },
    
    /**
     * Get JWT token from localStorage
     * @returns {string} JWT access token
     */
    getToken() {
      return localStorage.getItem('access_token');
    },
    
    /**
     * Fetch user's liked destinations
     * Retrieves first page of likes from the API
     */
    async fetchLikes() {
      if (!this.isAuthenticated()) {
        this.toast.warning('Login is required to view your liked destinations.');
        this.$router.push('/login');
        return;
      }
      
      this.isLoading = true;
      
      try {
        const response = await axios.get('http://localhost:8000/api/destinations/user/likes/', {
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        this.likes = response.data.results;
        this.hasMore = this.likes.length < response.data.count;
      } catch (error) {
        this.toast.error('Failed to load your liked destinations.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * Load more liked destinations
     * Fetches next page of likes and appends to current list
     */
    async loadMore() {
      if (this.isLoadingMore) return;
      
      this.isLoadingMore = true;
      this.page += 1;
      
      try {
        const response = await axios.get('http://localhost:8000/api/destinations/user/likes/', {
          params: { page: this.page },
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        this.likes = [...this.likes, ...response.data.results];
        this.hasMore = this.likes.length < response.data.count;
      } catch (error) {
        this.toast.error('Failed to load more liked destinations.');
      } finally {
        this.isLoadingMore = false;
      }
    },
    
    /**
     * Unlike a destination
     * Removes destination from liked list and updates UI
     * @param {number} likeId - ID of the like object
     * @param {number} locationId - ID of the location
     */
    async unlikeDestination(likeId, locationId) {
      try {
        await axios.delete(`http://localhost:8000/api/destinations/likes/unlike/`, {
          params: { location_id: locationId },
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        // Remove from likes list
        this.likes = this.likes.filter(like => like.id !== likeId);
        this.toast.success('Destination removed from your likes.');
      } catch (error) {
        this.toast.error('Failed to unlike destination.');
      }
    },
    
    /**
     * Truncate text to specified length
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum allowed length
     * @returns {string} Truncated text with ellipsis
     */
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    },
    
    /**
     * Format date to locale string
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date
     */
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }
};
</script>

<style scoped>
/* Main container */
.user-likes-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Section title */
.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
}

/* Loading spinner container */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

/* Spinner animation */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Empty state styling */
.empty-state {
  text-align: center;
  padding: 40px;
  background-color: #f8fafc;
  border-radius: 8px;
  color: #718096;
}

/* Browse link button */
.browse-link {
  display: inline-block;
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #4299e1;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.browse-link:hover {
  background-color: #3182ce;
}

/* Grid of liked destinations */
.likes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

/* Individual like card */
.like-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.like-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

/* Card image container */
.card-image {
  height: 180px;
  background-size: cover;
  background-position: center;
  position: relative;
}

/* Unlike button */
.unlike-button {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.8);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.unlike-button i {
  color: #e53e3e;
  font-size: 18px;
}

.unlike-button:hover {
  background-color: white;
}

/* Card content container */
.card-content {
  padding: 15px;
}

/* Destination name */
.destination-name {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

/* Destination location */
.destination-location {
  font-size: 14px;
  color: #718096;
  margin-bottom: 10px;
}

.destination-location i {
  margin-right: 5px;
}

/* Destination description */
.destination-description {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.5;
  margin-bottom: 15px;
  height: 63px;
  overflow: hidden;
}

/* Card footer with date and button */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Liked date display */
.liked-date {
  font-size: 12px;
  color: #718096;
}

/* View details button */
.view-button {
  padding: 6px 12px;
  background-color: #4299e1;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.view-button:hover {
  background-color: #3182ce;
}

/* Load more button container */
.load-more {
  text-align: center;
  margin-top: 30px;
}

/* Load more button styling */
.load-more-button {
  padding: 10px 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-button:hover:not(:disabled) {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

.load-more-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .likes-grid {
    grid-template-columns: 1fr;
  }
}
</style> 