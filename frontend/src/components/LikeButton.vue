<template>
  <!-- Like button component with toggle functionality -->
  <div class="like-button-container">
    <button 
      @click="toggleLike" 
      :class="['like-button', { 'liked': isLiked }]"
      :disabled="isLoading"
    >
      <i :class="['fas', isLiked ? 'fa-heart' : 'fa-heart-o']"></i>
      <span>{{ isLiked ? 'Unlike' : 'Like' }}</span>
    </button>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

/**
 * Like button component for destinations
 * Allows users to like/unlike travel destinations
 */
export default {
  name: 'LikeButton',
  props: {
    locationId: {
      type: Number,
      required: true
    },
    initialLiked: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isLiked: this.initialLiked,
      isLoading: false
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  watch: {
    // Update isLiked when initialLiked changes from parent component
    initialLiked: {
      immediate: true,
      handler(newValue) {
        this.isLiked = newValue;
      }
    }
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
     * Get JWT token from local storage
     * @returns {string} JWT access token
     */
    getToken() {
      return localStorage.getItem('access_token');
    },
    
    /**
     * Toggle like status for the location
     * Handles both liking and unliking a destination
     */
    async toggleLike() {
      if (!this.isAuthenticated()) {
        this.toast.warning('Need to login');
        this.$router.push('/login');
        return;
      }

      this.isLoading = true;

      try {
        if (this.isLiked) {
          // Unlike the location
          await axios.delete(`http://localhost:8000/api/destinations/likes/unlike/`, {
            params: { location_id: this.locationId },
            headers: {
              Authorization: `Bearer ${this.getToken()}`
            }
          });
          this.isLiked = false;
          this.toast.success('Liked removed');
        } else {
          // Like the location
          try {
            await axios.post(`http://localhost:8000/api/destinations/likes/`, 
              { location_id: this.locationId },
              {
                headers: {
                  Authorization: `Bearer ${this.getToken()}`
                }
              }
            );
            this.isLiked = true;
            this.toast.success('Liked added');
          } catch (error) {
            // Handle conflict if already liked (409 Conflict)
            if (error.response && error.response.status === 409) {
              this.isLiked = true; // Set to liked state anyway
              this.toast.info('Already liked');
            } else {
              throw error; // Rethrow other errors
            }
          }
        }
        
        // Emit event to notify parent component
        this.$emit('like-changed', this.isLiked);
      } catch (error) {
        console.error('Error processing like action:', error);
        if (error.response && error.response.status === 409) {
          this.isLiked = true; // Set to liked state
          this.toast.info('Already liked');
        } else {
          this.toast.error('Error processing like action');
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Container styling */
.like-button-container {
  margin: 10px 0;
}

/* Button styling with different states */
.like-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

/* Hover state styling */
.like-button:hover {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

/* Active/liked state styling */
.like-button.liked {
  background-color: #fed7d7;
  border-color: #fc8181;
  color: #e53e3e;
}

.like-button.liked:hover {
  background-color: #fecaca;
}

/* Disabled state styling */
.like-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Icon styling */
.like-button i {
  font-size: 16px;
}
</style> 