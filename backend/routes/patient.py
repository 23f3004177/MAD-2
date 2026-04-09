from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Patient, Doctor, Appointment, Treatment, Department, User
from datetime import datetime
from extensions import cache

patient_bp = Blueprint('patient', __name__)

DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
# Python weekday(): Mon=0 ... Sun=6  (same as our availability bitmask index)


# ----------------------
# HELPER: CHECK PATIENT
# ----------------------
def patient_required():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'patient':
        return None, jsonify({"msg": "Patient access required"}), 403

    patient = Patient.query.filter_by(user_id=current_user['id']).first()
    return patient, None, None


# ----------------------
# GET PROFILE
# ----------------------
@patient_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    patient, err, code = patient_required()
    if err:
        return err, code

    user = patient.user
    return jsonify({
        "id": patient.id,
        "user_id": user.id,
        "name": user.name or '',
        "email": user.username or '',
        "contact": user.contact or '',
    })


# ----------------------
# DASHBOARD
# ----------------------
@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    patient, err, code = patient_required()
    if err:
        return err, code

    appointments = Appointment.query.filter_by(patient_id=patient.id).all()

    result = []
    for a in appointments:
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        result.append({
            "id": a.id,
            "doctor_id": a.doctor_id,
            "doctor": a.doctor.user.name,
            "doctor_specialization": a.doctor.specialization,
            "department": a.doctor.department.name if a.doctor.department else "General",
            "date": str(a.date),
            "time": a.time,
            "status": a.status,
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None,
            "notes": treatment.notes if treatment else None
        })

    return jsonify(result)

# ----------------------
# UPDATE PROFILE
# ----------------------
@patient_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    patient, err, code = patient_required()
    if err:
        return err, code

    data = request.get_json()

    user = patient.user
    if 'name' in data:
        user.name = data['name']
    if 'contact' in data:
        user.contact = data['contact']
    if 'password' in data:
        user.password = data['password']

    db.session.commit()

    return jsonify({"msg": "Profile updated successfully"})


# ----------------------
# VIEW DEPARTMENTS
# ----------------------
@patient_bp.route('/departments', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600, query_string=True)
def get_departments():
    departments = Department.query.all()

    return jsonify([
        {
            "id": d.id,
            "name": d.name,
            "description": d.description
        } for d in departments
    ])


# ----------------------
# SEARCH DOCTORS
# ----------------------
@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def get_doctors():
    dept_id = request.args.get('department_id')
    query_str = request.args.get('q', '').lower()

    query = Doctor.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)

    doctors = query.all()

    result = []
    for d in doctors:
        if d.user.is_blacklisted:
            continue
            
        doc_name = (d.user.name or '').lower()
        doc_spec = (d.specialization or '').lower()
        dept_name = (d.department.name if d.department else '').lower()
        
        # Match search term with name, specialization or department
        if query_str and (query_str not in doc_name and query_str not in doc_spec and query_str not in dept_name):
            continue

        result.append({
            "id": d.id,
            "name": d.user.name,
            "specialization": d.specialization,
            "availability": d.availability,
            "department_id": d.department_id,
            "department_name": d.department.name if d.department else "General",
            "contact": d.user.contact or ''
        })

    return jsonify(result)


