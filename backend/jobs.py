from celery import shared_task
from models import db, User, Patient, Doctor, Appointment, Treatment
from extensions import mail
from flask_mail import Message
from datetime import datetime, timedelta, date
from flask import current_app, render_template_string
import csv
import io

@shared_task(ignore_result=False)
def send_daily_reminders():
    print("Running send_daily_reminders job...")
    today = date.today()
    # Find appointments scheduled for today
    appointments = Appointment.query.filter_by(date=today, status='booked').all()
    count = 0
    for appt in appointments:
        patient_user = appt.patient.user
        doctor_user = appt.doctor.user
        
        subject = "Scheduled Visit Reminder - TriMed Hospital"
        body = f"Hello {patient_user.name or patient_user.username},\n\nThis is a gentle reminder for your scheduled visit at TriMed Hospital.\nDr. {doctor_user.name or doctor_user.username} is expecting you at {appt.time} today.\n\nPlease be on time.\n\nRegards,\nTriMed Team"
        
        # We assume email is their username or we just send it to a fake address if username is not email.
        # But for homework purposes, mailing to user.username (which should be an email anyway) works.
        try:
            msg = Message(subject=subject, recipients=[patient_user.username], body=body)
            mail.send(msg)
            count += 1
        except Exception as e:
            print(f"Error sending email to {patient_user.username}: {str(e)}")

    return f"Sent {count} reminders for {today}"

@shared_task(ignore_result=False)
def send_monthly_activity_report():
    print("Running send_monthly_activity_report job...")
    # Get first day of current month
    today = date.today()
    first_day_of_current_month = today.replace(day=1)
    # Get last month's first day and last day
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

    template = """
    <html>
        <body>
            <h2>Monthly Doctor Activity Report - {{ month_year }}</h2>
            <p>Dear Dr. {{ doctor_name }},</p>
            <p>Here is the summary of your appointments for the past month:</p>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Status</th>
                    <th>Diagnosis</th>
                    <th>Prescription</th>
                </tr>
                {% for appt, treat in data %}
                <tr>
                    <td>{{ appt.date }}</td>
                    <td>{{ appt.time }}</td>
                    <td>{{ appt.patient.user.name or appt.patient.user.username }}</td>
                    <td>{{ appt.status }}</td>
                    <td>{{ treat.diagnosis if treat else 'N/A' }}</td>
                    <td>{{ treat.prescription if treat else 'N/A' }}</td>
                </tr>
                {% endfor %}
            </table>
            <p>Best Regards,<br>TriMed Admin</p>
        </body>
    </html>
    """

    doctors = Doctor.query.all()
    count = 0
    for doc in doctors:
        doc_user = doc.user
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.date >= first_day_of_previous_month,
            Appointment.date <= last_day_of_previous_month
        ).all()

        if not appointments:
            continue

        data = []
        for appt in appointments:
            treat = Treatment.query.filter_by(appointment_id=appt.id).first()
            data.append((appt, treat))

        html_body = render_template_string(template, 
            month_year=first_day_of_previous_month.strftime("%B %Y"), 
            doctor_name=doc_user.name or doc_user.username,
            data=data
        )

        subject = f"Monthly Activity Report - {first_day_of_previous_month.strftime('%Y-%m')}"
        try:
            msg = Message(subject=subject, recipients=[doc_user.username], html=html_body)
            mail.send(msg)
            count += 1
        except Exception as e:
            print(f"Error sending monthly report to {doc_user.username}: {str(e)}")

    return f"Sent {count} monthly reports."

@shared_task(ignore_result=False)
def export_treatment_history_csv(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return "Patient not found."
    
    # user_id, username, consulting doctor, appointment date, diagnosis given in that appointment, treatment given in that appointment, next visit suggested by the doctor etc.
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    
    # Save the CSV to a location or send via email to patient
    # Requirements say: "This should trigger a batch job, and send an alert once done."
    # I'll create the CSV in-memory and send it as an email attachment to the patient.
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "User ID", "Username", "Consulting Doctor", "Appointment Date", 
        "Appointment Time", "Diagnosis", "Prescription", "Notes (Contains Next Visit)"
    ])
    
    for appt in appointments:
        doc_user = appt.doctor.user
        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()
        
        diag = treatment.diagnosis if treatment else "N/A"
        presc = treatment.prescription if treatment else "N/A"
        notes = treatment.notes if treatment else "N/A"
        
        writer.writerow([
            patient.user.id,
            patient.user.username,
            doc_user.name or doc_user.username,
            appt.date.strftime("%Y-%m-%d"),
            appt.time,
            diag,
            presc,
            notes
        ])
        
    csv_data = output.getvalue()
    
    subject = "Export Complete: Your Treatment History CSV"
    body = "Please find attached your treatment history requested from the dashboard."
    
    try:
        msg = Message(subject=subject, recipients=[patient.user.username], body=body)
        msg.attach("treatment_history.csv", "text/csv", csv_data)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending CSV export to {patient.user.username}: {str(e)}")

    return "CSV Export generated and sent to patient."
