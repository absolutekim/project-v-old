<template>
  <div class="user-posts">
    <v-alert v-if="loading" type="info" text>
      Loading your posts...
    </v-alert>
    
    <v-alert v-else-if="error" type="error" text>
      {{ error }}
    </v-alert>
    
    <v-alert v-else-if="posts.length === 0" type="info" outlined>
      You haven't created any posts yet.
    </v-alert>
    
    <template v-else>
      <v-list class="post-list">
        <v-list-item
          v-for="post in posts"
          :key="post.id"
          @click="goToPost(post.id)"
          class="post-item"
        >
          <v-list-item-content>
            <v-list-item-title class="text-h6">
              {{ post.title }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <v-icon small class="mr-1">mdi-clock-outline</v-icon>
              {{ formatDate(post.created_at) }}
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
  name: 'UserPosts',
  data() {
    return {
      posts: [],
      loading: true,
      error: null
    };
  },
  async created() {
    await this.loadPosts();
  },
  methods: {
    async loadPosts() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/community/user/posts/');
        this.posts = response.data;
      } catch (err) {
        this.error = 'Failed to load your posts. Please try again.';
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
.post-list {
  border-radius: 8px;
  overflow: hidden;
}

.post-item {
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.post-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

.post-item:last-child {
  border-bottom: none;
}
</style> 