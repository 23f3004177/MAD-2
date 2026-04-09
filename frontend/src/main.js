import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Import Bootstrap JS - the bundle self-registers on window in browser environments
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Also do an explicit import to ensure window.bootstrap is set
import { Modal, Dropdown, Collapse, Tooltip } from 'bootstrap'
window.bootstrap = { Modal, Dropdown, Collapse, Tooltip }

createApp(App).use(router).mount('#app')
