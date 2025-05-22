from flask import (
    Blueprint, render_template, redirect, flash, url_for,
    request, send_from_directory, jsonify
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid

from .model import Content, User
from . import db
from .utils import allowed_file

views = Blueprint('views', __name__)

UPLOAD_FOLDER = os.path.join('web/static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@views.route('/home')
@jwt_required(locations=['cookies'])
def home():
    """Render home page showing user-specific content."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    contents = Content.query.filter_by(user_id=user_id).all() if user_id else []

    return render_template(
        'home.html',
        contents=contents,
        username=user.username if user else "User"
    )


@views.route('/upload', methods=['POST'])
@jwt_required(locations=['cookies'])
def upload():
    """Handle file upload, save to server, and record in DB."""
    try:
        if 'file' not in request.files:
            flash('No file selected', category='error')
            return redirect(url_for('views.home'))

        file = request.files['file']
        description = request.form.get('note', '').strip()

        if file.filename == '':
            flash('No file selected', category='error')
            return redirect(url_for('views.home'))

        if not allowed_file(file.filename):
            flash('Allowed file types: PNG, JPG, JPEG', category='error')
            return redirect(url_for('views.home'))

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        user_id = get_jwt_identity()
        if not user_id:
            flash('Login required', category='error')
            return redirect(url_for('authn.login'))

        new_content = Content(
            description=description,
            filename=filename,
            user_id=user_id
        )
        db.session.add(new_content)
        db.session.commit()

        flash('Upload successful!', category='success')
    except RequestEntityTooLarge:
        flash('File too large (max 1MB)', category='error')

    return redirect(url_for('views.home'))


@views.route('/display/<filename>', methods=['GET'])
@jwt_required(locations=['cookies'])
def display(filename):
    """Redirect to static file URL for displaying."""
    return redirect(url_for('static', filename=f'uploads/{filename}'))


@views.route('/download/<filename>')
@jwt_required(locations=['cookies'])
def download_content(filename):
    """Download a file if it belongs to the authenticated user."""
    user_id = get_jwt_identity()
    content = Content.query.filter_by(filename=filename, user_id=user_id).first()

    if not content:
        flash('File not found or unauthorized', category='error')
        return redirect(url_for('views.home'))

    return send_from_directory(
        os.path.abspath(UPLOAD_FOLDER),
        filename,
        as_attachment=True,
        download_name=filename
    )


@views.route('/edit/<int:content_id>', methods=['PUT'])
@jwt_required(locations=['cookies'])
def edit_description(content_id):
    """Edit the description of a user's content item."""
    user_id = int(get_jwt_identity())
    content = Content.query.get_or_404(content_id)

    if content.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    new_description = data.get('new_description', '').strip()

    if not new_description:
        return jsonify({'error': 'Description cannot be empty'}), 400

    content.description = new_description
    db.session.commit()
    return jsonify({'message': 'Description updated successfully'}), 200


@views.route('/delete/<int:content_id>', methods=['DELETE'])
@jwt_required(locations=['cookies'])
def delete_content(content_id):
    """Delete a content item if it belongs to the authenticated user."""
    user_id = int(get_jwt_identity())
    content = Content.query.get_or_404(content_id)

    if content.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        file_path = os.path.join(UPLOAD_FOLDER, content.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(content)
        db.session.commit()
        return jsonify({'message': 'Content deleted successfully'}), 200
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'error': 'Error deleting content'}), 500
