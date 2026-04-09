<template>
  <div class="patient-dashboard">
    <div class="container-fluid px-4 px-lg-5 py-4 position-relative">
      <!-- ═══════════════════════════════════════════ -->
      <!-- WELCOME HEADER                             -->
      <!-- ═══════════════════════════════════════════ -->
      <div class="row mb-4 fade-in">
        <div class="col-12">
          <div class="welcome-card">
            <div class="welcome-content">
              <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
                <div>
                  <h2 class="welcome-title mb-1">
                    Welcome back, <span class="text-gradient">{{ profile.name || 'Patient' }}</span> 👋
                  </h2>
                  <p class="welcome-subtitle mb-0">Here's your health overview for today</p>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn-glass btn-glass-primary" @click="openProfileModal" id="edit-profile-btn">
                    <i class="bi bi-person-gear me-2"></i>Edit Profile
                  </button>
                </div>
              </div>
            </div>
            <div class="welcome-decor"></div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════ -->
      <!-- STATS ROW                                  -->
      <!-- ═══════════════════════════════════════════ -->
      <div class="row g-3 mb-4 stagger-in">
        <div class="col-6 col-lg-3">
          <div class="stat-card stat-upcoming">
            <div class="stat-icon"><i class="bi bi-calendar-check"></i></div>
            <div class="stat-info">
              <span class="stat-number">{{ upcomingCount }}</span>
              <span class="stat-label">Upcoming</span>
            </div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="stat-card stat-completed">
            <div class="stat-icon"><i class="bi bi-check-circle"></i></div>
            <div class="stat-info">
              <span class="stat-number">{{ completedCount }}</span>
              <span class="stat-label">Completed</span>
            </div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="stat-card stat-treatments">
            <div class="stat-icon"><i class="bi bi-clipboard2-pulse"></i></div>
            <div class="stat-info">
              <span class="stat-number">{{ treatmentsCount }}</span>
              <span class="stat-label">Diagnoses</span>
            </div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="stat-card stat-departments">
            <div class="stat-icon"><i class="bi bi-building"></i></div>
            <div class="stat-info">
              <span class="stat-number">{{ departments.length }}</span>
              <span class="stat-label">Departments</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════ -->
      <!-- TAB NAVIGATION                             -->
      <!-- ═══════════════════════════════════════════ -->
      <div class="row mb-4 fade-in">
        <div class="col-12">
          <div class="tab-nav-container">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
              :id="'tab-' + tab.key"
            >
              <i :class="tab.icon" class="me-2"></i>
              <span class="d-none d-sm-inline">{{ tab.label }}</span>
              <span class="d-sm-none">{{ tab.short }}</span>
              <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════ -->
      <!-- TAB: DEPARTMENTS                           -->
      <!-- ═══════════════════════════════════════════ -->
      <div v-if="activeTab === 'departments'" class="tab-content fade-in" id="departments-section">
        <div class="section-header mb-4">
          <h4 class="section-title"><i class="bi bi-building me-2"></i>All Departments & Specializations</h4>
          <p class="section-subtitle">Browse our medical departments to find the right specialist for your needs</p>
        </div>
        <div class="row g-3">
          <div v-for="dept in departments" :key="dept.id" class="col-md-6 col-lg-4">
            <div class="dept-card" @click="filterDoctorsByDept(dept)">
              <div class="dept-icon-wrap">
                <i :class="getDeptIcon(dept.name)"></i>
              </div>
              <div class="dept-info">
                <h6 class="dept-name">{{ dept.name }}</h6>
                <p class="dept-desc">{{ dept.description || 'Specialized care and treatment' }}</p>
                <span class="dept-doctors-count">
                  <i class="bi bi-people me-1"></i>{{ getDoctorCountForDept(dept.id) }} Doctor(s)
                </span>
              </div>
              <i class="bi bi-chevron-right dept-arrow"></i>
            </div>
          </div>
          <div v-if="departments.length === 0" class="col-12">
            <div class="empty-state">
              <i class="bi bi-building display-1 text-muted opacity-25"></i>
              <p class="text-muted mt-3">No departments available yet</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════ -->
      <!-- TAB: FIND DOCTORS (7-Day Availability)     -->
      <!-- ═══════════════════════════════════════════ -->
      <div v-if="activeTab === 'doctors'" class="tab-content fade-in" id="doctors-section">
        <div class="section-header mb-4">
          <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
            <div>
              <h4 class="section-title"><i class="bi bi-person-badge me-2"></i>Find a Doctor</h4>
              <p class="section-subtitle">View doctor profiles and their availability for the next 7 days</p>
            </div>
            <div class="d-flex gap-2 flex-wrap">
              <select class="filter-select" v-model="doctorFilterDept" id="filter-department">
                <option value="">All Departments</option>
                <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
              <input type="text" class="filter-select" placeholder="Search doctor or spec..." v-model="doctorSearchQuery" style="max-width: 200px;">
              <button class="btn-glass btn-glass-primary" @click="openBookModal" id="book-appointment-btn">
                <i class="bi bi-plus-lg me-2"></i>Book Appointment
              </button>
            </div>
          </div>
        </div>

        <!-- Next 7 Days Header -->
        <div class="week-header mb-3">
          <div class="week-day-label" v-for="day in next7Days" :key="day.dateStr">
            <span class="week-day-name">{{ day.dayShort }}</span>
            <span class="week-day-date">{{ day.dateShort }}</span>
          </div>
        </div>

        <!-- Doctor Cards -->
        <div class="doctor-list">
          <div v-for="doc in filteredDoctors" :key="doc.id" class="doctor-card">
            <div class="doctor-card-main" @click="toggleDoctorProfile(doc.id)">
              <div class="doctor-avatar">
                {{ getInitials(doc.name) }}
              </div>
              <div class="doctor-info">
                <h6 class="doctor-name">Dr. {{ doc.name }}</h6>
                <span class="doctor-specialty">{{ doc.specialization }}</span>
                <span class="doctor-dept">{{ doc.department_name }}</span>
              </div>
              <div class="doctor-availability-row">
                <span
                  v-for="day in next7Days"
                  :key="doc.id + '-' + day.dateStr"
                  class="avail-dot"
                  :class="isDoctorAvailable(doc, day.dayIndex) ? 'available' : 'unavailable'"
                  :title="day.dayName + ': ' + (isDoctorAvailable(doc, day.dayIndex) ? 'Available' : 'Unavailable')"
                ></span>
              </div>
              <button class="btn-icon" @click.stop="openDoctorProfile(doc)" title="View Profile">
                <i class="bi bi-person-lines-fill"></i>
              </button>
            </div>

            <!-- Expanded Profile -->
            <transition name="slide-down">
              <div v-if="expandedDoctor === doc.id" class="doctor-profile-expanded">
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="profile-detail">
                      <label>Full Name</label>
                      <span>Dr. {{ doc.name }}</span>
                    </div>
                    <div class="profile-detail">
                      <label>Specialization</label>
                      <span>{{ doc.specialization }}</span>
                    </div>
                    <div class="profile-detail">
                      <label>Department</label>
                      <span>{{ doc.department_name }}</span>
                    </div>
                    <div class="profile-detail" v-if="doc.contact">
                      <label>Contact</label>
                      <span>{{ doc.contact }}</span>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="profile-detail-label mb-2">Weekly Availability</label>
                    <div class="avail-week-grid">
                      <div
                        v-for="(dayName, idx) in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']"
                        :key="idx"
                        class="avail-week-cell"
                        :class="doc.availability && doc.availability[idx] === '1' ? 'avail-yes' : 'avail-no'"
                      >
                        {{ dayName }}
                      </div>
                    </div>
                    <button class="btn-glass btn-glass-primary mt-3 w-100" @click="bookWithDoctor(doc)">
                      <i class="bi bi-calendar-plus me-2"></i>Book with Dr. {{ doc.name }}
                    </button>
                  </div>
                </div>
              </div>
            </transition>
          </div>
          <div v-if="filteredDoctors.length === 0" class="empty-state">
            <i class="bi bi-search display-1 text-muted opacity-25"></i>
            <p class="text-muted mt-3">No doctors found in this department</p>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════ -->
      <!-- TAB: UPCOMING APPOINTMENTS                 -->
      <!-- ═══════════════════════════════════════════ -->
      <div v-if="activeTab === 'appointments'" class="tab-content fade-in" id="appointments-section">
        <div class="section-header mb-4">
          <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
            <div>
              <h4 class="section-title"><i class="bi bi-calendar-check me-2"></i>Upcoming Appointments</h4>
              <p class="section-subtitle">Your scheduled appointments and their current status</p>
            </div>
            <button class="btn-glass btn-glass-primary" @click="openBookModal" id="book-new-apt-btn">
              <i class="bi bi-plus-lg me-2"></i>Book New
            </button>
          </div>
        </div>

        <div class="appointments-grid">
          <div v-for="apt in upcomingAppointments" :key="apt.id" class="appointment-card">
            <div class="appointment-card-left">
              <div class="apt-date-block">
                <span class="apt-month">{{ getMonth(apt.date) }}</span>
                <span class="apt-day">{{ getDay(apt.date) }}</span>
                <span class="apt-year">{{ getYear(apt.date) }}</span>
              </div>
            </div>
            <div class="appointment-card-body">
              <div class="d-flex align-items-center mb-2">
                <div class="doctor-avatar-sm me-2">{{ getInitials(apt.doctor) }}</div>
                <div>
                  <h6 class="mb-0 fw-bold">Dr. {{ apt.doctor }}</h6>
                  <small class="text-muted">{{ apt.doctor_specialization }} · {{ apt.department }}</small>
                </div>
              </div>
              <div class="apt-meta">
                <span><i class="bi bi-clock me-1"></i>{{ apt.time }}</span>
                <span :class="'apt-status apt-status-' + apt.status.toLowerCase()">
                  {{ apt.status }}
                </span>
              </div>
            </div>
            <div class="appointment-card-actions" v-if="apt.status.toLowerCase() === 'booked'">
              <button
                class="btn-icon-danger"
                @click="cancelAppointment(apt.id)"
                title="Cancel Appointment"
                :id="'cancel-apt-' + apt.id"
              >
                <i class="bi bi-x-circle"></i>
              </button>
            </div>
          </div>
          <div v-if="upcomingAppointments.length === 0" class="empty-state">
            <i class="bi bi-calendar-x display-1 text-muted opacity-25"></i>
            <p class="text-muted mt-3">No upcoming appointments</p>
            <button class="btn-glass btn-glass-primary" @click="openBookModal">
              <i class="bi bi-plus-lg me-2"></i>Book Your First Appointment
            </button>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════ -->
      <!-- TAB: PAST HISTORY                          -->
      <!-- ═══════════════════════════════════════════ -->
      <div v-if="activeTab === 'history'" class="tab-content fade-in" id="history-section">
        <div class="section-header mb-4">
          <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
            <div>
              <h4 class="section-title"><i class="bi bi-clock-history me-2"></i>Appointment History</h4>
              <p class="section-subtitle">Past appointments with diagnosis and prescription details</p>
            </div>
            <button class="btn-glass btn-glass-primary" @click="exportHistory" :disabled="exporting" id="export-history-btn">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-download me-2"></i>
              Export CSV
            </button>
          </div>
          <div v-if="exportMsg" class="alert alert-info mt-3 alert-sm">
            {{ exportMsg }}
          </div>
        </div>

        <div class="history-list">
          <div v-for="apt in pastAppointments" :key="apt.id" class="history-card">
            <div class="history-card-header">
              <div class="d-flex align-items-center gap-3">
                <div class="doctor-avatar-sm">{{ getInitials(apt.doctor) }}</div>
                <div>
                  <h6 class="mb-0 fw-bold">Dr. {{ apt.doctor }}</h6>
                  <small class="text-muted">{{ apt.doctor_specialization }} · {{ apt.department }}</small>
                </div>
              </div>
              <div class="text-end">
                <div class="fw-semibold">{{ formatDate(apt.date) }}</div>
                <small class="text-muted">{{ apt.time }}</small>
                <div>
                  <span :class="'apt-status apt-status-' + apt.status.toLowerCase()">{{ apt.status }}</span>
                </div>
              </div>
            </div>
            <div class="history-card-body" v-if="apt.diagnosis || apt.prescription || apt.notes">
              <div class="treatment-grid">
                <div class="treatment-item" v-if="apt.diagnosis">
                  <div class="treatment-icon treatment-icon-diag"><i class="bi bi-activity"></i></div>
                  <div>
                    <label>Diagnosis</label>
                    <p>{{ apt.diagnosis }}</p>
                  </div>
                </div>
                <div class="treatment-item" v-if="apt.prescription">
                  <div class="treatment-icon treatment-icon-rx"><i class="bi bi-capsule"></i></div>
                  <div>
                    <label>Prescription</label>
                    <p>{{ apt.prescription }}</p>
                  </div>
                </div>
                <div class="treatment-item" v-if="apt.notes">
                  <div class="treatment-icon treatment-icon-note"><i class="bi bi-journal-text"></i></div>
                  <div>
                    <label>Notes</label>
                    <p>{{ apt.notes }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="history-card-body text-muted small fst-italic">
              No treatment record available for this appointment.
            </div>
          </div>
          <div v-if="pastAppointments.length === 0" class="empty-state">
            <i class="bi bi-inbox display-1 text-muted opacity-25"></i>
            <p class="text-muted mt-3">No past appointments found</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════ -->
    <!-- MODAL: BOOK APPOINTMENT                    -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="modal fade" id="bookModal" tabindex="-1" ref="bookModalElement">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content glass-modal">
          <div class="modal-header glass-modal-header">
            <h5 class="modal-title fw-bold"><i class="bi bi-calendar-plus me-2"></i>Book Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="bookingError" class="alert alert-danger alert-sm d-flex align-items-center">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ bookingError }}
            </div>
            <div v-if="bookingSuccess" class="alert alert-success alert-sm d-flex align-items-center">
              <i class="bi bi-check-circle-fill me-2"></i>{{ bookingSuccess }}
            </div>
            <form @submit.prevent="bookAppointment">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold text-muted">Department</label>
                  <select class="form-select glass-input" v-model="newApt.department_id" required id="book-dept-select">
                    <option value="" disabled>Choose a department...</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold text-muted">Doctor</label>
                  <select class="form-select glass-input" v-model="newApt.doctor_id" :disabled="!newApt.department_id" required id="book-doctor-select">
                    <option value="" disabled>Choose a doctor...</option>
                    <option v-for="doc in bookingFilteredDoctors" :key="doc.id" :value="doc.id">
                      Dr. {{ doc.name }} ({{ doc.specialization }})
                    </option>
                  </select>
                </div>
                <div class="col-12" v-if="selectedBookingDoctor">
                  <div class="booking-avail-preview">
                    <label class="small fw-semibold text-muted mb-2 d-block">Dr. {{ selectedBookingDoctor.name }}'s Availability</label>
                    <div class="avail-week-grid compact">
                      <div
                        v-for="(dayName, idx) in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']"
                        :key="idx"
                        class="avail-week-cell"
                        :class="selectedBookingDoctor.availability && selectedBookingDoctor.availability[idx] === '1' ? 'avail-yes' : 'avail-no'"
                      >
                        {{ dayName }}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold text-muted">Date</label>
                  <input type="date" class="form-control glass-input" v-model="newApt.date" :min="todayStr" required id="book-date-input">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold text-muted">Time</label>
                  <input type="time" class="form-control glass-input" v-model="newApt.time" required id="book-time-input">
                </div>
                <!-- Day Availability Check -->
                <div class="col-12" v-if="selectedDoctorAvailInfo">
                  <div class="avail-check-msg" :class="selectedDoctorAvailInfo.ok ? 'avail-ok' : 'avail-bad'">
                    <i :class="selectedDoctorAvailInfo.ok ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'" class="me-2"></i>
                    {{ selectedDoctorAvailInfo.msg }}
                  </div>
                </div>
              </div>
              <button
                type="submit"
                class="btn-glass btn-glass-primary w-100 mt-4 py-3 fw-bold"
                :disabled="bookingLoading"
                id="confirm-booking-btn"
              >
                <span v-if="bookingLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-lg me-2"></i>
                Confirm Booking
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════ -->
    <!-- MODAL: EDIT PROFILE                        -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="modal fade" id="profileModal" tabindex="-1" ref="profileModalElement">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content glass-modal">
          <div class="modal-header glass-modal-header">
            <h5 class="modal-title fw-bold"><i class="bi bi-person-gear me-2"></i>Edit Profile</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="profileMsg" :class="'alert alert-sm ' + (profileMsgType === 'success' ? 'alert-success' : 'alert-danger')">
              {{ profileMsg }}
            </div>
            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label fw-semibold text-muted">Full Name</label>
                <input type="text" class="form-control glass-input" v-model="editProfile.name" required id="profile-name-input">
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-muted">Email</label>
                <input type="email" class="form-control glass-input" :value="profile.email" disabled id="profile-email-input">
                <small class="text-muted">Email cannot be changed</small>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-muted">Contact Number</label>
                <input type="text" class="form-control glass-input" v-model="editProfile.contact" id="profile-contact-input">
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-muted">New Password <small>(leave blank to keep current)</small></label>
                <input type="password" class="form-control glass-input" v-model="editProfile.password" id="profile-password-input">
              </div>
              <button
                type="submit"
                class="btn-glass btn-glass-primary w-100 py-3 fw-bold"
                :disabled="profileLoading"
                id="save-profile-btn"
              >
                <span v-if="profileLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-lg me-2"></i>
                Save Changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════ -->
    <!-- MODAL: DOCTOR PROFILE                      -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="modal fade" id="doctorProfileModal" tabindex="-1" ref="doctorProfileModalElement">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content glass-modal">
          <div class="modal-header glass-modal-header">
            <h5 class="modal-title fw-bold"><i class="bi bi-person-badge me-2"></i>Doctor Profile</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4" v-if="viewingDoctor">
            <div class="text-center mb-4">
              <div class="doctor-avatar-lg mx-auto mb-3">{{ getInitials(viewingDoctor.name) }}</div>
              <h4 class="fw-bold mb-1">Dr. {{ viewingDoctor.name }}</h4>
              <span class="badge-specialty">{{ viewingDoctor.specialization }}</span>
            </div>
            <div class="profile-detail">
              <label>Department</label>
              <span>{{ viewingDoctor.department_name }}</span>
            </div>
            <div class="profile-detail" v-if="viewingDoctor.contact">
              <label>Contact</label>
              <span>{{ viewingDoctor.contact }}</span>
            </div>
            <label class="profile-detail-label mt-3 mb-2">Weekly Availability</label>
            <div class="avail-week-grid">
              <div
                v-for="(dayName, idx) in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']"
                :key="idx"
                class="avail-week-cell"
                :class="viewingDoctor.availability && viewingDoctor.availability[idx] === '1' ? 'avail-yes' : 'avail-no'"
              >
                {{ dayName }}
              </div>
            </div>
            <button class="btn-glass btn-glass-primary w-100 mt-4" @click="bookWithDoctor(viewingDoctor)">
              <i class="bi bi-calendar-plus me-2"></i>Book Appointment with Dr. {{ viewingDoctor.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PatientDashboard',
  data() {
    return {
      // Modals
      bookModalInstance: null,
      profileModalInstance: null,
      doctorProfileModalInstance: null,
      // Tab state
      activeTab: 'appointments',
      tabs: [
        { key: 'appointments', label: 'My Appointments', short: 'Appts', icon: 'bi bi-calendar-check', badge: 0 },
        { key: 'doctors', label: 'Find Doctors', short: 'Doctors', icon: 'bi bi-person-badge', badge: null },
        { key: 'departments', label: 'Departments', short: 'Depts', icon: 'bi bi-building', badge: null },
        { key: 'history', label: 'History', short: 'History', icon: 'bi bi-clock-history', badge: null }
      ],
      // Data
      profile: { name: '', email: '', contact: '' },
      departments: [],
      doctors: [],
      appointments: [],
      // Filters
      doctorFilterDept: '',
      expandedDoctor: null,
      viewingDoctor: null,
      // Book form
      newApt: { department_id: '', doctor_id: '', date: '', time: '' },
      bookingError: '',
      bookingSuccess: '',
      bookingLoading: false,
      // Profile edit
      editProfile: { name: '', contact: '', password: '' },
      profileMsg: '',
      profileMsgType: 'success',
      profileLoading: false,
      // Search
      doctorSearchQuery: '',
      // Export
      exporting: false,
      exportMsg: ''
    }
  },
  computed: {
    todayStr() {
      return new Date().toISOString().split('T')[0];
    },
    upcomingAppointments() {
      const today = this.todayStr;
      return this.appointments.filter(a => {
        const s = a.status.toLowerCase();
        return s === 'booked' && a.date >= today;
      });
    },
    pastAppointments() {
      const today = this.todayStr;
      return this.appointments.filter(a => {
        const s = a.status.toLowerCase();
        return s === 'completed' || s === 'cancelled' || (s === 'booked' && a.date < today);
      });
    },
    upcomingCount() {
      return this.upcomingAppointments.length;
    },
    completedCount() {
      return this.appointments.filter(a => a.status.toLowerCase() === 'completed').length;
    },
    treatmentsCount() {
      return this.appointments.filter(a => a.diagnosis).length;
    },
    filteredDoctors() {
      let list = this.doctors;
      if (this.doctorFilterDept) {
         list = list.filter(d => d.department_id === this.doctorFilterDept);
      }
      if (this.doctorSearchQuery) {
         const q = this.doctorSearchQuery.toLowerCase();
         list = list.filter(d => 
            (d.name && d.name.toLowerCase().includes(q)) || 
            (d.specialization && d.specialization.toLowerCase().includes(q)) || 
            (d.department_name && d.department_name.toLowerCase().includes(q))
         );
      }
      return list;
    },
    bookingFilteredDoctors() {
      if (!this.newApt.department_id) return [];
      return this.doctors.filter(d => d.department_id === this.newApt.department_id);
    },
    selectedBookingDoctor() {
      if (!this.newApt.doctor_id) return null;
      return this.doctors.find(d => d.id === this.newApt.doctor_id) || null;
    },
    selectedDoctorAvailInfo() {
      if (!this.newApt.doctor_id || !this.newApt.date) return null;
      const doctor = this.doctors.find(d => d.id === this.newApt.doctor_id);
      if (!doctor || !doctor.availability || doctor.availability.length !== 7) return null;
      const date = new Date(this.newApt.date);
      const jsDay = date.getDay();
      const dayIndex = jsDay === 0 ? 6 : jsDay - 1;
      const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      const available = dayNames.filter((d, i) => doctor.availability[i] === '1').join(', ');
      if (doctor.availability[dayIndex] === '1') {
        return { ok: true, msg: `Doctor is available on ${dayNames[dayIndex]}. Available days: ${available}` };
      } else {
        return { ok: false, msg: `Doctor is NOT available on ${dayNames[dayIndex]}. Available days: ${available || 'None'}` };
      }
    },
    next7Days() {
      const days = [];
      const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      const pyDayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      for (let i = 0; i < 7; i++) {
        const d = new Date();
        d.setDate(d.getDate() + i);
        const jsDay = d.getDay();
        const pyDay = jsDay === 0 ? 6 : jsDay - 1;
        days.push({
          dateStr: d.toISOString().split('T')[0],
          dayShort: dayLabels[jsDay],
          dayName: pyDayLabels[pyDay],
          dateShort: d.getDate() + '/' + (d.getMonth() + 1),
          dayIndex: pyDay
        });
      }
      return days;
    }
  },
  async mounted() {
    if (window.bootstrap) {
      this.bookModalInstance = new window.bootstrap.Modal(this.$refs.bookModalElement);
      this.profileModalInstance = new window.bootstrap.Modal(this.$refs.profileModalElement);
      this.doctorProfileModalInstance = new window.bootstrap.Modal(this.$refs.doctorProfileModalElement);
    }
    await this.fetchAll();
  },
  methods: {
    async fetchAll() {
      const token = localStorage.getItem('access_token');
      if (!token) return;
      const headers = { 'Authorization': `Bearer ${token}` };

      try {
        // Fetch profile
        const resProfile = await fetch('http://localhost:5000/patient/profile', { headers });
        if (resProfile.ok) {
          this.profile = await resProfile.json();
          this.editProfile.name = this.profile.name;
          this.editProfile.contact = this.profile.contact;
        }

        // Fetch appointments (includes treatment data now)
        const resApt = await fetch('http://localhost:5000/patient/dashboard', { headers });
        if (resApt.ok) {
          this.appointments = await resApt.json();
        }

        // Fetch departments
        const resDept = await fetch('http://localhost:5000/patient/departments', { headers });
        if (resDept.ok) this.departments = await resDept.json();

        // Fetch doctors
        const resDocs = await fetch('http://localhost:5000/patient/doctors', { headers });
        if (resDocs.ok) this.doctors = await resDocs.json();

        // Update tab badge
        this.tabs[0].badge = this.upcomingCount || null;
      } catch (err) {
        console.error('Fetch error:', err);
      }
    },
    // ─── Helpers ──────────────────────────────────
    getInitials(name) {
      if (!name) return '??';
      const parts = name.split(' ');
      if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
      return (parts[0][0] + parts[1][0]).toUpperCase();
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    },
    getMonth(dateStr) {
      return new Date(dateStr).toLocaleDateString(undefined, { month: 'short' });
    },
    getDay(dateStr) {
      return new Date(dateStr).getDate();
    },
    getYear(dateStr) {
      return new Date(dateStr).getFullYear();
    },
    isDoctorAvailable(doc, pyDayIndex) {
      if (!doc.availability || doc.availability.length !== 7) return false;
      return doc.availability[pyDayIndex] === '1';
    },
    getDoctorCountForDept(deptId) {
      return this.doctors.filter(d => d.department_id === deptId).length;
    },
    getDeptIcon(name) {
      const n = (name || '').toLowerCase();
      if (n.includes('cardio') || n.includes('heart')) return 'bi bi-heart-pulse';
      if (n.includes('neuro') || n.includes('brain')) return 'bi bi-cpu';
      if (n.includes('ortho') || n.includes('bone')) return 'bi bi-bandaid';
      if (n.includes('pediatr') || n.includes('child')) return 'bi bi-emoji-smile';
      if (n.includes('derma') || n.includes('skin')) return 'bi bi-droplet';
      if (n.includes('ent') || n.includes('ear')) return 'bi bi-ear';
      if (n.includes('eye') || n.includes('ophthal')) return 'bi bi-eye';
      if (n.includes('dent') || n.includes('oral')) return 'bi bi-emoji-laughing';
      if (n.includes('surg')) return 'bi bi-scissors';
      if (n.includes('general') || n.includes('medicine')) return 'bi bi-plus-circle';
      return 'bi bi-hospital';
    },
    filterDoctorsByDept(dept) {
      this.doctorFilterDept = dept.id;
      this.activeTab = 'doctors';
    },
    toggleDoctorProfile(docId) {
      this.expandedDoctor = this.expandedDoctor === docId ? null : docId;
    },
    // ─── Doctor Profile Modal ─────────────────────
    openDoctorProfile(doc) {
      this.viewingDoctor = doc;
      if (this.doctorProfileModalInstance) this.doctorProfileModalInstance.show();
    },
    bookWithDoctor(doc) {
      if (this.doctorProfileModalInstance) this.doctorProfileModalInstance.hide();
      this.newApt.department_id = doc.department_id;
      this.newApt.doctor_id = doc.id;
      this.newApt.date = '';
      this.newApt.time = '';
      this.bookingError = '';
      this.bookingSuccess = '';
      setTimeout(() => {
        if (this.bookModalInstance) this.bookModalInstance.show();
      }, 300);
    },
    // ─── Booking ──────────────────────────────────
    openBookModal() {
      this.newApt = { department_id: '', doctor_id: '', date: '', time: '' };
      this.bookingError = '';
      this.bookingSuccess = '';
      if (this.bookModalInstance) this.bookModalInstance.show();
    },
    async bookAppointment() {
      this.bookingError = '';
      this.bookingSuccess = '';
      if (this.newApt.date && this.newApt.date < this.todayStr) {
        this.bookingError = 'Cannot book an appointment in the past.';
        return;
      }
      this.bookingLoading = true;
      const token = localStorage.getItem('access_token');
      try {
        const res = await fetch('http://localhost:5000/patient/appointment', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            doctor_id: this.newApt.doctor_id,
            date: this.newApt.date,
            time: this.newApt.time
          })
        });
        const data = await res.json();
        if (res.ok) {
          this.bookingSuccess = 'Appointment booked successfully!';
          await this.fetchAll();
          setTimeout(() => {
            if (this.bookModalInstance) this.bookModalInstance.hide();
            this.bookingSuccess = '';
          }, 1500);
        } else {
          this.bookingError = data.msg || 'Failed to book appointment';
        }
      } catch (err) {
        this.bookingError = 'Network error. Please try again.';
      } finally {
        this.bookingLoading = false;
      }
    },
    // ─── Cancel ───────────────────────────────────
    async cancelAppointment(id) {
      if (!confirm('Are you sure you want to cancel this appointment?')) return;
      const token = localStorage.getItem('access_token');
      try {
        const res = await fetch(`http://localhost:5000/patient/appointment/${id}/cancel`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          await this.fetchAll();
        } else {
          const data = await res.json();
          alert(data.msg || 'Failed to cancel');
        }
      } catch (err) {
        alert('Network error');
      }
    },
    // ─── Profile ──────────────────────────────────
    openProfileModal() {
      this.editProfile.name = this.profile.name;
      this.editProfile.contact = this.profile.contact;
      this.editProfile.password = '';
      this.profileMsg = '';
      if (this.profileModalInstance) this.profileModalInstance.show();
    },
    async updateProfile() {
      this.profileMsg = '';
      this.profileLoading = true;
      const token = localStorage.getItem('access_token');
      const body = {
        name: this.editProfile.name,
        contact: this.editProfile.contact
      };
      if (this.editProfile.password) body.password = this.editProfile.password;
      try {
        const res = await fetch('http://localhost:5000/patient/profile', {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
          this.profileMsg = 'Profile updated successfully!';
          this.profileMsgType = 'success';
          await this.fetchAll();
          setTimeout(() => {
            if (this.profileModalInstance) this.profileModalInstance.hide();
            this.profileMsg = '';
          }, 1500);
        } else {
          this.profileMsg = data.msg || 'Failed to update';
          this.profileMsgType = 'error';
        }
      } catch (err) {
        this.profileMsg = 'Network error';
        this.profileMsgType = 'error';
      } finally {
        this.profileLoading = false;
      }
    },
    // ─── Export ───────────────────────────────────
    async exportHistory() {
      this.exporting = true;
      this.exportMsg = '';
      const token = localStorage.getItem('access_token');
      try {
        const res = await fetch('http://localhost:5000/patient/export-history', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
          this.exportMsg = data.msg || 'Export job started!';
        } else {
          this.exportMsg = data.msg || 'Failed to start export';
        }
      } catch (err) {
        this.exportMsg = 'Network error during export request';
      } finally {
        this.exporting = false;
      }
    }
  }
}
</script>

