<template>
  <div class="achievements-container">
    <!-- Show loading state -->
    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <div class="mt-3">Loading achievement information...</div>
    </div>
    
    <!-- Show error message -->
    <div v-else-if="error" class="error-container pa-4 text-center">
      <v-icon color="error" size="48">mdi-alert-circle</v-icon>
      <p class="text-body-1 mt-2">{{ error }}</p>
      <v-btn color="primary" @click="fetchAchievements" class="mt-3">
        Try again
      </v-btn>
    </div>
    
    <!-- Show achievement data -->
    <div v-else>
      <!-- Show achievement progress -->
      <div class="achievement-progress mb-6">
        <v-card outlined class="pa-4">
          <div class="d-flex justify-space-between align-center mb-2">
            <div class="text-h6">Achievement Progress</div>
            <div class="text-subtitle-1">{{ achievementCount }} / {{ totalAchievements }} ({{ achievementPercentage }}%)</div>
          </div>
          <v-progress-linear
            :value="achievementPercentage"
            height="20"
            color="primary"
            striped
            rounded
          >
            <template v-slot:default>
              <strong>{{ achievementPercentage }}%</strong>
            </template>
          </v-progress-linear>
        </v-card>
      </div>
      
      <!-- Check new achievements button -->
      <div class="text-right mb-4">
        <v-btn 
          color="primary" 
          outlined 
          @click="checkNewAchievements"
          :loading="checkingNew"
          prepend-icon="mdi-refresh"
        >
          Check New Achievements
        </v-btn>
      </div>
      
      <!-- New achievement notification -->
      <v-expand-transition>
        <v-alert
          v-if="newAchievements.length > 0"
          type="success"
          prominent
          class="mb-4"
        >
          <div class="text-subtitle-1 font-weight-bold mb-2">New achievements earned!</div>
          <div class="d-flex flex-wrap">
            <v-chip
              v-for="achievement in newAchievements"
              :key="achievement.id"
              class="ma-1"
              color="success"
              outlined
              prepend-icon="mdi-trophy"
            >
              {{ achievement.name }}
            </v-chip>
          </div>
        </v-alert>
      </v-expand-transition>
      
      <!-- Show achievements by category -->
      <v-tabs v-model="activeCategory" show-arrows background-color="primary" dark slider-color="yellow">
        <v-tab v-for="(category, key) in categories" :key="key" :value="key">
          <v-icon left>{{ getCategoryIcon(key) }}</v-icon>
          {{ category.name }}
        </v-tab>
      </v-tabs>
      
      <v-window v-model="activeCategory" class="mt-4">
        <v-window-item
          v-for="(category, key) in categories"
          :key="key"
          :value="key"
        >
          <!-- Achievements list within category -->
          <v-card v-if="category.achievements.length" flat>
            <v-row>
              <v-col
                v-for="achievement in category.achievements"
                :key="achievement.achievement_type"
                cols="12"
                md="6"
                sm="6"
              >
                <v-card
                  :class="[
                    'achievement-card pa-3 d-flex flex-column',
                    {'achievement-earned': achievement.earned, 'achievement-locked': !achievement.earned}
                  ]"
                  outlined
                  :elevation="achievement.earned ? 2 : 0"
                >
                  <div class="d-flex align-center">
                    <v-avatar
                      :color="achievement.earned ? 'primary' : 'grey lighten-1'"
                      size="48"
                      class="mr-3"
                    >
                      <v-icon color="white">mdi-{{ achievement.icon }}</v-icon>
                    </v-avatar>
                    <div class="flex-grow-1">
                      <div class="d-flex justify-space-between align-center">
                        <div class="text-h6">{{ achievement.name }}</div>
                        <v-icon v-if="achievement.earned" color="success">mdi-check-circle</v-icon>
                        <v-icon v-else color="grey lighten-1">mdi-lock</v-icon>
                      </div>
                      <div class="text-body-2 mt-1">{{ achievement.description }}</div>
                    </div>
                  </div>
                  
                  <div v-if="achievement.earned" class="achievement-date mt-2 text-right">
                    <span class="text-caption text-grey">
                      {{ formatDate(achievement.earned_at) }} earned
                    </span>
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card>
          
          <!-- No achievements case -->
          <v-card v-else flat class="pa-5 text-center grey lighten-4">
            <v-icon color="grey" size="48">mdi-trophy-variant-outline</v-icon>
            <div class="mt-2 text-body-1">No achievements in this category.</div>
          </v-card>
        </v-window-item>
      </v-window>
    </div>
    
    <!-- Achievement details dialog -->
    <v-dialog v-model="achievementDialog" max-width="500">
      <v-card v-if="selectedAchievement">
        <v-card-title :class="selectedAchievement.earned ? 'primary white--text' : 'grey lighten-3'">
          <v-icon left :color="selectedAchievement.earned ? 'white' : 'grey darken-1'">
            mdi-{{ selectedAchievement.icon }}
          </v-icon>
          {{ selectedAchievement.name }}
        </v-card-title>
        <v-card-text class="pa-4">
          <p class="text-body-1">{{ selectedAchievement.description }}</p>
          
          <div v-if="selectedAchievement.earned" class="mt-4 d-flex align-center">
            <v-icon color="success" class="mr-2">mdi-check-circle</v-icon>
            <span>{{ formatDate(selectedAchievement.earned_at) }} earned</span>
          </div>
          <div v-else class="mt-4 d-flex align-center">
            <v-icon color="grey" class="mr-2">mdi-lock</v-icon>
            <span>Not yet earned</span>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="achievementDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import { format } from 'date-fns';
