from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from models import db, User, Patient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new patient account."""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    contact = data.get('contact')

    # Basic validations
    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "This username is already registered"}), 400

    # Ensure patient role for self-registration
    user = User(
        username=username,
        password=password,
        name=name,
        contact=contact,
        role='patient'
    )

    db.session.add(user)
    db.session.flush()

    patient = Patient(user_id=user.id)
    db.session.add(patient)
    db.session.commit()

    return jsonify({"msg": "Welcome! Your patient profile was created."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT."""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or user.password != password:
        return jsonify({"msg": "Invalid username or password"}), 401

    if user.is_blacklisted:
        return jsonify({"msg": "Oh snap! Your account has been suspended."}), 403

    # Generate token with user identity
    token = create_access_token(
        identity=json.dumps({
            "id": user.id,
            "role": user.role
        })
    )

    return jsonify({
        "access_token": token,
        "role": user.role,
        "msg": "Login successful!"
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Get the current logged-in user context."""
    current_user = json.loads(get_jwt_identity())
    return jsonify({
        "msg": "Found user info",
        "user": current_user
    }), 200