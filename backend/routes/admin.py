from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Doctor, Patient, Appointment, Department, Treatment
from datetime import datetime
import re
from extensions import cache

DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

admin_bp = Blueprint('admin', __name__)


# ----------------------
# HELPER: CHECK ADMIN
# ----------------------
def admin_required():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return None, jsonify({"msg": "Admin access required"}), 403
    return current_user, None, None


def is_valid_email(email):
    """Simple email validation."""
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


# ----------------------
# ADMIN DASHBOARD STATS
# ----------------------
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def dashboard():
    user, err, code = admin_required()
    if err:
        return err, code

    today = datetime.utcnow().date()
    upcoming = Appointment.query.filter(
        Appointment.date >= today,
        Appointment.status == 'booked'
    ).count()
    past = Appointment.query.filter(
        db.or_(
            Appointment.date < today,
            Appointment.status.in_(['completed', 'cancelled'])
        )
    ).count()
    blacklisted = User.query.filter_by(is_blacklisted=True).count()

    return jsonify({
        "total_doctors": Doctor.query.count(),
        "total_patients": Patient.query.count(),
        "total_appointments": Appointment.query.count(),
        "upcoming_appointments": upcoming,
        "past_appointments": past,
        "blacklisted_users": blacklisted
    })


# ----------------------
# ADD DOCTOR (with auto user creation)
# ----------------------
@admin_bp.route('/doctor', methods=['POST'])
@jwt_required()
def add_doctor():
    user, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()

    email = data.get('email', '').strip()
    if not email or not is_valid_email(email):
        return jsonify({"msg": "A valid email is required for the doctor account."}), 400

    # Check if user with this email already exists
    existing_user = User.query.filter_by(username=email).first()
    if existing_user:
        # Check if already a doctor
        existing_doc = Doctor.query.filter_by(user_id=existing_user.id).first()
        if existing_doc:
            return jsonify({"msg": "A doctor with this email already exists."}), 400
        # Reuse existing user, update role
        existing_user.role = 'doctor'
        existing_user.name = data.get('name', existing_user.name)
        db.session.flush()
        doctor = Doctor(
            user_id=existing_user.id,
            department_id=data.get('department_id'),
            specialization=data.get('specialization', 'General'),
            availability=data.get('availability', '0000000')
        )
        db.session.add(doctor)
        db.session.commit()
        return jsonify({"msg": "Doctor profile created for existing user."}), 201

    password = data.get('password', 'password123')
    new_user = User(
        username=email,
        password=password,
        role='doctor',
        name=data.get('name', ''),
        contact=data.get('contact', '')
    )
    db.session.add(new_user)
    db.session.flush()

    doctor = Doctor(
        user_id=new_user.id,
        department_id=data.get('department_id'),
        specialization=data.get('specialization', 'General'),
        availability=data.get('availability', '0000000')
    )
    db.session.add(doctor)
    db.session.commit()

    return jsonify({"msg": "Doctor created successfully."}), 201


# ----------------------
# GET ALL DOCTORS (null-safe)
# ----------------------
@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    user, err, code = admin_required()
    if err:
        return err, code

    doctors = Doctor.query.all()
    result = []
    for d in doctors:
        if not d.user:
            # Skip orphaned doctor records (no associated user)
            continue
        result.append({
            "id": d.id,
            "user_id": d.user_id,
            "name": d.user.name or '',
            "username": d.user.username or '',
            "contact": d.user.contact or '',
            "department_id": d.department_id,
            "department_name": d.department.name if d.department else 'N/A',
            "specialization": d.specialization or '',
            "availability": d.availability or '0000000',
            "is_blacklisted": d.user.is_blacklisted
        })

    return jsonify(result)


# ----------------------
# UPDATE DOCTOR
# ----------------------
@admin_bp.route('/doctor/<int:id>', methods=['PUT'])
@jwt_required()
def update_doctor(id):
    user, err, code = admin_required()
    if err:
        return err, code

    doctor = Doctor.query.get_or_404(id)
    data = request.get_json()

    doctor.availability = data.get('availability', doctor.availability)
    doctor.department_id = data.get('department_id', doctor.department_id)
    doctor.specialization = data.get('specialization', doctor.specialization)

    if doctor.user:
        if 'name' in data:
            doctor.user.name = data['name']
        if 'contact' in data:
            doctor.user.contact = data['contact']

    db.session.commit()
    return jsonify({"msg": "Doctor updated"})


