<template>
  <div class="admin-dashboard py-4">
    <div class="container-fluid px-3 px-md-4">
      <!-- Header -->
      <div class="admin-header mb-4">
        <div class="admin-header-text">
          <h2 class="fw-bold text-dark mb-1">Admin Dashboard</h2>
          <p class="text-muted mb-0">Manage hospital data &amp; operations</p>
        </div>
        <div class="admin-header-search">
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
            <input 
              type="text" 
              class="form-control border-start-0 ps-0" 
              placeholder="Search doctors, patients, users..." 
              v-model="globalSearch"
              @input="handleGlobalSearch"
            >
            <button v-if="globalSearch" class="btn btn-outline-secondary border-start-0 bg-white" @click="globalSearch = ''; searchResults = []">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Search Results Overlay -->
      <div v-if="searchResults.length > 0" class="card shadow-sm border-0 mb-4 search-results-card">
        <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
          <h6 class="mb-0 fw-bold"><i class="bi bi-search me-2 text-primary"></i>Search Results ({{ searchResults.length }})</h6>
          <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="searchResults = []; globalSearch = ''">
            <i class="bi bi-x-lg me-1"></i>Close
          </button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="text-secondary fw-semibold">Name</th>
                  <th class="text-secondary fw-semibold">Email</th>
                  <th class="text-secondary fw-semibold">Role</th>
                  <th class="text-secondary fw-semibold">Specialization</th>
                  <th class="text-secondary fw-semibold">Department</th>
                  <th class="text-secondary fw-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in searchResults" :key="r.id">
                  <td class="fw-semibold">{{ r.name || 'N/A' }}</td>
                  <td class="text-muted small">{{ r.username }}</td>
                  <td><span :class="getRoleBadge(r.role)">{{ r.role }}</span></td>
                  <td>{{ r.specialization || '—' }}</td>
                  <td>{{ r.department || '—' }}</td>
                  <td>
                    <span v-if="r.is_blacklisted" class="badge bg-danger bg-opacity-10 text-danger rounded-pill px-2 py-1">Blacklisted</span>
                    <span v-else class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1">Active</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Stats Cards Row -->
      <div class="row g-2 g-md-3 mb-4 stats-row">
        <div class="col-6 col-sm-4 col-lg-2">
          <div class="card stat-card border-0 shadow-sm h-100">
            <div class="card-body text-center py-3">
              <div class="stat-icon bg-primary bg-opacity-10 text-primary mx-auto mb-2"><i class="bi bi-heart-pulse-fill"></i></div>
              <h3 class="fw-bold mb-0">{{ stats.total_doctors }}</h3>
              <small class="text-muted">Doctors</small>
            </div>
          </div>
        </div>
        <div class="col-6 col-sm-4 col-lg-2">
          <div class="card stat-card border-0 shadow-sm h-100">
            <div class="card-body text-center py-3">
              <div class="stat-icon bg-success bg-opacity-10 text-success mx-auto mb-2"><i class="bi bi-people-fill"></i></div>
              <h3 class="fw-bold mb-0">{{ stats.total_patients }}</h3>
              <small class="text-muted">Patients</small>
            </div>
          </div>
        </div>
        <div class="col-6 col-sm-4 col-lg-2">
          <div class="card stat-card border-0 shadow-sm h-100">
            <div class="card-body text-center py-3">
              <div class="stat-icon bg-info bg-opacity-10 text-info mx-auto mb-2"><i class="bi bi-calendar-check-fill"></i></div>
              <h3 class="fw-bold mb-0">{{ stats.total_appointments }}</h3>
              <small class="text-muted">Total Appts</small>
            </div>
          </div>
        </div>
        <div class="col-6 col-sm-4 col-lg-2">
          <div class="card stat-card border-0 shadow-sm h-100">
            <div class="card-body text-center py-3">
              <div class="stat-icon bg-warning bg-opacity-10 text-warning mx-auto mb-2"><i class="bi bi-clock-fill"></i></div>
              <h3 class="fw-bold mb-0">{{ stats.upcoming_appointments }}</h3>
              <small class="text-muted">Upcoming</small>
            </div>
          </div>
        </div>
        <div class="col-6 col-sm-4 col-lg-2">
          <div class="card stat-card border-0 shadow-sm h-100">
            <div class="card-body text-center py-3">
              <div class="stat-icon bg-secondary bg-opacity-10 text-secondary mx-auto mb-2"><i class="bi bi-check-circle-fill"></i></div>
              <h3 class="fw-bold mb-0">{{ stats.past_appointments }}</h3>
              <small class="text-muted">Past</small>
            </div>
          </div>
        </div>
        <div class="col-6 col-sm-4 col-lg-2">
          <div class="card stat-card border-0 shadow-sm h-100">
            <div class="card-body text-center py-3">
              <div class="stat-icon bg-danger bg-opacity-10 text-danger mx-auto mb-2"><i class="bi bi-slash-circle-fill"></i></div>
              <h3 class="fw-bold mb-0">{{ stats.blacklisted_users }}</h3>
              <small class="text-muted">Blacklisted</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-pills mb-4 bg-white p-2 rounded shadow-sm flex-nowrap admin-tabs">
        <li class="nav-item" v-for="tab in tabs" :key="tab.id">
          <button 
            class="nav-link rounded-pill fw-semibold px-3 px-md-4 py-2 text-nowrap" 
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <i :class="tab.icon + ' me-1 me-md-2'"></i>
            <span class="tab-label">{{ tab.name }}</span>
            <span v-if="tab.count !== undefined" class="badge bg-white bg-opacity-25 ms-1 rounded-pill d-none d-sm-inline">{{ tab.count }}</span>
          </button>
        </li>
      </ul>

      <!-- ============== DOCTORS TAB ============== -->
      <div v-if="activeTab === 'doctors'">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center mb-2 mb-md-0">
              <h5 class="mb-0 fw-bold text-primary"><i class="bi bi-heart-pulse-fill me-2"></i>Doctors</h5>
              <button class="btn btn-primary btn-sm rounded-pill px-3" @click="openDoctorModal(null)">
                <i class="bi bi-plus-lg me-1"></i><span class="d-none d-sm-inline">Add Doctor</span><span class="d-sm-none">Add</span>
              </button>
            </div>
            <div class="d-flex gap-2 mt-2 flex-wrap">
              <input type="text" class="form-control form-control-sm filter-input" placeholder="Filter doctors..." v-model="doctorFilter">
              <select class="form-select form-select-sm filter-select" v-model="doctorDeptFilter">
                <option value="">All Departments</option>
                <option v-for="d in departmentsData" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- Desktop table view -->
            <div class="table-responsive d-none d-md-block">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="text-secondary fw-semibold">Name</th>
                    <th class="text-secondary fw-semibold">Email</th>
                    <th class="text-secondary fw-semibold">Department</th>
                    <th class="text-secondary fw-semibold">Specialization</th>
                    <th class="text-secondary fw-semibold">Availability</th>
                    <th class="text-secondary fw-semibold">Status</th>
                    <th class="text-end text-secondary fw-semibold pe-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="filteredDoctorsList.length === 0">
                    <td colspan="7" class="text-center py-4 text-muted">No doctors found.</td>
                  </tr>
                  <tr v-for="doc in filteredDoctorsList" :key="doc.id">
                    <td class="fw-semibold">{{ doc.name || 'N/A' }}</td>
                    <td class="text-muted small">{{ doc.username }}</td>
                    <td><span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-2 py-1">{{ doc.department_name }}</span></td>
                    <td>{{ doc.specialization }}</td>
                    <td class="small text-muted">{{ formatAvail(doc.availability) }}</td>
                    <td>
                      <span v-if="doc.is_blacklisted" class="badge bg-danger bg-opacity-10 text-danger rounded-pill px-2 py-1">Blacklisted</span>
                      <span v-else class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1">Active</span>
                    </td>
                    <td class="text-end pe-4">
                      <button class="btn btn-sm btn-outline-secondary me-1 rounded-circle" @click="openDoctorModal(doc)" title="Edit">
                        <i class="bi bi-pencil-fill"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-warning me-1 rounded-circle" @click="toggleDoctorBlacklist(doc)" :title="doc.is_blacklisted ? 'Unblock' : 'Blacklist'">
                        <i :class="doc.is_blacklisted ? 'bi bi-unlock-fill' : 'bi bi-slash-circle'"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger rounded-circle" @click="deleteDoctor(doc.id)" title="Delete">
                        <i class="bi bi-trash-fill"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Mobile card view -->
            <div class="d-md-none mobile-card-list">
              <div v-if="filteredDoctorsList.length === 0" class="text-center py-4 text-muted">No doctors found.</div>
              <div v-for="doc in filteredDoctorsList" :key="'m-doc-' + doc.id" class="mobile-card">
                <div class="mobile-card-header">
                  <div>
                    <div class="fw-semibold">{{ doc.name || 'N/A' }}</div>
                    <div class="text-muted small">{{ doc.username }}</div>
                  </div>
                  <div>
                    <span v-if="doc.is_blacklisted" class="badge bg-danger bg-opacity-10 text-danger rounded-pill px-2 py-1">Blacklisted</span>
                    <span v-else class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1">Active</span>
                  </div>
                </div>
                <div class="mobile-card-body">
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Department</span>
                    <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-2 py-1">{{ doc.department_name }}</span>
                  </div>
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Specialization</span>
                    <span>{{ doc.specialization }}</span>
                  </div>
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Availability</span>
                    <span class="small text-muted">{{ formatAvail(doc.availability) }}</span>
                  </div>
                </div>
                <div class="mobile-card-actions">
                  <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="openDoctorModal(doc)"><i class="bi bi-pencil-fill me-1"></i>Edit</button>
                  <button class="btn btn-sm btn-outline-warning rounded-pill" @click="toggleDoctorBlacklist(doc)"><i :class="doc.is_blacklisted ? 'bi bi-unlock-fill me-1' : 'bi bi-slash-circle me-1'"></i>{{ doc.is_blacklisted ? 'Unblock' : 'Block' }}</button>
                  <button class="btn btn-sm btn-outline-danger rounded-pill" @click="deleteDoctor(doc.id)"><i class="bi bi-trash-fill me-1"></i>Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============== PATIENTS TAB ============== -->
      <div v-if="activeTab === 'patients'">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center mb-2 mb-md-0">
              <h5 class="mb-0 fw-bold text-success"><i class="bi bi-person-badge me-2"></i>Patients</h5>
              <button class="btn btn-success btn-sm rounded-pill px-3" @click="openPatientModal(null)">
                <i class="bi bi-plus-lg me-1"></i><span class="d-none d-sm-inline">Add Patient</span><span class="d-sm-none">Add</span>
              </button>
            </div>
            <div class="d-flex gap-2 mt-2">
              <input type="text" class="form-control form-control-sm filter-input" placeholder="Filter patients..." v-model="patientFilter">
            </div>
          </div>
          <div class="card-body p-0">
            <!-- Desktop table -->
            <div class="table-responsive d-none d-md-block">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="text-secondary fw-semibold">Name</th>
                    <th class="text-secondary fw-semibold">Email</th>
                    <th class="text-secondary fw-semibold">Contact</th>
                    <th class="text-secondary fw-semibold">Status</th>
                    <th class="text-end text-secondary fw-semibold pe-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="filteredPatientsList.length === 0">
                    <td colspan="5" class="text-center py-4 text-muted">No patients found.</td>
                  </tr>
                  <tr v-for="p in filteredPatientsList" :key="p.id">
                    <td class="fw-semibold">{{ p.name || 'N/A' }}</td>
                    <td class="text-muted small">{{ p.username }}</td>
                    <td>{{ p.contact || '—' }}</td>
                    <td>
                      <span v-if="p.is_blacklisted" class="badge bg-danger bg-opacity-10 text-danger rounded-pill px-2 py-1">Blacklisted</span>
                      <span v-else class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1">Active</span>
                    </td>
                    <td class="text-end pe-4">
                      <button class="btn btn-sm btn-outline-secondary me-1 rounded-circle" @click="openPatientModal(p)" title="Edit">
                        <i class="bi bi-pencil-fill"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-warning me-1 rounded-circle" @click="togglePatientBlacklist(p)" :title="p.is_blacklisted ? 'Unblock' : 'Blacklist'">
                        <i :class="p.is_blacklisted ? 'bi bi-unlock-fill' : 'bi bi-slash-circle'"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger rounded-circle" @click="deletePatient(p.id)" title="Delete">
                        <i class="bi bi-trash-fill"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Mobile card view -->
            <div class="d-md-none mobile-card-list">
              <div v-if="filteredPatientsList.length === 0" class="text-center py-4 text-muted">No patients found.</div>
              <div v-for="p in filteredPatientsList" :key="'m-pat-' + p.id" class="mobile-card">
                <div class="mobile-card-header">
                  <div>
                    <div class="fw-semibold">{{ p.name || 'N/A' }}</div>
                    <div class="text-muted small">{{ p.username }}</div>
                  </div>
                  <div>
                    <span v-if="p.is_blacklisted" class="badge bg-danger bg-opacity-10 text-danger rounded-pill px-2 py-1">Blacklisted</span>
                    <span v-else class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1">Active</span>
                  </div>
                </div>
                <div class="mobile-card-body">
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Contact</span>
                    <span>{{ p.contact || '—' }}</span>
                  </div>
                </div>
                <div class="mobile-card-actions">
                  <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="openPatientModal(p)"><i class="bi bi-pencil-fill me-1"></i>Edit</button>
                  <button class="btn btn-sm btn-outline-warning rounded-pill" @click="togglePatientBlacklist(p)"><i :class="p.is_blacklisted ? 'bi bi-unlock-fill me-1' : 'bi bi-slash-circle me-1'"></i>{{ p.is_blacklisted ? 'Unblock' : 'Block' }}</button>
                  <button class="btn btn-sm btn-outline-danger rounded-pill" @click="deletePatient(p.id)"><i class="bi bi-trash-fill me-1"></i>Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============== APPOINTMENTS TAB ============== -->
      <div v-if="activeTab === 'appointments'">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center mb-2 mb-md-0">
              <h5 class="mb-0 fw-bold text-info"><i class="bi bi-calendar-check me-2"></i>Appointments</h5>
              <button class="btn btn-info btn-sm rounded-pill px-3 text-white" @click="openBookModal">
                <i class="bi bi-plus-lg me-1"></i><span class="d-none d-sm-inline">Book Appointment</span><span class="d-sm-none">Book</span>
              </button>
            </div>
            <div class="d-flex gap-2 mt-2 flex-wrap">
              <input type="text" class="form-control form-control-sm filter-input" placeholder="Filter..." v-model="aptFilter">
              <select class="form-select form-select-sm filter-select-sm" v-model="aptStatusFilter">
                <option value="">All Status</option>
                <option value="booked">Booked</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <select class="form-select form-select-sm filter-select-sm" v-model="aptSortOrder">
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- Desktop table -->
            <div class="table-responsive d-none d-md-block">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="text-secondary fw-semibold">ID</th>
                    <th class="text-secondary fw-semibold">Patient</th>
                    <th class="text-secondary fw-semibold">Doctor</th>
                    <th class="text-secondary fw-semibold cursor-pointer" @click="toggleAptSort">
                      Date <i :class="aptSortOrder === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down'"></i>
                    </th>
                    <th class="text-secondary fw-semibold">Time</th>
                    <th class="text-secondary fw-semibold">Status</th>
                    <th class="text-end text-secondary fw-semibold pe-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="filteredAppointments.length === 0">
                    <td colspan="7" class="text-center py-4 text-muted">No appointments found.</td>
                  </tr>
                  <tr v-for="apt in filteredAppointments" :key="apt.id">
                    <td class="text-muted">#{{ apt.id }}</td>
                    <td class="fw-semibold">{{ apt.patient }}</td>
                    <td>{{ apt.doctor }}</td>
                    <td>{{ apt.date }}</td>
                    <td>{{ apt.time }}</td>
                    <td>
                      <span :class="getAptStatusClass(apt.status)">{{ apt.status }}</span>
                    </td>
                    <td class="text-end pe-4">
                      <select class="form-select form-select-sm d-inline-block w-auto me-2" 
                              @change="updateAppointmentStatus(apt.id, $event.target.value)"
                              :value="apt.status">
                        <option value="booked">Booked</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                      <button class="btn btn-sm btn-outline-danger rounded-circle" @click="deleteAppointment(apt.id)" title="Delete">
                        <i class="bi bi-trash-fill"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Mobile card view -->
            <div class="d-md-none mobile-card-list">
              <div v-if="filteredAppointments.length === 0" class="text-center py-4 text-muted">No appointments found.</div>
              <div v-for="apt in filteredAppointments" :key="'m-apt-' + apt.id" class="mobile-card">
                <div class="mobile-card-header">
                  <div>
                    <div class="fw-semibold">{{ apt.patient }}</div>
                    <div class="text-muted small">with Dr. {{ apt.doctor }}</div>
                  </div>
                  <span :class="getAptStatusClass(apt.status)">{{ apt.status }}</span>
                </div>
                <div class="mobile-card-body">
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Date</span>
                    <span>{{ apt.date }}</span>
                  </div>
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Time</span>
                    <span>{{ apt.time }}</span>
                  </div>
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">ID</span>
                    <span class="text-muted">#{{ apt.id }}</span>
                  </div>
                </div>
                <div class="mobile-card-actions">
                  <select class="form-select form-select-sm flex-grow-1" 
                          @change="updateAppointmentStatus(apt.id, $event.target.value)"
                          :value="apt.status">
                    <option value="booked">Booked</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                  <button class="btn btn-sm btn-outline-danger rounded-pill" @click="deleteAppointment(apt.id)"><i class="bi bi-trash-fill me-1"></i>Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============== DEPARTMENTS TAB ============== -->
      <div v-if="activeTab === 'departments'">
        <GenericModelCRUD 
          title="Departments" 
          singularTitle="Department"
          :columns="departmentColumns" 
          :initialData="departmentsData" 
          @add-item="addDepartment"
          @edit-item="editDepartment"
          @delete-item="deleteDepartment"
        />
      </div>

      <!-- ============== TREATMENTS TAB ============== -->
      <div v-if="activeTab === 'treatments'">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
            <h5 class="mb-0 fw-bold text-purple"><i class="bi bi-clipboard2-pulse me-2"></i>Treatments</h5>
            <button class="btn btn-primary btn-sm rounded-pill px-3" @click="openTreatmentModal(null)">
              <i class="bi bi-plus-lg me-1"></i><span class="d-none d-sm-inline">Add New</span><span class="d-sm-none">Add</span>
            </button>
          </div>
          <div class="card-body p-0">
            <!-- Desktop table -->
            <div class="table-responsive d-none d-md-block">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="text-secondary fw-semibold">ID</th>
                    <th class="text-secondary fw-semibold">Appointment</th>
                    <th class="text-secondary fw-semibold">Diagnosis</th>
                    <th class="text-secondary fw-semibold">Prescription</th>
                    <th class="text-secondary fw-semibold">Notes</th>
                    <th class="text-end text-secondary fw-semibold pe-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="treatmentsData.length === 0">
                    <td colspan="6" class="text-center py-4 text-muted">No treatments found.</td>
                  </tr>
                  <tr v-for="t in treatmentsData" :key="t.id">
                    <td class="text-muted">{{ t.id }}</td>
                    <td>
                      <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-2 py-1 small">
                        {{ t.appointment_label || 'Apt #' + t.appointment_id }}
                      </span>
                    </td>
                    <td>{{ t.diagnosis }}</td>
                    <td>{{ t.prescription }}</td>
                    <td class="text-muted small">{{ t.notes }}</td>
                    <td class="text-end pe-4">
                      <button class="btn btn-sm btn-outline-secondary me-2 rounded-circle" @click="openTreatmentModal(t)" title="Edit">
                        <i class="bi bi-pencil-fill"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger rounded-circle" @click="deleteTreatment(t.id)" title="Delete">
                        <i class="bi bi-trash-fill"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Mobile card view -->
            <div class="d-md-none mobile-card-list">
              <div v-if="treatmentsData.length === 0" class="text-center py-4 text-muted">No treatments found.</div>
              <div v-for="t in treatmentsData" :key="'m-trt-' + t.id" class="mobile-card">
                <div class="mobile-card-header">
                  <div>
                    <div class="fw-semibold">{{ t.diagnosis }}</div>
                    <div class="text-muted small">
                      <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-2 py-1">
                        {{ t.appointment_label || 'Apt #' + t.appointment_id }}
                      </span>
                    </div>
                  </div>
                  <span class="text-muted small">#{{ t.id }}</span>
                </div>
                <div class="mobile-card-body">
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Prescription</span>
                    <span class="text-truncate" style="max-width: 180px;">{{ t.prescription || '—' }}</span>
                  </div>
                  <div class="mobile-card-row">
                    <span class="mobile-card-label">Notes</span>
                    <span class="text-muted small text-truncate" style="max-width: 180px;">{{ t.notes || '—' }}</span>
                  </div>
                </div>
                <div class="mobile-card-actions">
                  <button class="btn btn-sm btn-outline-secondary rounded-pill" @click="openTreatmentModal(t)"><i class="bi bi-pencil-fill me-1"></i>Edit</button>
                  <button class="btn btn-sm btn-outline-danger rounded-pill" @click="deleteTreatment(t.id)"><i class="bi bi-trash-fill me-1"></i>Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ============== DOCTOR MODAL ============== -->
    <div class="modal fade" id="doctorModal" tabindex="-1" ref="doctorModalEl">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header rounded-top-4" :class="doctorForm.id ? 'bg-success' : 'bg-primary'">
            <h5 class="modal-title fw-bold text-white">
              <i class="bi bi-heart-pulse-fill me-2"></i>
              {{ doctorForm.id ? 'Edit Doctor' : 'Add New Doctor' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="doctorMsg" :class="['alert', doctorMsgType === 'error' ? 'alert-danger' : 'alert-success', 'py-2']">
              {{ doctorMsg }}
            </div>
            <form @submit.prevent="saveDoctor">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary">Full Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="doctorForm.name" placeholder="Dr. John Smith" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary">Email (Username) <span class="text-danger">*</span></label>
                  <input type="email" class="form-control" v-model="doctorForm.email" placeholder="doctor@hospital.com" required :disabled="!!doctorForm.id">
                  <div class="form-text">Used as login credentials. Must be unique.</div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary">Department <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="doctorForm.department_id" required>
                    <option value="" disabled>Select department...</option>
                    <option v-for="d in departmentsData" :key="d.id" :value="d.id">{{ d.name }}</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary">Specialization <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="doctorForm.specialization" placeholder="Cardiology" required>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary">Contact</label>
                  <input type="text" class="form-control" v-model="doctorForm.contact" placeholder="+1 234 567 8900">
                </div>
                <div class="col-md-6 mb-3" v-if="!doctorForm.id">
                  <label class="form-label fw-semibold text-secondary">Password</label>
                  <input type="password" class="form-control" v-model="doctorForm.password" placeholder="Default: password123">
                  <div class="form-text">Leave blank for default password.</div>
                </div>
              </div>
              <div class="mb-4">
                <label class="form-label fw-semibold text-secondary">Weekly Availability</label>
                <div class="d-flex flex-wrap gap-2">
                  <div v-for="(day, idx) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="day"
                       class="form-check form-check-inline avail-check">
                    <input class="form-check-input" type="checkbox" :id="'doc-avail-' + idx"
                           v-model="doctorForm.availabilityArr[idx]" :true-value="1" :false-value="0">
                    <label class="form-check-label small" :for="'doc-avail-' + idx">{{ day }}</label>
                  </div>
                </div>
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn rounded-pill px-4 fw-bold" :class="doctorForm.id ? 'btn-success' : 'btn-primary'" :disabled="doctorLoading">
                  <span v-if="doctorLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ doctorForm.id ? 'Save Changes' : 'Create Doctor' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ============== PATIENT MODAL ============== -->
    <div class="modal fade" id="patientModal" tabindex="-1" ref="patientModalEl">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header rounded-top-4" :class="patientForm.id ? 'bg-success' : 'bg-primary'">
            <h5 class="modal-title fw-bold text-white">
              <i class="bi bi-person-badge me-2"></i>
              {{ patientForm.id ? 'Edit Patient' : 'Add New Patient' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="patientMsg" :class="['alert', patientMsgType === 'error' ? 'alert-danger' : 'alert-success', 'py-2']">
              {{ patientMsg }}
            </div>
            <form @submit.prevent="savePatient">
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary">Full Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="patientForm.name" placeholder="Jane Doe" required>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary">Email (Username) <span class="text-danger">*</span></label>
                <input type="email" class="form-control" v-model="patientForm.email" placeholder="patient@email.com" required :disabled="!!patientForm.id">
                <div class="form-text">Used as login credentials. Must be unique.</div>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary">Contact</label>
                <input type="text" class="form-control" v-model="patientForm.contact" placeholder="+1 234 567 8900">
              </div>
              <div class="mb-3" v-if="!patientForm.id">
                <label class="form-label fw-semibold text-secondary">Password</label>
                <input type="password" class="form-control" v-model="patientForm.password" placeholder="Default: password123">
                <div class="form-text">Leave blank for default password.</div>
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn rounded-pill px-4 fw-bold" :class="patientForm.id ? 'btn-success' : 'btn-primary'" :disabled="patientLoading">
                  <span v-if="patientLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ patientForm.id ? 'Save Changes' : 'Create Patient' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ============== BOOK APPOINTMENT MODAL ============== -->
    <div class="modal fade" id="adminBookModal" tabindex="-1" ref="adminBookModalEl">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header bg-info text-white rounded-top-4">
            <h5 class="modal-title fw-bold"><i class="bi bi-calendar-plus me-2"></i>Book Appointment</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="bookingMsg" :class="['alert', bookingMsgType === 'error' ? 'alert-danger' : 'alert-success', 'py-2']">
              {{ bookingMsg }}
            </div>
            <form @submit.prevent="adminBookAppointment">
              <div class="mb-3">
                <label class="form-label text-secondary fw-semibold">Patient <span class="text-danger">*</span></label>
                <select class="form-select" v-model="newApt.patient_id" required>
                  <option value="" disabled>Select a patient...</option>
                  <option v-for="p in patientsData" :key="p.id" :value="p.id">
                    {{ p.name || 'Patient #' + p.id }} ({{ p.username }})
                  </option>
                </select>
                <div v-if="newApt.patient_id && isPatientBlacklisted(newApt.patient_id)" class="text-danger small mt-1">
                  <i class="bi bi-exclamation-triangle-fill me-1"></i>Warning: This patient is blacklisted.
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label text-secondary fw-semibold">Department</label>
                <select class="form-select" v-model="newApt.department_id">
                  <option value="">All Departments</option>
                  <option v-for="dept in departmentsData" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label text-secondary fw-semibold">Doctor <span class="text-danger">*</span></label>
                <select class="form-select" v-model="newApt.doctor_id" required>
                  <option value="" disabled>Select a doctor...</option>
                  <option v-for="doc in bookingFilteredDoctors" :key="doc.id" :value="doc.id">
                    {{ doc.name }} — {{ doc.specialization }} ({{ formatAvail(doc.availability) }})
                  </option>
                </select>
                <div v-if="newApt.doctor_id && isDoctorBlacklisted(newApt.doctor_id)" class="text-danger small mt-1">
                  <i class="bi bi-exclamation-triangle-fill me-1"></i>Warning: This doctor is blacklisted.
                </div>
                <div v-if="newApt.doctor_id && newApt.date" class="mt-1">
                  <span v-if="isDoctorAvailableOnDate(newApt.doctor_id, newApt.date)" class="text-success small">
                    <i class="bi bi-check-circle-fill me-1"></i>Doctor is available on this day.
                  </span>
                  <span v-else class="text-danger small">
                    <i class="bi bi-x-circle-fill me-1"></i>Doctor is NOT available on this day.
                  </span>
                </div>
              </div>
              <div class="row mb-4">
                <div class="col-12 col-sm-6 mb-3 mb-sm-0">
                  <label class="form-label text-secondary fw-semibold">Date <span class="text-danger">*</span></label>
                  <input type="date" class="form-control" v-model="newApt.date" :min="todayStr" required>
                </div>
                <div class="col-12 col-sm-6">
                  <label class="form-label text-secondary fw-semibold">Time <span class="text-danger">*</span></label>
                  <input type="time" class="form-control" v-model="newApt.time" required>
                </div>
              </div>
              <button type="submit" class="btn btn-info w-100 rounded-pill py-2 fw-bold text-white" :disabled="bookingLoading">
                <span v-if="bookingLoading" class="spinner-border spinner-border-sm me-2"></span>
                Confirm Booking
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ============== TREATMENT MODAL ============== -->
    <div class="modal fade" id="treatmentModal" tabindex="-1" ref="treatmentModalEl">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header rounded-top-4" :class="treatmentForm.id ? 'bg-success' : 'bg-primary'">
            <h5 class="modal-title fw-bold text-white">
              <i class="bi bi-clipboard2-pulse me-2"></i>
              {{ treatmentForm.id ? 'Edit Treatment' : 'Add Treatment' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="treatmentMsg" :class="['alert', treatmentMsgType === 'error' ? 'alert-danger' : 'alert-success', 'py-2']">
              {{ treatmentMsg }}
            </div>
            <form @submit.prevent="saveTreatment">
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary">Appointment <span class="text-danger">*</span></label>
                <select class="form-select" v-model="treatmentForm.appointment_id" required>
                  <option value="" disabled>Select an appointment...</option>
                  <option v-for="apt in appointmentsData" :key="apt.id" :value="apt.id">
                    #{{ apt.id }} — {{ apt.date }} {{ apt.time }} — {{ apt.patient }} with Dr. {{ apt.doctor }}
                    {{ apt.status !== 'booked' ? '(' + apt.status + ')' : '' }}
                  </option>
                </select>
                <div class="form-text text-muted">Choose the appointment this treatment is linked to.</div>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary">Diagnosis <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="treatmentForm.diagnosis" placeholder="e.g. Acute Bronchitis" required>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary">Prescription</label>
                <textarea class="form-control" v-model="treatmentForm.prescription" rows="3" placeholder="List medications and dosages..."></textarea>
              </div>
              <div class="mb-4">
                <label class="form-label fw-semibold text-secondary">Notes</label>
                <textarea class="form-control" v-model="treatmentForm.notes" rows="2" placeholder="Additional clinical notes..."></textarea>
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn rounded-pill px-4 fw-bold" :class="treatmentForm.id ? 'btn-success' : 'btn-primary'" :disabled="treatmentLoading">
                  <span v-if="treatmentLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ treatmentForm.id ? 'Save Changes' : 'Add Treatment' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import GenericModelCRUD from './admin/GenericModelCRUD.vue'

export default {
  name: 'AdminDashboard',
  components: { GenericModelCRUD },
  data() {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    return {
      activeTab: 'doctors',
      todayStr,

      // Stats
      stats: {
        total_doctors: 0,
        total_patients: 0,
        total_appointments: 0,
        upcoming_appointments: 0,
        past_appointments: 0,
        blacklisted_users: 0
      },

      // Global search
      globalSearch: '',
      searchResults: [],
      searchTimeout: null,

      // Data
      doctorsData: [],
      patientsData: [],
      appointmentsData: [],
      departmentsData: [],
      treatmentsData: [],
      usersData: [],

      // Filters
      doctorFilter: '',
      doctorDeptFilter: '',
      patientFilter: '',
      aptFilter: '',
      aptStatusFilter: '',
      aptSortOrder: 'desc',

      // Department columns (for GenericModelCRUD)
      departmentColumns: [
        { key: 'id', label: 'ID', type: 'number' },
        { key: 'name', label: 'Dept Name', type: 'text' },
        { key: 'description', label: 'Description', type: 'textarea' }
      ],

      // Doctor modal
      doctorForm: { id: null, name: '', email: '', department_id: '', specialization: '', contact: '', password: '', availabilityArr: [0,0,0,0,0,0,0] },
      doctorMsg: '',
      doctorMsgType: '',
      doctorLoading: false,
      doctorModalInstance: null,

      // Patient modal
      patientForm: { id: null, name: '', email: '', contact: '', password: '' },
      patientMsg: '',
      patientMsgType: '',
      patientLoading: false,
      patientModalInstance: null,

      // Booking modal
      newApt: { patient_id: '', department_id: '', doctor_id: '', date: '', time: '' },
      bookingMsg: '',
      bookingMsgType: '',
      bookingLoading: false,
      bookModalInstance: null,

      // Treatment modal
      treatmentForm: { id: null, appointment_id: '', diagnosis: '', prescription: '', notes: '' },
      treatmentMsg: '',
      treatmentMsgType: '',
      treatmentLoading: false,
      treatmentModalInstance: null,
    }
  },
  computed: {
    tabs() {
      return [
        { id: 'doctors', name: 'Doctors', icon: 'bi-heart-pulse-fill', count: this.doctorsData.length },
        { id: 'patients', name: 'Patients', icon: 'bi-person-badge', count: this.patientsData.length },
        { id: 'appointments', name: 'Appointments', icon: 'bi-calendar-check', count: this.appointmentsData.length },
        { id: 'departments', name: 'Departments', icon: 'bi-building', count: this.departmentsData.length },
        { id: 'treatments', name: 'Treatments', icon: 'bi-clipboard2-pulse', count: this.treatmentsData.length }
      ]
    },
    filteredDoctorsList() {
      let list = this.doctorsData;
      if (this.doctorDeptFilter) {
        list = list.filter(d => d.department_id == this.doctorDeptFilter);
      }
      if (this.doctorFilter) {
        const q = this.doctorFilter.toLowerCase();
        list = list.filter(d => 
          (d.name && d.name.toLowerCase().includes(q)) || 
          (d.username && d.username.toLowerCase().includes(q)) ||
          (d.specialization && d.specialization.toLowerCase().includes(q))
        );
      }
      return list;
    },
    filteredPatientsList() {
      if (!this.patientFilter) return this.patientsData;
      const q = this.patientFilter.toLowerCase();
      return this.patientsData.filter(p =>
        (p.name && p.name.toLowerCase().includes(q)) ||
        (p.username && p.username.toLowerCase().includes(q)) ||
        (p.contact && p.contact.toLowerCase().includes(q)) ||
        (p.id && String(p.id).includes(q))
      );
    },
    filteredAppointments() {
      let list = [...this.appointmentsData];
      if (this.aptStatusFilter) {
        list = list.filter(a => a.status === this.aptStatusFilter);
      }
      if (this.aptFilter) {
        const q = this.aptFilter.toLowerCase();
        list = list.filter(a =>
          (a.patient && a.patient.toLowerCase().includes(q)) ||
          (a.doctor && a.doctor.toLowerCase().includes(q)) ||
          (a.date && a.date.includes(q))
        );
      }
      list.sort((a, b) => {
        const da = new Date(a.date + ' ' + (a.time || '00:00'));
        const db = new Date(b.date + ' ' + (b.time || '00:00'));
        return this.aptSortOrder === 'asc' ? da - db : db - da;
      });
      return list;
    },
    bookingFilteredDoctors() {
      if (!this.newApt.department_id) return this.doctorsData;
      return this.doctorsData.filter(d => d.department_id == this.newApt.department_id);
    }
  },
  async mounted() {
    await this.fetchDashboardData();
  },
  methods: {
    getHeaders() {
      const token = localStorage.getItem('access_token');
      return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    },

    async fetchDashboardData() {
      const headers = this.getHeaders();
      try {
        const endpoints = [
          { url: 'dashboard', ref: 'stats' },
          { url: 'doctors', ref: 'doctorsData' },
          { url: 'patients', ref: 'patientsData' },
          { url: 'appointments', ref: 'appointmentsData' },
          { url: 'departments', ref: 'departmentsData' },
          { url: 'treatments', ref: 'treatmentsData' },
          { url: 'users', ref: 'usersData' }
        ];

        const promises = endpoints.map(e => 
          fetch(`http://localhost:5000/admin/${e.url}`, { headers }).then(r => r.ok ? r.json() : null)
        );
        const results = await Promise.all(promises);
        endpoints.forEach((e, i) => {
          if (results[i]) this[e.ref] = results[i];
        });
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      }
    },

    // ===== Global Search =====
    handleGlobalSearch() {
      clearTimeout(this.searchTimeout);
      if (!this.globalSearch.trim()) {
        this.searchResults = [];
        return;
      }
      this.searchTimeout = setTimeout(async () => {
        try {
          const res = await fetch(`http://localhost:5000/admin/search?q=${encodeURIComponent(this.globalSearch)}`, {
            headers: this.getHeaders()
          });
          if (res.ok) this.searchResults = await res.json();
        } catch (e) {
          console.error('Search error:', e);
        }
      }, 300);
    },

    getRoleBadge(role) {
      const base = 'badge rounded-pill px-2 py-1 ';
      if (role === 'admin') return base + 'bg-warning bg-opacity-10 text-warning';
      if (role === 'doctor') return base + 'bg-primary bg-opacity-10 text-primary';
      if (role === 'patient') return base + 'bg-success bg-opacity-10 text-success';
      return base + 'bg-secondary bg-opacity-10 text-secondary';
    },

    // ===== DOCTOR MODAL =====
    getModalInstance(refName, elId) {
      const key = refName + 'Instance';
      if (!this[key]) {
        const el = this.$refs[refName] || document.getElementById(elId);
        if (el && window.bootstrap) {
          this[key] = new window.bootstrap.Modal(el);
        }
      }
      return this[key];
    },

    openDoctorModal(doc) {
      this.doctorMsg = '';
      if (doc) {
        const avail = doc.availability || '0000000';
        this.doctorForm = {
          id: doc.id,
          name: doc.name || '',
          email: doc.username || '',
          department_id: doc.department_id || '',
          specialization: doc.specialization || '',
          contact: doc.contact || '',
          password: '',
          availabilityArr: avail.split('').map(Number)
        };
      } else {
        this.doctorForm = { id: null, name: '', email: '', department_id: '', specialization: '', contact: '', password: '', availabilityArr: [0,0,0,0,0,0,0] };
      }
      const modal = this.getModalInstance('doctorModalEl', 'doctorModal');
      if (modal) modal.show();
    },

    async saveDoctor() {
      this.doctorMsg = '';
      this.doctorLoading = true;
      try {
        const isEdit = !!this.doctorForm.id;
        const availability = this.doctorForm.availabilityArr.join('');
        const payload = {
          name: this.doctorForm.name,
          department_id: Number(this.doctorForm.department_id),
          specialization: this.doctorForm.specialization,
          contact: this.doctorForm.contact,
          availability
        };
        if (!isEdit) {
          payload.email = this.doctorForm.email;
          if (this.doctorForm.password) payload.password = this.doctorForm.password;
        }

        const url = isEdit ? `http://localhost:5000/admin/doctor/${this.doctorForm.id}` : 'http://localhost:5000/admin/doctor';
        const res = await fetch(url, {
          method: isEdit ? 'PUT' : 'POST',
          headers: this.getHeaders(),
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
          this.doctorMsgType = 'success';
          this.doctorMsg = data.msg;
          await this.fetchDashboardData();
          setTimeout(() => {
            const modal = this.getModalInstance('doctorModalEl', 'doctorModal');
            if (modal) modal.hide();
          }, 1200);
        } else {
          this.doctorMsgType = 'error';
          this.doctorMsg = data.msg || 'Failed to save doctor.';
        }
      } catch {
        this.doctorMsgType = 'error';
        this.doctorMsg = 'Network error. Please try again.';
      } finally {
        this.doctorLoading = false;
      }
    },

    async deleteDoctor(id) {
      if (!confirm('Delete this doctor? This will also remove their user account.')) return;
      const res = await fetch(`http://localhost:5000/admin/doctor/${id}`, { method: 'DELETE', headers: this.getHeaders() });
      if (res.ok) this.fetchDashboardData();
      else alert('Failed to delete doctor.');
    },

    async toggleDoctorBlacklist(doc) {
      if (!doc.user_id) return;
      const user = this.usersData.find(u => u.id === doc.user_id);
      if (!user) return;
      const res = await fetch(`http://localhost:5000/admin/user/${user.id}/blacklist`, {
        method: 'POST', headers: this.getHeaders()
      });
      if (res.ok) this.fetchDashboardData();
    },

    // ===== PATIENT MODAL =====
    openPatientModal(patient) {
      this.patientMsg = '';
      if (patient) {
        this.patientForm = {
          id: patient.id,
          name: patient.name || '',
          email: patient.username || '',
          contact: patient.contact || '',
          password: ''
        };
      } else {
        this.patientForm = { id: null, name: '', email: '', contact: '', password: '' };
      }
      const modal = this.getModalInstance('patientModalEl', 'patientModal');
      if (modal) modal.show();
    },

    async savePatient() {
      this.patientMsg = '';
      this.patientLoading = true;
      try {
        const isEdit = !!this.patientForm.id;
        let url, method, payload;

        if (isEdit) {
          url = `http://localhost:5000/admin/patient/${this.patientForm.id}`;
          method = 'PUT';
          payload = { name: this.patientForm.name, contact: this.patientForm.contact };
        } else {
          url = 'http://localhost:5000/admin/patient';
          method = 'POST';
          payload = {
            email: this.patientForm.email,
            name: this.patientForm.name,
            contact: this.patientForm.contact
          };
          if (this.patientForm.password) payload.password = this.patientForm.password;
        }

        const res = await fetch(url, {
          method,
          headers: this.getHeaders(),
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
          this.patientMsgType = 'success';
          this.patientMsg = data.msg;
          await this.fetchDashboardData();
          setTimeout(() => {
            const modal = this.getModalInstance('patientModalEl', 'patientModal');
            if (modal) modal.hide();
          }, 1200);
        } else {
          this.patientMsgType = 'error';
          this.patientMsg = data.msg || 'Failed to save patient.';
        }
      } catch {
        this.patientMsgType = 'error';
        this.patientMsg = 'Network error. Please try again.';
      } finally {
        this.patientLoading = false;
      }
    },

    async deletePatient(id) {
      if (!confirm('Delete this patient? This will also remove their user account and appointments.')) return;
      const res = await fetch(`http://localhost:5000/admin/patient/${id}`, { method: 'DELETE', headers: this.getHeaders() });
      if (res.ok) this.fetchDashboardData();
      else alert('Failed to delete patient.');
    },

    async togglePatientBlacklist(p) {
      if (!p.user_id) return;
      const res = await fetch(`http://localhost:5000/admin/user/${p.user_id}/blacklist`, {
        method: 'POST', headers: this.getHeaders()
      });
      if (res.ok) this.fetchDashboardData();
    },

    // ===== BOOKING MODAL =====
    openBookModal() {
      this.newApt = { patient_id: '', department_id: '', doctor_id: '', date: '', time: '' };
      this.bookingMsg = '';
      const modal = this.getModalInstance('adminBookModalEl', 'adminBookModal');
      if (modal) modal.show();
    },

    async adminBookAppointment() {
      this.bookingMsg = '';
      this.bookingLoading = true;
      try {
        const res = await fetch('http://localhost:5000/admin/appointment', {
          method: 'POST',
          headers: this.getHeaders(),
          body: JSON.stringify({
            patient_id: Number(this.newApt.patient_id),
            doctor_id: Number(this.newApt.doctor_id),
            date: this.newApt.date,
            time: this.newApt.time
          })
        });
        const data = await res.json();
        if (res.ok) {
          this.bookingMsgType = 'success';
          this.bookingMsg = data.msg;
          await this.fetchDashboardData();
          setTimeout(() => {
            const modal = this.getModalInstance('adminBookModalEl', 'adminBookModal');
            if (modal) modal.hide();
          }, 1500);
        } else {
          this.bookingMsgType = 'error';
          this.bookingMsg = data.msg || 'Failed to book appointment.';
        }
      } catch {
        this.bookingMsgType = 'error';
        this.bookingMsg = 'Network error. Please try again.';
      } finally {
        this.bookingLoading = false;
      }
    },

    async updateAppointmentStatus(id, status) {
      const res = await fetch(`http://localhost:5000/admin/appointment/${id}`, {
        method: 'PUT', headers: this.getHeaders(),
        body: JSON.stringify({ status })
      });
      if (res.ok) this.fetchDashboardData();
      else alert('Failed to update appointment status.');
    },

    async deleteAppointment(id) {
      if (!confirm('Delete this appointment?')) return;
      const res = await fetch(`http://localhost:5000/admin/appointment/${id}`, {
        method: 'DELETE', headers: this.getHeaders()
      });
      if (res.ok) this.fetchDashboardData();
    },

    toggleAptSort() {
      this.aptSortOrder = this.aptSortOrder === 'asc' ? 'desc' : 'asc';
    },

    // ===== TREATMENT MODAL =====
    openTreatmentModal(treatment) {
      this.treatmentMsg = '';
      if (treatment) {
        this.treatmentForm = {
          id: treatment.id,
          appointment_id: treatment.appointment_id,
          diagnosis: treatment.diagnosis || '',
          prescription: treatment.prescription || '',
          notes: treatment.notes || ''
        };
      } else {
        this.treatmentForm = { id: null, appointment_id: '', diagnosis: '', prescription: '', notes: '' };
      }
      const modal = this.getModalInstance('treatmentModalEl', 'treatmentModal');
      if (modal) modal.show();
    },

    async saveTreatment() {
      this.treatmentMsg = '';
      this.treatmentLoading = true;
      try {
        const isEdit = !!this.treatmentForm.id;
        const url = isEdit
          ? `http://localhost:5000/admin/treatment/${this.treatmentForm.id}`
          : 'http://localhost:5000/admin/treatment';
        const res = await fetch(url, {
          method: isEdit ? 'PUT' : 'POST',
          headers: this.getHeaders(),
          body: JSON.stringify({
            appointment_id: Number(this.treatmentForm.appointment_id),
            diagnosis: this.treatmentForm.diagnosis,
            prescription: this.treatmentForm.prescription,
            notes: this.treatmentForm.notes
          })
        });
        const data = await res.json();
        if (res.ok) {
          this.treatmentMsgType = 'success';
          this.treatmentMsg = data.msg;
          await this.fetchDashboardData();
          setTimeout(() => {
            const modal = this.getModalInstance('treatmentModalEl', 'treatmentModal');
            if (modal) modal.hide();
          }, 1200);
        } else {
          this.treatmentMsgType = 'error';
          this.treatmentMsg = data.msg || 'Failed to save treatment.';
        }
      } catch {
        this.treatmentMsgType = 'error';
        this.treatmentMsg = 'Network error. Please try again.';
      } finally {
        this.treatmentLoading = false;
      }
    },

    async deleteTreatment(id) {
      if (!confirm('Delete this treatment?')) return;
      const res = await fetch(`http://localhost:5000/admin/treatment/${id}`, {
        method: 'DELETE', headers: this.getHeaders()
      });
      if (res.ok) this.fetchDashboardData();
      else alert('Failed to delete treatment.');
    },

    // ===== DEPARTMENT ACTIONS =====
    async addDepartment(dept) {
      const res = await fetch('http://localhost:5000/admin/departments', {
        method: 'POST', headers: this.getHeaders(),
        body: JSON.stringify({ name: dept.name, description: dept.description })
      });
      if (res.ok) this.fetchDashboardData();
    },
    async editDepartment(dept) {
      const res = await fetch(`http://localhost:5000/admin/department/${dept.id}`, {
        method: 'PUT', headers: this.getHeaders(),
        body: JSON.stringify({ name: dept.name, description: dept.description })
      });
      if (res.ok) this.fetchDashboardData();
    },
    async deleteDepartment(id) {
      const res = await fetch(`http://localhost:5000/admin/department/${id}`, {
        method: 'DELETE', headers: this.getHeaders()
      });
      if (res.ok) this.fetchDashboardData();
    },

    // ===== HELPERS =====
    formatAvail(bits) {
      if (!bits || bits.length !== 7) return 'N/A';
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return days.filter((d, i) => bits[i] === '1').join(', ') || 'None';
    },

    getAptStatusClass(status) {
      const base = 'badge rounded-pill px-3 py-2 fw-semibold ';
      if (status === 'booked') return base + 'bg-primary bg-opacity-10 text-primary';
      if (status === 'completed') return base + 'bg-success bg-opacity-10 text-success';
      if (status === 'cancelled') return base + 'bg-danger bg-opacity-10 text-danger';
      return base + 'bg-secondary bg-opacity-10 text-secondary';
    },

    isDoctorAvailableOnDate(doctorId, dateStr) {
      if (!doctorId || !dateStr) return true;
      const doctor = this.doctorsData.find(d => d.id === doctorId);
      if (!doctor || !doctor.availability || doctor.availability.length !== 7) return true;
      const date = new Date(dateStr);
      const jsDay = date.getDay();
      const dayIndex = jsDay === 0 ? 6 : jsDay - 1;
      return doctor.availability[dayIndex] === '1';
    },

    isPatientBlacklisted(patientId) {
      const p = this.patientsData.find(pt => pt.id === patientId);
      return p ? p.is_blacklisted : false;
    },

    isDoctorBlacklisted(doctorId) {
      const d = this.doctorsData.find(doc => doc.id === doctorId);
      return d ? d.is_blacklisted : false;
    }
  }
}
</script>

<style scoped>
/* ===== HEADER ===== */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.admin-header-search {
  max-width: 320px;
  width: 100%;
}

/* ===== NAV TABS ===== */
.admin-tabs {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;          /* Firefox */
  -ms-overflow-style: none;       /* IE/Edge */
}
.admin-tabs::-webkit-scrollbar {
  display: none;                  /* Chrome/Safari */
}
.nav-pills .nav-link {
  color: #6c757d;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}
.nav-pills .nav-link.active {
  background: linear-gradient(90deg, var(--bs-primary), var(--bs-primary-rgb));
  box-shadow: 0 4px 10px rgba(var(--bs-primary-rgb), 0.3);
  color: #fff;
}
.nav-pills .nav-link:hover:not(.active) {
  background-color: #f8f9fa;
  color: var(--bs-primary);
}

/* ===== STAT CARDS ===== */
.stat-card {
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.08) !important;
}
.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

/* ===== FILTER INPUTS ===== */
.filter-input {
  min-width: 0;
  flex: 1 1 140px;
  max-width: 220px;
}
.filter-select {
  min-width: 0;
  flex: 0 1 180px;
}
.filter-select-sm {
  min-width: 0;
  flex: 0 1 140px;
}

/* ===== TABLE ===== */
.table th {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.btn-outline-danger { border-color: transparent; }
.btn-outline-danger:hover { background-color: #f8f9fa; color: #dc3545; }
.btn-outline-secondary { border-color: transparent; }
.btn-outline-secondary:hover { background-color: #f8f9fa; color: var(--bs-primary); }
.btn-outline-warning { border-color: transparent; }
.btn-outline-warning:hover { background-color: #fff3cd; }

.cursor-pointer { cursor: pointer; }

.search-results-card {
  border-left: 4px solid var(--bs-primary) !important;
}

.avail-check {
  background: #f8f9fa;
  padding: 6px 12px;
  border-radius: 8px;
}

.text-purple { color: #6f42c1; }

.input-group:focus-within .input-group-text {
  border-color: #86b7fe;
}

/* ===== MOBILE CARD LIST ===== */
.mobile-card-list {
  padding: 0.75rem;
}
.mobile-card {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  margin-bottom: 0.75rem;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}
.mobile-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.mobile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.875rem 1rem 0.5rem;
  gap: 0.5rem;
}
.mobile-card-body {
  padding: 0 1rem 0.5rem;
}
.mobile-card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.3rem 0;
  border-bottom: 1px solid #f1f3f5;
}
.mobile-card-row:last-child {
  border-bottom: none;
}
.mobile-card-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.mobile-card-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  flex-wrap: wrap;
}
.mobile-card-actions .btn {
  font-size: 0.78rem;
  padding: 0.3rem 0.75rem;
}

/* ===== RESPONSIVE BREAKPOINTS ===== */
@media (max-width: 767.98px) {
  /* Header stacks vertically on mobile */
  .admin-header {
    flex-direction: column;
    align-items: stretch;
  }
  .admin-header-search {
    max-width: 100%;
  }

  /* Compact stat cards */
  .stat-card .card-body {
    padding: 0.75rem 0.5rem !important;
  }
  .stat-card h3 {
    font-size: 1.35rem;
  }
  .stat-icon {
    width: 36px;
    height: 36px;
    font-size: 1rem;
  }

  /* Tab font sizing */
  .nav-pills .nav-link {
    font-size: 0.82rem;
    padding: 0.4rem 0.75rem;
  }

  /* Filter inputs go full-width */
  .filter-input,
  .filter-select,
  .filter-select-sm {
    flex: 1 1 100%;
    max-width: 100%;
  }

  /* Search results scroll horizontally */
  .search-results-card .table-responsive {
    max-height: 50vh;
  }

  /* Modal improvements */
  .modal-dialog {
    margin: 0.5rem;
  }
  .modal-body {
    padding: 1rem !important;
  }
}

@media (max-width: 575.98px) {
  /* Even smaller stat cards on extra-small */
  .stats-row .col-6 {
    padding-left: 0.35rem;
    padding-right: 0.35rem;
  }
  .stat-card h3 {
    font-size: 1.2rem;
  }
  .stat-card small {
    font-size: 0.72rem;
  }
}
</style>
