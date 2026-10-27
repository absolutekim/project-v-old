<template>
  <!-- User profile page container -->
  <v-container class="mypage">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <!-- Profile information card -->
        <v-card class="mx-auto" elevation="3">
          <v-card-title class="text-h4 font-weight-bold text-center py-6 primary white--text">
            My Page
          </v-card-title>

          <v-card-text v-if="profile" class="pa-6">
            <v-row>
              <!-- Profile image section -->
              <v-col cols="12" sm="4" class="text-center">
                <v-avatar size="200" class="profile-avatar">
                  <v-img
                    :src="getProfileImageUrl(profile.profile_image)"
                    alt="Profile Image"
                    @error="handleImageError"
                  >
                    <template v-slot:placeholder>
                      <v-row class="fill-height ma-0" align="center" justify="center">
                        <v-progress-circular indeterminate color="primary"></v-progress-circular>
                      </v-row>
                    </template>
                  </v-img>
                </v-avatar>
              </v-col>

              <!-- Profile information section -->
              <v-col cols="12" sm="8">
                <div v-if="!isEditing">
                  <h2 class="text-h5 font-weight-bold mb-4">
                    {{ profile.nickname || profile.user.username }}
                  </h2>
                  <v-card outlined class="pa-4 mb-4 bio-card">
                    <p class="text-body-1">{{ profile.bio || 'No introduction available.' }}</p>
                  </v-card>
                  
                  <!-- User Info Cards -->
                  <v-row class="mb-4">
                    <!-- Age Group Card -->
                    <v-col cols="12" sm="6">
                      <v-card outlined class="info-card" :class="{'info-card-empty': !profile.user.age_group}">
                        <div class="d-flex align-center">
                          <v-avatar color="primary" size="36" class="mr-3">
                            <v-icon color="white">mdi-calendar-account</v-icon>
                          </v-avatar>
                          <div>
                            <div class="caption grey--text text--darken-1">Age Group</div>
                            <div class="subtitle-1 font-weight-medium">
                              {{ getAgeGroupText(profile.user.age_group) || 'Not specified' }}
                            </div>
                          </div>
                        </div>
                      </v-card>
                    </v-col>
                    
                    <!-- Gender Card -->
                    <v-col cols="12" sm="6">
                      <v-card outlined class="info-card" :class="{'info-card-empty': !profile.user.gender}">
                        <div class="d-flex align-center">
                          <v-avatar :color="profile.user.gender === 'M' ? 'blue' : profile.user.gender === 'F' ? 'pink' : 'grey'" size="36" class="mr-3">
                            <v-icon color="white">{{ profile.user.gender === 'M' ? 'mdi-gender-male' : profile.user.gender === 'F' ? 'mdi-gender-female' : 'mdi-gender-non-binary' }}</v-icon>
                          </v-avatar>
                          <div>
                            <div class="caption grey--text text--darken-1">Gender</div>
                            <div class="subtitle-1 font-weight-medium">
                              {{ getGenderText(profile.user.gender) || 'Not specified' }}
                            </div>
                          </div>
                        </div>
                      </v-card>
                    </v-col>
                  </v-row>
                  
                  <v-btn
                    color="primary"
                    @click="startEditing"
                    prepend-icon="mdi-account-edit"
                    class="mr-2"
                  >
                    Modify Profile
                  </v-btn>
                  <v-btn
                    color="error"
                    @click="showDeleteAccountDialog"
                    prepend-icon="mdi-account-remove"
                  >
                    Delete Account
                  </v-btn>
                </div>

                <!-- Profile edit form -->
                <v-form v-else ref="profileForm" @submit.prevent="updateProfile">
                  <v-tabs v-model="activeEditTab" background-color="primary" dark class="mb-4">
                    <v-tab value="profile">
                      <v-icon left>mdi-account-edit</v-icon>
                      Profile Information
                    </v-tab>
                    <v-tab value="password">
                      <v-icon left>mdi-lock-reset</v-icon>
                      Change Password
                    </v-tab>
                  </v-tabs>
                  
                  <v-window v-model="activeEditTab">
                    <!-- Profile Info Tab -->
                    <v-window-item value="profile">
                      <v-text-field
                        v-model="editForm.nickname"
                        label="Nickname"
                        outlined
                        dense
                        class="mb-4"
                        :error-messages="nicknameErrors"
                        counter="30"
                        @input="validateNickname"
                      />
                      
                      <v-textarea
                        v-model="editForm.bio"
                        label="Introduction"
                        outlined
                        auto-grow
                        rows="4"
                        class="mb-4"
                      />

                      <!-- User Info Edit Section -->
                      <v-card outlined class="mb-4 pa-4">
                        <v-card-title class="text-subtitle-1 pa-0 pb-2">Personal Information</v-card-title>
                        
                        <!-- Age Group Selection -->
                        <v-select
                          v-model="editForm.age_group"
                          label="Age Group"
                          outlined
                          dense
                          :items="ageGroupOptions"
                          item-title="text"
                          item-value="value"
                          prepend-icon="mdi-calendar-account"
                          class="mb-4"
                          return-object
                        >
                        </v-select>

                        <!-- Gender Selection -->
                        <v-radio-group
                          v-model="editForm.gender"
                          row
                          class="mt-0"
                        >
                          <template v-slot:label>
                            <div class="d-flex align-center">
                              <v-icon class="mr-2">mdi-gender-male-female</v-icon>
                              <span>Gender</span>
                            </div>
                          </template>
                          <v-radio
                            label="Male"
                            value="M"
                            color="blue"
                          >
                            <template v-slot:label>
                              <div class="d-flex align-center">
                                <v-icon color="blue" class="mr-1">mdi-gender-male</v-icon>
                                <span>Male</span>
                              </div>
                            </template>
                          </v-radio>
                          <v-radio
                            label="Female"
                            value="F"
                            color="pink"
                          >
                            <template v-slot:label>
                              <div class="d-flex align-center">
                                <v-icon color="pink" class="mr-1">mdi-gender-female</v-icon>
                                <span>Female</span>
                              </div>
                            </template>
                          </v-radio>
                        </v-radio-group>
                      </v-card>

                      <v-file-input
                        v-model="editForm.profile_image"
                        label="Profile Image"
                        prepend-icon="mdi-camera"
                        outlined
                        dense
                        accept="image/*"
                        class="mb-4"
                      />
                    </v-window-item>
                    
                    <!-- Password Change Tab -->
                    <v-window-item value="password">
                      <v-alert
                        v-if="passwordChangeMessage.text"
                        :type="passwordChangeMessage.type"
                        class="mb-4"
                        dismissible
                      >
                        {{ passwordChangeMessage.text }}
                      </v-alert>
                      
                      <v-form ref="passwordForm" @submit.prevent="changePassword">
                        <v-text-field
                          v-model="passwordForm.old_password"
                          label="Current Password"
                          type="password"
                          outlined
                          dense
                          class="mb-4"
                          :error-messages="passwordErrors.old_password"
                          required
                        />
                        
                        <v-text-field
                          v-model="passwordForm.new_password"
                          label="New Password"
                          type="password"
                          outlined
                          dense
                          class="mb-4"
                          :error-messages="passwordErrors.new_password"
                          hint="Enter a password of at least 8 characters"
                          required
                        />
                        
                        <v-text-field
                          v-model="passwordForm.confirm_password"
                          label="Confirm New Password"
                          type="password"
                          outlined
                          dense
                          class="mb-4"
                          :error-messages="passwordErrors.confirm_password"
                          required
                        />
                        
                        <v-btn
                          color="primary"
                          type="submit"
                          class="mr-2"
                          :loading="isChangingPassword"
                        >
                          Change Password
                        </v-btn>
                      </v-form>
                    </v-window-item>
                  </v-window>
                  
                  <div class="mt-4">
                    <v-btn
                      v-if="activeEditTab === 'profile'"
                      color="primary"
                      type="submit"
                      class="mr-4"
                      prepend-icon="mdi-content-save"
                      :disabled="!!nicknameErrors"
                    >
                      Save
                    </v-btn>
                    <v-btn
                      color="grey"
                      @click="cancelEditing"
                      prepend-icon="mdi-close"
                    >
                      Cancel
                    </v-btn>
                  </div>
                </v-form>
              </v-col>
            </v-row>
          </v-card-text>

          <!-- Loading state indicator -->
          <v-card-text v-else class="text-center pa-6">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
            />
          </v-card-text>
        </v-card>

        <!-- Likes and reviews tabs -->
        <v-card class="mx-auto mt-6" elevation="3">
          <v-tabs v-model="activeTab" background-color="primary" dark>
            <v-tab value="likes">
              <v-icon left>mdi-heart</v-icon>
              Liked Destinations
            </v-tab>
            <v-tab value="reviews">
              <v-icon left>mdi-comment</v-icon>
              Your Reviews
            </v-tab>
            <v-tab value="posts">
              <v-icon left>mdi-file-document</v-icon>
              Your Posts
            </v-tab>
            <v-tab value="comments">
              <v-icon left>mdi-comment-text</v-icon>
              Your Comments
            </v-tab>
            <v-tab value="achievements">
              <v-icon left>mdi-trophy</v-icon>
              Your Achievements
            </v-tab>
          </v-tabs>

          <v-card-text class="pa-0">
            <v-window v-model="activeTab">
              <!-- Liked destinations tab content -->
              <v-window-item value="likes">
                <div class="pa-4">
                  <user-likes />
                </div>
              </v-window-item>

              <!-- User reviews tab content -->
              <v-window-item value="reviews">
                <div class="pa-4">
                  <user-reviews />
                </div>
              </v-window-item>
              
              <!-- User posts tab content -->
              <v-window-item value="posts">
                <div class="pa-4">
                  <user-posts />
                </div>
              </v-window-item>
              
              <!-- User comments tab content -->
              <v-window-item value="comments">
                <div class="pa-4">
                  <user-comments />
                </div>
              </v-window-item>
              
              <!-- User achievements tab content -->
              <v-window-item value="achievements">
                <div class="pa-4">
                  <user-achievements @achievement-earned="showAchievementEarnedMessage" @no-new-achievements="showNoNewAchievementsMessage" @achievement-error="showAchievementErrorMessage" />
                </div>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>

        <!-- Account deletion confirmation dialog -->
        <v-dialog v-model="deleteAccountDialog" max-width="500">
          <v-card>
            <v-card-title class="text-h5 error white--text">
              Delete Account
            </v-card-title>
            <v-card-text class="pt-4">
              <p class="mb-4">If you delete your account, all data will be permanently deleted and cannot be recovered. Are you sure you want to delete it?</p>
              <v-form @submit.prevent="deleteAccount">
                <v-text-field
                  v-model="deleteAccountPassword"
                  label="Confirm Password"
                  type="password"
                  outlined
                  dense
                  :error-messages="deleteAccountError"
                  required
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey" text @click="deleteAccountDialog = false">
                Cancel
              </v-btn>
              <v-btn color="error" @click="deleteAccount" :loading="isDeleting">
                Delete Account
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        
        <!-- Achievement success snackbar -->
        <v-snackbar
          v-model="showAchievementSnackbar"
          :color="achievementSnackbarColor"
          :timeout="5000"
          bottom
          right
        >
          {{ achievementSnackbarText }}
          <template v-slot:action="{ attrs }">
            <v-btn
              text
              v-bind="attrs"
              @click="showAchievementSnackbar = false"
            >
              Close
            </v-btn>
          </template>
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
import UserLikes from '@/components/UserLikes.vue'
import UserReviews from '@/components/UserReviews.vue'
import UserPosts from '@/components/UserPosts.vue'
import UserComments from '@/components/UserComments.vue'
import UserAchievements from '@/components/UserAchievements.vue'

