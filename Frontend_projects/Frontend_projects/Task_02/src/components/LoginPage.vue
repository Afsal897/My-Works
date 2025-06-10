<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-body">
            <h2 class="card-title text-center mb-4">Login</h2>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input 
                  v-model="username"
                  type="text" 
                  class="form-control"
                  id="username"
                >
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input 
                  v-model="password"
                  type="password" 
                  class="form-control"
                  id="password"
                >
              </div>
              <button 
                type="submit" 
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
              <div v-if="error" class="alert alert-danger mt-3 mb-0">
                {{ error }}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    }
  },
  mounted() {
    const token = localStorage.getItem('accessToken');
    if (token) {
      this.$router.push('/calculator');
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = '';

      try {
        const response = await axios.post('http://localhost:5000/login', {
          username: this.username,
          password: this.password
        });

        // Save token to localStorage
        localStorage.setItem('accessToken', response.data.access_token);

        // Redirect after successful login
        this.$router.push('/calculator');
      } catch (error) {
        this.error = error.response?.data?.message || 'Login failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 1rem;
}
</style>
