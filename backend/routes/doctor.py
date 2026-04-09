from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from models import db, Doctor, Appointment, Treatment, Patient

doctor_bp = Blueprint('doctor', __name__)

def get_current_doctor():
    """Helper to fetch the current doctor or return an error response."""
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'doctor':
        return None, jsonify({"msg": "Hold up! This area is for doctors only."}), 403

    return Doctor.query.filter_by(user_id=current_user['id']).first(), None, None

@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    doctor, err, code = get_current_doctor()
    if err: return err, code

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    return jsonify([{
        "id": a.id,
        "patient": a.patient.user.name,
        "patient_id": a.patient_id,
        "date": str(a.date),
        "time": a.time,
        "status": a.status
    } for a in appointments])

@doctor_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    doctor, err, code = get_current_doctor()
    if err: return err, code

    patient_ids = {a.patient_id for a in Appointment.query.filter_by(doctor_id=doctor.id).all()}
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    
    return jsonify([{
        "id": p.id,
        "name": p.user.name,
        "contact": p.user.contact
    } for p in patients])

@doctor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    doctor, err, code = get_current_doctor()
    if err: return err, code
    
    return jsonify({
        "id": doctor.id,
        "name": doctor.user.name or 'Doc',
        "specialization": doctor.specialization,
        "availability": doctor.availability,
        "department": doctor.department.name if doctor.department else "General"
    })

@doctor_bp.route('/appointment/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    doctor, err, code = get_current_doctor()
    if err: return err, code

    appointment = Appointment.query.get_or_404(id)
    if appointment.doctor_id != doctor.id:
        return jsonify({"msg": "You can't touch another doctor's appointment!"}), 403

    data = request.get_json()
    if 'status' in data:
        appointment.status = data['status']
        db.session.commit()

    return jsonify({"msg": f"Appointment marked as {appointment.status}."})

@doctor_bp.route('/appointment/<int:id>/treatment', methods=['POST'])
@jwt_required()
def add_treatment(id):
    doctor, err, code = get_current_doctor()
    if err: return err, code

    appointment = Appointment.query.get_or_404(id)
    if appointment.doctor_id != doctor.id:
        return jsonify({"msg": "That's not your patient to treat!"}), 403

    data = request.get_json()
    
    db.session.add(Treatment(
        appointment_id=id,
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        notes=data.get('notes')
    ))

    appointment.status = 'completed'
    db.session.commit()

    return jsonify({"msg": "Great job! Treatment plan saved and appointment completed."}), 201

@doctor_bp.route('/patient/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def patient_history(patient_id):
    doctor, err, code = get_current_doctor()
    if err: return err, code

    has_access = Appointment.query.filter_by(patient_id=patient_id, doctor_id=doctor.id).first()
    if not has_access:
        return jsonify({"msg": "Access denied. You haven't treated this patient yet."}), 403

    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()
    result = []
    
    for a in appointments:
        trt = Treatment.query.filter_by(appointment_id=a.id).first()
        result.append({
            "appointment_id": a.id,
            "date": str(a.date),
            "status": a.status,
            "doctor_name": a.doctor.user.name if a.doctor and a.doctor.user else "Unknown",
            "doctor_specialization": a.doctor.specialization if a.doctor else "",
            "diagnosis": trt.diagnosis if trt else None,
            "prescription": trt.prescription if trt else None,
            "notes": trt.notes if trt else None
        })

    return jsonify(result)

@doctor_bp.route('/availability', methods=['PUT'])
@jwt_required()
def set_availability():
    doctor, err, code = get_current_doctor()
    if err: return err, code

    data = request.get_json()
    new_avail = data.get('availability', '0000000')

    if isinstance(new_avail, list):
        doctor.set_availability(new_avail)
    else:
        doctor.availability = str(new_avail)

    db.session.commit()
    return jsonify({"msg": "Schedule updated! Time to relax or get to work."})