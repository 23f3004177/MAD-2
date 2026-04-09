import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import LandingPage from '../components/LandingPage.vue'
import AdminDashboard from '../components/AdminDashboard.vue'
import PatientDashboard from '../components/PatientDashboard.vue'
import DoctorDashboard from '../components/DoctorDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'LandingPage',
    component: LandingPage
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/patient',
    name: 'PatientDashboard',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/doctor',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  const role = localStorage.getItem('user_role');

  if (to.meta.requiresAuth) {
    if (!token) {
      return next({ name: 'Login' });
    }
    if (to.meta.role && to.meta.role !== role) {
      if (role === 'admin') return next({ name: 'AdminDashboard' });
      if (role === 'doctor') return next({ name: 'DoctorDashboard' });
      if (role === 'patient') return next({ name: 'PatientDashboard' });
      return next({ name: 'Login' });
    }
  }
  
  // Prevent logged-in users from seeing login/register again
  if ((to.name === 'Login' || to.name === 'Register') && token) {
     if (role === 'admin') return next({ name: 'AdminDashboard' });
     if (role === 'doctor') return next({ name: 'DoctorDashboard' });
     if (role === 'patient') return next({ name: 'PatientDashboard' });
  }

  next();
})

export default router