/**
 * User Profile Page Component
 * Displays and manages the user's profile information and activities
 * Features:
 * - Profile information display
 * - Profile editing
 * - Profile image upload
 * - Account deletion
 * - Tabs for liked destinations, user reviews, posts, comments, and achievements
 */
export default {
  name: 'MyPage',
  components: {
    UserLikes,
    UserReviews,
    UserPosts,
    UserComments,
    UserAchievements
  },
  data() {
    return {
      profile: null, // User profile data
      isEditing: false, // Profile editing mode flag
      deleteAccountDialog: false, // Delete account confirmation dialog visibility
      confirmEmail: '', // Email confirmation for account deletion
      deleteError: null, // Account deletion error message
      activeTab: 'likes', // Active tab in the tabs section
      activeEditTab: 'profile', // Active tab in the edit form
      // Edit form data fields
      editForm: {
        nickname: '',
        bio: '',
        profile_image: null,
        age_group: '',
        gender: ''
      },
      // Age group options for dropdown
      ageGroupOptions: [
        { text: "Under 18", value: "under18" },
        { text: "18-24", value: "18to24" },
        { text: "25-34", value: "25to34" },
        { text: "35-44", value: "35to44" },
        { text: "45-54", value: "45to54" },
        { text: "55-64", value: "55to64" },
        { text: "65 and Above", value: "65plus" }
      ],
      deleteAccountPassword: '', // Password confirmation for account deletion
      deleteAccountError: '', // Error message for account deletion
      isDeleting: false, // Account deletion loading state
      
      // Password change form
      passwordForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      passwordErrors: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      isChangingPassword: false,
      passwordChangeMessage: {
        text: '',
        type: 'success'
      },
      
      // Nickname validation
      nicknameErrors: '',
      
      // Achievement related state
      showAchievementSnackbar: false,
      achievementSnackbarText: '',
      achievementSnackbarColor: 'success'
    }
  },
  methods: {
    /**
     * Get readable text for age group value
     */
    getAgeGroupText(ageGroupValue) {
      if (!ageGroupValue) return null;
      const found = this.ageGroupOptions.find(opt => opt.value === ageGroupValue);
      return found ? found.text : ageGroupValue;
    },
    
    /**
     * Get readable text for gender value
     */
    getGenderText(genderValue) {
      if (!genderValue) return null;
      return genderValue === 'M' ? 'Male' : genderValue === 'F' ? 'Female' : genderValue;
    },
    
    /**
     * Get proper URL for profile image
     * @param {String} imagePath - The image path from the API
     */
    getProfileImageUrl(imagePath) {
      if (!imagePath) {
        const defaultAvatar = `https://ui-avatars.com/api/?name=${this.profile.user.username}&background=random&size=200`;
        return defaultAvatar;
      }
      
      // Check if the image path starts with http or https
      if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
      }
      
      // Handle case where image is stored in the old directory structure
      // This is a temporary fix - eventually all images should be in the media directory
      const baseUrl = process.env.VUE_APP_API_URL || 'http://localhost:8000';
      let normalizedPath = '';
      
      // Check if the path already includes /media/
      if (imagePath.includes('/media/')) {
        normalizedPath = imagePath;
      } else if (imagePath.startsWith('/')) {
        // Prepend /media if needed
        normalizedPath = `/media${imagePath}`;
      } else {
        // Handle paths like profile_images/image.jpg
        normalizedPath = `/media/${imagePath}`;
      }
      
      const fullUrl = `${baseUrl}${normalizedPath}`;
      return fullUrl;
    },
    
    /**
     * Fetch user profile data from API
     * Loads the current user's profile information
     */
    async fetchProfile() {
      try {
        const response = await axios.get('/api/mypage/profile/')
        this.profile = response.data
      } catch (error) {
        // Failed to load profile
      }
    },
    
    /**
     * Begin profile editing mode
     * Populates the edit form with current profile data
     */
    startEditing() {
      // Find the age group option that matches the user's value
      const ageOption = this.ageGroupOptions.find(option => 
        option.value === this.profile.user.age_group
      ) || '';
      
      this.editForm = {
        nickname: this.profile.nickname,
        bio: this.profile.bio,
        age_group: ageOption,
        gender: this.profile.user.gender || ''
      }
      
      // Reset password form and error messages
      this.passwordForm = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
      this.passwordErrors = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
      this.passwordChangeMessage = {
        text: '',
        type: 'success'
      }
      
      // Reset validation errors
      this.nicknameErrors = '';
      
      this.activeEditTab = 'profile';
      this.isEditing = true
    },
    
    /**
     * Cancel profile editing mode
     * Reverts to display mode without saving changes
     */
    cancelEditing() {
      this.isEditing = false
    },
    
    /**
     * Validate nickname input
     * Checks for empty input and max length
     */
    validateNickname() {
      this.nicknameErrors = '';
      
      if (!this.editForm.nickname || this.editForm.nickname.trim() === '') {
        this.nicknameErrors = 'Please enter a nickname.';
        return false;
      }
      
      if (this.editForm.nickname.length > 30) {
        this.nicknameErrors = 'Nickname cannot exceed 30 characters.';
        return false;
      }
      
      return true;
    },
    
    /**
     * Handle profile image file selection
     * @param {Event} event - Input change event with selected file
     */
    handleImageChange(event) {
      this.editForm.profile_image = event.target.files[0]
    },
    
    /**
     * Update profile information
     * Saves changes to nickname, bio, and profile image
     */
    async updateProfile() {
      // Validate nickname before submission
      if (!this.validateNickname()) {
        return;
      }
      
      try {
        // Extract age group value from the object
        const ageGroupValue = this.editForm.age_group && this.editForm.age_group.value ? 
          this.editForm.age_group.value : '';
        
        const formData = new FormData()
        formData.append('nickname', this.editForm.nickname)
        formData.append('bio', this.editForm.bio)
        formData.append('age_group', ageGroupValue)
        formData.append('gender', this.editForm.gender)
        
        if (this.editForm.profile_image) {
          formData.append('profile_image', this.editForm.profile_image)
        }

        await axios.put('/api/mypage/profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        await this.fetchProfile()
        this.isEditing = false
      } catch (error) {
        console.error('Failed to update profile:', error)
      }
    },
    
    /**
     * Change user password
     * Validates and submits password change request
     */
    async changePassword() {
      // Reset error messages
      this.passwordErrors = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      };
      this.passwordChangeMessage = {
        text: '',
        type: 'success'
      };
      
      // Validate form fields
      let isValid = true;
      
      if (!this.passwordForm.old_password) {
        this.passwordErrors.old_password = 'Please enter your current password.';
        isValid = false;
      }
      
      if (!this.passwordForm.new_password) {
        this.passwordErrors.new_password = 'Please enter a new password.';
        isValid = false;
      } else if (this.passwordForm.new_password.length < 8) {
        this.passwordErrors.new_password = 'Password must be at least 8 characters long.';
        isValid = false;
      }
      
      if (!this.passwordForm.confirm_password) {
        this.passwordErrors.confirm_password = 'Please enter your new password again.';
        isValid = false;
      } else if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
        this.passwordErrors.confirm_password = 'New Password and Confirmation Password do not match.';
        isValid = false;
      }
      
      if (!isValid) {
        return;
      }
      
      this.isChangingPassword = true;
      
      try {
        const response = await axios.post('/api/mypage/change-password/', this.passwordForm);
        
        // Show success message
        this.passwordChangeMessage = {
          text: response.data.message || 'Password changed successfully.',
          type: 'success'
        };
        
        // Reset form
        this.passwordForm = {
          old_password: '',
          new_password: '',
          confirm_password: ''
        };
      } catch (error) {
        // Show error message
        this.passwordChangeMessage = {
          text: error.response?.data?.error || 'An error occurred while changing the password.',
          type: 'error'
        };
      } finally {
        this.isChangingPassword = false;
      }
    },
    
    /**
     * Show account deletion confirmation dialog
     * Resets error messages and password field
     */
    showDeleteAccountDialog() {
      this.deleteAccountDialog = true
      this.deleteAccountPassword = ''
      this.deleteAccountError = ''
    },
    
    /**
     * Delete user account
     * Requires password confirmation for security
     */
    async deleteAccount() {
      if (!this.deleteAccountPassword) {
        this.deleteAccountError = 'Please enter your password.'
        return
      }
      
      this.isDeleting = true
      
      try {
        await axios.delete('/api/accounts/delete-account/', {
          data: {
            password: this.deleteAccountPassword
          }
        })
        
        // Clear browser local storage data
        // 1. Delete authentication related data
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // 2. Delete visited history and recommendation related local storage data
        localStorage.removeItem('recently_viewed')
        localStorage.removeItem('saved_destinations')
        localStorage.removeItem('search_history')
        localStorage.removeItem('destination_recommendations')
        
        // 3. Delete session storage data
        sessionStorage.clear()
        
        // 4. Delete cookies (if needed)
        document.cookie.split(";").forEach(function(c) {
          document.cookie = c.replace(/^ +/, "")
            .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        
        // 5. Initialize shopping cart and other states (if needed)
        // ... other local data initialization code ...
        
        // Delete authentication information from API headers
        delete axios.defaults.headers.common['Authorization']
        
        // Trigger auth state change event
        document.dispatchEvent(new Event('auth-changed'))
        
        // Notify the user
        alert('Your account has been successfully deleted.')
        
        // Refresh the page and redirect to home
        window.location.href = '/'
      } catch (error) {
        if (error.response && error.response.data && error.response.data.error) {
          this.deleteAccountError = error.response.data.error
        } else {
          this.deleteAccountError = 'An error occurred while deleting your account.'
        }
      } finally {
        this.isDeleting = false
      }
    },
    
    /**
     * Handle image loading error
     */
    handleImageError() {
      // If image fails to load, try a fallback
      if (this.profile.profile_image) {
        // Mark the current path as invalid
        // We could implement additional fallback logic here if needed
      }
    },
    
    /**
     * Display a notification message when a new achievement is earned
     * @param {Array} achievements - List of earned achievements
     */
    showAchievementEarnedMessage(achievements) {
      if (achievements && achievements.length > 0) {
        // Display the name of the first achievement
        const achievementName = achievements[0].name;
        this.achievementSnackbarText = achievements.length > 1 
          ? `"${achievementName}" and ${achievements.length - 1} other achievements earned!` 
          : `"${achievementName}" achievement earned!`;
        this.achievementSnackbarColor = 'success';
        this.showAchievementSnackbar = true;
        
        // Automatically switch to the achievements tab
        this.activeTab = 'achievements';
      }
    },
    
    /**
     * Display a message when there are no new achievements
     */
    showNoNewAchievementsMessage() {
      this.achievementSnackbarText = 'No new achievements.';
      this.achievementSnackbarColor = 'info';
      this.showAchievementSnackbar = true;
    },
    
    /**
     * Display a message when an error occurs while checking achievements
     * @param {String} errorMessage - Error message
     */
    showAchievementErrorMessage(errorMessage) {
      this.achievementSnackbarText = errorMessage || 'An error occurred while checking achievements.';
      this.achievementSnackbarColor = 'error';
      this.showAchievementSnackbar = true;
    }
  },
  created() {
    this.fetchProfile()
  }
}
</script>

<style scoped>
/* Main container styling */
.mypage {
  padding-top: 40px;
  padding-bottom: 40px;
}

/* Profile avatar styling with border and shadow */
.profile-avatar {
  border: 4px solid #1976d2;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Bio card background styling */
.bio-card {
  background-color: #f5f5f5;
  min-height: 100px;
}

/* User info cards styling */
.info-card {
  padding: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.info-card:hover {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.info-card-empty {
  background-color: #f5f5f5;
  border: 1px dashed #bdbdbd;
}

/* Card styling with rounded corners */
.v-card {
  border-radius: 16px;
}

/* Card title styling */
.v-card-title {
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
}

/* Responsive design for mobile devices */
@media (max-width: 600px) {
  .profile-avatar {
    margin-bottom: 20px;
  }
  
  .v-card-title {
    font-size: 1.5rem !important;
  }
}
</style> 