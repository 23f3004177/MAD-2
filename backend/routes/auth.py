from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from models import db, User, Patient

auth_bp = Blueprint('auth', __name__)


# ----------------------
# REGISTER (Patient only)
# ----------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    contact = data.get('contact')

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 400

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

    return jsonify({"msg": "User registered successfully"}), 201


# ----------------------
# LOGIN (All roles)
# ----------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data.get('username')).first()

    if not user or user.password != data.get('password'):
        return jsonify({"msg": "Invalid credentials"}), 401

    if user.is_blacklisted:
        return jsonify({"msg": "Account is suspended/blacklisted"}), 403

    import json
    token = create_access_token(
        identity=json.dumps({
            "id": user.id,
            "role": user.role
        })
    )

    return jsonify({
        "access_token": token,
        "role": user.role
    }), 200


# ----------------------
# GET PROFILE (Protected)
# ----------------------
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    import json
    current_user = json.loads(get_jwt_identity())

    return jsonify({
        "msg": "User info",
        "user": current_user
    }), 200