# ----------------------
# DELETE DOCTOR
# ----------------------
@admin_bp.route('/doctor/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(id):
    user, err, code = admin_required()
    if err:
        return err, code

    doctor = Doctor.query.get_or_404(id)

    # Delete associated appointments first
    Appointment.query.filter_by(doctor_id=doctor.id).delete()

    if doctor.user:
        db.session.delete(doctor.user)
    db.session.delete(doctor)
    db.session.commit()

    return jsonify({"msg": "Doctor deleted"})


# ----------------------
# GET ALL APPOINTMENTS
# ----------------------
@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    user, err, code = admin_required()
    if err:
        return err, code

    appointments = Appointment.query.order_by(Appointment.date.desc()).all()

    result = []
    for a in appointments:
        patient_name = 'Unknown'
        doctor_name = 'Unknown'
        if a.patient and a.patient.user:
            patient_name = a.patient.user.name or 'Unnamed'
        if a.doctor and a.doctor.user:
            doctor_name = a.doctor.user.name or 'Unnamed'

        result.append({
            "id": a.id,
            "patient": patient_name,
            "patient_id": a.patient_id,
            "doctor": doctor_name,
            "doctor_id": a.doctor_id,
            "date": str(a.date),
            "time": a.time,
            "status": a.status
        })

    return jsonify(result)


# ----------------------
# BOOK APPOINTMENT (ADMIN)
# ----------------------
@admin_bp.route('/appointment', methods=['POST'])
@jwt_required()
def admin_book_appointment():
    user, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    time = data.get('time')

    if not all([patient_id, doctor_id, date_str, time]):
        return jsonify({"msg": "patient_id, doctor_id, date, and time are required"}), 400

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404
    if patient.user and patient.user.is_blacklisted:
        return jsonify({"msg": f"Patient '{patient.user.name}' is blacklisted and cannot book appointments."}), 403

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404
    if doctor.user and doctor.user.is_blacklisted:
        return jsonify({"msg": f"Doctor '{doctor.user.name}' is blacklisted and cannot accept appointments."}), 403

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_index = date.weekday()
    if doctor.availability and len(doctor.availability) == 7 and doctor.availability[day_index] != '1':
        available_days = [DAY_NAMES[i] for i, ch in enumerate(doctor.availability) if ch == '1']
        doc_name = doctor.user.name if doctor.user else 'Doctor'
        return jsonify({
            "msg": f"Dr. {doc_name} is not available on {DAY_NAMES[day_index]}. "
                   f"Available days: {', '.join(available_days) or 'None'}"
        }), 400

    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=date,
        time=time
    ).filter(Appointment.status != 'cancelled').first()

    if existing:
        return jsonify({"msg": "This time slot is already booked. Please choose another time."}), 400

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=date,
        time=time,
        status='booked'
    )
    db.session.add(appointment)
    db.session.commit()

    return jsonify({"msg": "Appointment booked successfully!"}), 201


# ----------------------
# CANCEL/UPDATE APPOINTMENT (ADMIN)
# ----------------------
@admin_bp.route('/appointment/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_appointment(id):
    user, err, code = admin_required()
    if err:
        return err, code

    appointment = Appointment.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({"msg": "Appointment deleted"})

    if request.method == 'PUT':
        data = request.get_json()
        appointment.status = data.get('status', appointment.status)
        db.session.commit()
        return jsonify({"msg": "Appointment updated"})


# ----------------------
# SEARCH USERS
# ----------------------
@admin_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    user, err, code = admin_required()
    if err:
        return err, code

    query = request.args.get('q', '')

    users = User.query.filter(
        db.or_(
            User.username.ilike(f"%{query}%"),
            User.name.ilike(f"%{query}%"),
            User.contact.ilike(f"%{query}%")
        )
    ).all()

    depts = Department.query.filter(Department.name.ilike(f"%{query}%")).all()
    dept_ids = [d.id for d in depts]

    if dept_ids:
        doctors_in_depts = Doctor.query.filter(Doctor.department_id.in_(dept_ids)).all()
        existing_user_ids = [u.id for u in users]
        for doc in doctors_in_depts:
            if doc.user and doc.user.id not in existing_user_ids:
                users.append(doc.user)

    result = []
    for u in users:
        doc = None
        if u.role == 'doctor':
            doc = Doctor.query.filter_by(user_id=u.id).first()

        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "name": u.name,
            "contact": u.contact,
            "is_blacklisted": u.is_blacklisted,
            "specialization": doc.specialization if doc else None,
            "department": doc.department.name if doc and doc.department else None
        })

    return jsonify(result)


