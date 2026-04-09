from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ----------------------
# USER MODEL (All roles)
# ----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  
    # roles: 'admin', 'doctor', 'patient'

    # extra fields (optional)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    is_blacklisted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"



# ----------------------
# DEPARTMENT
# ----------------------
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    
    doctors_registered = db.relationship('Doctor', back_populates='department', lazy=True)

    def __repr__(self):
        return f"<Department {self.name}>"



# ----------------------
# DOCTOR PROFILE
# ----------------------
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)

    # NEW: specialization field
    specialization = db.Column(db.String(100), nullable=False)

    # UPDATED: 7-bit availability string (e.g., "1010110")
    # Order example: Mon, Tue, Wed, Thu, Fri, Sat, Sun
    availability = db.Column(db.String(7), nullable=False, default="0000000")

    user = db.relationship('User')
    department = db.relationship('Department', back_populates='doctors_registered')

    def set_availability(self, days_list):
        """
        Accepts a list like [1,0,1,0,1,1,0]
        Converts it to string '1010110'
        """
        if len(days_list) != 7 or any(d not in [0, 1] for d in days_list):
            raise ValueError("Availability must be a list of 7 binary values (0 or 1)")
        
        self.availability = ''.join(map(str, days_list))

    def get_availability(self):
        """
        Returns availability as list [1,0,1,0,1,1,0]
        """
        return [int(char) for char in self.availability]

    def __repr__(self):
        return f"<Doctor {self.user_id} - {self.specialization}>"



# ----------------------
# PATIENT PROFILE
# ----------------------
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User')

    def __repr__(self):
        return f"<Patient {self.user_id}>"



# ----------------------
# APPOINTMENT
# ----------------------
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)

    status = db.Column(db.String(20), default='booked')  
    # booked / completed / cancelled

    patient = db.relationship('Patient')
    doctor = db.relationship('Doctor')

    def __repr__(self):
        return f"<Appointment {self.id}>"



# ----------------------
# TREATMENT
# ----------------------
class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    diagnosis = db.Column(db.String(200))
    prescription = db.Column(db.String(200))
    notes = db.Column(db.String(300))

    appointment = db.relationship('Appointment')

    def __repr__(self):
        return f"<Treatment {self.id}>"