<style scoped>
/* ═══════════════════════════════════════════
   DESIGN SYSTEM TOKENS
   ═══════════════════════════════════════════ */
.patient-dashboard {
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

  min-height: 100vh;
  color: var(--pd-text);
  position: relative;
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}



.container-fluid { position: relative; z-index: 1; }

/* ═══════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════ */
.fade-in {
  animation: fadeInUp 0.5s ease-out;
}
.stagger-in > * {
  animation: fadeInUp 0.5s ease-out both;
}
.stagger-in > *:nth-child(1) { animation-delay: 0.05s; }
.stagger-in > *:nth-child(2) { animation-delay: 0.1s; }
.stagger-in > *:nth-child(3) { animation-delay: 0.15s; }
.stagger-in > *:nth-child(4) { animation-delay: 0.2s; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.slide-down-enter-active { transition: all 0.35s ease; }
.slide-down-leave-active { transition: all 0.25s ease; }
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0; max-height: 0; padding-top: 0; padding-bottom: 0; overflow: hidden;
}
.slide-down-enter-to, .slide-down-leave-from {
  opacity: 1; max-height: 400px;
}

/* ═══════════════════════════════════════════
   WELCOME CARD
   ═══════════════════════════════════════════ */
.welcome-card {
  background: #ffffff;
  border: 1px solid var(--pd-border);
  border-left: 5px solid var(--pd-primary);
  border-radius: var(--pd-radius);
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}
.welcome-decor {
  position: absolute;
  top: -40px; right: -40px;
  width: 180px; height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(79,70,229,0.1) 0%, transparent 70%);
  pointer-events: none;
}
.welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--pd-text);
}
.text-gradient {
  background: linear-gradient(135deg, var(--pd-primary-light), var(--pd-info));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.welcome-subtitle {
  color: var(--pd-text-muted);
  font-size: 0.95rem;
}

/* ═══════════════════════════════════════════
   GLASS BUTTONS
   ═══════════════════════════════════════════ */
.btn-glass {
  display: inline-flex;
  align-items: center;
  padding: 10px 20px;
  border: 1px solid var(--pd-border);
  border-radius: 50px;
  background: var(--pd-surface);
  color: var(--pd-text);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.25s ease;
  backdrop-filter: blur(10px);
  text-decoration: none;
}
.btn-glass:hover {
  background: var(--pd-surface-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.btn-glass-primary {
  background: linear-gradient(135deg, var(--pd-primary), var(--pd-primary-dark));
  border-color: rgba(79,70,229,0.4);
  color: #fff;
}
.btn-glass-primary:hover {
  background: linear-gradient(135deg, var(--pd-primary-light), var(--pd-primary));
  box-shadow: 0 4px 20px rgba(79,70,229,0.4);
}

.btn-icon {
  width: 38px; height: 38px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--pd-border);
  border-radius: 10px;
  background: var(--pd-surface);
  color: var(--pd-primary-light);
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
  flex-shrink: 0;
}
.btn-icon:hover {
  background: var(--pd-primary);
  color: #fff;
  border-color: var(--pd-primary);
}

.btn-icon-danger {
  width: 38px; height: 38px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 10px;
  background: rgba(239,68,68,0.1);
  color: var(--pd-danger);
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
  flex-shrink: 0;
}
.btn-icon-danger:hover {
  background: var(--pd-danger);
  color: #fff;
}

/* ═══════════════════════════════════════════
   STAT CARDS
   ═══════════════════════════════════════════ */
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: var(--pd-radius-sm);
  border: 1px solid var(--pd-border);
  background: var(--pd-surface);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
  border-color: rgba(255,255,255,0.12);
}
.stat-icon {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px;
  font-size: 1.4rem;
  flex-shrink: 0;
}
.stat-upcoming .stat-icon { background: rgba(79,70,229,0.15); color: var(--pd-primary-light); }
.stat-completed .stat-icon { background: rgba(16,185,129,0.15); color: var(--pd-success); }
.stat-treatments .stat-icon { background: rgba(245,158,11,0.15); color: var(--pd-warning); }
.stat-departments .stat-icon { background: rgba(6,182,212,0.15); color: var(--pd-info); }

.stat-info { display: flex; flex-direction: column; }
.stat-number { font-size: 1.5rem; font-weight: 800; line-height: 1; }
.stat-label { font-size: 0.78rem; color: var(--pd-text-muted); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }

/* ═══════════════════════════════════════════
   TAB NAVIGATION
   ═══════════════════════════════════════════ */
.tab-nav-container {
  display: flex;
  gap: 6px;
  padding: 6px;
  background: var(--pd-surface);
  border: 1px solid var(--pd-border);
  border-radius: 50px;
  overflow-x: auto;
  backdrop-filter: blur(10px);
}
.tab-btn {
  flex: 1;
  min-width: max-content;
  padding: 10px 20px;
  border: none;
  border-radius: 50px;
  background: transparent;
  color: var(--pd-text-muted);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  position: relative;
  white-space: nowrap;
}
.tab-btn:hover { color: var(--pd-text); background: var(--pd-surface-hover); }
.tab-btn.active {
  background: linear-gradient(135deg, var(--pd-primary), var(--pd-primary-dark));
  color: #ffffff !important;
  box-shadow: 0 4px 15px rgba(79,70,229,0.3);
}
.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 50px;
  background: rgba(255,255,255,0.2);
  font-size: 0.7rem;
  font-weight: 700;
}
.tab-btn:not(.active) .tab-badge {
  background: rgba(79,70,229,0.15);
  color: var(--pd-primary);
}

