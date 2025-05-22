from flask import make_response, redirect, url_for, flash
from flask_jwt_extended import (
    decode_token, create_access_token, create_refresh_token
)
from jwt import ExpiredSignatureError, InvalidTokenError
import re

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def is_valid_access_token(token):
    """
    Validates an access token by attempting to decode it.
    
    Returns True if valid, False if expired or malformed.
    """
    try:
        decode_token(token)
        return True
    except (ExpiredSignatureError, InvalidTokenError):
        return False


def create_login_response(user_id, redirect_endpoint, message):
    """
    Generates access and refresh tokens, sets them in cookies,
    flashes a success message, and redirects to the given endpoint.
    """
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))

    response = make_response(redirect(url_for(redirect_endpoint)))
    response.set_cookie(
        'access_token_cookie',
        access_token,
        httponly=True,
        samesite='Strict'
    )
    response.set_cookie(
        'refresh_token_cookie',
        refresh_token,
        httponly=True,
        samesite='Strict'
    )

    flash(message, category='success')
    return response


def allowed_file(filename):
    """
    Checks if the uploaded file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_valid_password(username, password):
    """
    Validates the password based on the following rules:
    1. Password should not contain the username.
    2. Password should not contain any number between 1900 and 2100.
    3. Password should not contain four consecutive natural numbers.

    Args:
    - username (str): The user's username.
    - password (str): The password to be checked.

    Returns:
    - (bool): True if the password is valid, False if invalid.
    - (str): A message indicating the reason for invalidity.
    """
    # Check if the password is min8 characters long
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    # Check if the password contains the username
    if username.lower() in password.lower():
        return False, "Password should not contain the username."
    
    # Check if the password contains any year-like number between 1900 and 2100
    year_pattern = r'\b(19[0-9]{2}|20[0-1][0-9]|2020|2100)\b'
    if re.search(year_pattern, password):
        return False, "Password should not contain any number between 1900 and 2100."
    
    # Check for four consecutive natural numbers
    for i in range(10):
        consecutive = ''.join(str(i+j) for j in range(4))  # e.g., "1234", "5678"
        if consecutive in password:
            return False, "Password should not contain four consecutive natural numbers."
    
    # If all checks pass, the password is valid
    return True, " "


