from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from models import db, Patient, Doctor, Appointment, Treatment, Department
from datetime import datetime
from extensions import cache

patient_bp = Blueprint('patient', __name__)
DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def get_current_patient():
    """Helper to fetch the current patient or return an error response."""
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'patient':
        return None, jsonify({"msg": "Hey! Only patients can do this."}), 403
    return Patient.query.filter_by(user_id=current_user['id']).first(), None, None

@patient_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    patient, err, code = get_current_patient()
    if err: return err, code

    if request.method == 'GET':
        return jsonify({
            "id": patient.id,
            "name": patient.user.name or 'New Patient',
            "email": patient.user.username or '',
            "contact": patient.user.contact or '',
        })

    # Handle PUT
    data = request.get_json()
    if 'name' in data: patient.user.name = data['name']
    if 'contact' in data: patient.user.contact = data['contact']
    if 'password' in data: patient.user.password = data['password']

    db.session.commit()
    return jsonify({"msg": "Awesome! Profile updated."})

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Combines upcoming appointments and past history."""
    patient, err, code = get_current_patient()
    if err: return err, code

    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()
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

@patient_bp.route('/departments', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600, query_string=True)
def get_departments():
    departments = Department.query.all()
    return jsonify([{"id": d.id, "name": d.name, "description": d.description} for d in departments])

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def search_doctors():
    dept_id = request.args.get('department_id')
    query_str = request.args.get('q', '').lower()

    query = Doctor.query
    if dept_id: query = query.filter_by(department_id=dept_id)

    result = []
    for d in query.all():
        if d.user.is_blacklisted: continue
        
        doc_name = (d.user.name or '').lower()
        doc_spec = (d.specialization or '').lower()
        dept_name = (d.department.name if d.department else '').lower()
        
        if query_str and not any(query_str in x for x in [doc_name, doc_spec, dept_name]):
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

@patient_bp.route('/appointment', methods=['POST'])
@jwt_required()
def book_appointment():
    patient, err, code = get_current_patient()
    if err: return err, code

    if patient.user.is_blacklisted:
        return jsonify({"msg": "Oh snap! Your account is blacklisted. Contact admin."}), 403

    data = request.get_json()
    doctor_id, date_str, time = data.get('doctor_id'), data.get('date'), data.get('time')

    if not all([doctor_id, date_str, time]):
        return jsonify({"msg": "Please pick a doctor, date, and time."}), 400

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if date < datetime.today().date():
        return jsonify({"msg": "Oops! We can't time travel. Pick a future date."}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor or doctor.user.is_blacklisted:
        return jsonify({"msg": "This doctor is currently unavailable."}), 403

    day_index = date.weekday()
    if len(doctor.availability) == 7 and doctor.availability[day_index] != '1':
        avail_days = [DAY_NAMES[i] for i, ch in enumerate(doctor.availability) if ch == '1']
        return jsonify({"msg": f"Dr. {doctor.user.name} isn't available on {DAY_NAMES[day_index]}. They are available on: {', '.join(avail_days) or 'None'}"}), 400

    if Appointment.query.filter_by(doctor_id=doctor_id, date=date, time=time).filter(Appointment.status != 'cancelled').first():
        return jsonify({"msg": "Yikes, that slot just got snatched! Try another time."}), 400

    db.session.add(Appointment(patient_id=patient.id, doctor_id=doctor_id, date=date, time=time, status='booked'))
    db.session.commit()

    return jsonify({"msg": "Woohoo! Your appointment is locked in."}), 201

@patient_bp.route('/appointment/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(id):
    patient, err, code = get_current_patient()
    if err: return err, code

    appointment = Appointment.query.get_or_404(id)
    if appointment.patient_id != patient.id:
        return jsonify({"msg": "Sneaky! You can't cancel someone else's appointment."}), 403

    appointment.status = 'cancelled'
    db.session.commit()
    return jsonify({"msg": "It's all good, appointment cancelled."})

@patient_bp.route('/export-history', methods=['POST'])
@jwt_required()
def export_history():
    patient, err, code = get_current_patient()
    if err: return err, code

    from jobs import export_treatment_history_csv
    export_treatment_history_csv.delay(patient.id)

    return jsonify({"msg": "Got it! We're preparing your history. Check your email soon."}), 202