import { en } from 'date-fns/locale';

/**
 * User achievements component
 * Displays user achievements and available achievements by category.
 */
export default {
  name: 'UserAchievements',
  
  data() {
    return {
      // Data loading state
      loading: true,
      error: null,
      
      // Achievement data
      categories: {},
      achievementCount: 0,
      totalAchievements: 0,
      achievementPercentage: 0,
      newAchievements: [],
      checkingNew: false,
      
      // UI state
      activeCategory: 'basics',
      achievementDialog: false,
      selectedAchievement: null
    }
  },
  
  methods: {
    /**
     * Get all user achievements
     * @returns {Promise} Achievement list and statistics data
     */
    async getUserAchievements() {
      try {
        const response = await axios.get('/api/mypage/achievements/');
        return response.data;
      } catch (error) {
        console.error('Failed to get achievement list:', error);
        throw error;
      }
    },

    /**
     * Get specific achievement details
     * @param {number} achievementId - Achievement ID
     * @returns {Promise} Achievement details
     */
    async getAchievementDetail(achievementId) {
      try {
        const response = await axios.get(`/api/mypage/achievements/${achievementId}/`);
        return response.data;
      } catch (error) {
        console.error('Failed to get achievement details:', error);
        throw error;
      }
    },

    /**
     * Get all available achievements
     * Includes both earned and unearned achievements.
     * @returns {Promise} Achievement list and statistics data
     */
    async getAvailableAchievements() {
      try {
        const response = await axios.get('/api/mypage/achievements/available/');
        return response.data;
      } catch (error) {
        console.error('Failed to get available achievements:', error);
        throw error;
      }
    },

    /**
     * Get achievements categorized by category
     * @returns {Promise} Category-based achievement data
     */
    async getAchievementsByCategory() {
      try {
        const response = await axios.get('/api/mypage/achievements/by-category/');
        return response.data;
      } catch (error) {
        console.error('Failed to get achievements by category:', error);
        throw error;
      }
    },
    
    /**
     * Get achievement data
     */
    async fetchAchievements() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await this.getAvailableAchievements();
        this.categories = response.categories;
        this.achievementCount = response.earned_count;
        this.totalAchievements = response.total_count;
        this.achievementPercentage = response.percentage;
        
        // If categories exist, set first category
        if (Object.keys(this.categories).length > 0) {
          this.activeCategory = Object.keys(this.categories)[0];
        }
      } catch (error) {
        console.error('Failed to get achievement data:', error);
        this.error = 'Failed to load achievement data. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Check if new achievements have been earned
     * If new achievements are earned, automatically create them
     */
    async checkNewAchievements() {
      this.checkingNew = true;
      
      try {
        const response = await axios.get('/api/mypage/achievements/check-new/');
        
        // If new achievements exist, display them
        if (response.data.new_achievements && response.data.new_achievements.length > 0) {
          this.newAchievements = response.data.new_achievements;
          
          // Display toast message
          this.$emit('achievement-earned', response.data.new_achievements);
          
          // Reload data
          await this.fetchAchievements();
        } else {
          // No new achievements
          this.newAchievements = [];
          
          // Display toast message
          this.$emit('no-new-achievements');
        }
      } catch (error) {
        console.error('Failed to check new achievements:', error);
        this.$emit('achievement-error', 'Failed to check new achievements.');
      } finally {
        this.checkingNew = false;
      }
    },
    
    /**
     * Return icon based on achievement category
     * @param {string} category - Achievement category
     * @returns {string} Icon name
     */
    getCategoryIcon(category) {
      const icons = {
        basics: 'trophy',
        content: 'pencil',
        engagement: 'heart',
        profile: 'account',
        time: 'clock',
        misc: 'star'
      };
      
      return icons[category] || 'trophy';
    },
    
    /**
     * Format date
     * @param {string} dateString - ISO format date string
     * @returns {string} Formatted date
     */
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        return format(new Date(dateString), 'yyyy-MM-dd', { locale: en });
      } catch (error) {
        return dateString;
      }
    },
    
    /**
     * Select achievement to display details
     * @param {Object} achievement - Achievement object
     */
    selectAchievement(achievement) {
      this.selectedAchievement = achievement;
      this.achievementDialog = true;
    }
  },
  
  created() {
    // Load achievement data when component is created
    this.fetchAchievements();
  }
}
</script>

<style scoped>
.achievements-container {
  padding-bottom: 20px;
}

.achievement-card {
  height: 100%;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.achievement-earned {
  border-color: #1976d2;
}

.achievement-earned:hover {
  box-shadow: 0 4px 8px rgba(25, 118, 210, 0.2) !important;
  transform: translateY(-2px);
}

.achievement-locked {
  background-color: #f5f5f5;
  opacity: 0.7;
}

.achievement-date {
  margin-top: auto;
}

.error-container {
  border: 1px dashed #f44336;
  border-radius: 8px;
  background-color: #ffebee;
}

/* Media query for responsive design */
@media (max-width: 600px) {
  .achievement-card {
    padding: 12px !important;
  }
  
  .v-avatar {
    size: 36px !important;
  }
}
</style> 