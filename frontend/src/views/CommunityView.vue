<template>
  <!-- Main community page container -->
  <v-container class="community-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="community-card" elevation="4">
          <!-- Page title -->
          <v-card-title class="text-center text-h4 font-weight-bold primary--text">
            Community
          </v-card-title>

          <v-card-text>
            <!-- Create new post button -->
            <v-btn
              color="primary"
              block
              large
              class="mb-4"
              @click="$router.push('/community/new')"
            >
              <v-icon left>mdi-plus</v-icon>
              Create Post
            </v-btn>
            
            <!-- Search bar -->
            <v-row class="mb-6">
              <v-col cols="12">
                <v-card outlined class="search-card pa-2">
                  <v-row no-gutters>
                    <v-col cols="9" sm="10">
                      <v-text-field
                        v-model="searchQuery"
                        :placeholder="searchPlaceholder"
                        hide-details
                        single-line
                        filled
                        rounded
                        dense
                        prepend-inner-icon="mdi-magnify"
                        class="search-input"
                        @keyup.enter="searchPosts"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="3" sm="2">
                      <v-btn
                        color="primary"
                        block
                        :loading="searching"
                        :disabled="!searchQuery"
                        @click="searchPosts"
                        elevation="1"
                        class="ml-1"
                        height="40"
                      >
                        Search
                      </v-btn>
                    </v-col>
                  </v-row>
                  
                  <!-- Search options -->
                  <v-row no-gutters class="mt-2">
                    <v-col cols="12">
                      <v-radio-group 
                        v-model="searchType" 
                        row 
                        dense 
                        hide-details 
                        class="mt-0 pt-0"
                      >
                        <v-radio label="All" value="all"></v-radio>
                        <v-radio label="Post Title" value="title"></v-radio>
                        <v-radio label="Author" value="author"></v-radio>
                      </v-radio-group>
                    </v-col>
                  </v-row>
                </v-card>
              </v-col>
            </v-row>
            
            <!-- Search results info -->
            <div v-if="isSearchActive" class="my-3 d-flex align-center search-info">
              <div class="text-subtitle-1">
                {{ searchResultText }}
                <span class="ml-2 text-caption">({{ posts.length }} results found)</span>
              </div>
              <v-spacer></v-spacer>
              <v-btn
                text
                small
                color="grey"
                @click="clearSearch"
                class="ml-2"
              >
                <v-icon small left>mdi-close</v-icon>
                Clear
              </v-btn>
            </div>

            <!-- No results message -->
            <v-alert
              v-if="isSearchActive && posts.length === 0"
              type="info"
              dense
              outlined
              class="mb-4"
            >
              No posts found for "{{ searchQuery }}". Try different keywords.
            </v-alert>

            <!-- List of community posts -->
            <v-list class="post-list">
              <v-list-item
                v-for="post in paginatedPosts"
                :key="post.id"
                :to="`/community/${post.id}`"
                class="post-item"
                ripple
                @click="$router.push(`/community/${post.id}`)"
              >
                <template v-slot:default>
                  <v-list-item-title class="text-h6 mb-2">
                    {{ post.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="d-flex align-center">
                    <user-avatar
                      :username="post.author"
                      :profile-image="post.author_profile_image"
                      :size="24"
                      class="mr-2"
                    ></user-avatar>
                    {{ post.author }}
                    <v-spacer></v-spacer>
                    <v-icon small class="mr-1">mdi-clock-outline</v-icon>
                    {{ formatDate(post.created_at) }}
                  </v-list-item-subtitle>
                </template>
              </v-list-item>
            </v-list>

            <!-- Pagination controls -->
            <v-pagination
              v-model="currentPage"
              :length="totalPages"
              :total-visible="7"
              color="primary"
              class="mt-4"
              @update:model-value="handlePageChange"
            ></v-pagination>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';
import UserAvatar from '@/components/UserAvatar.vue';

/**
 * Community View Component
 * Displays a list of community posts with pagination and search functionality
 */
export default {
  components: {
    UserAvatar
  },
  data() {
    return { 
      posts: [],
      loading: false,
      searching: false,
      currentPage: 1,
      itemsPerPage: 10,
      searchQuery: '',
      isSearchActive: false,
      searchType: 'all'
    };
  },
  computed: {
    /**
     * Calculate total number of pages based on posts count
     */
    totalPages() {
      return Math.ceil(this.posts.length / this.itemsPerPage);
    },
    /**
     * Get posts for the current page
     */
    paginatedPosts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.posts.slice(start, end);
    },
    /**
     * Get search placeholder text based on search type
     */
    searchPlaceholder() {
      switch(this.searchType) {
        case 'title':
          return 'Search by post title...';
        case 'author':
          return 'Search by author name...';
        default:
          return 'Search by title or author...';
      }
    },
    /**
     * Get search result text based on search type
     */
    searchResultText() {
      const baseText = 'Search results';
      
      switch(this.searchType) {
        case 'title':
          return `${baseText} for title: <span class="font-weight-bold">${this.searchQuery}</span>`;
        case 'author':
          return `${baseText} for author: <span class="font-weight-bold">${this.searchQuery}</span>`;
        default:
          return `${baseText} for: <span class="font-weight-bold">${this.searchQuery}</span>`;
      }
    }
  },
  watch: {
    // Re-search when search type changes
    searchType() {
      if (this.isSearchActive && this.searchQuery.trim()) {
        this.searchPosts();
      }
    }
  },
  async created() {
    await this.loadPosts();
  },
  methods: {
    /**
     * Load all posts from the API
     */
    async loadPosts() {
      this.loading = true;
      try {
        const response = await axios.get('/api/community/posts/');
        this.posts = response.data;
        this.isSearchActive = false;
      } catch (error) {
        // Error handled silently
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Search posts by title or author
     */
    async searchPosts() {
      if (!this.searchQuery.trim()) {
        return;
      }
      
      this.searching = true;
      this.currentPage = 1; // Reset to first page
      
      try {
        const response = await axios.get('/api/community/posts/search/', {
          params: { 
            query: this.searchQuery.trim(),
            search_type: this.searchType
          }
        });
        
        this.posts = response.data;
        this.isSearchActive = true;
      } catch (error) {
        // Error handled silently
      } finally {
        this.searching = false;
      }
    },
    
    /**
     * Clear search results and return to all posts
     */
    async clearSearch() {
      this.searchQuery = '';
      this.isSearchActive = false;
      await this.loadPosts();
    },
    
    /**
     * Format date to localized string
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date string
     */
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    /**
     * Handle page change and scroll to top
     * @param {number} page - New page number
     */
    handlePageChange(page) {
      this.currentPage = page;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
};
</script>

<style scoped>
/* Background with parallax effect */
.community-container {
  background-image: url('@/assets/commback.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
  margin: 0;
  padding: 0;
}

/* Container sizing */
.v-container {
  margin: 0;
  padding: 0;
  max-width: 100% !important;
}

/* Card styling */
.community-card {
  border-radius: 12px;
  overflow: hidden;
}

/* Search card styling */
.search-card {
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8f8f8;
}

/* Search input styling */
.search-input :deep(.v-field__field) {
  height: 40px;
}

/* Search info styling */
.search-info {
  border-radius: 8px;
  padding: 4px 12px;
  background-color: #e3f2fd;
}

/* Post list container with scroll */
.post-list {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Individual post item styling */
.post-item {
  transition: all 0.3s ease;
  border-bottom: 1px solid #eee;
  margin-bottom: 4px;
}

.post-item:last-child {
  border-bottom: none;
}

/* Hover effect for posts */
.post-item:hover {
  transform: translateX(8px);
  background-color: #f5f5f5;
}

/* Post title styling */
.v-list-item-title {
  color: #333;
  font-weight: 500;
  line-height: 1.4;
}

/* Post subtitle styling */
.v-list-item-subtitle {
  color: #666;
  font-size: 0.9rem;
}

/* Button styling */
.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}

/* Card title styling */
.v-card-title {
  padding: 24px 16px;
  border-bottom: 2px solid #eee;
}

/* Card content styling */
.v-card-text {
  padding: 24px 16px;
}

/* Pagination styling */
.v-pagination {
  justify-content: center;
}

/* Row margin adjustment */
.v-row {
  margin: 0 !important;
}
</style>
