<template>
  <div class="planner-container">
    <h1 class="page-title">Travel Planner</h1>
    
    <div v-if="loadingPlanners" class="loading-container">
      <div class="spinner"></div>
      <p>Loading Planner Info...</p>
    </div>
    
    <!-- Planner selection and creation section -->
    <div v-else class="planner-selection">
      <div v-if="userPlanners.length > 0" class="planner-list">
        <h2>Your Planner</h2>
        <div class="planner-tabs">
          <button 
            v-for="planner in userPlanners" 
            :key="planner.id"
            @click="currentPlanner = planner; fetchPlannerItems();"
            :class="['planner-tab', { active: currentPlanner && currentPlanner.id === planner.id }]"
          >
            {{ planner.title }}
            <span class="item-count">({{ planner.items_count || 0 }})</span>
          </button>
          <button @click="currentPlanner = null" class="planner-tab new-planner">
            <i class="fas fa-plus"></i> New Planner
          </button>
        </div>
      </div>
      
      <!-- Planner creation form -->
      <div v-if="!currentPlanner" class="create-planner-form">
        <h2>Create New Planner</h2>
        <div class="form-group">
          <label for="planner-title">Planner Title</label>
          <input 
            type="text" 
            id="planner-title" 
            v-model="newPlanner.title" 
            placeholder="e.g. Europe Trip"
            class="form-control"
          >
        </div>
        <div class="form-group">
          <label for="planner-description">Explanation (Optional)</label>
          <textarea 
            id="planner-description" 
            v-model="newPlanner.description" 
            placeholder="Enter Explanation for Planner"
            class="form-control"
          ></textarea>
        </div>
        <button @click="createPlanner" class="btn-primary">Create Planner</button>
      </div>
      
      <!-- Planner management screen -->
      <div v-else class="planner-management">
        <div class="planner-header">
          <div>
            <h2>{{ currentPlanner.title }}</h2>
            <p v-if="currentPlanner.description" class="planner-description">{{ currentPlanner.description }}</p>
          </div>
          <div class="planner-actions">
            <button @click="savePlannerOrder" class="btn-primary">Save Changes</button>
            <button @click="currentPlanner = null" class="btn-secondary">Create Another Planner</button>
            <button @click="deletePlanner" class="btn-danger">
              <i class="fas fa-trash"></i> Delete Planner
            </button>
          </div>
        </div>
        
        <div class="planner-content">
          <!-- Left side: Planner area -->
          <div class="planner-area">
            <h3>My Travel Plan <span class="item-count">({{ plannerItems.length }}/10)</span></h3>
            <div 
              class="planner-drop-area"
              @dragover.prevent
              @drop="onDrop"
            >
              <div v-if="plannerItems.length === 0" class="empty-planner">
                <p>Drag your destination here to add it to your planner</p>
                <p class="small">You can add up to 10 Destinations</p>
              </div>
              <draggable 
                v-model="plannerItems" 
                group="destinations"
                item-key="id"
                class="planner-items-list"
                @change="onDraggableChange"
              >
                <template #item="{ element }">
                  <div class="planner-item">
                    <div class="item-image">
                      <img :src="element.location_details.image || 'https://via.placeholder.com/100x60?text=No+Image'" :alt="element.location_details.name">
                    </div>
                    <div class="item-info">
                      <h4>{{ element.location_details.name }}</h4>
                      <p class="location">
                        {{ getLocationString(element.location_details) }}
                      </p>
                    </div>
                    <button @click="removeFromPlanner(element)" class="btn-remove" title="Remove destination">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </template>
              </draggable>
            </div>
          </div>
          
          <!-- Right side: Destination search and listing -->
          <div class="destinations-area">
            <h3>Search Destinations</h3>
            <div class="filter-controls">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="Search for Destinations... (More than 2 Words)" 
                  class="search-input"
                >
              </div>
              <div class="country-filter" v-if="countries.length > 0">
                <select v-model="selectedCountry" class="country-select">
                  <option value="">All Countries</option>
                  <option v-for="country in countries" :key="country" :value="country">
                    {{ country }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="destinations-list">
              <div v-if="searchQuery.trim().length < 2" class="search-prompt">
                <p>More than 2 Words to Search Destinations</p>
              </div>
              
              <div 
                v-else-if="filteredDestinations.length > 0"
                v-for="destination in filteredDestinations" 
                :key="destination.id"
                class="destination-card"
                draggable="true"
                @dragstart="onDragStart($event, destination)"
              >
                <div class="destination-image">
                  <img :src="destination.image || 'https://via.placeholder.com/150x100?text=No+Image'" :alt="destination.name">
                </div>
                <div class="destination-info">
                  <h4>{{ destination.name }}</h4>
                  <p class="location">{{ getLocationString(destination) }}</p>
                </div>
                <button 
                  @click="addToPlanner(destination)" 
                  class="btn-add"
                  :disabled="isDestinationInPlanner(destination) || plannerItems.length >= 10"
                >
                  <i class="fas fa-plus"></i>
                </button>
              </div>
              
              <div v-else-if="searchQuery.trim().length >= 2 && filteredDestinations.length === 0 && !isLoading" class="no-results">
                <p>No Results</p>
              </div>
              
              <div v-if="isLoading" class="loading">
                <div class="spinner"></div>
                <p>Loading Destinations...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, computed, onMounted, watch } from 'vue';
