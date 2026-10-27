<template>
  <v-dialog
    v-model="showModal"
    max-width="500px"
    @click:outside="close"
  >
    <v-card class="user-profile-modal">
      <!-- Show loading state -->
      <v-progress-linear
        v-if="loading"
        indeterminate
        color="primary"
      ></v-progress-linear>

      <!-- Show error -->
      <v-alert
        v-if="error"
        type="error"
        class="ma-3"
      >
        {{ error }}
      </v-alert>

      <!-- Profile information -->
      <template v-if="!loading && !error && userProfile">
        <v-card-title class="d-flex flex-column align-center pa-4">
          <!-- Profile image -->
          <v-avatar size="120" class="mb-3">
            <v-img
              v-if="userProfile.profile_image"
              :src="userProfile.profile_image"
              alt="User profile image"
              @error="handleImageError"
            ></v-img>
            <v-icon v-else size="80" color="primary">mdi-account</v-icon>
          </v-avatar>
          
          <!-- Username -->
          <h2 class="text-h5 font-weight-bold">{{ userProfile.username }}</h2>
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="pa-4">
          <!-- Personal information -->
          <v-list>
            <!-- Introduction -->
            <v-list-item v-if="userProfile.introduction">
              <template v-slot:prepend>
                <v-icon color="primary">mdi-information</v-icon>
              </template>
              <v-list-item-title>Introduction</v-list-item-title>
              <v-list-item-subtitle>{{ userProfile.introduction }}</v-list-item-subtitle>
            </v-list-item>

            <!-- Gender -->
            <v-list-item v-if="userProfile.gender">
              <template v-slot:prepend>
                <v-icon color="primary">{{ userProfile.gender === 'Male' ? 'mdi-gender-male' : 'mdi-gender-female' }}</v-icon>
              </template>
              <v-list-item-title>Gender</v-list-item-title>
              <v-list-item-subtitle>{{ userProfile.gender }}</v-list-item-subtitle>
            </v-list-item>

            <!-- Age -->
            <v-list-item v-if="userProfile.age">
              <template v-slot:prepend>
                <v-icon color="primary">mdi-cake-variant</v-icon>
              </template>
              <v-list-item-title>Age</v-list-item-title>
              <v-list-item-subtitle>{{ userProfile.age }} years old</v-list-item-subtitle>
            </v-list-item>

            <!-- Join date -->
            <v-list-item v-if="userProfile.date_joined">
              <template v-slot:prepend>
                <v-icon color="primary">mdi-calendar</v-icon>
              </template>
              <v-list-item-title>Join date</v-list-item-title>
              <v-list-item-subtitle>{{ formatDate(userProfile.date_joined) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn 
            color="primary" 
            variant="tonal"
            @click="close"
          >
            Close
          </v-btn>
        </v-card-actions>
      </template>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserProfileModal',
  props: {
    /**
     * Username
     */
    username: {
      type: String,
      required: true
    },
    /**
     * Show modal
     */
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      userProfile: null,
      loading: false,
      error: null,
      imageError: false
    };
  },
  computed: {
    /**
     * Show modal state getter/setter
     */
    showModal: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    }
  },
  watch: {
    /**
     * When the modal opens, get user information
     */
    modelValue(newVal) {
      if (newVal && this.username) {
        this.fetchUserProfile();
      }
    },
    /**
     * When the user changes, get the information again
     */
    username(newVal) {
      if (this.modelValue && newVal) {
        this.fetchUserProfile();
      }
    }
  },
  methods: {
    /**
     * Get user profile information
     */
    async fetchUserProfile() {
      if (!this.username) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:8000/api/accounts/profile/${this.username}/`);
        this.userProfile = response.data;
      } catch (error) {
        this.error = 'Failed to get user information. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Handle image loading error
     */
    handleImageError() {
      this.imageError = true;
    },
    
    /**
     * Format date
     */
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    /**
     * Close modal
     */
    close() {
      this.showModal = false;
    }
  }
};
</script>

<style scoped>
.user-profile-modal {
  border-radius: 8px;
  overflow: hidden;
}
</style> 