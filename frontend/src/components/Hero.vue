<template>
  <div class="hero-section position-relative bg-white overflow-hidden">
    <!-- Decorative background blobs -->
    <div class="position-absolute top-0 start-0 w-100 h-100 bg-primary bg-opacity-10" style="clip-path: polygon(0 0, 100% 0, 100% 85%, 0% 100%);"></div>
    
    <div class="container position-relative z-1 py-5 my-5">
      <div class="row align-items-center g-5">
        <div class="col-lg-6 text-center text-lg-start">
          <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-3 py-2 mb-3 fw-semibold">Next Generation Healthcare</span>
          <h1 class="display-4 fw-bold text-dark mb-4 lh-sm">
            Advanced Care Systems <br/>
            <span class="text-primary">For Better Health</span>
          </h1>
          <p class="lead text-muted mb-5 pe-lg-4">
            Trimed provides an integrated, robust platform to manage patient records, doctor scheduling, and hospital administration with uncompromising efficiency and security.
          </p>
          <div class="d-flex flex-column flex-sm-row justify-content-center justify-content-lg-start gap-3">
            <router-link to="/patient" class="btn btn-primary btn-lg rounded-pill px-5 shadow-sm fw-semibold">Book Appointment</router-link>
            <router-link to="/admin" class="btn btn-outline-secondary btn-lg rounded-pill px-5 fw-semibold border-2">Administrative Hub</router-link>
          </div>
        </div>
        <div class="col-lg-6 d-none d-lg-block text-center mt-5 mt-lg-0">
          <img src="/Doctors-rafiki.svg" alt="Doctor Illustration" class="img-fluid" style="max-height: 650px; transform: scale(1.15);" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Hero"
}
</script>

<style scoped>
.hero-section {
  min-height: calc(100vh - 76px);
  display: flex;
  align-items: center;
}
</style>