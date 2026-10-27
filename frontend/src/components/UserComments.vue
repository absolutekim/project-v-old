<template>
  <div class="user-comments">
    <v-alert v-if="loading" type="info" text>
      Loading your comments...
    </v-alert>
    
    <v-alert v-else-if="error" type="error" text>
      {{ error }}
    </v-alert>
    
    <v-alert v-else-if="comments.length === 0" type="info" outlined>
      You haven't written any comments yet.
    </v-alert>
    
    <template v-else>
      <v-list class="comment-list">
        <v-list-item
          v-for="comment in comments"
          :key="comment.id"
          @click="goToPost(comment.post_id)"
          class="comment-item"
        >
          <v-list-item-content>
            <v-list-item-title class="text-subtitle-1 font-weight-medium">
              On post: {{ comment.post_title }}
            </v-list-item-title>
            <v-list-item-subtitle class="mt-1 comment-content">
              {{ comment.content }}
            </v-list-item-subtitle>
            <v-list-item-subtitle class="mt-2 text-caption">
              <v-icon small class="mr-1">mdi-clock-outline</v-icon>
              {{ formatDate(comment.created_at) }}
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-icon>mdi-chevron-right</v-icon>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </template>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserComments',
  data() {
    return {
      comments: [],
      loading: true,
      error: null
    };
  },
  async created() {
    await this.loadComments();
  },
  methods: {
    async loadComments() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/community/user/comments/');
        this.comments = response.data;
      } catch (err) {
        this.error = 'Failed to load your comments. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    goToPost(postId) {
      this.$router.push(`/community/${postId}`);
    }
  }
};
</script>

<style scoped>
.comment-list {
  border-radius: 8px;
  overflow: hidden;
}

.comment-item {
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
  padding-top: 12px;
  padding-bottom: 12px;
}

.comment-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content {
  white-space: normal;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  color: #666;
}
</style> 