from flask import (
    Blueprint, render_template, request, flash, redirect,
    url_for, make_response, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    unset_jwt_cookies, jwt_required, get_jwt_identity, create_access_token
)

from .model import User
from . import db
from .utils import is_valid_access_token, create_login_response, is_valid_password

authn = Blueprint('authn', __name__)


@authn.route('/', methods=['GET', 'POST'])
def login():
    """Login route. Validates user credentials and returns access token."""
    token = request.cookies.get('access_token_cookie')

    if token and is_valid_access_token(token):
        return redirect(url_for('views.home'))

    session['logged_in'] = False

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash('Invalid credentials', 'error')
        return redirect(url_for('authn.login'))

    session['logged_in'] = True
    return create_login_response(user.id, 'views.home', 'Login successful!')


@authn.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup route. Registers a new user if input is valid."""
    token = request.cookies.get('access_token_cookie')

    if token and is_valid_access_token(token):
        return redirect(url_for('views.home'))

    if request.method == 'GET':
        return render_template('signup.html')

    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    is_valid, message = is_valid_password(username, password1)
    
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('authn.signup'))

    if password1 != password2:
        flash('Passwords do not match', 'error')
        return redirect(url_for('authn.signup'))

    if User.query.filter_by(username=username).first():
        flash('Username is already taken', 'error')
        return redirect(url_for('authn.signup'))

    hashed_pw = generate_password_hash(password1, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_pw)

    db.session.add(new_user)
    db.session.commit()

    session['logged_in'] = True
    return create_login_response(new_user.id, 'views.home', 'Account created!')


@authn.route('/logout')
def logout():
    """Logout route. Clears session and cookies."""
    session.clear()
    response = make_response(redirect(url_for('authn.login')))
    unset_jwt_cookies(response)
    flash('Logged out', 'success')
    return response


@authn.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['cookies'])
def refresh_token():
    """Refreshes the access token using a valid refresh token."""
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(user_id))

    response = jsonify({'message': 'Token refreshed'})
    response.set_cookie(
        'access_token_cookie',
        new_access_token,
        httponly=True,
        samesite='Strict'
    )
    return response