/* ═══════════════════════════════════════════
   SECTION HEADERS
   ═══════════════════════════════════════════ */
.section-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--pd-text);
  margin-bottom: 4px;
}
.section-subtitle {
  font-size: 0.9rem;
  color: var(--pd-text-muted);
  margin-bottom: 0;
}

/* ═══════════════════════════════════════════
   DEPARTMENT CARDS
   ═══════════════════════════════════════════ */
.dept-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: var(--pd-radius-sm);
  border: 1px solid var(--pd-border);
  background: var(--pd-surface);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}
.dept-card:hover {
  border-color: rgba(79,70,229,0.3);
  background: var(--pd-surface-hover);
  transform: translateX(4px);
}
.dept-icon-wrap {
  width: 50px; height: 50px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(79,70,229,0.15), rgba(6,182,212,0.1));
  color: var(--pd-primary-light);
  font-size: 1.3rem;
  flex-shrink: 0;
}
.dept-info { flex: 1; min-width: 0; }
.dept-name { font-weight: 700; font-size: 0.95rem; margin-bottom: 2px; color: var(--pd-text); }
.dept-desc { font-size: 0.8rem; color: var(--pd-text-muted); margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dept-doctors-count { font-size: 0.75rem; color: var(--pd-primary-light); font-weight: 600; }
.dept-arrow { color: var(--pd-text-muted); font-size: 0.9rem; transition: all 0.2s; }
.dept-card:hover .dept-arrow { color: var(--pd-primary-light); transform: translateX(3px); }

/* ═══════════════════════════════════════════
   DOCTOR CARDS / AVAILABILITY
   ═══════════════════════════════════════════ */
.week-header {
  display: flex;
  gap: 6px;
  padding-left: 280px;
  padding-right: 48px;
}
.week-day-label {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.week-day-name { font-size: 0.7rem; font-weight: 700; color: var(--pd-text-muted); text-transform: uppercase; }
.week-day-date { font-size: 0.7rem; color: var(--pd-text-muted); opacity: 0.6; }

.doctor-list { display: flex; flex-direction: column; gap: 8px; }

.doctor-card {
  border-radius: var(--pd-radius-sm);
  border: 1px solid var(--pd-border);
  background: var(--pd-surface);
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}
.doctor-card:hover { border-color: rgba(79,70,229,0.3); }

.doctor-card-main {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  cursor: pointer;
}

.doctor-avatar {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--pd-primary), var(--pd-primary-dark));
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
  flex-shrink: 0;
  letter-spacing: 1px;
}
.doctor-avatar-sm {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--pd-primary), var(--pd-primary-dark));
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.doctor-avatar-lg {
  width: 80px; height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--pd-primary), var(--pd-primary-dark));
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800;
  font-size: 1.5rem;
  letter-spacing: 2px;
}

