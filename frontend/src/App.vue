<template>
  <div id="app">
    <Navbar />
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  components: {
    Navbar
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bs-primary: #4f46e5;
  --bs-primary-rgb: 79, 70, 229;
  --bs-success: #10b981;
  --bs-success-rgb: 16, 185, 129;
  --bs-warning: #f59e0b;
  --bs-warning-rgb: 245, 158, 11;
  --bs-danger: #ef4444;
  --bs-danger-rgb: 239, 68, 68;
  --bs-info: #06b6d4;
  --bs-info-rgb: 6, 182, 212;
  --bs-body-font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --bs-body-bg: #f5f7fa;
  --bs-body-color: #1e293b;
  --bs-secondary-color: #64748b;
  
  --pd-primary: #4f46e5;
  --pd-primary-light: #818cf8;
  --pd-primary-dark: #3730a3;
  --pd-success: #10b981;
  --pd-warning: #f59e0b;
  --pd-danger: #ef4444;
  --pd-info: #06b6d4;
  --pd-bg: #f5f7fa;
  --pd-surface: #ffffff;
  --pd-surface-hover: #f8fafc;
  --pd-border: #e2e8f0;
  --pd-text: #1e293b;
  --pd-text-muted: #64748b;
  --pd-radius: 16px;
  --pd-radius-sm: 10px;
  --pd-radius-xs: 6px;
}

body {
  font-family: var(--bs-body-font-family) !important;
  background-color: var(--bs-body-bg) !important;
  color: var(--bs-body-color) !important;
  position: relative;
  min-height: 100vh;
}

body::before {
  content: "";
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 20%, rgba(79,70,229,0.05) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16,185,129,0.05) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 50% 50%, rgba(6,182,212,0.03) 0%, transparent 60%);
  pointer-events: none;
  z-index: -1;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>