# ----------------------
# BOOK APPOINTMENT
# ----------------------
@patient_bp.route('/appointment', methods=['POST'])
@jwt_required()
def book_appointment():
    patient, err, code = patient_required()
    if err:
        return err, code

    # Check if this patient's user is blacklisted
    if patient.user.is_blacklisted:
        return jsonify({"msg": "Your account has been blacklisted. You cannot book appointments."}), 403

    data = request.get_json()

    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    time = data.get('time')

    if not doctor_id or not date_str or not time:
        return jsonify({"msg": "doctor_id, date, and time are required"}), 400

    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Prevent booking on past dates
    if date < datetime.today().date():
        return jsonify({"msg": "Cannot book an appointment in the past. Please choose a future date."}), 400

    # Fetch doctor and check blacklist
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404
    if doctor.user.is_blacklisted:
        return jsonify({"msg": "This doctor is currently unavailable."}), 403

    # Check doctor availability for the chosen day (Mon=0 ... Sun=6)
    day_index = date.weekday()  # 0=Mon, 6=Sun
    if len(doctor.availability) == 7 and doctor.availability[day_index] != '1':
        available_days = [DAY_NAMES[i] for i, ch in enumerate(doctor.availability) if ch == '1']
        return jsonify({
            "msg": f"Doctor is not available on {DAY_NAMES[day_index]}. "
                   f"Available days: {', '.join(available_days) or 'None'}"
        }), 400

    # Prevent double booking for same slot
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=date,
        time=time
    ).filter(Appointment.status != 'cancelled').first()

    if existing:
        return jsonify({"msg": "This time slot is already booked. Please choose another time."}), 400

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        date=date,
        time=time,
        status='booked'
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"msg": "Appointment booked successfully!"}), 201


# ----------------------
# CANCEL APPOINTMENT
# ----------------------
@patient_bp.route('/appointment/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(id):
    patient, err, code = patient_required()
    if err:
        return err, code

    appointment = Appointment.query.get_or_404(id)

    if appointment.patient_id != patient.id:
        return jsonify({"msg": "Unauthorized"}), 403

    appointment.status = 'cancelled'
    db.session.commit()

    return jsonify({"msg": "Appointment cancelled"})


# ----------------------
# RESCHEDULE APPOINTMENT
# ----------------------
@patient_bp.route('/appointment/<int:id>/reschedule', methods=['PUT'])
@jwt_required()
def reschedule_appointment(id):
    patient, err, code = patient_required()
    if err:
        return err, code

    # Check patient blacklist
    if patient.user.is_blacklisted:
        return jsonify({"msg": "Your account has been blacklisted. You cannot reschedule appointments."}), 403

    appointment = Appointment.query.get_or_404(id)

    if appointment.patient_id != patient.id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()

    new_date = datetime.strptime(data['date'], "%Y-%m-%d").date()

    # Prevent rescheduling to a past date
    if new_date < datetime.today().date():
        return jsonify({"msg": "Cannot reschedule to a past date. Please choose a future date."}), 400
    new_time = data['time']

    # Check doctor availability for the new day
    doctor = appointment.doctor
    day_index = new_date.weekday()
    if len(doctor.availability) == 7 and doctor.availability[day_index] != '1':
        available_days = [DAY_NAMES[i] for i, ch in enumerate(doctor.availability) if ch == '1']
        return jsonify({
            "msg": f"Doctor is not available on {DAY_NAMES[day_index]}. "
                   f"Available days: {', '.join(available_days) or 'None'}"
        }), 400

    # Check slot conflict (exclude current appointment and cancelled ones)
    existing = Appointment.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=new_date,
        time=new_time
    ).filter(
        Appointment.id != id,
        Appointment.status != 'cancelled'
    ).first()

    if existing:
        return jsonify({"msg": "New slot is already taken. Please choose another time."}), 400

    appointment.date = new_date
    appointment.time = new_time

    db.session.commit()

    return jsonify({"msg": "Appointment rescheduled successfully!"})


# ----------------------
# VIEW TREATMENT HISTORY
# ----------------------
@patient_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    patient, err, code = patient_required()
    if err:
        return err, code

    appointments = Appointment.query.filter_by(patient_id=patient.id).all()

    result = []

    for a in appointments:
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()

        result.append({
            "appointment_id": a.id,
            "doctor": a.doctor.user.name,
            "date": str(a.date),
            "status": a.status,
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None,
            "notes": treatment.notes if treatment else None
        })

    return jsonify(result)

# ----------------------
# EXPORT TREATMENT HISTORY (CSV)
# ----------------------
@patient_bp.route('/export-history', methods=['POST'])
@jwt_required()
def export_history():
    patient, err, code = patient_required()
    if err:
        return err, code

    # Trigger async job
    from jobs import export_treatment_history_csv
    export_treatment_history_csv.delay(patient.id)

    return jsonify({"msg": "Export job started! You will receive an alert (email) once it's done."}), 202