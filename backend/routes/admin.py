from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import re
from datetime import datetime
from models import db, User, Doctor, Patient, Appointment, Department, Treatment
from extensions import cache

DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
admin_bp = Blueprint('admin', __name__)

def admin_required():
    """Ensure the user is an admin."""
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return None, jsonify({"msg": "Admin access required!"}), 403
    return current_user, None, None

def is_valid_email(email):
    """Simple email wrapper."""
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


# ----------------------
# DASHBOARD STATS
# ----------------------
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def dashboard():
    user, err, code = admin_required()
    if err: return err, code

    today = datetime.utcnow().date()
    # Summarize all counts needed for the admin layout
    upcoming = Appointment.query.filter(Appointment.date >= today, Appointment.status == 'booked').count()
    past = Appointment.query.filter(db.or_(Appointment.date < today, Appointment.status.in_(['completed', 'cancelled']))).count()

    return jsonify({
        "total_doctors": Doctor.query.count(),
        "total_patients": Patient.query.count(),
        "total_appointments": Appointment.query.count(),
        "upcoming_appointments": upcoming,
        "past_appointments": past,
        "blacklisted_users": User.query.filter_by(is_blacklisted=True).count()
    })


# ----------------------
# DOCTORS
# ----------------------
@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    user, err, code = admin_required()
    if err: return err, code

    return jsonify([{
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
    } for d in Doctor.query.all() if d.user])

@admin_bp.route('/doctor', methods=['POST'])
@jwt_required()
def add_doctor():
    user, err, code = admin_required()
    if err: return err, code

    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email or not is_valid_email(email):
        return jsonify({"msg": "Wait, we need a valid email to make a doctor account."}), 400

    existing_user = User.query.filter_by(username=email).first()
    
    if existing_user:
        if Doctor.query.filter_by(user_id=existing_user.id).first():
            return jsonify({"msg": "A doctor with this email is already registered."}), 400
        
        # Promote existing user to doctor
        existing_user.role = 'doctor'
        existing_user.name = data.get('name', existing_user.name)
        db.session.flush()
        uid = existing_user.id
    else:
        # Create fresh user
        new_user = User(
            username=email,
            password=data.get('password', 'password123'),
            role='doctor',
            name=data.get('name', ''),
            contact=data.get('contact', '')
        )
        db.session.add(new_user)
        db.session.flush()
        uid = new_user.id

    db.session.add(Doctor(
        user_id=uid,
        department_id=data.get('department_id'),
        specialization=data.get('specialization', 'General'),
        availability=data.get('availability', '0000000')
    ))
    db.session.commit()
    
    return jsonify({"msg": "Doctor added successfully."}), 201

@admin_bp.route('/doctor/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_doctor(id):
    user, err, code = admin_required()
    if err: return err, code

    doctor = Doctor.query.get_or_404(id)

    if request.method == 'DELETE':
        Appointment.query.filter_by(doctor_id=doctor.id).delete()
        if doctor.user: db.session.delete(doctor.user)
        db.session.delete(doctor)
        db.session.commit()
        return jsonify({"msg": "Doctor removed from system."})

    data = request.get_json()
    if 'availability' in data: doctor.availability = data['availability']
    if 'department_id' in data: doctor.department_id = data['department_id']
    if 'specialization' in data: doctor.specialization = data['specialization']

    if doctor.user:
        if 'name' in data: doctor.user.name = data['name']
        if 'contact' in data: doctor.user.contact = data['contact']

    db.session.commit()
    return jsonify({"msg": "Doctor updated."})


# ----------------------
# PATIENTS
# ----------------------
@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30, query_string=True)
def get_patients():
    user, err, code = admin_required()
    if err: return err, code

    query_str = request.args.get('q', '').lower()
    
    result = []
    for p in Patient.query.all():
        if not p.user: continue
        
        # Simple text search on name or contact or ID
        str_fields = [p.user.name or '', p.user.contact or '', str(p.id)]
        if query_str and not any(query_str in f.lower() for f in str_fields):
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
    user, err, code = admin_required()
    if err: return err, code

    data = request.get_json()
    email = data.get('email', '').strip()
    if not email or not is_valid_email(email):
        return jsonify({"msg": "Please provide a valid email."}), 400

    existing_user = User.query.filter_by(username=email).first()
    if existing_user:
        if Patient.query.filter_by(user_id=existing_user.id).first():
            return jsonify({"msg": "Patient already registered!"}), 400
        
        # Attach to existing
        existing_user.role = 'patient'
        existing_user.name = data.get('name', existing_user.name)
        db.session.add(Patient(user_id=existing_user.id))
        db.session.commit()
        return jsonify({"msg": "Attached patient profile to existing user."}), 201

    new_user = User(
        username=email,
        password=data.get('password', 'password123'),
        role='patient',
        name=data.get('name', ''),
        contact=data.get('contact', '')
    )
    db.session.add(new_user)
    db.session.flush()
    db.session.add(Patient(user_id=new_user.id))
    db.session.commit()

    return jsonify({"msg": "Patient created successfully."}), 201

