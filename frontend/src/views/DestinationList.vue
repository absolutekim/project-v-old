<template>
  <div class="destination-list-container">
    <div class="search-section">
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search destinations..." 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-button">
          <i class="fas fa-search"></i> Search
        </button>
      </div>
      
      <div class="search-options">
        <div class="sort-container">
          <label for="sort-select">Sort by:</label>
          <select id="sort-select" v-model="sortOption" @change="handleSort" class="sort-select">
            <option value="name">Alphabet</option>
            <option value="rating">Score</option>
            <option value="popularity">Likes Count</option>
            <option value="recent">Newest</option>
          </select>
        </div>
        
        <div class="filter-container">
          <label for="category-select">Category:</label>
          <select id="category-select" v-model="selectedCategory" @change="handleFilter" class="filter-select">
            <option value="">All</option>
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
        </div>
        
        <div class="filter-container">
          <label for="country-select">Country:</label>
          <select id="country-select" v-model="selectedCountry" @change="handleFilter" class="filter-select">
            <option value="">All</option>
            <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
          </select>
        </div>
        
        <div class="limit-container">
          <label for="result-limit">Number of Results:</label>
          <select id="result-limit" v-model="resultLimit" class="limit-select" @change="handleLimitChange">
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="200">200</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading Destination's Info...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchDestinations" class="retry-button">Try Again</button>
    </div>

    <div v-else>
      <div v-if="isSearchMode" class="search-results-header">
        <h2>
          <i class="fas fa-search"></i> 
          "{{ searchQuery }}" Search Result ({{ filteredDestinations.length }})
          <span class="search-type">Sentiment Analysis Search</span>
        </h2>
        <button @click="clearSearch" class="clear-search-button">
          <i class="fas fa-times"></i> Initialize Search
        </button>
      </div>

      <div v-if="filteredDestinations.length === 0" class="no-results">
        <p v-if="isSearchMode">No search results, try searching with a different keyword.</p>
        <p v-else>There are no destinations to display.</p>
      </div>

      <div v-else class="destinations-grid">
        <div 
          v-for="destination in paginatedDestinations" 
          :key="destination.id" 
          class="destination-card"
          @click="viewDestinationDetails(destination.id)"
        >
          <div 
            class="destination-image" 
            :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
          ></div>
          <div class="destination-info">
            <h3>{{ destination.name }}</h3>
            <p class="location">{{ getLocationString(destination) }}</p>
            
            <div class="destination-meta">
              <span v-if="destination.category" class="category-tag">{{ destination.category }}</span>
              <span v-if="destination.average_rating" class="rating">
                <i class="fas fa-star"></i> {{ destination.average_rating.toFixed(1) }}
              </span>
              <span v-if="destination.likes_count !== undefined" class="likes-count">
                <i class="fas fa-heart"></i> {{ destination.likes_count }}
              </span>
            </div>
            
            <!-- Similarity score information -->
            <div v-if="isSearchMode && destination.similarity_score" class="similarity-score">
              <span class="score-label">Similarity:</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
              </div>
              <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
            </div>
            
            <p v-if="destination.description" class="description">
              {{ truncateText(destination.description, 100) }}
            </p>
            
            <div class="card-actions">
              <button class="view-details-button">
                View Details <i class="fas fa-arrow-right"></i>
              </button>
              
              <button 
                v-if="isAuthenticated" 
                @click.stop="addToPlanner(destination)" 
                class="add-to-planner-button"
              >
                <i class="fas fa-plus"></i> Add to Planner
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination controls -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <button 
          v-for="page in displayedPages" 
          :key="page" 
          @click="changePage(page)"
          :class="['pagination-button', { active: currentPage === page }]"
        >
          {{ page }}
        </button>
        
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="pagination-button"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

/**
 * Destination List Component
 * Displays a searchable, filterable list of travel destinations
 * Features:
 * - Text search with NLP/sentiment analysis capabilities
 * - Filtering by category and country
 * - Sorting by different criteria (alphabet, rating, popularity, recency)
 * - Pagination for large result sets
 * - Adding destinations to planners
 */
