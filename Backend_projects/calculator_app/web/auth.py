'''Authentication routes for the Flask application.

This module defines the /login route using JWT for issuing access tokens
based on hardcoded user credentials.
'''

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

# Hardcoded user credentials for demo purposes
USER_DATA = {
    "username": "admin",
    "password": "password"
}

# Define the authentication blueprint
authn = Blueprint('authn', __name__)

@authn.route('/login', methods=['GET', 'POST'])
def login():
    '''Login endpoint to authenticate user and return JWT access token.

    Expects JSON payload with 'username' and 'password'.

    Returns:
        JSON response containing access token or error message.
    '''
    # Check if request contains JSON
    if not request.is_json:
        return jsonify({"msg": "Missing JSON"}), 400

    # Extract credentials from request JSON
    username = request.json.get("username", "")
    password = request.json.get("password", "")

    # Verify credentials
    if username != USER_DATA["username"] or password != USER_DATA["password"]:
        return jsonify({"msg": "Bad username or password"}), 401

    # Generate JWT access token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200