@admin_bp.route('/patient/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_patient(id):
    user, err, code = admin_required()
    if err: return err, code

    patient = Patient.query.get_or_404(id)

    if request.method == 'DELETE':
        Appointment.query.filter_by(patient_id=patient.id).delete()
        if patient.user: db.session.delete(patient.user)
        db.session.delete(patient)
        db.session.commit()
        return jsonify({"msg": "Patient deleted."})

    data = request.get_json()
    if patient.user:
        if 'name' in data: patient.user.name = data['name']
        if 'contact' in data: patient.user.contact = data['contact']
        db.session.commit()
        
    return jsonify({"msg": "Patient updated."})


# ----------------------
# APPOINTMENTS
# ----------------------
@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    user, err, code = admin_required()
    if err: return err, code

    return jsonify([{
        "id": a.id,
        "patient": a.patient.user.name if a.patient and a.patient.user else 'Unknown',
        "patient_id": a.patient_id,
        "doctor": a.doctor.user.name if a.doctor and a.doctor.user else 'Unknown',
        "doctor_id": a.doctor_id,
        "date": str(a.date),
        "time": a.time,
        "status": a.status
    } for a in Appointment.query.order_by(Appointment.date.desc()).all()])

@admin_bp.route('/appointment', methods=['POST'])
@jwt_required()
def admin_book_appointment():
    user, err, code = admin_required()
    if err: return err, code

    data = request.get_json()
    patient_id, doctor_id, date_str, time = data.get('patient_id'), data.get('doctor_id'), data.get('date'), data.get('time')

    if not all([patient_id, doctor_id, date_str, time]):
        return jsonify({"msg": "Missing required booking details."}), 400

    patient, doctor = Patient.query.get(patient_id), Doctor.query.get(doctor_id)
    if not patient or not doctor: return jsonify({"msg": "Invalid patient or doctor."}), 404
    
    if patient.user and patient.user.is_blacklisted:
        return jsonify({"msg": "Cannot book for blacklisted patient."}), 403
    if doctor.user and doctor.user.is_blacklisted:
        return jsonify({"msg": "Cannot book with blacklisted doctor."}), 403

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_index = date.weekday()
    
    if len(doctor.availability) == 7 and doctor.availability[day_index] != '1':
        avail_days = [DAY_NAMES[i] for i, ch in enumerate(doctor.availability) if ch == '1']
        return jsonify({"msg": f"Dr. {doctor.user.name or ''} isn't available on {DAY_NAMES[day_index]}. Day(s) available: {', '.join(avail_days)}"}), 400

    if Appointment.query.filter_by(doctor_id=doctor_id, date=date, time=time).filter(Appointment.status != 'cancelled').first():
        return jsonify({"msg": "Timeslot already booked!"}), 400

    db.session.add(Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date, time=time, status='booked'))
    db.session.commit()

    return jsonify({"msg": "Appointment booked to schedule!"}), 201

