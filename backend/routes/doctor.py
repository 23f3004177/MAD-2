from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Doctor, Appointment, Treatment, Patient
from extensions import cache

doctor_bp = Blueprint('doctor', __name__)


# ----------------------
# HELPER: CHECK DOCTOR
# ----------------------
def doctor_required():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'doctor':
        return None, jsonify({"msg": "Doctor access required"}), 403

    doctor = Doctor.query.filter_by(user_id=current_user['id']).first()
    return doctor, None, None


# ----------------------
# DASHBOARD (UPCOMING)
# ----------------------
@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    doctor, err, code = doctor_required()
    if err:
        return err, code

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()

    result = []
    for a in appointments:
        result.append({
            "id": a.id,
            "patient": a.patient.user.name,
            "patient_id": a.patient_id,
            "date": str(a.date),
            "time": a.time,
            "status": a.status
        })

    return jsonify(result)

# ----------------------
# GET ASSIGNED PATIENTS
# ----------------------
@doctor_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    doctor, err, code = doctor_required()
    if err:
        return err, code

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    patient_ids = {a.patient_id for a in appointments}

    # Fetch those patients
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.user.name,
            "contact": p.user.contact
        })
    return jsonify(result)

@doctor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    doctor, err, code = doctor_required()
    if err: return err, code
    
    return jsonify({
        "id": doctor.id,
        "name": doctor.user.name,
        "specialization": doctor.specialization,
        "availability": doctor.availability,
        "department": doctor.department.name if doctor.department else None
    })


# ----------------------
# MARK APPOINTMENT STATUS
# ----------------------
@doctor_bp.route('/appointment/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    doctor, err, code = doctor_required()
    if err:
        return err, code

    appointment = Appointment.query.get_or_404(id)

    if appointment.doctor_id != doctor.id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()
    appointment.status = data.get('status', appointment.status)

    db.session.commit()

    return jsonify({"msg": "Status updated"})


# ----------------------
# ADD TREATMENT
# ----------------------
@doctor_bp.route('/appointment/<int:id>/treatment', methods=['POST'])
@jwt_required()
def add_treatment(id):
    doctor, err, code = doctor_required()
    if err:
        return err, code

    appointment = Appointment.query.get_or_404(id)

    if appointment.doctor_id != doctor.id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()

    treatment = Treatment(
        appointment_id=id,
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        notes=data.get('notes')
    )

    db.session.add(treatment)

    # mark completed automatically
    appointment.status = 'completed'

    db.session.commit()

    return jsonify({"msg": "Treatment added"}), 201


# ----------------------
# UPDATE TREATMENT
# ----------------------
@doctor_bp.route('/treatment/<int:tr_id>', methods=['PUT'])
@jwt_required()
def update_treatment(tr_id):
    doctor, err, code = doctor_required()
    if err:
        return err, code

    treatment = Treatment.query.get_or_404(tr_id)
    appointment = Appointment.query.get(treatment.appointment_id)

    if appointment.doctor_id != doctor.id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()

    if 'diagnosis' in data:
        treatment.diagnosis = data['diagnosis']
    if 'prescription' in data:
        treatment.prescription = data['prescription']
    if 'notes' in data:
        treatment.notes = data['notes']

    db.session.commit()

    return jsonify({"msg": "Treatment updated"})


# ----------------------
# GET PATIENT HISTORY
# ----------------------
@doctor_bp.route('/patient/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def patient_history(patient_id):
    doctor, err, code = doctor_required()
    if err:
        return err, code

    # Ensure doctor has authorization to view patient (e.g. they have at least one appointment together)
    has_access = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).first()
    
    if not has_access:
        return jsonify({"msg": "Unauthorized. You haven't treated this patient."}), 403

    appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).order_by(Appointment.date.desc()).all()

    result = []

    for a in appointments:
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()

        result.append({
            "appointment_id": a.id,
            "date": str(a.date),
            "status": a.status,
            "doctor_name": a.doctor.user.name if a.doctor and a.doctor.user else "Unknown",
            "doctor_specialization": a.doctor.specialization if a.doctor else "",
            "diagnosis": treatment.diagnosis if treatment else None,
            "prescription": treatment.prescription if treatment else None,
            "notes": treatment.notes if treatment else None
        })

    return jsonify(result)


# ----------------------
# SET AVAILABILITY
# ----------------------
@doctor_bp.route('/availability', methods=['PUT'])
@jwt_required()
def set_availability():
    doctor, err, code = doctor_required()
    if err:
        return err, code

    data = request.get_json()
    new_avail = data.get('availability', '0000000')

    if isinstance(new_avail, list):
        doctor.set_availability(new_avail)
    else:
        doctor.availability = str(new_avail)

    db.session.commit()

    return jsonify({"msg": "Availability updated"})