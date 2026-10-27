<template>
  <!-- Tag selection component -->
  <div class="tag-choose-container">
    <h3>Please select your travel interests (3-7 categories)</h3>
    <p class="tag-instruction">Selected tags: {{ selectedTags.length }} (minimum 3, maximum 7)</p>
    
    <!-- Tag selection grid -->
    <div class="tags-grid">
      <div 
        v-for="tag in tags" 
        :key="tag" 
        :class="['tag-item', { selected: isSelected(tag) }]"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </div>
    </div>
    
    <!-- Error message display -->
    <div class="error-message" v-if="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios';

/**
 * Component for selecting travel interest tags
 * Used in user profile and registration for preference-based recommendations
 */
export default {
  name: 'TagChoose',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      tags: [],
      selectedTags: [],
      error: '',
      isLoading: false
    };
  },
  created() {
    // Initialize with provided value
    this.selectedTags = Array.isArray(this.modelValue) ? [...this.modelValue] : [];
    this.fetchTags();
  },
  methods: {
    /**
     * Check if a tag is currently selected
     * @param {string} tag - Tag name to check
     * @returns {boolean} Whether tag is selected
     */
    isSelected(tag) {
      return this.selectedTags.includes(tag);
    },
    
    /**
     * Toggle tag selection status
     * Handles adding/removing tags and validation
     * @param {string} tag - Tag to toggle
     */
    toggleTag(tag) {
      let newSelectedTags;
      
      if (this.isSelected(tag)) {
        // Remove tag if already selected
        newSelectedTags = this.selectedTags.filter(t => t !== tag);
      } else {
        // Check maximum limit when adding a new tag
        if (this.selectedTags.length >= 7) {
          this.error = 'You can select a maximum of 7 tags.';
          return;
        }
        // Add tag if not already selected
        newSelectedTags = [...this.selectedTags, tag];
      }
      
      // Update local state
      this.selectedTags = newSelectedTags;
      
      // Notify parent component of changes (Vue 3 v-model)
      this.$emit('update:modelValue', newSelectedTags);
      
      // Update error message based on tag count
      if (newSelectedTags.length < 3) {
        this.error = 'Please select at least 3 tags.';
      } else if (newSelectedTags.length > 7) {
        this.error = 'You can select a maximum of 7 tags.';
      } else {
        this.error = '';
      }
    },
    
    /**
     * Fetch available tags from the API
     */
    async fetchTags() {
      try {
        this.isLoading = true;
        const response = await axios.get('/api/accounts/tags/');
        this.tags = response.data.tags;
      } catch (error) {
        this.error = 'Failed to load available tags.';
      } finally {
        this.isLoading = false;
      }
    }
  },
  watch: {
    modelValue: {
      handler(newVal) {
        // Update local state when prop changes
        this.selectedTags = Array.isArray(newVal) ? [...newVal] : [];
      },
      deep: true
    }
  }
};
</script>

<style scoped>
/* Main container */
.tag-choose-container {
  margin: 20px 0;
}

/* Section title */
h3 {
  margin-bottom: 10px;
  color: #4a5568;
}

/* Selection instruction text */
.tag-instruction {
  margin-bottom: 15px;
  font-size: 14px;
  color: #718096;
}

/* Grid layout for tags */
.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

/* Individual tag item */
.tag-item {
  padding: 10px 15px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

/* Hover state */
.tag-item:hover {
  background-color: #edf2f7;
}

/* Selected state */
.tag-item.selected {
  background-color: #667eea;
  color: white;
  border-color: #5a67d8;
}

/* Error message */
.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-top: 10px;
}
</style> 