export default {
  name: 'DestinationList',
  data() {
    return {
      destinations: [], // All destinations from API
      isLoading: true, // Loading state indicator
      error: null, // Error message if API call fails
      currentPage: 1, // Current page for pagination
      itemsPerPage: 12, // Number of items to show per page
      searchQuery: '', // User's search query text
      isSearchMode: false, // Whether in search mode or browsing mode
      searchResults: [], // Results from NLP search endpoint
      sortOption: 'name', // Current sort option (name, rating, popularity, recent)
      selectedCategory: '', // Selected category filter
      categories: [], // Available categories for filtering
      resultLimit: 50, // Maximum search results to request
      selectedCountry: '', // Selected country filter
      countries: [] // Available countries for filtering
    };
  },
  computed: {
    /**
     * Filter and sort destinations based on current selections
     * Applies category and country filters, then sorts according to sortOption
     * @returns {Array} Filtered and sorted destination list
     */
    filteredDestinations() {
      let result = this.isSearchMode ? this.searchResults : this.destinations;
      
      // Filter by category
      if (this.selectedCategory) {
        result = result.filter(dest => dest.category === this.selectedCategory);
      }
      
      // Filter by country
      if (this.selectedCountry) {
        result = result.filter(dest => dest.country === this.selectedCountry);
      }
      
      // Sort results
      result = [...result].sort((a, b) => {
        switch (this.sortOption) {
          case 'name': {
            return a.name.localeCompare(b.name);
          }
          case 'rating': {
            const ratingA = a.average_rating || 0;
            const ratingB = b.average_rating || 0;
            return ratingB - ratingA;
          }
          case 'popularity': {
            const likesA = a.likes_count || 0;
            const likesB = b.likes_count || 0;
            return likesB - likesA;
          }
          case 'recent': {
            // Assuming created_at field exists
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return dateB - dateA;
          }
          default:
            return 0;
        }
      });
      
      return result;
    },
    
    /**
     * Get destinations for the current page only
     * Slices the filtered destinations array based on pagination settings
     * @returns {Array} Destinations for current page
     */
    paginatedDestinations() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredDestinations.slice(start, end);
    },
    
    /**
     * Calculate total number of pages based on filtered results
     * @returns {number} Total pages
     */
    totalPages() {
      return Math.ceil(this.filteredDestinations.length / this.itemsPerPage);
    },
    
    /**
     * Generate array of page numbers to display in pagination controls
     * Shows a window of pages centered around current page
     * @returns {Array} Page numbers to display
     */
    displayedPages() {
      const pages = [];
      const maxPagesToShow = 5;
      
      let startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
      let endPage = startPage + maxPagesToShow - 1;
      
      if (endPage > this.totalPages) {
        endPage = this.totalPages;
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      return pages;
    },
    
    /**
     * Check if user is authenticated
     * @returns {boolean} True if user has an access token
     */
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  },
  methods: {
    /**
     * Fetch all destinations from API
     * Loads destination data and extracts category and country lists
     */
    async fetchDestinations() {
      try {
        this.isLoading = true;
        this.error = null;
        
        const response = await axios.get('http://localhost:8000/api/destinations/');
        this.destinations = response.data;
        
        // Extract category list
        this.extractCategories();
        
        // Extract country list
        this.extractCountries();
        
        this.isLoading = false;
      } catch (error) {
        console.error('Failed to load destination information:', error);
        this.error = 'Failed to load destinations. Please try again.';
        this.isLoading = false;
      }
    },
    
    /**
     * Extract unique categories from destination data
     * Populates the categories array for filter dropdown
     */
    extractCategories() {
      const categorySet = new Set();
      this.destinations.forEach(dest => {
        if (dest.category) {
          categorySet.add(dest.category);
        }
      });
      this.categories = Array.from(categorySet).sort();
    },
    
    /**
     * Extract unique countries from destination data
     * Populates the countries array for filter dropdown
     */
    extractCountries() {
      const countrySet = new Set();
      const destinations = this.isSearchMode ? this.searchResults : this.destinations;
      
      destinations.forEach(dest => {
        if (dest.country) {
          countrySet.add(dest.country);
        }
      });
      
      this.countries = Array.from(countrySet).sort();
    },
    
    /**
     * Handle search button click
     * Calls the NLP search API with the current search query
     */
    async handleSearch() {
      if (!this.searchQuery.trim()) {
        this.clearSearch();
        return;
      }
      
      try {
        this.isLoading = true;
        this.error = null;
        
        const response = await axios.get(`http://localhost:8000/api/destinations/search/nlp/?query=${encodeURIComponent(this.searchQuery)}&limit=${this.resultLimit}`);
        
        if (response.data && response.data.results) {
          this.searchResults = response.data.results;
          this.isSearchMode = true;
          this.currentPage = 1; // Move to first page on search
          
          // Extract country list
          this.extractCountries();
          
          // Update URL query parameters (preserve search state)
          this.$router.replace({
            path: this.$route.path,
            query: { ...this.$route.query, q: this.searchQuery, limit: this.resultLimit }
          });
        } else {
          this.searchResults = [];
        }
        
        this.isLoading = false;
      } catch (error) {
        console.error('An error occurred during search:', error);
        this.error = 'An error occurred during search. Please try again.';
        this.isLoading = false;
      }
    },
    
    /**
     * Handle change in result limit dropdown
     * Reruns search with new limit if in search mode
     */
    handleLimitChange() {
      // Perform search again when result limit changes
      if (this.isSearchMode && this.searchQuery) {
        this.handleSearch();
      }
    },
    
    /**
     * Clear search and return to browse mode
     * Resets search-related state variables
     */
    clearSearch() {
      this.searchQuery = '';
      this.isSearchMode = false;
      this.searchResults = [];
      this.currentPage = 1;
      this.selectedCountry = ''; // Reset country filter
      
      // Remove search term and result limit from URL query parameters
      this.$router.replace({
        path: this.$route.path,
        query: { ...this.$route.query, q: undefined, limit: undefined }
      });
      
      // Re-extract country list
      this.extractCountries();
    },
    
    /**
     * Handle sort option change
     * Resets to first page to show properly sorted results
     */
    handleSort() {
      // Move to first page when sort option changes
      this.currentPage = 1;
    },
    
    /**
     * Handle filter option change
     * Resets to first page to show properly filtered results
     */
    handleFilter() {
      // Move to first page when filter option changes
      this.currentPage = 1;
    },
    
    /**
     * Change current page in pagination
     * @param {number} page - Page number to navigate to
     */
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        // Scroll to top on page change
        window.scrollTo(0, 0);
      }
    },
    
    /**
     * Navigate to destination detail page
     * @param {number} id - Destination ID to view
     */
    viewDestinationDetails(id) {
      this.$router.push(`/destinations/${id}`);
    },
    
    /**
     * Format location string from destination data
     * @param {Object} destination - Destination object
     * @returns {string} Formatted location string (city, state, country)
     */
    getLocationString(destination) {
      const parts = [];
      if (destination.city) parts.push(destination.city);
      if (destination.state) parts.push(destination.state);
      if (destination.country) parts.push(destination.country);
      
      return parts.join(', ') || 'No location information';
    },
    
    /**
     * Truncate text to specified length with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length before truncation
     * @returns {string} Truncated text with ellipsis if needed
     */
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.slice(0, maxLength) + '...';
    },
    
    /**
     * Add destination to planner
     * Redirects to planner page with destination ID in query params
     * @param {Object} destination - Destination to add to planner
     */
    addToPlanner(destination) {
      // If user is not logged in
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      // Navigate to planner page with destination info
      this.$router.push({
        path: '/planner',
        query: { destination: destination.id }
      });
    }
  },
  created() {
    this.fetchDestinations();
    
    // Get search term and result limit from URL query parameters
    const query = this.$route.query.q;
    const limit = this.$route.query.limit;
    
    if (limit) {
      this.resultLimit = parseInt(limit);
    }
    
    if (query) {
      this.searchQuery = query;
      this.handleSearch();
    }
  },
  watch: {
    /**
     * Watch for URL query parameter changes
     * Updates search when URL is changed (e.g., browser back button)
     */
    '$route.query.q': function(newQuery) {
      if (newQuery !== this.searchQuery) {
        this.searchQuery = newQuery || '';
        if (newQuery) {
          this.handleSearch();
        } else {
          this.clearSearch();
        }
      }
    }
  }
};
</script>

