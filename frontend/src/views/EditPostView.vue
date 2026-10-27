<template>
  <!-- Post editing form container -->
  <div>
    <h1>Modify Post</h1>
    <!-- Post edit form with title and content fields -->
    <form @submit.prevent="updatePost">
      <label>Title:</label>
      <input type="text" v-model="title" required maxlength="255">
      <div class="character-counter">
        {{ title.length }} / 255 characters
      </div>
      
      <label>Content:</label>
      <textarea v-model="content" required maxlength="3000"></textarea>
      <div class="character-counter">
        {{ content.length }} / 3000 characters
      </div>
      
      <div class="button-group">
        <button type="submit" class="submit-button">Update</button>
        <button type="button" class="cancel-button" @click="cancel">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

/**
 * Edit Post View Component
 * Allows users to modify their existing community posts
 * Loads existing post data and handles form submission for updates
 */
export default {
  data() {
    return {
      title: '', // Post title field
      content: '' // Post content field
    };
  },
  /**
   * Fetch the current post data when component is created
   * Populates form fields with existing post data
   */
  async created() {
    const postId = this.$route.params.id;
    const response = await axios.get(`/api/community/posts/${postId}/`);
    this.title = response.data.title;
    this.content = response.data.content;
  },
  methods: {
    /**
     * Submit the updated post data to the server
     * Validates inputs and redirects to the post page on success
     */
    async updatePost() {
      if (!this.title.trim() || !this.content.trim()) return;
      await axios.put(`/api/community/posts/${this.$route.params.id}/`, {
        title: this.title,
        content: this.content
      });
      this.$router.push(`/community/${this.$route.params.id}`);
    },
    
    /**
     * Cancel edit and return to post detail page
     */
    cancel() {
      this.$router.push(`/community/${this.$route.params.id}`);
    }
  }
};
</script>

<style scoped>
/* Form container styling */
div {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

/* Page title styling */
h1 {
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 2rem;
}

/* Form element styling */
form {
  display: flex;
  flex-direction: column;
}

/* Form label styling */
label {
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #2c3e50;
}

/* Input field styling */
input[type="text"] {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/* Textarea styling */
textarea {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 200px;
  font-size: 1rem;
  resize: vertical;
}

/* Character counter styling */
.character-counter {
  font-size: 12px;
  color: #718096;
  text-align: right;
  margin-bottom: 1.5rem;
}

/* Button group styling */
.button-group {
  display: flex;
  gap: 1rem;
}

/* Submit button styling */
.submit-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Submit button hover state */
.submit-button:hover {
  background-color: #2980b9;
}

/* Cancel button styling */
.cancel-button {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Cancel button hover state */
.cancel-button:hover {
  background-color: #c0392b;
}
</style>