.doctor-info {
  min-width: 180px;
  flex-shrink: 0;
}
.doctor-name { font-weight: 700; font-size: 0.9rem; margin-bottom: 0; color: var(--pd-text); }
.doctor-specialty { font-size: 0.78rem; color: var(--pd-primary-light); display: block; }
.doctor-dept { font-size: 0.72rem; color: var(--pd-text-muted); display: block; }

.doctor-availability-row {
  display: flex;
  gap: 6px;
  flex: 1;
  justify-content: space-around;
}

.avail-dot {
  width: 28px; height: 28px;
  border-radius: 8px;
  transition: all 0.2s;
}
.avail-dot.available {
  background: rgba(16,185,129,0.2);
  border: 1.5px solid rgba(16,185,129,0.5);
}
.avail-dot.unavailable {
  background: rgba(239,68,68,0.1);
  border: 1.5px solid rgba(239,68,68,0.2);
}

.doctor-profile-expanded {
  padding: 20px;
  border-top: 1px solid var(--pd-border);
  background: rgba(79,70,229,0.03);
}

.profile-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--pd-border);
}
.profile-detail:last-of-type { border-bottom: none; }
.profile-detail label { font-size: 0.8rem; color: var(--pd-text-muted); font-weight: 600; }
.profile-detail span { font-weight: 600; font-size: 0.9rem; color: var(--pd-text); }
.profile-detail-label { font-size: 0.8rem; color: var(--pd-text-muted); font-weight: 600; display: block; }

