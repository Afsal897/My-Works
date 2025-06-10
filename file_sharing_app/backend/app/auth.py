from flask import (
    Blueprint, request, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
     jwt_required, get_jwt_identity, create_access_token
)
from flask_mail import Message
from app import mail, get_serializer 
from .models import User
from . import db
from .utils import create_login_response, validate_registration_data, validate_login_data, allowed_file, is_valid_password
from datetime import datetime
import os
import uuid

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROFILE_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'profile')
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS_PROFILE = {'png', 'jpg', 'jpeg'}
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_PROFILE

authn = Blueprint('authn', __name__)


@authn.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    validation_error = validate_login_data(data)
    if validation_error:
        return validation_error

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    return create_login_response(user.id), 200


@authn.route('/register', methods=['POST'])
def register():
    data = request.form

    # Validate registration data
    validation_error = validate_registration_data(data)
    if validation_error:
        return validation_error

    email = data.get('email')
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already taken'}), 409

    # Parse and validate DOB
    dob = data.get('dob')
    try:
        dob_obj = datetime.strptime(dob, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Check for unique username
    username = f"{data['first_name']} {data['last_name']}"
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already taken'}), 409

    # Handle profile image
    profile = request.files.get('profile_image')
    if profile:
        if not allowed_file(profile.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        filename = f"{uuid.uuid4().hex}_{secure_filename(profile.filename)}"
        filepath = os.path.join(PROFILE_UPLOAD_FOLDER, filename)
        profile.save(filepath)
    else:
        filename = None  # Or a default image filename if needed

    # Create user and save to DB
    hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        username=username,
        email=email,
        password=hashed_pw,
        dob=dob_obj,
        profile_picture=filename
    )
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(username=username).first()
    return create_login_response(user.id), 201


@authn.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    user_id= get_jwt_identity()
    new_access_token = create_access_token(identity=str(user_id))

    return jsonify({
        'access_token': new_access_token,
        'message': 'Token refreshed'
    }), 200


@authn.route('/validate_token', methods=['GET'])
@jwt_required()
def validate_token():
    return jsonify({'message': 'Token is valid',}), 200


@authn.route('/forgot-password', methods=['POST'])
def forgot_password():
    data=request.get_json()
    email=data['email']
    if not email:
        return jsonify({"error":"email empty"}),400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error":"user not found"}),400
    
    serializer = get_serializer()
    token = serializer.dumps(email, salt='password-reset-salt')
    reset_url = f"http://localhost:5173/reset-password?token={token}"
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f"Hi {user.username},\n\nClick the link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore."

    try:
        user.reset_token_used = False
        db.session.commit()
        print('commit forgot',user.reset_token_used)
        mail.send(msg)
        return jsonify({"message": "Password reset link has been sent to your email"}), 200
    except Exception as e:
        print('msg except',e)
        return jsonify({"message": "Failed to send email", "error": str(e)}), 500
    

@authn.route('/reset-password', methods=['PUT'])
def reset_password():
    try:
        data=request.get_json()
        token=data['token']
        serializer = get_serializer()
        email = serializer.loads(token, salt='password-reset-salt', max_age=300)
    except Exception as e:
        return jsonify({"message": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    username = user.username
    data = request.get_json()
    new_password = data.get('password')
    is_valid_password(username, new_password)

    if user.reset_token_used:
            return jsonify({"message": "This link has already been used."}), 400
    
    if user:
        user.password = generate_password_hash(new_password) 
        user.reset_token_used = True
        db.session.commit()
        print('commit reset',user.reset_token_used)
        return jsonify({"message": "Password updated successfully. Redirecting to Login"}), 200
    return jsonify({"message": "User not found"}), 404
