<template>
  <!-- Post detail page container -->
  <v-container class="post-detail-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <!-- Back to Community button -->
        <v-btn 
          color="primary" 
          text 
          class="mb-4" 
          @click="$router.push('/community')"
        >
          <v-icon left>mdi-arrow-left</v-icon>
          Back to Community
        </v-btn>
        
        <!-- Post detail card with elevation -->
        <v-card class="post-detail-card" elevation="4">
          <!-- Post title and author information -->
          <v-card-title class="text-h4 font-weight-bold primary--text">
            {{ post.title }}
          </v-card-title>

          <v-card-subtitle class="d-flex align-center">
            <user-avatar
              :username="post.author"
              :profile-image="post.author_profile_image"
              :size="36"
              class="mr-2"
            ></user-avatar>
            {{ post.author }}
            <v-spacer></v-spacer>
            <v-icon small class="mr-1">mdi-clock-outline</v-icon>
            {{ formatDate(post.created_at) }}
          </v-card-subtitle>

          <v-divider></v-divider>

          <!-- Post content section -->
          <v-card-text class="text-body-1">
            {{ post.content }}
          </v-card-text>

          <!-- Edit and delete buttons (visible only to author) -->
          <v-card-actions v-if="isAuthor" class="px-4">
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              text
              @click="$router.push(`/community/${post.id}/edit`)"
            >
              <v-icon left>mdi-pencil</v-icon>
              Modify
            </v-btn>
            <v-btn
              color="error"
              text
              @click="deletePost"
            >
              <v-icon left>mdi-delete</v-icon>
              Delete
            </v-btn>
          </v-card-actions>

          <v-divider></v-divider>

          <!-- Comments section -->
          <v-card-text>
            <div class="text-h6 font-weight-bold mb-4">
              <v-icon left>mdi-comment</v-icon>
              Comment
            </div>

            <!-- Comments list -->
            <v-list>
              <v-list-item
                v-for="comment in post.comments"
                :key="comment.id"
                class="comment-item"
              >
                <v-list-item-content>
                  <v-list-item-title class="d-flex align-center">
                    <user-avatar
                      :username="comment.author"
                      :profile-image="comment.author_profile_image"
                      :size="24"
                      class="mr-2"
                    ></user-avatar>
                    {{ comment.author }}
                    <v-spacer></v-spacer>
                    <v-btn
                      v-if="isCommentAuthor(comment)"
                      icon
                      small
                      color="error"
                      @click="deleteComment(comment.id)"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </v-list-item-title>
                  <v-list-item-subtitle class="mt-2">
                    {{ comment.content }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>

            <!-- New comment form -->
            <v-form @submit.prevent="addComment" class="mt-4">
              <v-textarea
                v-model="newComment"
                label="Write Comment"
                rows="3"
                outlined
                dense
                hide-details
                class="mb-2"
                placeholder="Remain your Comment..."
                maxlength="500"
              ></v-textarea>
              <div class="character-counter mb-2">
                {{ newComment.length }} / 500 characters
              </div>
              <v-btn
                color="primary"
                type="submit"
                :disabled="!newComment.trim()"
              >
                Write Comment
              </v-btn>
            </v-form>
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
 * Post Detail View Component
 * Displays a community post with details and comments
 * Features:
 * - Post title, author, and creation time display
 * - Post content rendering
 * - Comment section with add/delete functionality
 * - Post edit and delete options for authors
 */
export default {
  components: {
    UserAvatar // UserAvatar component registration
  },
  data() {
    return {
      post: {
        comments: [] // Array of comments for the post
      },
      newComment: '', // New comment input text
    };
  },
  computed: {
    /**
     * Check if current user is the post author
     * @returns {boolean} True if logged in user is the post author
     */
    isAuthor() {
      const username = localStorage.getItem('username');
      return this.post.author === username;
    }
  },
  async created() {
    try {
      const postId = this.$route.params.id;
      const response = await axios.get(`/api/community/posts/${postId}/`);
      this.post = response.data;

      const commentsResponse = await axios.get(`/api/community/posts/${postId}/comments/all/`);
      this.post.comments = commentsResponse.data;
    } catch (error) {
      // Error handled silently
    }
  },
  methods: {
    /**
     * Format date string to localized format
     * @param {string} dateString - ISO date string to format
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
     * Check if current user is a comment author
     * @param {Object} comment - Comment object to check
     * @returns {boolean} True if logged in user is the comment author
     */
    isCommentAuthor(comment) {
      const username = localStorage.getItem('username');
      return comment.author === username;
    },
    
    /**
     * Delete the current post
     * Confirms with user before deletion and redirects on success
     */
    async deletePost() {
      if (confirm("Are you sure you want to delete this post?")) {
        try {
          await axios.delete(`/api/community/posts/${this.post.id}/`);
          alert("The post has been deleted.");
          this.$router.push('/community');
        } catch (error) {
          // Error handled silently
        }
      }
    },
    
    /**
     * Add a new comment to the post
     * Validates tag selection and sends registration request to API
     */
    async addComment() {
      if (!this.newComment.trim()) return;
      try {
        await axios.post(`/api/community/posts/${this.post.id}/comments/`, {
          content: this.newComment,
        });

        this.newComment = '';

        const commentsResponse = await axios.get(`/api/community/posts/${this.post.id}/comments/all/`);
        this.post.comments = commentsResponse.data;
      } catch (error) {
        // Error handled silently
      }
    },
    
    /**
     * Delete a comment
     * @param {number} commentId - ID of the comment to delete
     * Confirms with user before deletion and updates the UI on success
     */
    async deleteComment(commentId) {
      if (confirm("Are you sure you want to delete this comment?")) {
        try {
          await axios.delete(`/api/community/comments/${commentId}/`);
          this.post.comments = this.post.comments.filter(c => c.id !== commentId);
        } catch (error) {
          // Error handled silently
        }
      }
    }
  }
};
</script>

<style scoped>
/* Main container styling with gradient background */
.post-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
  padding: 40px 0;
}

/* Post detail card styling */
.post-detail-card {
  border-radius: 12px;
  overflow: hidden;
}

/* Title section padding */
.v-card-title {
  padding: 24px 16px;
}

/* Subtitle styling and color */
.v-card-subtitle {
  padding: 0 16px 16px;
  color: #666;
}

/* Content section styling */
.v-card-text {
  padding: 24px 16px;
  line-height: 1.8;
}

/* Comment item styling with bottom border */
.comment-item {
  border-bottom: 1px solid #eee;
  padding: 16px 0;
}

/* Remove border from last comment */
.comment-item:last-child {
  border-bottom: none;
}

/* Comment author name styling */
.v-list-item-title {
  font-weight: 500;
  color: #333;
}

/* Comment content styling */
.v-list-item-subtitle {
  color: #666;
  white-space: pre-wrap;
}

/* Button text styling */
.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}

/* Comment textarea styling */
.v-textarea {
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Character counter styling */
.character-counter {
  font-size: 12px;
  color: #718096;
  text-align: right;
  margin-top: 4px;
}
</style>
