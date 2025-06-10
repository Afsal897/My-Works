from flask import (
    Blueprint, request, jsonify
    )
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from .utils import is_valid_password, PROFILE_UPLOAD_FOLDER, allowed_image
from .models import User
from . import db
from datetime import datetime
import re

profile_view = Blueprint('profile_view', __name__)

MAX_PROFILE_PIC_SIZE = 5 * 1024 * 1024

@profile_view.route("/add_profile_picture", methods=["POST"])
@jwt_required()
def add_profile_picture():
    try:
        if 'profile_picture' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['profile_picture']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_image(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Validate file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)  # Reset the stream position

        if file_length > MAX_PROFILE_PIC_SIZE:
            return jsonify({'error': 'Profile picture must be under 5 MB'}), 413

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(PROFILE_UPLOAD_FOLDER, filename)
        file.save(filepath)

        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Delete old profile picture if exists
        if user.profile_picture:
            old_path = os.path.join(PROFILE_UPLOAD_FOLDER, user.profile_picture)
            if os.path.exists(old_path):
                os.remove(old_path)

        user.profile_picture = filename
        db.session.commit()

        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'avatarUrl': filename
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@profile_view.route('/profiledata', methods=['GET'])
@jwt_required()
def get_user_data():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "dob": user.dob.isoformat(),
        "profile_picture": user.profile_picture,
        "balance_space": user.balance_space,
    }

    return jsonify(user_data), 200


@profile_view.route("/savechanges", methods=["PUT"])
@jwt_required()
def save_changes():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip()
    dob_str = data.get("dob", "").strip()

    if not first_name:
        return jsonify({"error": "First name is required"}), 400
    if not last_name:
        return jsonify({"error": "Last name is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not dob_str:
        return jsonify({"error": "Date of birth is required"}), 400

    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email address."}), 400

    user_id = get_jwt_identity()

    existing_email = User.query.filter(User.email == email, User.id != user_id).first()
    if existing_email:
        return jsonify({"error": "Email already in use by another user."}), 400

    new_username = f"{first_name} {last_name}"

    existing_user = User.query.filter(User.username == new_username, User.id != user_id).first()
    if existing_user:
        return jsonify({"error": "Username already in use by another user."}), 400
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.today()
        if dob > today:
            return jsonify({"error": "Date of birth cannot be in the future."}), 400
        age = (today - dob).days // 365
        if age < 13:
            return jsonify({"error": "User must be at least 13 years old."}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    new_username = f"{first_name} {last_name}"

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.dob = dob
    user.username = new_username

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500
    

@profile_view.route("/change_password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    username=user.username
    
    
    password=request.json.get('password')
    if not check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 400
    
    new_password=request.json.get('new_password')
    confirm_new_password=request.json.get('confirm_new_password')
    if new_password!=confirm_new_password:
        return jsonify({'error':"password do not match"}),400
    
    is_valid_password(username,new_password)
    if user:
        user.password = generate_password_hash(new_password) 
        user.reset_token_used = True
        db.session.commit()
        print('commit reset',user.reset_token_used)
        return jsonify({"message": "Password updated successfully. Redirecting to Login"}), 200
    return jsonify({"message": "User not found"}), 404