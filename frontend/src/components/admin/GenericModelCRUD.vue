<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center py-3 flex-wrap gap-2">
      <h5 class="mb-0 fw-bold text-primary">{{ title }}</h5>
      <button class="btn btn-primary btn-sm rounded-pill px-3" data-bs-toggle="modal" :data-bs-target="'#' + modalId" @click="openAddModal">
        <i class="bi bi-plus-lg me-1"></i><span class="d-none d-sm-inline">Add New</span><span class="d-sm-none">Add</span>
      </button>
    </div>
    <div class="card-body p-0">
      <!-- Desktop table -->
      <div class="table-responsive d-none d-md-block">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th v-for="col in columns" :key="col.key" class="text-secondary fw-semibold">
                {{ col.label }}
              </th>
              <th class="text-end text-secondary fw-semibold pe-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="localData.length === 0">
              <td :colspan="columns.length + 1" class="text-center py-4 text-muted">
                No records found.
              </td>
            </tr>
            <tr v-for="item in localData" :key="item.id">
              <td v-for="col in columns" :key="col.key">
                <span v-if="col.type === 'badge'" :class="getBadgeClass(item[col.key])">
                  {{ item[col.key] }}
                </span>
                <div v-else-if="col.type === 'availability'" class="small text-muted">
                  {{ formatAvailability(item[col.key]) }}
                </div>
                <span v-else>{{ item[col.key] }}</span>
              </td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-2 rounded-circle" data-bs-toggle="modal" :data-bs-target="'#' + modalId" @click="openEditModal(item)" title="Edit">
                  <i class="bi bi-pencil-fill"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger rounded-circle" @click="deleteItem(item.id)" title="Delete">
                  <i class="bi bi-trash-fill"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Mobile card view -->
      <div class="d-md-none mobile-card-list">
        <div v-if="localData.length === 0" class="text-center py-4 text-muted">No records found.</div>
        <div v-for="item in localData" :key="'m-' + item.id" class="mobile-card">
          <div class="mobile-card-header">
            <div class="fw-semibold">{{ item[columns[0]?.key] || '—' }}</div>
            <span v-if="columns.find(c => c.key === 'id')" class="text-muted small">#{{ item.id }}</span>
          </div>
          <div class="mobile-card-body">
            <div v-for="col in columns.filter(c => c.key !== columns[0]?.key && c.key !== 'id')" :key="col.key" class="mobile-card-row">
              <span class="mobile-card-label">{{ col.label }}</span>
              <span v-if="col.type === 'badge'" :class="getBadgeClass(item[col.key])">{{ item[col.key] }}</span>
              <span v-else-if="col.type === 'availability'" class="small text-muted">{{ formatAvailability(item[col.key]) }}</span>
              <span v-else class="text-truncate" style="max-width: 180px;">{{ item[col.key] || '—' }}</span>
            </div>
          </div>
          <div class="mobile-card-actions">
            <button class="btn btn-sm btn-outline-secondary rounded-pill" data-bs-toggle="modal" :data-bs-target="'#' + modalId" @click="openEditModal(item)"><i class="bi bi-pencil-fill me-1"></i>Edit</button>
            <button class="btn btn-sm btn-outline-danger rounded-pill" @click="deleteItem(item.id)"><i class="bi bi-trash-fill me-1"></i>Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal for Add/Edit -->
    <div class="modal fade" :id="modalId" tabindex="-1" aria-hidden="true" ref="crudModal">
      <div class="modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header text-white" :class="isEdit ? 'bg-success' : 'bg-primary'">
            <h5 class="modal-title">{{ isEdit ? 'Edit' : 'Add' }} {{ singularTitle }}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="saveItem">
              <div class="mb-3" v-for="col in formColumns" :key="col.key">
                <label class="form-label text-secondary fw-semibold">{{ col.label }}</label>
                
                <select v-if="col.type === 'select'" v-model="formData[col.key]" class="form-select" required>
                  <option v-for="opt in col.options" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>

                <textarea v-else-if="col.type === 'textarea'" v-model="formData[col.key]" class="form-control" rows="3" required></textarea>

                <div v-else-if="col.type === 'availability'">
                  <div v-if="Array.isArray(formData[col.key])" class="d-flex flex-wrap gap-2">
                    <div v-for="(day, index) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="day" class="form-check form-check-inline">
                      <input 
                        class="form-check-input" 
                        type="checkbox" 
                        :id="'check-' + day + index"
                        v-model="formData[col.key][index]"
                        :true-value="1"
                        :false-value="0"
                      >
                      <label class="form-check-label small" :for="'check-' + day + index">{{ day }}</label>
                    </div>
                  </div>
                  <div v-else class="text-muted small">Loading availability...</div>
                </div>

                <input v-else :type="col.type || 'text'" v-model="formData[col.key]" class="form-control" required>
              </div>
              <div class="d-flex justify-content-end mt-4">
                <button type="button" ref="closeModalBtn" class="btn btn-light me-2 rounded-pill px-4" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn rounded-pill px-4" :class="isEdit ? 'btn-success' : 'btn-primary'">
                  {{ isEdit ? 'Save Changes' : 'Create' }}
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
// We use bootstrap from window if imported in main.js
export default {
  name: 'GenericModelCRUD',
  props: {
    title: { type: String, required: true },
    singularTitle: { type: String, required: true },
    columns: { type: Array, required: true },
    initialData: { type: Array, required: true }
  },
  data() {
    return {
      localData: [...this.initialData],
      isEdit: false,
      formData: {},
      modalId: 'crudModal-' + Math.random().toString(36).substr(2, 9),
      modalInstance: null
    }
  },
  computed: {
    // Exclude basic id from form columns unless specifically needed, but typically we auto-gen id
    formColumns() {
      return this.columns.filter(c => c.key !== 'id');
    }
  },
  watch: {
    initialData: {
      handler(newVal) {
        this.localData = [...newVal];
      },
      deep: true,
      immediate: true
    }
  },
  mounted() {
    // Bootstrap modal init
  },
  methods: {
    openAddModal() {
      this.isEdit = false;
      this.formData = {};
      
      // Initialize form with default types
      this.formColumns.forEach(c => {
        if (c.type === 'availability') {
          this.formData[c.key] = [0, 0, 0, 0, 0, 0, 0];
        } else {
          this.formData[c.key] = c.default || '';
        }
      });
    },
    openEditModal(item) {
      this.isEdit = true;
      this.formData = { ...item };
      
      // Try to parse availability if it's a string
      this.formColumns.forEach(c => {
        if (c.type === 'availability') {
          const val = this.formData[c.key];
          if (typeof val === 'string' && val.length === 7) {
             this.formData[c.key] = val.split('').map(Number);
          } else if (!Array.isArray(val)) {
             this.formData[c.key] = [0, 0, 0, 0, 0, 0, 0];
          }
        }
      });
    },
    saveItem() {
      // Stringify availability before emitting
      const submitData = { ...this.formData };
      this.formColumns.forEach(c => {
        if (c.type === 'availability' && Array.isArray(submitData[c.key])) {
          submitData[c.key] = submitData[c.key].join('');
        }
      });

      if (this.isEdit) {
        const index = this.localData.findIndex(i => i.id === submitData.id);
        if (index !== -1) {
          this.localData[index] = { ...submitData };
        }
        this.$emit('edit-item', { ...submitData });
      } else {
        this.$emit('add-item', { ...submitData });
      }
      
      // Close modal gracefully
      if (this.$refs.closeModalBtn) {
        this.$refs.closeModalBtn.click();
      }
      this.$emit('data-changed', this.localData);
    },
    deleteItem(id) {
      if (confirm(`Are you sure you want to delete this ${this.singularTitle}?`)) {
        this.$emit('delete-item', id);
        this.localData = this.localData.filter(i => i.id !== id);
        this.$emit('data-changed', this.localData);
      }
    },
    getBadgeClass(value) {
      const v = String(value).toLowerCase();
      if (['admin', 'completed'].includes(v)) return 'badge bg-success';
      if (['doctor', 'booked'].includes(v)) return 'badge bg-primary';
      if (['patient'].includes(v)) return 'badge bg-info text-dark';
      if (['cancelled'].includes(v)) return 'badge bg-danger';
      return 'badge bg-secondary';
    },
    formatAvailability(val) {
      if (!val || typeof val !== 'string' || val.length !== 7) return 'Not set';
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      const available = [];
      for (let i = 0; i < 7; i++) {
        if (val[i] === '1') available.push(days[i]);
      }
      return available.length > 0 ? available.join(', ') : 'None';
    }
  }
}
</script>

<style scoped>
.table th {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.btn-outline-secondary {
  border-color: transparent;
}
.btn-outline-secondary:hover {
  background-color: #f8f9fa;
  color: #0d6efd;
}
.btn-outline-danger {
  border-color: transparent;
}
.btn-outline-danger:hover {
  background-color: #f8f9fa;
  color: #dc3545;
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
  align-items: center;
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
</style>
