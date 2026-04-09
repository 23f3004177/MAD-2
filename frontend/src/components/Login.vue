<template>
  <div class="login-container d-flex align-items-center justify-content-center">
    <div class="card login-card shadow-lg pattern-bg">
      <div class="card-body p-5">
        <div class="text-center mb-4">
          <h2 class="fw-bold text-primary mb-2">Welcome Back</h2>
          <p class="text-muted">Sign in to your Trimed account</p>
        </div>
        
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="email" class="form-label text-secondary fw-semibold">Email address</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-envelope text-primary"></i>
              </span>
              <input 
                type="email" 
                class="form-control border-start-0 ps-0" 
                id="email" 
                v-model="email" 
                placeholder="name@example.com" 
                required
              >
            </div>
          </div>
          
          <div class="mb-4">
            <label for="password" class="form-label text-secondary fw-semibold d-flex justify-content-between">
              Password
              <a href="#" class="text-primary text-decoration-none small">Forgot password?</a>
            </label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-lock text-primary"></i>
              </span>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                class="form-control border-start-0 border-end-0 ps-0" 
                id="password" 
                v-model="password" 
                placeholder="Enter your password" 
                required
              >
              <button 
                class="btn btn-outline-secondary bg-white border-start-0 text-primary" 
                type="button" 
                @click="togglePassword"
              >
                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>
          
          <div class="mb-4 form-check">
            <input type="checkbox" class="form-check-input" id="rememberMe" v-model="rememberMe">
            <label class="form-check-label text-muted small" for="rememberMe">Remember me</label>
          </div>
          
          <button type="submit" class="btn btn-primary w-100 py-2 mb-3 fw-bold rounded-pill shadow-sm transition-all login-btn">
            Sign In
          </button>
          
          <div class="text-center mt-4">
            <p class="text-muted small">
              Don't have an account? 
              <router-link to="/register" class="text-primary fw-bold text-decoration-none">Create an account</router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      showPassword: false
    }
  },
  methods: {
    async handleLogin() {
      // Basic validation
      if (!this.email || !this.password) return;
      
      try {
        const response = await fetch('http://localhost:5000/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
             // Backend model uses "username" for authentication
            username: this.email,
            password: this.password
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          alert(data.msg || 'Login failed');
          return;
        }

        console.log('Login successful:', data);
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user_role', data.role);
        
        // Redirect based on role
        if (data.role === 'admin') {
          this.$router.push('/admin');
        } else if (data.role === 'doctor') {
          this.$router.push('/doctor');
        } else {
          this.$router.push('/patient');
        }
      } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred connecting to the server');
      }
    },
    togglePassword() {
      this.showPassword = !this.showPassword;
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 76px); /* Adjust based on navbar height */
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 450px;
  border: none;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.pattern-bg::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 6px;
  background: linear-gradient(90deg, #0d6efd, #0dcaf0);
}

.form-control:focus {
  box-shadow: none;
  border-color: #dee2e6;
}

.input-group:focus-within .input-group-text,
.input-group:focus-within .form-control,
.input-group:focus-within .btn {
  border-color: #0d6efd;
}

.input-group-text {
  border-right: none;
}

.form-control {
  border-left: none;
}

.transition-all {
  transition: all 0.3s ease;
}

.login-btn {
  background: linear-gradient(90deg, #0d6efd, #0b5ed7);
  border: none;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(13, 110, 253, 0.4) !important;
}

/* Ensure Bootstrap Icons are loaded in your project */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");
</style>
