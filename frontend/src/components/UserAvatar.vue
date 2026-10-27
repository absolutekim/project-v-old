<template>
  <div>
    <div class="user-avatar-wrapper d-inline-flex align-center" @click="showUserProfile">
      <v-avatar :size="size" class="user-avatar" :class="{ 'clickable': clickable }">
        <v-img
          v-if="profileImage"
          :src="getProfileImageUrl(profileImage)"
          :alt="`${username}'s avatar`"
          @error="handleImageError"
        >
          <template v-slot:placeholder>
            <v-row class="fill-height ma-0" align="center" justify="center">
              <v-progress-circular indeterminate color="primary" size="24"></v-progress-circular>
            </v-row>
          </template>
        </v-img>
        <v-icon v-else :size="size * 0.7" color="primary">mdi-account</v-icon>
      </v-avatar>
      <span v-if="showUsername" class="username ml-2 text-body-2">{{ username }}</span>
    </div>
    
    <!-- User profile modal -->
    <user-profile-modal 
      v-model="profileModalOpen" 
      :username="username"
    />
  </div>
</template>

<script>
import UserProfileModal from './UserProfileModal.vue';

/**
 * User Avatar Component
 * Displays a user's avatar with optional username text
 * Handles missing or invalid profile images gracefully
 */
export default {
  name: 'UserAvatar',
  components: {
    UserProfileModal
  },
  props: {
    /**
     * Username to display
     */
    username: {
      type: String,
      required: true
    },
    /**
     * Profile image URL or path
     */
    profileImage: {
      type: String,
      default: null
    },
    /**
     * Avatar size in pixels
     */
    size: {
      type: Number,
      default: 40
    },
    /**
     * Whether to show the username next to the avatar
     */
    showUsername: {
      type: Boolean,
      default: false
    },
    /**
     * Whether the avatar is clickable to show profile
     */
    clickable: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      imageError: false,
      profileModalOpen: false
    };
  },
  methods: {
    /**
     * Get the full profile image URL
     * @param {string} imageUrl - Profile image path
     * @returns {string} Full URL for the profile image
     */
    getProfileImageUrl(imageUrl) {
      if (!imageUrl) return null;
      
      // Handle already complete URLs
      if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
        return imageUrl;
      }
      
      // Handle relative URLs by prepending the backend URL
      return `http://localhost:8000${imageUrl}`;
    },
    
    /**
     * Handle image loading errors
     * Shows the default user icon if image fails to load
     */
    handleImageError() {
      this.imageError = true;
      console.warn(`Failed to load profile image for user: ${this.username}`);
    },
    
    /**
     * Show user profile modal
     */
    showUserProfile() {
      if (this.clickable) {
        this.profileModalOpen = true;
      }
    }
  }
};
</script>

<style scoped>
.user-avatar {
  position: relative;
  background-color: #f0f0f0;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.user-avatar.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.user-avatar.clickable:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.username {
  font-weight: 500;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 