<style scoped>
.destination-list-container {
  background-image: url('@/assets/destback.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  min-height: 100vh;
  padding: 20px;
}

/* Main container for the destination list page */
.destination-list-container {
  max-width: 100%; 
  width: 100%;
  margin: 0;
  padding: 2rem;
}

/* Search and filter section at the top of the page */
.search-section {
  margin-bottom: 2rem;
  background-color: rgba(248, 249, 250, 0.9);
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* Search input and button container */
.search-container {
  display: flex;
  margin-bottom: 1rem;
}

/* Search input field styling */
.search-input {
  flex-grow: 1;
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
}

/* Search button styling */
.search-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0 1.5rem;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

/* Hover effect for search button */
.search-button:hover {
  background-color: #2980b9;
}

/* Container for filter and sort options */
.search-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Styling for sort, filter, and limit containers */
.sort-container, .filter-container, .limit-container {
  display: flex;
  align-items: center;
}

/* Labels for sort, filter, and limit options */
.sort-container label, .filter-container label, .limit-container label {
  margin-right: 0.5rem;
  font-weight: 500;
  color: #4a5568;
}

/* Dropdown select styling */
.sort-select, .filter-select, .limit-select {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background-color: white;
}

/* Loading indicator container */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

/* Loading spinner animation */
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

/* Spinner animation keyframes */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error message container */
.error-container {
  text-align: center;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  color: #e53e3e;
}

/* Retry button for error state */
.retry-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

/* Search results header with title and clear button */
.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

/* Search results title styling */
.search-results-header h2 {
  font-size: 1.5rem;
  color: #2d3748;
  margin: 0;
}

/* Search type badge (NLP/sentiment analysis) */
.search-type {
  font-size: 0.9rem;
  color: #3498db;
  background-color: #e6f7ff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  margin-left: 0.5rem;
  font-weight: normal;
}

/* Clear search button styling */
.clear-search-button {
  background-color: #e2e8f0;
  color: #4a5568;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

/* Hover effect for clear search button */
.clear-search-button:hover {
  background-color: #cbd5e0;
}

/* No results message styling */
.no-results {
  text-align: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #4a5568;
}

/* Grid layout for destination cards */
.destinations-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Individual destination card styling */
.destination-card {
  background-color: rgba(255, 255, 255, 0.9);  
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

/* Hover effect for destination cards */
.destination-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

/* Destination image container */
.destination-image {
  height: 180px;
  background-size: cover;
  background-position: center;
}

/* Destination information container */
.destination-info {
  padding: 1.2rem;
}

/* Destination name styling */
.destination-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #2d3748;
}

/* Location text styling */
.location {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
}

/* Container for category tag and rating */
.destination-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

/* Category tag styling */
.category-tag {
  background-color: #e6f7ff;
  color: #0070f3;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* Rating display styling */
.rating {
  color: #f6ad55;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Similarity score container for search results */
.similarity-score {
  display: flex;
  align-items: center;
  margin: 0.8rem 0;
  font-size: 0.9rem;
}

/* Similarity score label */
.score-label {
  margin-right: 0.5rem;
  color: #7f8c8d;
}

/* Similarity score progress bar container */
.score-bar {
  flex-grow: 1;
  height: 6px;
  background-color: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
  margin: 0 0.5rem;
}

/* Similarity score progress bar fill */
.score-fill {
  height: 100%;
  background-color: #3498db;
  border-radius: 3px;
}

/* Similarity score percentage display */
.score-value {
  color: #3498db;
  font-weight: bold;
}

/* Description text styling */
.description {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  line-height: 1.4;
}

/* Container for card action buttons */
.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

/* View details button styling */
.view-details-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  flex: 1;
  margin-right: 0.5rem;
}

/* Add to planner button styling */
.add-to-planner-button {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  flex: 1;
}

/* Hover effect for add to planner button */
.add-to-planner-button:hover {
  background-color: #219653;
}

/* Pagination controls container */
.pagination {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

/* Pagination button styling */
.pagination-button {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

/* Active page button styling */
.pagination-button.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

/* Hover effect for pagination buttons */
.pagination-button:hover:not(:disabled) {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

/* Disabled pagination button styling */
.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive styling for mobile devices */
@media (max-width: 1200px) {
  /* For large tablets/small desktops, show 3 cards per row */
  .destinations-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  /* For tablets, show 2 cards per row */
  .destinations-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  /* For mobile, show 1 card per row */
  .destinations-grid {
    grid-template-columns: 1fr;
  }
  
  /* Adjust container padding for smaller screens */
  .destination-list-container {
    padding: 1rem;
  }
  
  /* Stack search input and button for mobile */
  .search-container {
    flex-direction: column;
  }
  
  /* Adjust search input border radius for stacked layout */
  .search-input {
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }
  
  /* Adjust search button for stacked layout */
  .search-button {
    border-radius: 4px;
    width: 100%;
    padding: 0.8rem;
  }
  
  /* Stack filter options for mobile */
  .search-options {
    flex-direction: column;
  }
}

.likes-count {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background-color: rgba(255, 0, 0, 0.1);
  color: #e91e63;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-left: 4px;
}

.likes-count i {
  font-size: 0.85rem;
}
</style> 