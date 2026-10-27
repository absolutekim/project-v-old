<template>
  <!-- Component for displaying the current user's reviews -->
  <div class="user-reviews-container">
    <h2 class="section-title">My Reviews</h2>
    
    <!-- Loading indicator -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading reviews...</p>
    </div>
    
    <!-- Empty state when no reviews exist -->
    <div v-else-if="reviews.length === 0" class="empty-state">
      <p>You haven't written any reviews yet.</p>
      <router-link to="/destinations" class="browse-link">Browse Destinations</router-link>
    </div>
    
    <!-- List of user's reviews -->
    <div v-else class="reviews-list">
      <div v-for="review in reviews" :key="review.id" class="review-card">
        <!-- Review header with destination info and rating -->
        <div class="review-header">
          <div class="destination-info">
            <router-link 
              v-if="review.location_id || (review.location && review.location.id)" 
              :to="`/destinations/${review.location_id || (review.location && review.location.id)}`" 
              class="destination-name"
            >
              {{ review.location_name || (review.location && review.location.name) || 'Unknown Destination' }}
            </router-link>
            <span v-else class="destination-name">
              {{ review.location_name || (review.location && review.location.name) || 'Unknown Destination' }}
            </span>
            <p v-if="review.location_city || review.location_country || (review.location && (review.location.city || review.location.country))" class="destination-location">
              <i class="fas fa-map-marker-alt"></i>
              {{ getLocationString(review) }}
            </p>
          </div>
          <div class="review-meta">
            <div class="rating">
              <span v-for="star in 5" :key="star" class="star" :class="{ 'filled': star <= review.rating }">
                <i class="fas fa-star"></i>
              </span>
            </div>
            <span class="review-date">{{ formatDate(review.created_at) }}</span>
          </div>
        </div>
        
        <!-- Review content -->
        <div class="review-content">
          <p>{{ review.content }}</p>
        </div>
        
        <!-- Sentiment analysis display -->
        <div v-if="review.sentiment" class="review-sentiment" :class="getSentimentClass(review.sentiment)">
          <span class="sentiment-label">Sentiment:</span>
          <span class="sentiment-value">{{ getSentimentText(review.sentiment) }}</span>
        </div>
        
        <!-- Keywords display -->
        <div v-if="review.keywords && review.keywords.length > 0" class="review-keywords">
          <span v-for="(keyword, index) in review.keywords" :key="index" class="keyword-tag">
            {{ keyword }}
          </span>
        </div>
        
        <!-- Review actions buttons -->
        <div class="review-actions">
          <button @click="editReview(review)" class="action-button edit">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button @click="deleteReview(review.id)" class="action-button delete">
            <i class="fas fa-trash"></i> Delete
          </button>
        </div>
      </div>
    </div>
    
    <!-- Load more button for pagination -->
    <div v-if="hasMore" class="load-more">
      <button @click="loadMore" :disabled="isLoadingMore" class="load-more-button">
        {{ isLoadingMore ? 'Loading...' : 'Load More' }}
      </button>
    </div>
    
    <!-- Review edit modal -->
    <div v-if="showEditModal" class="edit-modal-overlay" @click="closeEditModal">
      <div class="edit-modal" @click.stop>
        <h3 class="modal-title">Edit Review</h3>
        
        <!-- Rating selection -->
        <div class="rating-container">
          <span class="rating-label">Rating:</span>
          <div class="stars">
            <span 
              v-for="star in 5" 
              :key="star" 
              @click="setRating(star)"
              :class="['star', { 'active': star <= editingReview.rating }]"
            >
              <i class="fas fa-star"></i>
            </span>
          </div>
        </div>
        
        <!-- Review content textarea -->
        <div class="content-container">
          <textarea 
            v-model="editingReview.content" 
            placeholder="Share your experience about this destination..." 
            rows="4"
            :disabled="isSubmitting"
            maxlength="1000"
          ></textarea>
          <div class="character-counter">
            {{ editingReview.content.length }} / 1000 characters
          </div>
        </div>
        
        <!-- Modal action buttons -->
        <div class="modal-actions">
          <button 
            @click="submitEditReview" 
            class="submit-button"
            :disabled="isSubmitting || !isEditValid"
          >
            {{ isSubmitting ? 'Processing...' : 'Update' }}
          </button>
          
          <button 
            @click="closeEditModal" 
            class="cancel-button"
            :disabled="isSubmitting"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

/**
 * Component for displaying and managing a user's reviews
 * Allows users to view, edit, and delete their own reviews
 */