.avail-week-grid {
  display: flex;
  gap: 6px;
}
.avail-week-grid.compact { gap: 4px; }
.avail-week-cell {
  flex: 1;
  text-align: center;
  padding: 8px 4px;
  border-radius: var(--pd-radius-xs);
  font-size: 0.75rem;
  font-weight: 700;
  transition: all 0.2s;
}
.avail-week-cell.avail-yes {
  background: rgba(16,185,129,0.15);
  color: var(--pd-success);
  border: 1px solid rgba(16,185,129,0.3);
}
.avail-week-cell.avail-no {
  background: rgba(239,68,68,0.08);
  color: rgba(239,68,68,0.5);
  border: 1px solid rgba(239,68,68,0.15);
}

.badge-specialty {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 50px;
  background: rgba(79,70,229,0.15);
  color: var(--pd-primary-light);
  font-size: 0.8rem;
  font-weight: 600;
}

/* ═══════════════════════════════════════════
   APPOINTMENTS
   ═══════════════════════════════════════════ */
.appointments-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.appointment-card {
  display: flex;
  align-items: stretch;
  gap: 0;
  border-radius: var(--pd-radius-sm);
  border: 1px solid var(--pd-border);
  background: var(--pd-surface);
  overflow: hidden;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}
.appointment-card:hover {
  border-color: rgba(79,70,229,0.3);
  transform: translateX(4px);
}