# ----------------------
# USERS CRUD
# ----------------------
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30)
def get_users():
    user, err, code = admin_required()
    if err:
        return err, code

    users = User.query.all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "name": u.name,
            "contact": u.contact,
            "is_blacklisted": u.is_blacklisted
        })
    return jsonify(result)


@admin_bp.route('/user', methods=['POST'])
@jwt_required()
def add_user():
    user, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    email = data.get('username', '').strip()
    if not email or not is_valid_email(email):
        return jsonify({"msg": "A valid email address is required as username."}), 400

    # Check duplicate
    if User.query.filter_by(username=email).first():
        return jsonify({"msg": "A user with this email already exists."}), 400

    role = data.get('role', 'patient')
    new_user = User(
        username=email,
        password=data.get('password', 'defaultpassword'),
        role=role,
        name=data.get('name', ''),
        contact=data.get('contact', ''),
        is_blacklisted=False
    )
    db.session.add(new_user)
    db.session.flush()

    # Auto-create Patient profile if role is patient
    if role == 'patient':
        patient = Patient(user_id=new_user.id)
        db.session.add(patient)

    db.session.commit()
    return jsonify({"msg": f"User created successfully as {role}."}), 201


@admin_bp.route('/user/<int:id>/blacklist', methods=['POST'])
@jwt_required()
def toggle_blacklist(id):
    user, err, code = admin_required()
    if err:
        return err, code

    target_user = User.query.get_or_404(id)
    if target_user.id == user['id']:
        return jsonify({"msg": "Cannot blacklist yourself"}), 400

    target_user.is_blacklisted = not target_user.is_blacklisted
    db.session.commit()
    msg = "blacklisted" if target_user.is_blacklisted else "un-blacklisted"
    return jsonify({"msg": f"User successfully {msg}", "is_blacklisted": target_user.is_blacklisted})


