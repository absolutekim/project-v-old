<!-- This file has created but replaced by other files. However, to do not corrupt system, it's being kept. -->
<template>
  <!-- Profile page container -->
  <div class="profile-container">
    <!-- Profile header with user information -->
    <div class="profile-header">
      <h1 class="profile-title">My Profile</h1>
      <!-- User information section (visible when authenticated) -->
      <div v-if="isAuthenticated" class="user-info">
        <p class="username">{{ username }}</p>
        <p class="email">{{ email }}</p>
      </div>
    </div>

    <!-- Login required message for unauthenticated users -->
    <div v-if="!isAuthenticated" class="login-required">
      <p>Tou must be logged in to view profile</p>
      <router-link to="/login" class="login-button">Login</router-link>
    </div>

    <!-- Profile content section (visible when authenticated) -->
    <div v-else class="profile-content">
      <!-- Navigation tabs for likes and reviews -->
      <div class="tabs">
        <button 
          @click="activeTab = 'likes'" 
          :class="['tab-button', { active: activeTab === 'likes' }]"
        >
          <i class="fas fa-heart"></i> Liked Destinations
        </button>
        <button 
          @click="activeTab = 'reviews'" 
          :class="['tab-button', { active: activeTab === 'reviews' }]"
        >
          <i class="fas fa-comment"></i> Your Reviews
        </button>
      </div>

      <!-- Tab content area with component caching -->
      <div class="tab-content">
        <keep-alive>
          <user-likes v-if="activeTab === 'likes'" />
          <user-reviews v-else-if="activeTab === 'reviews'" />
        </keep-alive>
      </div>
    </div>
  </div>
</template>

<script>
import UserLikes from '@/components/UserLikes.vue';
import UserReviews from '@/components/UserReviews.vue';

/**
 * Profile View Component
 * Displays user profile information and manages likes/reviews tabs
 * Features:
 * - User information display
 * - Tabs for liked destinations and user reviews
 * - Authentication-based conditional rendering
 */
export default {
  name: 'ProfileView',
  components: {
    UserLikes, // Component for showing user-liked destinations
    UserReviews // Component for showing user reviews
  },
  data() {
    return {
      activeTab: 'likes' // Currently active tab selection
    };
  },
  computed: {
    /**
     * Check if user is authenticated
     * @returns {boolean} True if user is authenticated
     */
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    },
    
    /**
     * Get current user's username
     * @returns {string} Username of logged in user
     */
    username() {
      return this.$store.getters.username;
    },
    
    /**
     * Get current user's email
     * @returns {string} Email of logged in user
     */
    email() {
      return this.$store.getters.email;
    }
  }
};
</script>

<style scoped>
/* Main container styling */
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* Profile header section with bottom border */
.profile-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

/* Profile title styling */
.profile-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 15px;
}

/* User information container */
.user-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

/* Username styling */
.username {
  font-size: 18px;
  font-weight: 600;
  color: #4a5568;
}

/* Email styling */
.email {
  font-size: 16px;
  color: #718096;
}

/* Login required message container */
.login-required {
  text-align: center;
  padding: 60px 20px;
  background-color: #f8fafc;
  border-radius: 8px;
  color: #718096;
}

/* Login button styling */
.login-button {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #4299e1;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

/* Login button hover state */
.login-button:hover {
  background-color: #3182ce;
}

/* Tabs container with bottom border */
.tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

/* Tab button styling */
.tab-button {
  padding: 12px 20px;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 500;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Tab button hover state */
.tab-button:hover {
  color: #4299e1;
}

/* Active tab styling */
.tab-button.active {
  color: #4299e1;
  border-bottom-color: #4299e1;
}

/* Tab icon styling */
.tab-button i {
  font-size: 14px;
}

/* Tab content container */
.tab-content {
  min-height: 400px;
}

/* Responsive styling for mobile devices */
@media (max-width: 768px) {
  .profile-container {
    padding: 20px 15px;
  }
  
  .profile-title {
    font-size: 24px;
  }
  
  .tabs {
    overflow-x: auto;
  }
  
  .tab-button {
    padding: 10px 15px;
    font-size: 14px;
  }
}
</style> 