.appointment-card-left {
  display: flex;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(79,70,229,0.05));
  border-right: 1px solid var(--pd-border);
}
.apt-date-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 56px;
}
.apt-month { font-size: 0.7rem; text-transform: uppercase; font-weight: 700; color: var(--pd-primary-light); letter-spacing: 1px; }
.apt-day { font-size: 1.6rem; font-weight: 800; line-height: 1; color: var(--pd-text); }
.apt-year { font-size: 0.65rem; color: var(--pd-text-muted); }

.appointment-card-body {
  flex: 1;
  padding: 16px 20px;
}
.apt-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.82rem;
  color: var(--pd-text-muted);
}

.apt-status {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 50px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.apt-status-booked { background: rgba(79,70,229,0.15); color: var(--pd-primary-light); }
.apt-status-completed { background: rgba(16,185,129,0.15); color: var(--pd-success); }
.apt-status-cancelled { background: rgba(239,68,68,0.12); color: var(--pd-danger); }

.appointment-card-actions {
  display: flex;
  align-items: center;
  padding: 0 16px;
}

/* ═══════════════════════════════════════════
   HISTORY
   ═══════════════════════════════════════════ */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  border-radius: var(--pd-radius-sm);
  border: 1px solid var(--pd-border);
  background: var(--pd-surface);
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.history-card:hover {
  border-color: rgba(255,255,255,0.12);
}

.history-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.history-card-body {
  padding: 16px 20px;
  border-top: 1px solid var(--pd-border);
}

.treatment-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.treatment-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.treatment-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
  font-size: 1rem;
}
.treatment-icon-diag { background: rgba(245,158,11,0.15); color: var(--pd-warning); }
.treatment-icon-rx { background: rgba(79,70,229,0.15); color: var(--pd-primary-light); }
.treatment-icon-note { background: rgba(6,182,212,0.15); color: var(--pd-info); }

