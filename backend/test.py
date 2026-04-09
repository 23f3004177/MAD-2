import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def log(title, response):
    print("\n" + "="*60)
    print(f"🔹 {title}")
    print("Status:", response.status_code)
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response (raw):", response.text)


# ----------------------
# AUTH TESTS
# ----------------------
def test_auth():
    # Register patient1
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "patient1",
        "password": "123"
    })
    log("Register Patient1", r)

    # Duplicate registration ❌
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "patient1",
        "password": "123"
    })
    log("Duplicate Register (Edge Case)", r)

    # Register patient2
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "patient2",
        "password": "123"
    })
    log("Register Patient2", r)

    # Invalid login ❌
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "patient1",
        "password": "wrong"
    })
    log("Invalid Login (Edge Case)", r)

    # Login patient1
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "patient1",
        "password": "123"
    })
    patient1_token = r.json().get("access_token")
    log("Login Patient1", r)

    # Login patient2
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "patient2",
        "password": "123"
    })
    patient2_token = r.json().get("access_token")
    log("Login Patient2", r)

    # Login admin
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    admin_token = r.json().get("access_token")
    log("Login Admin", r)

    return patient1_token, patient2_token, admin_token


# ----------------------
# ADMIN
# ----------------------
def test_admin(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Add doctor
    r = requests.post(f"{BASE_URL}/admin/doctor", json={
        "username": "doc1",
        "password": "123",
        "name": "Dr. Who",
        "availability": "9AM-5PM"
    }, headers=headers)
    log("Add Doctor", r)

    # Get doctors
    r = requests.get(f"{BASE_URL}/admin/doctors", headers=headers)
    log("Get Doctors", r)

    doctor_id = r.json()[0]["id"]
    return doctor_id


# ----------------------
# DOUBLE BOOKING TEST
# ----------------------
def test_double_booking(patient1_token, patient2_token, doctor_id):
    h1 = {"Authorization": f"Bearer {patient1_token}"}
    h2 = {"Authorization": f"Bearer {patient2_token}"}

    payload = {
        "doctor_id": doctor_id,
        "date": "2026-04-10",
        "time": "10:00"
    }

    # Patient1 books ✅
    r1 = requests.post(f"{BASE_URL}/patient/appointment", json=payload, headers=h1)
    log("Patient1 Booking", r1)

    # Patient2 tries same slot ❌
    r2 = requests.post(f"{BASE_URL}/patient/appointment", json=payload, headers=h2)
    log("Double Booking Attempt (Edge Case)", r2)

    return r1.json()


# ----------------------
# RESCHEDULE CONFLICT
# ----------------------
def test_reschedule_conflict(patient1_token, patient2_token, doctor_id):
    h1 = {"Authorization": f"Bearer {patient1_token}"}
    h2 = {"Authorization": f"Bearer {patient2_token}"}

    # Patient2 books another slot
    r = requests.post(f"{BASE_URL}/patient/appointment", json={
        "doctor_id": doctor_id,
        "date": "2026-04-10",
        "time": "11:00"
    }, headers=h2)

    log("Patient2 Booking Another Slot", r)

    appt2_id = r.json().get("id")

    # Try reschedule to occupied slot ❌
    r = requests.put(
        f"{BASE_URL}/patient/appointment/{appt2_id}/reschedule",
        json={
            "date": "2026-04-10",
            "time": "10:00"
        },
        headers=h2
    )
    log("Reschedule Conflict (Edge Case)", r)


# ----------------------
# UNAUTHORIZED ACCESS
# ----------------------
def test_unauthorized(patient1_token):
    headers = {"Authorization": f"Bearer {patient1_token}"}

    # patient trying admin route ❌
    r = requests.get(f"{BASE_URL}/admin/dashboard", headers=headers)
    log("Unauthorized Admin Access (Edge Case)", r)


# ----------------------
# DOCTOR ACCESS CONTROL
# ----------------------
def test_doctor_security():
    # login doctor
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "doc1",
        "password": "123"
    })
    token = r.json().get("access_token")

    headers = {"Authorization": f"Bearer {token}"}

    # try accessing patient endpoint ❌
    r = requests.get(f"{BASE_URL}/patient/dashboard", headers=headers)
    log("Doctor accessing Patient API (Edge Case)", r)


# ----------------------
# MAIN
# ----------------------
if __name__ == "__main__":
    print("🚀 Running FULL EDGE CASE TESTS...")

    p1, p2, admin = test_auth()

    doctor_id = test_admin(admin)

    test_double_booking(p1, p2, doctor_id)

    test_reschedule_conflict(p1, p2, doctor_id)

    test_unauthorized(p1)

    test_doctor_security()

    print("\n✅ Edge case testing completed!")