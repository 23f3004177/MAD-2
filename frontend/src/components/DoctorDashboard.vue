<template>
  <div class="doctor-dashboard py-5">
    <div class="container">
      <!-- Welcome Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card bg-white border-0 shadow-sm rounded-4 overflow-hidden">
            <div class="card-body p-4 p-md-5 d-flex justify-content-between align-items-center">
              <div>
                <h2 class="fw-bold text-dark mb-2">Welcome, Doctor! 🩺</h2>
                <p class="text-muted mb-0">Manage your schedule, patients, and treatments efficiently.</p>
              </div>
              <div class="d-none d-md-block text-end">
                 <h5 class="fw-bold text-primary mb-1">{{ currentDate }}</h5>
                 <p class="text-muted small mb-0">Trimed Hospital</p>
              </div>
            </div>
            <!-- Decorative border -->
            <div class="position-absolute bottom-0 start-0 w-100" style="height: 4px; background: linear-gradient(90deg, var(--bs-info), var(--bs-primary));"></div>
          </div>
        </div>
      </div>

      <!-- Quick Actions / Stats -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm rounded-4 h-100">
            <div class="card-body p-4 text-center">
              <div class="bg-primary bg-opacity-10 text-primary rounded-circle p-3 mx-auto mb-3" style="width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-calendar-check-fill fs-4"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ upcomingAppointments.length }}</h3>
              <h6 class="text-muted fw-semibold mb-0">Upcoming</h6>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm rounded-4 h-100">
            <div class="card-body p-4 text-center">
              <div class="bg-success bg-opacity-10 text-success rounded-circle p-3 mx-auto mb-3" style="width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-check-circle-fill fs-4"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ completedAppointments.length }}</h3>
              <h6 class="text-muted fw-semibold mb-0">Completed</h6>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm rounded-4 h-100">
            <div class="card-body p-4 text-center">
              <div class="bg-info bg-opacity-10 text-info rounded-circle p-3 mx-auto mb-3" style="width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-people-fill fs-4"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ patients.length }}</h3>
              <h6 class="text-muted fw-semibold mb-0">Total Patients</h6>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <button class="btn btn-outline-primary w-100 h-100 rounded-4 shadow-sm fw-bold d-flex flex-column align-items-center justify-content-center p-4 border-2" @click="openAvailabilityModal">
            <i class="bi bi-clock-history fs-1 mb-2"></i>
            Manage Availability
          </button>
        </div>
      </div>

      <!-- Main Layout -->
      <div class="row g-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm rounded-4 h-100">
            <div class="card-header bg-white border-bottom pt-4 px-4 pb-0">
               <ul class="nav nav-tabs border-bottom-0 pb-1" role="tablist">
                  <li class="nav-item" role="presentation">
                    <button class="nav-link fs-5 fw-semibold border-0 text-dark bg-transparent" :class="{ 'active text-primary border-bottom border-primary border-3': activeTab === 'schedule' }" @click="activeTab = 'schedule'">
                      My Schedule
                    </button>
                  </li>
                  <li class="nav-item ms-3" role="presentation">
                    <button class="nav-link fs-5 fw-semibold border-0 text-dark bg-transparent" :class="{ 'active text-primary border-bottom border-primary border-3': activeTab === 'patients' }" @click="activeTab = 'patients'">
                      My Patients
                    </button>
                  </li>
                </ul>
            </div>

            <!-- Schedule Tab -->
            <div class="card-body p-0" v-if="activeTab === 'schedule'">
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th class="ps-4 py-3 text-secondary fw-semibold">Date & Time</th>
                      <th class="py-3 text-secondary fw-semibold">Patient Name</th>
                      <th class="py-3 text-secondary fw-semibold">Status</th>
                      <th class="pe-4 py-3 text-end text-secondary fw-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="appointments.length === 0">
                       <td colspan="4" class="text-center py-5 text-muted">No appointments found.</td>
                    </tr>
                    <tr v-for="apt in appointments" :key="apt.id">
                      <td class="ps-4">
                        <div class="fw-bold text-dark">{{ apt.date }}</div>
                        <div class="small text-muted">{{ apt.time }}</div>
                      </td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="avatar bg-secondary bg-opacity-10 text-dark fw-bold rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 35px; height: 35px; font-size: 0.8rem;">
                            {{ getInitials(apt.patient) }}
                          </div>
                          <div>
                             <div class="fw-semibold text-dark">{{ apt.patient }}</div>
                             <div class="small text-muted">ID: #PT-{{ String(apt.patient_id).padStart(4, '0') }}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span :class="getStatusClass(apt.status)">{{ capitalize(apt.status) }}</span>
                      </td>
                      <td class="pe-4 text-end">
                        <div class="d-flex gap-2 justify-content-end" v-if="apt.status === 'booked' || apt.status === 'Scheduled'">
                           <button class="btn btn-sm btn-outline-success rounded-pill px-3 fw-semibold shadow-sm" @click="openTreatmentModal(apt)">
                             <i class="bi bi-check2-circle me-1"></i> Complete
                           </button>
                           <button class="btn btn-sm btn-outline-danger rounded-pill px-3 fw-semibold shadow-sm" @click="cancelAppointment(apt.id)">
                             <i class="bi bi-x-circle me-1"></i> Cancel
                           </button>
                        </div>
                        <div v-else>
                            <button class="btn btn-sm btn-light text-primary rounded-pill px-3 fw-semibold shadow-sm" @click="viewPatientHistoryById(apt.patient_id, apt.patient)">
                              <i class="bi bi-journal-medical me-1"></i> View History
                            </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Patients Tab -->
            <div class="card-body p-0" v-if="activeTab === 'patients'">
               <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th class="ps-4 py-3 text-secondary fw-semibold">Patient ID</th>
                      <th class="py-3 text-secondary fw-semibold">Patient Name</th>
                      <th class="py-3 text-secondary fw-semibold">Contact</th>
                      <th class="pe-4 py-3 text-end text-secondary fw-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="patients.length === 0">
                       <td colspan="4" class="text-center py-5 text-muted">No assigned patients found.</td>
                    </tr>
                    <tr v-for="pt in patients" :key="pt.id">
                      <td class="ps-4 fw-bold text-dark">
                        #PT-{{ String(pt.id).padStart(4, '0') }}
                      </td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="avatar bg-info bg-opacity-10 text-info fw-bold rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 35px; height: 35px; font-size: 0.8rem;">
                            {{ getInitials(pt.name) }}
                          </div>
                          <span class="fw-semibold text-dark">{{ pt.name }}</span>
                        </div>
                      </td>
                      <td>
                        <span class="text-muted"><i class="bi bi-telephone me-2"></i>{{ pt.contact || 'N/A' }}</span>
                      </td>
                      <td class="pe-4 text-end">
                        <button class="btn btn-sm btn-light text-primary rounded-pill px-3 fw-semibold shadow-sm" @click="viewPatientHistory(pt)">
                          <i class="bi bi-clipboard2-pulse me-1"></i> History
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Availability Modal -->
    <div class="modal fade" id="availabilityModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4">
          <div class="modal-header bg-primary text-white border-bottom-0 p-4">
            <h5 class="modal-title fw-bold">Manage 7-Day Availability</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <p class="text-muted mb-4">Select the days you are available to take appointments:</p>
            <div class="row g-3">
              <div v-for="(day, index) in days" :key="day" class="col-6 col-md-4">
                <div class="form-check form-switch p-3 border rounded-3 text-center transition-all" :class="editAvailability[index] ? 'border-primary bg-primary bg-opacity-10' : 'bg-light'">
                  <input class="form-check-input ms-0 mb-2 float-none" type="checkbox" :id="'day-'+index" v-model="editAvailability[index]" :true-value="1" :false-value="0">
                  <label class="form-check-label d-block fw-bold" :for="'day-'+index">{{ day }}</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0 p-4">
            <button type="button" class="btn btn-light rounded-pill px-4 fw-bold" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary rounded-pill px-4 fw-bold" @click="saveAvailability">Save Changes</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Treatment Modal (Completes Appointment) -->
    <div class="modal fade" id="treatmentModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow-lg rounded-4">
          <div class="modal-header bg-success text-white border-bottom-0 p-4">
            <h5 class="modal-title fw-bold">Complete Appointment - Add Treatment</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
             <div v-if="selectedAppointment" class="mb-4 p-3 bg-light rounded-3 d-flex justify-content-between align-items-center">
                <div>
                   <h6 class="fw-bold mb-1 text-dark">Patient: {{ selectedAppointment.patient }}</h6>
                   <p class="text-muted small mb-0">Scheduled for Date: {{ selectedAppointment.date }} at {{ selectedAppointment.time }}</p>
                </div>
             </div>
             <form @submit.prevent="submitTreatment">
                <div class="mb-3">
                  <label class="form-label fw-bold text-secondary">Diagnosis <span class="text-danger">*</span></label>
                  <input type="text" class="form-control rounded-3 p-2 bg-light border-0" v-model="treatmentForm.diagnosis" placeholder="Enter diagnosis" required>
                </div>
                <div class="mb-3">
                  <label class="form-label fw-bold text-secondary">Prescription (Rx)</label>
                  <textarea class="form-control rounded-3 p-2 bg-light border-0" rows="3" v-model="treatmentForm.prescription" placeholder="Medications, dosage, and instructions"></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label fw-bold text-secondary">Additional Notes</label>
                  <textarea class="form-control rounded-3 p-2 bg-light border-0" rows="3" v-model="treatmentForm.notes" placeholder="Any extra instructions for the patient"></textarea>
                </div>
                <div class="modal-footer border-top-0 p-0 pt-3 mt-4">
                  <button type="button" class="btn btn-light rounded-pill px-4 fw-bold" data-bs-dismiss="modal">Cancel</button>
                  <button type="submit" class="btn btn-success rounded-pill px-4 fw-bold">Save & Complete</button>
                </div>
             </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient History Modal -->
    <div class="modal fade" id="historyModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content border-0 shadow-lg rounded-4">
          <div class="modal-header bg-primary text-white border-bottom-0 p-4">
            <h5 class="modal-title fw-bold">Patient History</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4 bg-light">
            <div v-if="selectedPatient" class="mb-4 d-flex align-items-center">
              <div class="avatar bg-white shadow-sm text-primary fw-bold rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px; font-size: 1.2rem;">
                 {{ getInitials(selectedPatient.name) }}
              </div>
              <div>
                 <h5 class="fw-bold mb-0 text-dark">{{ selectedPatient.name }}</h5>
                 <p class="text-muted small mb-0">ID: #PT-{{ String(selectedPatient.id).padStart(4, '0') }}</p>
              </div>
            </div>

            <div v-if="patientHistoryLoading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            
            <div v-else-if="patientHistory.length === 0" class="text-center py-5 text-muted">
               <i class="bi bi-inbox fs-1 d-block mb-3 opacity-50"></i>
               No medical history found for this patient.
            </div>

            <div v-else class="history-timeline">
               <div v-for="hist in patientHistory" :key="hist.appointment_id" class="card border-0 shadow-sm rounded-4 mb-3">
                 <div class="card-header bg-white border-bottom-0 pt-3 pb-0 px-4 d-flex justify-content-between align-items-center">
                    <div>
                       <span class="fw-bold text-dark d-block"><i class="bi bi-calendar mb-1 me-2 text-primary"></i>{{ hist.date }}</span>
                       <small class="text-muted"><i class="bi bi-person-badge me-1"></i> Dr. {{ hist.doctor_name }} <span v-if="hist.doctor_specialization">({{ hist.doctor_specialization }})</span></small>
                    </div>
                    <span :class="getStatusClass(hist.status)">{{ capitalize(hist.status) }}</span>
                 </div>
                 <div class="card-body px-4 pb-4">
                    <div v-if="hist.diagnosis" class="mb-2">
                       <span class="fw-bold text-secondary text-uppercase" style="font-size: 0.8rem;">Diagnosis</span>
                       <p class="mb-0 text-dark">{{ hist.diagnosis }}</p>
                    </div>
                    <div v-if="hist.prescription" class="mb-2">
                       <span class="fw-bold text-secondary text-uppercase" style="font-size: 0.8rem;">Prescription</span>
                       <div class="bg-light p-2 rounded-3 text-dark mt-1" style="font-family: monospace;">{{ hist.prescription }}</div>
                    </div>
                    <div v-if="hist.notes" class="mb-0">
                       <span class="fw-bold text-secondary text-uppercase" style="font-size: 0.8rem;">Notes</span>
                       <p class="mb-0 text-muted small">{{ hist.notes }}</p>
                    </div>
                    <div v-if="!hist.diagnosis && !hist.prescription && !hist.notes" class="text-muted fst-italic small">
                      No treatment details recorded for this appointment.
                    </div>
                 </div>
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'DoctorDashboard',
  data() {
    return {
      activeTab: 'schedule',
      appointments: [],
      patients: [],
      patientHistory: [],
      patientHistoryLoading: false,
      isLoading: true,
      editAvailability: [0, 0, 0, 0, 0, 0, 0],
      days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      treatmentForm: {
        diagnosis: '',
        prescription: '',
        notes: ''
      },
      selectedAppointment: null,
      selectedPatient: null
    }
  },
  computed: {
    currentDate() {
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      return new Date().toLocaleDateString(undefined, options);
    },
    upcomingAppointments() {
       return this.appointments.filter(a => a.status.toLowerCase() === 'booked' || a.status.toLowerCase() === 'scheduled');
    },
    completedAppointments() {
       return this.appointments.filter(a => a.status.toLowerCase() === 'completed');
    }
  },
  async mounted() {
    await this.fetchDashboardData();
    await this.fetchPatients();
  },
  methods: {
    getInitials(name) {
      if (!name) return 'PT';
      return name.split(' ').map(n => n.charAt(0)).join('').toUpperCase().substring(0, 2);
    },
    capitalize(str) {
      if (!str) return '';
      return str.charAt(0).toUpperCase() + str.slice(1);
    },
    async fetchDashboardData() {
      this.isLoading = true;
      const token = localStorage.getItem('access_token');
      if (!token) return;

      try {
        const res = await fetch('http://localhost:5000/doctor/dashboard', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
          const data = await res.json();
          this.appointments = data.sort((a,b) => new Date(b.date) - new Date(a.date)); // Most recent first
        }
      } catch (err) {
        console.error('Error fetching doctor dashboard:', err);
      } finally {
        this.isLoading = false;
      }
    },
    async fetchPatients() {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      try {
        const res = await fetch('http://localhost:5000/doctor/patients', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
          this.patients = await res.json();
        }
      } catch (err) {
        console.error('Error fetching patients:', err);
      }
    },
    getStatusClass(status) {
      const st = (status || '').toLowerCase();
      const base = 'badge rounded-pill px-3 py-2 fw-semibold ';
      if (st === 'completed') return base + 'bg-success bg-opacity-10 text-success';
      if (st === 'booked' || st === 'scheduled') return base + 'bg-primary bg-opacity-10 text-primary';
      if (st === 'cancelled') return base + 'bg-danger bg-opacity-10 text-danger';
      return base + 'bg-secondary bg-opacity-10 text-secondary';
    },
    async openAvailabilityModal() {
      const token = localStorage.getItem('access_token');
      try {
        const res = await fetch('http://localhost:5000/doctor/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const profile = await res.json();
          this.editAvailability = profile.availability.split('').map(Number);
          const modal = Modal.getOrCreateInstance(document.getElementById('availabilityModal'));
          modal.show();
        }
      } catch (err) {
         console.error(err);
      }
    },
    async saveAvailability() {
      const token = localStorage.getItem('access_token');
      try {
        const res = await fetch('http://localhost:5000/doctor/availability', {
          method: 'PUT',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json' 
          },
          body: JSON.stringify({ availability: this.editAvailability.join('') })
        });
        if (res.ok) {
          Modal.getInstance(document.getElementById('availabilityModal')).hide();
        } else {
          alert('Failed to update availability.');
        }
      } catch(err) {
        console.error(err);
      }
    },
    async cancelAppointment(id) {
       if(!confirm('Are you sure you want to cancel this appointment?')) return;
       const token = localStorage.getItem('access_token');
       try {
         const res = await fetch(`http://localhost:5000/doctor/appointment/${id}/status`, {
           method: 'PUT',
           headers: { 
             'Authorization': `Bearer ${token}`,
             'Content-Type': 'application/json' 
           },
           body: JSON.stringify({ status: 'cancelled' })
         });
         if (res.ok) {
            this.fetchDashboardData();
         }
       } catch (err) {
         console.error('Error cancelling appointment:', err);
       }
    },
    openTreatmentModal(apt) {
       this.selectedAppointment = apt;
       this.treatmentForm = { diagnosis: '', prescription: '', notes: '' };
       const modal = Modal.getOrCreateInstance(document.getElementById('treatmentModal'));
       modal.show();
    },
    async submitTreatment() {
       if (!this.selectedAppointment) return;
       const token = localStorage.getItem('access_token');
       try {
         const res = await fetch(`http://localhost:5000/doctor/appointment/${this.selectedAppointment.id}/treatment`, {
           method: 'POST',
           headers: { 
             'Authorization': `Bearer ${token}`,
             'Content-Type': 'application/json' 
           },
           body: JSON.stringify(this.treatmentForm)
         });
         if (res.ok) {
            Modal.getInstance(document.getElementById('treatmentModal')).hide();
            this.fetchDashboardData();
         } else {
            alert('Failed to submit treatment.');
         }
       } catch (err) {
         console.error('Error submitting treatment:', err);
       }
    },
    viewPatientHistoryById(id, name) {
        this.viewPatientHistory({id: id, name: name});
    },
    async viewPatientHistory(patient) {
       this.selectedPatient = patient;
       this.patientHistoryLoading = true;
       this.patientHistory = [];
       const modal = Modal.getOrCreateInstance(document.getElementById('historyModal'));
       modal.show();

       const token = localStorage.getItem('access_token');
       try {
         const res = await fetch(`http://localhost:5000/doctor/patient/${patient.id}/history`, {
           headers: { 'Authorization': `Bearer ${token}` }
         });
         if (res.ok) {
            const data = await res.json();
            this.patientHistory = data.sort((a,b) => new Date(b.date) - new Date(a.date));
         }
       } catch (err) {
         console.error('Error fetching patient history:', err);
       } finally {
         this.patientHistoryLoading = false;
       }
    }
  }
}
</script>

<style scoped>
.table th {
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.nav-tabs .nav-link {
   transition: all 0.3s ease;
}
.nav-tabs .nav-link:hover {
   color: var(--bs-primary) !important;
}
.transition-all {
   transition: all 0.2s ease-in-out;
}
.history-timeline .card {
   border-left: 4px solid var(--bs-info) !important;
}
</style>