.treatment-item label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--pd-text-muted);
  margin-bottom: 2px;
  display: block;
}
.treatment-item p {
  font-size: 0.88rem;
  color: var(--pd-text);
  margin-bottom: 0;
  line-height: 1.5;
}

/* ═══════════════════════════════════════════
   MODALS (Glass)
   ═══════════════════════════════════════════ */
.glass-modal {
  background: var(--pd-surface);
  border: 1px solid var(--pd-border);
  border-radius: var(--pd-radius) !important;
  overflow: hidden;
  color: var(--pd-text);
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}
.glass-modal-header {
  background: var(--pd-surface);
  border-bottom: 1px solid var(--pd-border);
  padding: 18px 24px;
}
.glass-modal-header .modal-title {
  color: var(--pd-text);
}
.glass-input {
  background: var(--pd-bg) !important;
  border: 1px solid var(--pd-border) !important;
  color: var(--pd-text) !important;
  border-radius: var(--pd-radius-xs) !important;
}
.glass-input:focus {
  background: var(--pd-surface) !important;
  border-color: var(--pd-primary) !important;
  box-shadow: 0 0 0 3px rgba(79,70,229,0.15) !important;
}
.glass-input:disabled {
  opacity: 0.6;
  background: #e2e8f0 !important;
}