@admin_bp.route('/user/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_user(id):
    user, err, code = admin_required()
    if err:
        return err, code

    target_user = User.query.get_or_404(id)

    if request.method == 'DELETE':
        # Delete associated profiles
        Doctor.query.filter_by(user_id=id).delete()
        Patient.query.filter_by(user_id=id).delete()
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({"msg": "User deleted"})

    if request.method == 'PUT':
        data = request.get_json()
        target_user.name = data.get('name', target_user.name)
        target_user.contact = data.get('contact', target_user.contact)
        if 'role' in data:
            target_user.role = data['role']
        db.session.commit()
        return jsonify({"msg": "User updated"})


# ----------------------
# DEPARTMENTS CRUD
# ----------------------
@admin_bp.route('/departments', methods=['GET', 'POST'])
@jwt_required()
@cache.cached(timeout=3600, query_string=True, unless=lambda: request.method != 'GET')
def manage_departments():
    user, err, code = admin_required()
    if err:
        return err, code

    if request.method == 'GET':
        depts = Department.query.all()
        return jsonify([{"id": d.id, "name": d.name, "description": d.description} for d in depts])

    if request.method == 'POST':
        data = request.get_json()
        dept = Department(name=data['name'], description=data.get('description', ''))
        db.session.add(dept)
        db.session.commit()
        return jsonify({"msg": "Department added"}), 201


@admin_bp.route('/department/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def modify_department(id):
    user, err, code = admin_required()
    if err:
        return err, code
    dept = Department.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(dept)
        db.session.commit()
        return jsonify({"msg": "Department deleted"})

    if request.method == 'PUT':
        data = request.get_json()
        dept.name = data.get('name', dept.name)
        dept.description = data.get('description', dept.description)
        db.session.commit()
        return jsonify({"msg": "Department updated"})


# ----------------------
# PATIENTS CRUD
# ----------------------
@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30, query_string=True)
def get_patients():
    user, err, code = admin_required()
    if err:
        return err, code
        
    query_str = request.args.get('q', '').lower()
    
    patients = Patient.query.all()
    result = []
    for p in patients:
        if not p.user:
            continue
            
        p_name = (p.user.name or '').lower()
        p_contact = (p.user.contact or '').lower()
        p_id = str(p.id)
        
        if query_str and (query_str not in p_name and query_str not in p_contact and query_str != p_id):
            continue
            
        result.append({
            "id": p.id,
            "user_id": p.user_id,
            "name": p.user.name or '',
            "username": p.user.username or '',
            "contact": p.user.contact or '',
            "is_blacklisted": p.user.is_blacklisted
        })
    return jsonify(result)


@admin_bp.route('/patient', methods=['POST'])
@jwt_required()
def add_patient():
    """Add a new patient (auto-creates user account)."""
    user, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    email = data.get('email', '').strip()
    if not email or not is_valid_email(email):
        return jsonify({"msg": "A valid email is required for the patient account."}), 400

    existing_user = User.query.filter_by(username=email).first()
    if existing_user:
        existing_patient = Patient.query.filter_by(user_id=existing_user.id).first()
        if existing_patient:
            return jsonify({"msg": "A patient with this email already exists."}), 400
        # Create patient profile for existing user
        existing_user.role = 'patient'
        existing_user.name = data.get('name', existing_user.name)
        patient = Patient(user_id=existing_user.id)
        db.session.add(patient)
        db.session.commit()
        return jsonify({"msg": "Patient profile created for existing user."}), 201

    password = data.get('password', 'password123')
    new_user = User(
        username=email,
        password=password,
        role='patient',
        name=data.get('name', ''),
        contact=data.get('contact', '')
    )
    db.session.add(new_user)
    db.session.flush()

    patient = Patient(user_id=new_user.id)
    db.session.add(patient)
    db.session.commit()

    return jsonify({"msg": "Patient created successfully."}), 201


@admin_bp.route('/patient/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_patient(id):
    user, err, code = admin_required()
    if err:
        return err, code

    patient = Patient.query.get_or_404(id)

    if request.method == 'DELETE':
        # Delete associated appointments
        Appointment.query.filter_by(patient_id=patient.id).delete()
        if patient.user:
            db.session.delete(patient.user)
        db.session.delete(patient)
        db.session.commit()
        return jsonify({"msg": "Patient deleted"})

    if request.method == 'PUT':
        data = request.get_json()
        if patient.user:
            patient.user.name = data.get('name', patient.user.name)
            patient.user.contact = data.get('contact', patient.user.contact)
        db.session.commit()
        return jsonify({"msg": "Patient updated"})


# ----------------------
# TREATMENTS CRUD
# ----------------------
@admin_bp.route('/treatments', methods=['GET'])
@jwt_required()
def get_treatments():
    user, err, code = admin_required()
    if err:
        return err, code
    treatments = Treatment.query.all()
    result = []
    for t in treatments:
        apt = t.appointment
        label = f"Apt #{t.appointment_id}"
        if apt:
            patient_name = 'Unknown'
            doctor_name = 'Unknown'
            if apt.patient and apt.patient.user:
                patient_name = apt.patient.user.name or 'Unnamed'
            if apt.doctor and apt.doctor.user:
                doctor_name = apt.doctor.user.name or 'Unnamed'
            label = f"#{apt.id} — {patient_name} with Dr. {doctor_name} on {apt.date}"

        result.append({
            "id": t.id,
            "appointment_id": t.appointment_id,
            "appointment_label": label,
            "diagnosis": t.diagnosis,
            "prescription": t.prescription,
            "notes": t.notes
        })
    return jsonify(result)


@admin_bp.route('/treatment', methods=['POST'])
@jwt_required()
def add_treatment():
    user, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    appointment_id = data.get('appointment_id')
    if not appointment_id:
        return jsonify({"msg": "appointment_id is required"}), 400

    apt = Appointment.query.get(appointment_id)
    if not apt:
        return jsonify({"msg": "Appointment not found"}), 404

    treatment = Treatment(
        appointment_id=appointment_id,
        diagnosis=data.get('diagnosis', ''),
        prescription=data.get('prescription', ''),
        notes=data.get('notes', '')
    )
    db.session.add(treatment)
    db.session.commit()
    return jsonify({"msg": "Treatment added", "id": treatment.id}), 201


@admin_bp.route('/treatment/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_treatment(id):
    user, err, code = admin_required()
    if err:
        return err, code

    treatment = Treatment.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(treatment)
        db.session.commit()
        return jsonify({"msg": "Treatment deleted"})

    if request.method == 'PUT':
        data = request.get_json()
        treatment.appointment_id = data.get('appointment_id', treatment.appointment_id)
        treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
        treatment.prescription = data.get('prescription', treatment.prescription)
        treatment.notes = data.get('notes', treatment.notes)
        db.session.commit()
        return jsonify({"msg": "Treatment updated"})