import draggable from 'vuedraggable';

/**
 * Travel Planner Component
 * Allows users to create, manage, and organize their travel itineraries
 * Features:
 * - Creating new planners with title and description
 * - Viewing and selecting existing planners
 * - Adding destinations to planners via search or drag-and-drop
 * - Reordering destinations within a planner
 * - Deleting planners
 */
export default {
  name: 'CreatePlanner',
  components: {
    draggable
  },
  setup() {
    // State variables
    const destinations = ref([]); // Search results for destinations
    const countries = ref([]); // List of available countries for filtering
    const searchQuery = ref(''); // User's destination search query
    const selectedCountry = ref(''); // Selected country filter
    const isLoading = ref(true); // Loading state for destinations
    const currentPlanner = ref(null); // Currently selected planner
    const plannerItems = ref([]); // Destinations in the current planner
    const originalOrder = ref([]); // Original order of planner items for change detection
    const newPlanner = ref({
      title: '',
      description: ''
    }); // New planner form data
    const draggedDestination = ref(null); // Currently dragged destination
    const userPlanners = ref([]);  // List of user's planners
    const loadingPlanners = ref(false);  // Planner loading state
    const searchTimeout = ref(null); // Timeout for search debouncing
    
    /**
     * Filtered destinations based on selected country
     * The destination list is already filtered by search term from the backend
     * @returns {Array} Filtered destination list
     */
    const filteredDestinations = computed(() => {
      let filtered = destinations.value;
      
      // Filter by search term (already done by backend)
      // We don't filter by search term here as the backend already returns filtered results
      
      // Filter by country
      if (selectedCountry.value) {
        filtered = filtered.filter(dest => 
          dest.country === selectedCountry.value
        );
      }
      
      return filtered;
    });
    
    /**
     * Check if planner item order has changed from original
     * Used to determine if save button should be enabled
     * @returns {boolean} True if order has changed
     */
    const hasOrderChanged = computed(() => {
      if (plannerItems.value.length !== originalOrder.value.length) return true;
      
      for (let i = 0; i < plannerItems.value.length; i++) {
        if (plannerItems.value[i].id !== originalOrder.value[i]) return true;
      }
      
      return false;
    });
    
    /**
     * Fetch user's planner list from the API
     * Loads all planners belonging to the current user
     */
    const fetchUserPlanners = async () => {
      try {
        loadingPlanners.value = true;
        const response = await axios.get('/api/planner/planners/');
        userPlanners.value = response.data;
        
        // Select first planner if available
        if (userPlanners.value.length > 0) {
          currentPlanner.value = userPlanners.value[0];
        }
        
        loadingPlanners.value = false;
      } catch (error) {
        loadingPlanners.value = false;
      }
    };
    
    /**
     * Handle destination ID from URL query parameter
     * Used when adding a destination to planner from other pages
     */
    const handleDestinationFromQuery = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const destinationId = urlParams.get('destination');
      
      if (destinationId && currentPlanner.value) {
        try {
          // Get destination information
          const response = await axios.get(`/api/destinations/${destinationId}/`);
          const destination = response.data;
          
          // Add destination to planner
          addToPlanner(destination);
          
          // Remove query parameter from URL
          const url = new URL(window.location);
          url.searchParams.delete('destination');
          window.history.replaceState({}, '', url);
        } catch (error) {
          // Failed to load destination information
        }
      }
    };
    
    /**
     * Fetch destinations matching the search query
     * Uses NLP/sentiment analysis API for enhanced search capabilities
     */
    const fetchDestinations = async () => {
      if (searchQuery.value.trim() === '') {
        destinations.value = [];
        isLoading.value = false;
        return;
      }
      
      try {
        isLoading.value = true;
        const response = await axios.get(`/api/destinations/search/nlp/?query=${encodeURIComponent(searchQuery.value)}&limit=20`);
        
        if (response.data && response.data.results) {
          destinations.value = response.data.results;
          
          // Retry if results are fewer than expected (less than 10) but there are more available
          if (destinations.value.length < 10 && response.data.results_count > 10) {
            setTimeout(async () => {
              try {
                const retryResponse = await axios.get(`/api/destinations/search/nlp/?query=${encodeURIComponent(searchQuery.value)}&limit=20&retry=true`);
                if (retryResponse.data && retryResponse.data.results && retryResponse.data.results.length > destinations.value.length) {
                  destinations.value = retryResponse.data.results;
                }
              } catch (retryError) {
                // Error during retry search
              }
            }, 500);
          }
        } else {
          destinations.value = [];
        }
        
        // Extract country list for filtering
        const countrySet = new Set();
        destinations.value.forEach(dest => {
          if (dest.country) countrySet.add(dest.country);
        });
        countries.value = Array.from(countrySet).sort();
        
        isLoading.value = false;
      } catch (error) {
        isLoading.value = false;
      }
    };
    
    // Watch for search query changes with debouncing
    watch(searchQuery, () => {
      // Cancel previous timeout
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }
      
      if (searchQuery.value.trim().length >= 2) {
        // Apply 500ms debouncing to prevent excess API calls
        searchTimeout.value = setTimeout(() => {
          fetchDestinations();
        }, 500);
      } else if (searchQuery.value.trim() === '') {
        destinations.value = [];
      }
    });
    
    /**
     * Create a new planner
     * Sends planner data to the API and updates the UI
     */
    const createPlanner = async () => {
      if (!newPlanner.value.title) {
        alert('Please enter a planner title.');
        return;
      }
      
      try {
        const response = await axios.post('/api/planner/planners/', {
          title: newPlanner.value.title,
          description: newPlanner.value.description
        });
        
        // Add newly created planner to userPlanners list
        userPlanners.value.unshift(response.data);
        
        // Set newly created planner as current planner
        currentPlanner.value = response.data;
        newPlanner.value = { title: '', description: '' };
      } catch (error) {
        alert('Failed to create planner. Please try again.');
      }
    };
    
    /**
     * Reset planner selection
     * Clears current planner and items
     */
    const resetPlanner = () => {
      currentPlanner.value = null;
      plannerItems.value = [];
      originalOrder.value = [];
    };
    
    /**
     * Add destination to current planner
     * Limits to 10 destinations per planner
     * @param {Object} destination - Destination object to add
     */
    const addToPlanner = async (destination) => {
      if (plannerItems.value.length >= 10) {
        alert('You can add a maximum of 10 destinations to your planner.');
        return;
      }
      
      if (isDestinationInPlanner(destination)) {
        alert('This destination is already in your planner.');
        return;
      }
      
      try {
        const response = await axios.post('/api/planner/planner-items/', {
          planner: currentPlanner.value.id,
          location: destination.id,
          order: plannerItems.value.length
        });
        
        // Add location_details if not present in response
        if (!response.data.location_details) {
          response.data.location_details = destination;
        }
        
        plannerItems.value.push(response.data);
        updateOriginalOrder();
      } catch (error) {
        alert('Failed to add destination. Please try again.');
      }
    };
    
    /**
     * Remove destination from planner
     * @param {Object} item - Planner item to remove
     */
    const removeFromPlanner = async (item) => {
      try {
        await axios.delete(`/api/planner/planner-items/${item.id}/`);
        plannerItems.value = plannerItems.value.filter(i => i.id !== item.id);
        
        // Update order
        plannerItems.value.forEach((item, index) => {
          item.order = index;
        });
        
        updateOriginalOrder();
      } catch (error) {
        alert('Failed to remove destination. Please try again.');
      }
    };
    
    /**
     * Save planner item order to the server
     * Updates item order after drag-and-drop reordering
     */
    const savePlannerOrder = async () => {
      try {
        // No need to save if there are no items
        if (plannerItems.value.length === 0) {
          alert('There are no destinations to save.');
          return;
        }
        
        // Sync with server data before saving
        await fetchPlannerItems();
        
        // Create item data to save
        const items = plannerItems.value.map((item, index) => ({
          id: item.id,
          order: index
        }));
        
        await axios.post('/api/planner/planner-items/reorder/', {
          items: items
        });
        
        updateOriginalOrder();
        
        // Reload planner list
        await fetchUserPlanners();
        
        alert('Planner order has been saved.');
      } catch (error) {
        if (error.response) {
          // If items not found, reload planner items
          if (error.response.status === 400 && error.response.data.detail === 'Some items could not be found.') {
            alert('Some items could not be found. Reloading planner items.');
            await fetchPlannerItems();
            return;
          }
        }
        alert('Failed to save planner order. Please try again.');
      }
    };
    
    /**
     * Fetch items for the currently selected planner
     * Loads destination details for each planner item
     */
    const fetchPlannerItems = async () => {
      if (!currentPlanner.value) return;
      
      try {
        const response = await axios.get(`/api/planner/planners/${currentPlanner.value.id}/items/`);
        
        // Update data
        plannerItems.value = response.data;
        updateOriginalOrder();
      } catch (error) {
        alert('Failed to load planner items. Please refresh the page.');
      }
    };
    
    /**
     * Update original order to match current order
     * Used to track changes for the save button
     */
    const updateOriginalOrder = () => {
      originalOrder.value = plannerItems.value.map(item => item.id);
    };
    
    /**
     * Check if destination is already in planner
     * @param {Object} destination - Destination to check
     * @returns {boolean} True if destination exists in planner
     */
    const isDestinationInPlanner = (destination) => {
      return plannerItems.value.some(item => 
        item.location === destination.id || 
        (item.location_details && item.location_details.id === destination.id)
      );
    };
    
    /**
     * Format location string from destination data
     * @param {Object} destination - Destination object with location data
     * @returns {string} Formatted location string (city, country)
     */
    const getLocationString = (destination) => {
      const parts = [];
      if (destination.city) parts.push(destination.city);
      if (destination.country) parts.push(destination.country);
      
      return parts.join(', ') || 'No location information';
    };
    
    /**
     * Handle drag start event for drag-and-drop
     * @param {Event} event - Drag event
     * @param {Object} destination - Dragged destination
     */
    // eslint-disable-next-line no-unused-vars
    const onDragStart = (event, destination) => {
      draggedDestination.value = destination;
      event.dataTransfer.effectAllowed = 'move';
    };
    
    /**
     * Handle drop event for drag-and-drop
     * @param {Event} event - Drop event
     */
    // eslint-disable-next-line no-unused-vars
    const onDrop = (event) => {
      if (draggedDestination.value) {
        addToPlanner(draggedDestination.value);
        draggedDestination.value = null;
      }
    };
    
    /**
     * Handle draggable component change event
     * Updates item order after drag-and-drop within the list
     */
    const onDraggableChange = () => {
      // Update order
      plannerItems.value.forEach((item, index) => {
        item.order = index;
      });
      
      // Don't update originalOrder to compare with hasOrderChanged
      // This will return true to show that the save button is active
      
      // Auto save feature (optionally enabled)
      // savePlannerOrder();
    };
    
    // Load user's planner list on mount
    onMounted(() => {
      fetchUserPlanners().then(() => {
        // Process URL query parameters after loading planner list
        handleDestinationFromQuery();
      });
    });
    
    // Watch for current planner changes
    watch(currentPlanner, () => {
      fetchPlannerItems();
    });
    
    /**
     * Delete the current planner
     * Removes planner and all its items after confirmation
     */
    const deletePlanner = async () => {
      if (confirm('Are you sure you want to delete this planner? Deleted planners cannot be recovered.')) {
        try {
          await axios.delete(`/api/planner/planners/${currentPlanner.value.id}/`);
          currentPlanner.value = null;
          // Reload planner list
          await fetchUserPlanners();
          alert('Planner has been successfully deleted.');
        } catch (error) {
          alert('Failed to delete planner. Please try again.');
        }
      }
    };
    
    return {
      destinations,
      countries,
      searchQuery,
      selectedCountry,
      isLoading,
      currentPlanner,
      plannerItems,
      newPlanner,
      filteredDestinations,
      hasOrderChanged,
      userPlanners,
      loadingPlanners,
      createPlanner,
      resetPlanner,
      addToPlanner,
      removeFromPlanner,
      savePlannerOrder,
      isDestinationInPlanner,
      getLocationString,
      onDragStart,
      onDrop,
      onDraggableChange,
      fetchDestinations,
      fetchPlannerItems,
      deletePlanner
    };
  }
};
</script>

