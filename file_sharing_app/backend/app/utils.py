from flask import jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)
import re
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg'}


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'files')
PROFILE_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'profile')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS_PROFILE = {'png', 'jpg', 'jpeg'}
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_PROFILE


def create_login_response(user_id):
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })


def validate_login_data(data):
    if not data.get('email') and not data.get('password'):
        return jsonify({'error': 'Missing email id and password'}), 400
    if not data.get('email'):
        return jsonify({'error': 'Missing email id'}), 400
    if not data.get('password'):
        return jsonify({'error': 'Missing password'}), 400

    email_check = is_valid_email(data['email'])
    if email_check:
        return email_check
    return None


def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email address."}), 400


def is_valid_password(username, password):
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long."}), 400

    if username.lower() in password.lower():
        return jsonify({"error": "Password should not contain the username."}), 400

    year_pattern = r'\b(19[0-9]{2}|20[0-1][0-9]|2020|2100)\b'
    if re.search(year_pattern, password):
        return jsonify({"error": "Password should not contain any number between 1900 and 2100."}), 400

    for i in range(10):
        consecutive = ''.join(str(i + j) for j in range(3))
        if consecutive in password:
            return jsonify({"error": "Password should not contain three consecutive natural numbers."}), 400

    if password.isdigit():
        return jsonify({"error": "Password should not be a number."}), 400

    if password.isalpha():
        return jsonify({"error": "Password should not be a word."}), 400



def is_valid_dob(dob_str):
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

    return None


def validate_registration_data(data):
    required_fields = ['first_name', 'last_name', 'email', 'password', 'confirmpassword', 'dob']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing {field.replace("_", " ")}'}), 400

    if data['password'] != data['confirmpassword']:
        return jsonify({'error': 'Passwords do not match'}), 400

    email_check = is_valid_email(data['email'])
    if email_check:
        return email_check

    username = f"{data['first_name']} {data['last_name']}".lower()
    password_check = is_valid_password(username, data['password'])
    if password_check:
        return password_check

    dob_check = is_valid_dob(data['dob'])
    if dob_check:
        return dob_check

    return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv('MAIL_USERNAME')
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.send_message(msg)
