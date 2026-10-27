<template>
  <!-- New post creation container -->
  <v-container class="new-post-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <!-- Post creation card -->
        <v-card class="new-post-card" elevation="4">
          <v-card-title class="text-center text-h4 font-weight-bold primary--text">
            Create New Post
          </v-card-title>

          <v-card-text>
            <!-- Post submission form with validation -->
            <v-form @submit.prevent="createPost" ref="form">
              <v-text-field
                v-model="title"
                label="Title"
                outlined
                dense
                required
                :rules="[v => !!v || 'Write your Title']"
                class="mb-2"
                placeholder="Please Write your Title..."
                maxlength="255"
              ></v-text-field>
              <div class="character-counter mb-4">
                {{ title.length }} / 255 characters
              </div>

              <v-textarea
                v-model="content"
                label="Content"
                outlined
                dense
                required
                :rules="[v => !!v || 'Write your Content']"
                rows="10"
                class="mb-2"
                placeholder="Please Write your Content..."
                maxlength="3000"
              ></v-textarea>
              <div class="character-counter mb-4">
                {{ content.length }} / 3000 characters
              </div>

              <div class="d-flex justify-space-between">
                <!-- Back button to return to community page -->
                <v-btn
                  color="grey"
                  text
                  @click="$router.push('/community')"
                >
                  <v-icon left>mdi-arrow-left</v-icon>
                  Back to List
                </v-btn>
                <!-- Submit button for post creation -->
                <v-btn
                  color="primary"
                  type="submit"
                  :loading="loading"
                  :disabled="!title.trim() || !content.trim()"
                >
                  <v-icon left>mdi-check</v-icon>
                  Upload Post
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

/**
 * New Post View Component
 * Allows users to create new community posts
 * Features:
 * - Form with title and content fields
 * - Input validation
 * - Loading state during submission
 * - Navigation back to community page
 */
export default {
  data() {
    return {
      title: '', // Post title input field
      content: '', // Post content textarea
      loading: false // Loading state for form submission
    };
  },
  methods: {
    /**
     * Create a new post with the form data
     * Validates inputs, submits to API, and redirects on success
     */
    async createPost() {
      if (!this.title.trim() || !this.content.trim()) return;
      
      this.loading = true;
      try {
        const userId = localStorage.getItem('user_id');
        await axios.post(`http://localhost:8000/api/community/posts/`, {
          title: this.title,
          content: this.content,
          author_id: userId
        });

        this.$router.push('/community');
      } catch (error) {
        // Error handled silently
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Main container styling with gradient background */
.new-post-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
  padding: 40px 0;
}

/* Card styling with rounded corners */
.new-post-card {
  border-radius: 12px;
  overflow: hidden;
}

/* Card title styling with bottom border */
.v-card-title {
  padding: 24px 16px;
  border-bottom: 2px solid #eee;
}

/* Card content padding */
.v-card-text {
  padding: 24px 16px;
}

/* Text field background styling */
.v-text-field {
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Textarea background styling */
.v-textarea {
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Button text styling */
.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}

/* Form width constraint */
.v-form {
  max-width: 100%;
}

/* Character counter styling */
.character-counter {
  font-size: 12px;
  color: #718096;
  text-align: right;
  margin-top: 4px;
}
</style>
