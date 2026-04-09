<template>
  <div class="register-container d-flex align-items-center justify-content-center">
    <div class="card register-card shadow-lg pattern-bg">
      <div class="card-body p-5">
        <div class="text-center mb-4">
          <h2 class="fw-bold text-primary mb-2">Create Account</h2>
          <p class="text-muted">Join Trimed today</p>
        </div>
        
        <form @submit.prevent="handleRegister">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="firstName" class="form-label text-secondary fw-semibold">First Name</label>
              <div class="input-group">
                <span class="input-group-text bg-white border-end-0">
                  <i class="bi bi-person text-primary"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control border-start-0 ps-0" 
                  id="firstName" 
                  v-model="firstName" 
                  placeholder="John" 
                  required
                >
              </div>
            </div>
            <div class="col-md-6 mb-3">
              <label for="lastName" class="form-label text-secondary fw-semibold">Last Name</label>
              <input 
                type="text" 
                class="form-control" 
                id="lastName" 
                v-model="lastName" 
                placeholder="Doe" 
                required
              >
            </div>
          </div>

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
          
          <div class="mb-3">
            <label for="password" class="form-label text-secondary fw-semibold">Password</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-lock text-primary"></i>
              </span>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                class="form-control border-start-0 border-end-0 ps-0" 
                id="password" 
                v-model="password" 
                placeholder="Create a strong password" 
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
            <div class="form-text small mt-1">Must be at least 8 characters.</div>
          </div>

          <div class="mb-4">
            <label for="confirmPassword" class="form-label text-secondary fw-semibold">Confirm Password</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-shield-check text-primary"></i>
              </span>
              <input 
                :type="showConfirmPassword ? 'text' : 'password'" 
                class="form-control border-start-0 border-end-0 ps-0" 
                id="confirmPassword" 
                v-model="confirmPassword" 
                placeholder="Repeat your password" 
                required
              >
               <button 
                class="btn btn-outline-secondary bg-white border-start-0 text-primary" 
                type="button" 
                @click="toggleConfirmPassword"
              >
                <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
            <div v-if="passwordMismatch" class="text-danger small mt-1">Passwords do not match.</div>
          </div>
          
          <div class="mb-4 form-check">
            <input type="checkbox" class="form-check-input" id="terms" v-model="agreeTerms" required>
            <label class="form-check-label text-muted small" for="terms">
              I agree to the <a href="#" class="text-primary text-decoration-none">Terms of Service</a> and <a href="#" class="text-primary text-decoration-none">Privacy Policy</a>
            </label>
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary w-100 py-2 mb-3 fw-bold rounded-pill shadow-sm transition-all register-btn"
            :disabled="passwordMismatch || !agreeTerms"
          >
            Create Account
          </button>
          
          <div class="text-center mt-4">
            <p class="text-muted small">
              Already have an account? 
              <router-link to="/login" class="text-primary fw-bold text-decoration-none">Sign in</router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeTerms: false,
      showPassword: false,
      showConfirmPassword: false
    }
  },
  computed: {
    passwordMismatch() {
      // Only show mismatch if both fields have some input
      if (this.password.length > 0 && this.confirmPassword.length > 0) {
        return this.password !== this.confirmPassword;
      }
      return false;
    }
  },
  methods: {
    async handleRegister() {
      if (this.passwordMismatch || !this.agreeTerms) return;
      
      try {
        const response = await fetch('http://localhost:5000/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.email,
            password: this.password,
            name: (this.firstName + ' ' + this.lastName).trim()
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          alert(data.msg || 'Registration failed');
          return;
        }

        console.log('Registration successful:', data);
        alert('Registration successful! Please login.');
        this.$router.push('/login');
      } catch (error) {
        console.error('Registration error:', error);
        alert('An error occurred connecting to the server');
      }
    },
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    toggleConfirmPassword() {
      this.showConfirmPassword = !this.showConfirmPassword;
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: calc(100vh - 76px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.register-card {
  width: 100%;
  max-width: 550px; /* Slightly wider than login for the 2-column layout */
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

.register-btn {
  background: linear-gradient(90deg, #0d6efd, #0b5ed7);
  border: none;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(13, 110, 253, 0.4) !important;
}

.register-btn:disabled {
  opacity: 0.65;
  background: #6c757d;
}
</style>