.avail-check-msg {
  padding: 10px 16px;
  border-radius: var(--pd-radius-xs);
  font-size: 0.85rem;
  font-weight: 600;
}
.avail-check-msg.avail-ok {
  background: rgba(16,185,129,0.1);
  border: 1px solid rgba(16,185,129,0.3);
  color: var(--pd-success);
}
.avail-check-msg.avail-bad {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.3);
  color: var(--pd-danger);
}

.booking-avail-preview {
  padding: 12px 16px;
  border-radius: var(--pd-radius-xs);
  background: rgba(79,70,229,0.05);
  border: 1px solid var(--pd-border);
}

/* ═══════════════════════════════════════════
   FILTER SELECT
   ═══════════════════════════════════════════ */
.filter-select {
  padding: 10px 16px;
  border: 1px solid var(--pd-border);
  border-radius: 50px;
  background: var(--pd-surface);
  color: var(--pd-text);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  appearance: auto;
  min-width: 160px;
  backdrop-filter: blur(10px);
}
.filter-select:focus {
  outline: none;
  border-color: var(--pd-primary);
}
.filter-select option {
  background: var(--pd-surface);
  color: var(--pd-text);
}

/* ═══════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

/* ═══════════════════════════════════════════
   ALERTS
   ═══════════════════════════════════════════ */
.alert-sm {
  font-size: 0.85rem;
  padding: 10px 16px;
  border-radius: var(--pd-radius-xs);
}

/* ═══════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════ */
@media (max-width: 992px) {
  .week-header { display: none; }
  .doctor-availability-row { display: none; }
  .doctor-info { min-width: auto; }
}

@media (max-width: 768px) {
  .welcome-card { padding: 20px; }
  .welcome-title { font-size: 1.25rem; }
}
</style>