export default {
  name: 'UserReviews',
  data() {
    return {
      reviews: [],
      isLoading: true,
      isLoadingMore: false,
      page: 1,
      hasMore: false,
      showEditModal: false,
      editingReview: {
        id: null,
        rating: 0,
        content: ''
      },
      isSubmitting: false
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  computed: {
    /**
     * Check if the review being edited is valid
     * @returns {boolean} True if review has rating and content
     */
    isEditValid() {
      return this.editingReview.rating > 0 && this.editingReview.content.trim().length > 0;
    }
  },
  mounted() {
    this.fetchReviews();
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
     * Format location string from various location data formats
     * @param {Object} review - Review object with location data
     * @returns {string} Formatted location string
     */
    getLocationString(review) {
      const parts = [];
      
      // Handle when backend provides location as an object
      if (review.location) {
        if (review.location.city) parts.push(review.location.city);
        if (review.location.country) parts.push(review.location.country);
      } 
      // Handle when backend provides location_city and location_country fields
      else {
        if (review.location_city) parts.push(review.location_city);
        if (review.location_country) parts.push(review.location_country);
      }
      
      return parts.join(', ') || 'Location unknown';
    },
    
    /**
     * Fetch user's reviews from the API
     */
    async fetchReviews() {
      if (!this.isAuthenticated()) {
        this.toast.warning('Login is required to view your reviews.');
        this.$router.push('/login');
        return;
      }
      
      this.isLoading = true;
      
      try {
        const response = await axios.get('http://localhost:8000/api/destinations/user/reviews/', {
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        // Process review data and fetch missing location info if needed
        this.reviews = response.data.results.map(review => {
          // If we only have location_id but no location details, fetch them
          if (review.location_id && (!review.location || !review.location.name)) {
            this.fetchLocationInfo(review);
          }
          return review;
        });
        
        this.hasMore = this.reviews.length < response.data.count;
      } catch (error) {
        this.toast.error('Failed to load your reviews.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * Fetch location details for a review
     * @param {Object} review - Review object to update with location data
     */
    async fetchLocationInfo(review) {
      try {
        const response = await axios.get(`http://localhost:8000/api/destinations/${review.location_id}/`);
        // Add location details to the review object
        review.location_name = response.data.name;
        review.location_city = response.data.city;
        review.location_country = response.data.country;
      } catch (error) {
        // Error fetching location info
      }
    },
    
    /**
     * Load more reviews for pagination
     */
    async loadMore() {
      if (this.isLoadingMore) return;
      
      this.isLoadingMore = true;
      this.page += 1;
      
      try {
        const response = await axios.get('http://localhost:8000/api/destinations/user/reviews/', {
          params: { page: this.page },
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        this.reviews = [...this.reviews, ...response.data.results];
        this.hasMore = this.reviews.length < response.data.count;
      } catch (error) {
        this.toast.error('Failed to load more reviews.');
      } finally {
        this.isLoadingMore = false;
      }
    },
    
    /**
     * Open edit modal for a review
     * @param {Object} review - Review to edit
     */
    editReview(review) {
      this.editingReview = {
        id: review.id,
        rating: review.rating,
        content: review.content,
        location_id: review.location_id || (review.location && review.location.id)
      };
      this.showEditModal = true;
    },
    
    /**
     * Close the edit modal and reset form
     */
    closeEditModal() {
      this.showEditModal = false;
      this.editingReview = {
        id: null,
        rating: 0,
        content: ''
      };
    },
    
    /**
     * Set rating value for the review being edited
     * @param {number} rating - Rating value (1-5)
     */
    setRating(rating) {
      if (!this.isSubmitting) {
        this.editingReview.rating = rating;
      }
    },
    
    /**
     * Submit edited review to the API
     */
    async submitEditReview() {
      if (!this.isEditValid) {
        this.toast.warning('Please provide both rating and review content.');
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        // Prepare review data - only send rating and content
        const requestData = {
          rating: this.editingReview.rating,
          content: this.editingReview.content
        };
        
        // Use PATCH for partial updates
        const response = await axios.patch(
          `http://localhost:8000/api/destinations/reviews/${this.editingReview.id}/`,
          requestData,
          {
            headers: {
              Authorization: `Bearer ${this.getToken()}`
            }
          }
        );
        
        // Update review in the list
        const index = this.reviews.findIndex(r => r.id === this.editingReview.id);
        if (index !== -1) {
          this.reviews[index] = response.data;
        }
        
        this.toast.success('Review updated successfully.');
        this.closeEditModal();
      } catch (error) {
        this.toast.error('Failed to update review.');
      } finally {
        this.isSubmitting = false;
      }
    },
    
    /**
     * Delete a review after confirmation
     * @param {number} reviewId - ID of the review to delete
     */
    async deleteReview(reviewId) {
      if (!confirm('Are you sure you want to delete this review?')) {
        return;
      }
      
      try {
        await axios.delete(`http://localhost:8000/api/destinations/reviews/${reviewId}/`, {
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        // Remove review from the list
        this.reviews = this.reviews.filter(review => review.id !== reviewId);
        this.toast.success('Review deleted successfully.');
      } catch (error) {
        this.toast.error('Failed to delete review.');
      }
    },
    
    /**
     * Format date string to localized format
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date string
     */
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    /**
     * Get CSS class for sentiment display
     * @param {string} sentiment - Sentiment value
     * @returns {string} CSS class name
     */
    getSentimentClass(sentiment) {
      switch (sentiment) {
        case 'POSITIVE':
          return 'positive';
        case 'NEGATIVE':
          return 'negative';
        default:
          return 'neutral';
      }
    },
    
    /**
     * Get display text for sentiment value
     * @param {string} sentiment - Sentiment value
     * @returns {string} Display text
     */
    getSentimentText(sentiment) {
      switch (sentiment) {
        case 'POSITIVE':
          return 'Positive';
        case 'NEGATIVE':
          return 'Negative';
        default:
          return 'Neutral';
      }
    }
  }
};
</script>

<style scoped>
/* Main container */
.user-reviews-container {
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

/* Loading indicator container */
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

/* Browse destinations link */
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

/* Reviews list container */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Individual review card */
.review-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Review header with destination and rating */
.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

/* Destination information section */
.destination-info {
  display: flex;
  flex-direction: column;
}

/* Destination name styling */
.destination-name {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  text-decoration: none;
  margin-bottom: 5px;
}

.destination-name:hover {
  color: #4299e1;
}

/* Destination location styling */
.destination-location {
  font-size: 14px;
  color: #718096;
}

.destination-location i {
  margin-right: 5px;
}

/* Review metadata section */
.review-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* Star rating display */
.rating {
  display: flex;
  margin-bottom: 5px;
}

.star {
  color: #cbd5e0;
  margin-right: 2px;
}

.star.filled {
  color: #f6ad55;
}

/* Review date display */
.review-date {
  font-size: 12px;
  color: #718096;
}

/* Review content styling */
.review-content {
  font-size: 16px;
  line-height: 1.6;
  color: #4a5568;
  margin-bottom: 15px;
}

/* Sentiment analysis badge */
.review-sentiment {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 10px;
}

/* Sentiment types styling */
.review-sentiment.positive {
  background-color: #c6f6d5;
  color: #2f855a;
}

.review-sentiment.negative {
  background-color: #fed7d7;
  color: #c53030;
}

.review-sentiment.neutral {
  background-color: #e2e8f0;
  color: #4a5568;
}

/* Sentiment label */
.sentiment-label {
  font-weight: 500;
  margin-right: 5px;
}

/* Keywords container */
.review-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 15px;
}

/* Individual keyword tag */
.keyword-tag {
  background-color: #e2e8f0;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* Review actions container */
.review-actions {
  display: flex;
  gap: 10px;
}

/* Action button base styling */
.action-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Edit button styling */
.action-button.edit {
  background-color: #4299e1;
  color: white;
  border: none;
}

.action-button.edit:hover {
  background-color: #3182ce;
}

/* Delete button styling */
.action-button.delete {
  background-color: white;
  color: #e53e3e;
  border: 1px solid #e53e3e;
}

.action-button.delete:hover {
  background-color: #fff5f5;
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

/* Edit modal styles */
.edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Modal content container */
.edit-modal {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

/* Modal title */
.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
}

/* Rating container in modal */
.rating-container {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

/* Rating label */
.rating-label {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-right: 10px;
}

/* Stars container */
.stars {
  display: flex;
}

/* Star styling */
.star {
  font-size: 20px;
  color: #cbd5e0;
  cursor: pointer;
  margin-right: 5px;
  transition: color 0.2s;
}

/* Star hover and active state */
.star:hover,
.star.active {
  color: #f6ad55;
}

/* Content container in modal */
.content-container {
  margin-bottom: 20px;
}

/* Textarea styling */
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.2s;
}

/* Textarea focus state */
textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

/* Textarea disabled state */
textarea:disabled {
  background-color: #f7fafc;
  cursor: not-allowed;
}

/* Character counter style */
.character-counter {
  font-size: 12px;
  color: #718096;
  text-align: right;
  margin-top: 4px;
}

/* Modal actions container */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Submit and cancel buttons */
.submit-button,
.cancel-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

/* Submit button styling */
.submit-button {
  background-color: #4299e1;
  color: white;
  border: none;
}

/* Submit button hover state */
.submit-button:hover:not(:disabled) {
  background-color: #3182ce;
}

/* Submit button disabled state */
.submit-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

/* Cancel button styling */
.cancel-button {
  background-color: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

/* Cancel button hover state */
.cancel-button:hover:not(:disabled) {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

/* Cancel button disabled state */
.cancel-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .review-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .review-meta {
    align-items: flex-start;
  }
}
</style> 