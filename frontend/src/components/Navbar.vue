<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm py-3 sticky-top">
    <div class="container">
      <router-link class="navbar-brand fw-bold fs-4 d-flex align-items-center" to="/">
        <i class="bi bi-heart-pulse-fill text-primary me-2"></i>
        <span class="text-dark">Trimed</span>
      </router-link>

      <button
        class="navbar-toggler border-0 shadow-none px-0"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mx-auto fw-semibold">
          <li class="nav-item mx-lg-2">
            <router-link class="nav-link" active-class="active text-primary" exact-active-class="active text-primary" to="/">Home</router-link>
          </li>
          <li class="nav-item mx-lg-2" v-if="role === 'admin'">
            <router-link class="nav-link" active-class="active text-primary" to="/admin">Admin</router-link>
          </li>
          <li class="nav-item mx-lg-2" v-if="role === 'doctor'">
            <router-link class="nav-link" active-class="active text-primary" to="/doctor">Doctor Hub</router-link>
          </li>
          <li class="nav-item mx-lg-2" v-if="role === 'patient'">
            <router-link class="nav-link" active-class="active text-primary" to="/patient">Patient Hub</router-link>
          </li>
          <li class="nav-item mx-lg-2">
            <a class="nav-link" href="#">Services</a>
          </li>
          <li class="nav-item mx-lg-2">
            <a class="nav-link" href="#">Contact</a>
          </li>
        </ul>
        <div class="d-flex align-items-center gap-3 mt-3 mt-lg-0">
          <template v-if="!token">
            <router-link to="/login" class="text-dark text-decoration-none fw-semibold border-0 bg-transparent px-2">Login</router-link>
            <router-link to="/register" class="btn btn-primary rounded-pill px-4 fw-semibold shadow-sm">Register</router-link>
          </template>
          <template v-else>
            <button @click="logout" class="btn btn-outline-danger rounded-pill px-4 fw-semibold shadow-sm">Logout</button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  data() {
    return {
      token: localStorage.getItem('access_token'),
      role: localStorage.getItem('user_role')
    }
  },
  watch: {
    $route() {
      // Re-evaluate auth state on route change
      this.token = localStorage.getItem('access_token');
      this.role = localStorage.getItem('user_role');
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      this.token = null;
      this.role = null;
      this.$router.push('/login');
    }
  }
}
</script>