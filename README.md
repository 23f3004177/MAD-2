# Trimed backend API structure

This documentation provides an overview of the core endpoints used within the Trimed Hospital Management System (HMS), organized by user role and domain logic.

## 🔑 Authentication Routes
Handled by `auth.py`.

* **`POST /auth/register`** 
  Register a new patient account in the system (auto-creates User & Patient records).
* **`POST /auth/login`** 
  Universal login for Admin, Doctor, and Patient roles. Returns a JWT access token.
* **`GET /auth/me`** 
  Returns the current profile of the decoded JWT token.

## 🛠️ Admin Routes
All start with `/admin/` and require Admin JWT permissions (`admin.py`).

### Dashboard & Analytics
* **`GET /dashboard`** - High-level statistics (upcoming/past appointments, total users).

### Doctors
* **`GET /doctors`** - List all active doctors.
* **`POST /doctor`** - Create a new doctor profile (and user credentials).
* **`PUT /doctor/<id>`** - Update doctor details (specialization, availability, department etc).
* **`DELETE /doctor/<id>`** - Delete a doctor (and cascading appointment history).

### Patients
* **`GET /patients`** - List all registered patients.
* **`POST /patient`** - Admin manually registers a patient.
* **`PUT /patient/<id>`** - Update patient records.
* **`DELETE /patient/<id>`** - Remove a patient from the system.

### Appointments & Treatments
* **`GET /appointments`** - Full list of all appointments.
* **`POST /appointment`** - Book an appointment on behalf of a patient.
* **`PUT /appointment/<id>`** - Change appointment status (e.g. booked to cancelled).
* **`DELETE /appointment/<id>`** - Remove a specific appointment completely.
* **`GET /treatments`** - Pull wide treatment details mapped for appointments.
* **`POST /treatment`** - Attach a treatment to an appointment.
* **`PUT /treatment/<id>`** - Update treatment data.
* **`DELETE /treatment/<id>`** - Remove treatment references.

### Operations & Config
* **`GET /departments`** / **`POST /departments`** - Create and list hospital departments.
* **`PUT /department/<id>`** / **`DELETE /department/<id>`** - Modify department configs.
* **`GET /search?q=`** - System-wide global fuzzy search for users.
* **`GET /users`** - List raw system application users.
* **`POST /user/<id>/blacklist`** - Instantly blocklist or unblocklist any specific user in the ecosystem.

## 🩺 Doctor Routes
All start with `/doctor/` and require Doctor JWT permissions (`doctor.py`).

* **`GET /dashboard`** - Upcoming schedules and booked appointments for the doc.
* **`GET /patients`** - List unique patients registered under this doctor's appointments.
* **`GET /profile`** - Current doctor profile and bio constraints.
* **`PUT /availability`** - Updates a 7-day bitmask (e.g., `1111100`) defining their shifts.
* **`PUT /appointment/<id>/status`** - Toggles statuses on their own appointments.
* **`POST /appointment/<id>/treatment`** - Fills out diagnosis & prescription for a completed visit.
* **`GET /patient/<id>/history`** - Fetches medical history for a chosen patient (safeguarded logic).

## 🧑‍⚕️ Patient Routes
All start with `/patient/` and require Patient JWT permissions (`patient.py`).

* **`GET /profile`** / **`PUT /profile`** - View and manage personal details.
* **`GET /dashboard`** - Timeline visualization of upcoming slots & history overviews.
* **`POST /export-history`** - Dispatches an async Celery task sending a CSV email representation of the patient's record over time.
* **`GET /departments`** - List domains they can book from.
* **`GET /doctors`** - Explore and search valid hospital doctors based on specialization / department.
* **`POST /appointment`** - Reserve a timeline block matching doctor shifts.
* **`PUT /appointment/<id>/cancel`** - Self-cancel a booked upcoming meeting.
