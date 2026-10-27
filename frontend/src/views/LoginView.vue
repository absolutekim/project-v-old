<template>
  <!-- Login page container with gradient background -->
  <div class="login-container">
    <!-- Login form card box -->
    <div class="login-box">
      <h2>Welcome Back</h2>
      <!-- Login form with username and password inputs -->
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="username" required placeholder="Enter your username" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" required placeholder="Enter your password" />
        </div>

        <button type="submit" class="submit-btn">Sign In</button>
      </form>
      <!-- Error message display area -->
      <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
      <!-- Registration link for new users -->
      <div class="register-link">
        Don't have an account? <router-link to="/register">Register here</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

/**
 * Login View Component
 * Provides authentication functionality for users to sign in
 * Handles form submission, JWT token storage, and error states
 */
export default {
  data() {
    return {
      username: '', // Username input field
      password: '', // Password input field
      errorMessage: '' // Error message for failed login attempts
    };
  },
  methods: {
    /**
     * Handle login form submission
     * Authenticates user with the server and stores JWT tokens
     * Redirects to home page on success, displays error on failure
     */
    async login() {
      try {
        const response = await axios.post('/api/accounts/login/', {
          username: this.username,
          password: this.password
        }, {
          headers: { 'Content-Type': 'application/json' }
        });

        // Store authentication tokens in localStorage
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        // Store username if available
        if (response.data.username) {
          localStorage.setItem('username', response.data.username);
        }
        
        // Trigger auth state change event for other components
        document.dispatchEvent(new Event('auth-changed'));
        
        // Redirect to home page
        this.$router.push('/');
        
      } catch (error) {
        this.errorMessage = "Invalid username or password. Please try again.";
      }
    }
  }
};
</script>

<style scoped>
/* Main container with gradient background */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e39047 0%, #65b009 100%);
  padding: 20px;
}

/* Login form card styling */
.login-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

/* Login form heading */
h2 {
  color: #2d3748;
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
}

/* Form layout styling */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Form group container for inputs */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Form label styling */
label {
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
}

/* Text input styling */
input[type="text"],
input[type="password"] {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

/* Focus state for text inputs */
input[type="text"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Submit button styling */
.submit-btn {
  background: #667eea;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 20px;
}

/* Submit button hover state */
.submit-btn:hover {
  background: #5a67d8;
}

/* Message container styling */
.message {
  margin-top: 20px;
  padding: 12px;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
}

/* Error message styling */
.error {
  background: #fed7d7;
  color: #c53030;
}

/* Registration link container */
.register-link {
  margin-top: 20px;
  text-align: center;
  color: #4a5568;
  font-size: 14px;
}

/* Registration link styling */
.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

/* Registration link hover state */
.register-link a:hover {
  text-decoration: underline;
}

/* Responsive design for smaller screens */
@media (max-width: 640px) {
  .login-box {
    padding: 20px;
  }
  
  h2 {
    font-size: 24px;
  }
}
</style>