<style scoped>
/* Main container - holds the entire planner interface */
.planner-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Page title styling - main heading for the planner page */
.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
}

/* Planner creation form - container for the new planner form */
.create-planner-form {
  max-width: 600px;
  margin: 0 auto;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Creation form heading styling */
.create-planner-form h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

/* Form group - container for each form field */
.form-group {
  margin-bottom: 1.5rem;
}

/* Form label styling */
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

/* Form control - styling for inputs and textareas */
.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/* Textarea specific styling */
textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

/* Planner management screen - container for active planner view */
.planner-management {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Planner header - contains title and action buttons */
.planner-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

/* Planner title styling */
.planner-header h2 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

/* Planner action buttons container */
.planner-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

/* Planner content - main area with two columns */
.planner-content {
  display: flex;
  min-height: 600px;
}

/* Left side: Planner area - contains the current planner items */
.planner-area {
  flex: 1;
  padding: 1.5rem;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

/* Planner area heading */
.planner-area h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Item count badge - shows number of destinations in planner */
.item-count {
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
}

/* Drop area - target for drag and drop operations */
.planner-drop-area {
  flex: 1;
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 1rem;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

/* Empty planner state - shown when no destinations added */
.empty-planner {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  text-align: center;
}

/* Small text in empty planner message */
.empty-planner .small {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* Container for planner item list */
.planner-items-list {
  flex: 1;
  overflow-y: auto;
}

/* Individual planner item styling */
.planner-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  cursor: move;
}

/* Destination image container in planner item */
.item-image {
  width: 60px;
  height: 60px;
  margin-right: 1rem;
  border-radius: 4px;
  overflow: hidden;
}

/* Image styling within item image container */
.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Destination info container */
.item-info {
  flex: 1;
}

/* Destination name in planner item */
.item-info h4 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}

/* Location text styling */
.location {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

/* Remove button for planner items */
.btn-remove {
  background: transparent;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

/* Hover effect for remove button */
.btn-remove:hover {
  background-color: rgba(231, 76, 60, 0.1);
}

/* Right side: Destination search and listing */
.destinations-area {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

/* Destination area heading */
.destinations-area h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Filter and search controls container */
.filter-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Search box container */
.search-box {
  flex: 1;
}

/* Search input styling */
.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/* Country filter dropdown styling */
.country-select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 150px;
}

/* Destination search results grid */
.destinations-list {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  max-height: 500px;
  padding-right: 0.5rem;
  grid-auto-rows: min-content;
}

/* Individual destination card in search results */
.destination-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: grab;
  position: relative;
  height: auto;
  min-height: 220px;
  display: flex;
  flex-direction: column;
}

/* Destination image container */
.destination-image {
  height: 120px;
  overflow: hidden;
}

/* Image styling within destination card */
.destination-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Destination info container */
.destination-info {
  padding: 1rem;
}

/* Destination name styling */
.destination-info h4 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

/* Add to planner button */
.btn-add {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* Disabled state for add button */
.btn-add:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* No search results message */
.no-results, .loading {
  grid-column: 1 / -1;
  padding: 2rem;
  text-align: center;
  color: #666;
}

/* Loading indicator container */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Loading spinner animation */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

/* Spinner animation keyframes */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Primary button styling - for main actions */
.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Hover effect for primary button */
.btn-primary:hover {
  background-color: #2980b9;
}

/* Disabled state for primary button */
.btn-primary:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

/* Secondary button styling - for secondary actions */
.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: 1px solid #ddd;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Hover effect for secondary button */
.btn-secondary:hover {
  background-color: #dde4e6;
}

/* Danger button styling - for destructive actions */
.btn-danger {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Hover effect for danger button */
.btn-danger:hover {
  background-color: #c0392b;
}

/* Planner selection container */
.planner-selection {
  margin-bottom: 2rem;
}

/* Planner list container */
.planner-list {
  margin-bottom: 2rem;
}

/* Planner list heading */
.planner-list h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Planner tabs container - for switching between planners */
.planner-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

/* Individual planner tab button */
.planner-tab {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

/* Active planner tab styling */
.planner-tab.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

/* Hover effect for inactive planner tabs */
.planner-tab:hover:not(.active) {
  background-color: #e9ecef;
}

/* Item count within planner tab */
.planner-tab .item-count {
  font-size: 0.8rem;
  color: inherit;
  opacity: 0.8;
  margin-left: 0.25rem;
}

/* New planner tab button styling */
.planner-tab.new-planner {
  background-color: #27ae60;
  color: white;
  border-color: #27ae60;
}

/* Hover effect for new planner tab */
.planner-tab.new-planner:hover {
  background-color: #219653;
}

/* Planner description text styling */
.planner-description {
  color: #666;
  margin-top: 0.5rem;
}

/* Search prompt - shown when search input is too short */
.search-prompt {
  grid-column: 1 / -1;
  padding: 2rem;
  text-align: center;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* Responsive styles for smaller screens */
@media (max-width: 768px) {
  /* Stack planner tabs vertically on small screens */
  .planner-tabs {
    flex-direction: column;
  }
  
  /* Full width tabs on small screens */
  .planner-tab {
    width: 100%;
  }
  
  /* Stack planner content areas vertically */
  .planner-content {
    flex-direction: column;
  }
  
  /* Adjust planner area and destinations area for mobile */
  .planner-area, .destinations-area {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #eee;
  }
  
  /* Stack filter controls vertically */
  .filter-controls {
    flex-direction: column;
  }
}
</style>