@admin_bp.route('/appointment/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_appointment(id):
    user, err, code = admin_required()
    if err: return err, code

    appointment = Appointment.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({"msg": "Appointment destroyed."})

    data = request.get_json()
    if 'status' in data: appointment.status = data['status']
    db.session.commit()
    return jsonify({"msg": "Appointment status updated."})


# ----------------------
# TREATMENTS
# ----------------------
@admin_bp.route('/treatments', methods=['GET'])
@jwt_required()
def get_treatments():
    user, err, code = admin_required()
    if err: return err, code

    result = []
    for t in Treatment.query.all():
        apt = t.appointment
        label = f"Apt #{t.appointment_id}"
        
        if apt:
            patient_name = apt.patient.user.name if apt.patient and apt.patient.user else 'Unknown'
            doc_name = apt.doctor.user.name if apt.doctor and apt.doctor.user else 'Unknown'
            label = f"#{apt.id} \u2014 {patient_name} & Dr. {doc_name} ({apt.date})"

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
    if err: return err, code

    data = request.get_json()
    apt_id = data.get('appointment_id')
    if not Appointment.query.get(apt_id):
        return jsonify({"msg": "Appointment does not exist."}), 404

    db.session.add(Treatment(
        appointment_id=apt_id,
        diagnosis=data.get('diagnosis', ''),
        prescription=data.get('prescription', ''),
        notes=data.get('notes', '')
    ))
    db.session.commit()
    return jsonify({"msg": "Treatment saved!"}), 201

@admin_bp.route('/treatment/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_treatment(id):
    user, err, code = admin_required()
    if err: return err, code

    treatment = Treatment.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(treatment)
        db.session.commit()
        return jsonify({"msg": "Treatment deleted."})

    data = request.get_json()
    if 'appointment_id' in data: treatment.appointment_id = data['appointment_id']
    if 'diagnosis' in data: treatment.diagnosis = data['diagnosis']
    if 'prescription' in data: treatment.prescription = data['prescription']
    if 'notes' in data: treatment.notes = data['notes']
    
    db.session.commit()
    return jsonify({"msg": "Treatment record updated."})


# ----------------------
# DEPARTMENTS
# ----------------------
@admin_bp.route('/departments', methods=['GET', 'POST'])
@jwt_required()
@cache.cached(timeout=3600, query_string=True, unless=lambda: request.method != 'GET')
def manage_departments():
    user, err, code = admin_required()
    if err: return err, code

    if request.method == 'POST':
        data = request.get_json()
        db.session.add(Department(name=data['name'], description=data.get('description', '')))
        db.session.commit()
        return jsonify({"msg": "Department added"}), 201

    return jsonify([{"id": d.id, "name": d.name, "description": d.description} for d in Department.query.all()])

@admin_bp.route('/department/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def modify_department(id):
    user, err, code = admin_required()
    if err: return err, code
    
    dept = Department.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(dept)
        db.session.commit()
        return jsonify({"msg": "Department removed."})

    data = request.get_json()
    if 'name' in data: dept.name = data['name']
    if 'description' in data: dept.description = data['description']
    db.session.commit()
    
    return jsonify({"msg": "Department updated."})


# ----------------------
# UTILITIES / GLOBAL
# ----------------------
@admin_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    user, err, code = admin_required()
    if err: return err, code

    query = request.args.get('q', '')
    users = User.query.filter(db.or_(User.username.ilike(f"%{query}%"), User.name.ilike(f"%{query}%"), User.contact.ilike(f"%{query}%"))).all()
    dept_ids = [d.id for d in Department.query.filter(Department.name.ilike(f"%{query}%")).all()]

    if dept_ids:
        docs = Doctor.query.filter(Doctor.department_id.in_(dept_ids)).all()
        existing_ids = {u.id for u in users}
        for doc in docs:
            if doc.user and doc.user.id not in existing_ids:
                users.append(doc.user)

    result = []
    for u in users:
        doc = Doctor.query.filter_by(user_id=u.id).first() if u.role == 'doctor' else None
        result.append({
            "id": u.id, "username": u.username, "role": u.role, 
            "name": u.name, "contact": u.contact, "is_blacklisted": u.is_blacklisted,
            "specialization": doc.specialization if doc else None,
            "department": doc.department.name if doc and doc.department else None
        })
    return jsonify(result)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30)
def get_users():
    user, err, code = admin_required()
    if err: return err, code

    return jsonify([{
        "id": u.id, "username": u.username, "role": u.role, "name": u.name, 
        "contact": u.contact, "is_blacklisted": u.is_blacklisted
    } for u in User.query.all()])

@admin_bp.route('/user/<int:id>/blacklist', methods=['POST'])
@jwt_required()
def toggle_blacklist(id):
    user, err, code = admin_required()
    if err: return err, code

    target = User.query.get_or_404(id)
    if target.id == user['id']:
        return jsonify({"msg": "Don't blacklist yourself! That's bad news."}), 400

    target.is_blacklisted = not target.is_blacklisted
    db.session.commit()
    
    return jsonify({
        "msg": "User blacklisted" if target.is_blacklisted else "User's block has been lifted.",
        "is_blacklisted": target.is_blacklisted
    })