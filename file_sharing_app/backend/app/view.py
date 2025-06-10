from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid

from .models import Content, User, SharedFile, Friendship
from . import db
from .utils import allowed_file, send_email, is_valid_email, UPLOAD_FOLDER
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

@views.route('/home', methods=['GET'])
@jwt_required()
def home():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    user_page = int(request.args.get('user_page', 1))
    file_page = int(request.args.get('file_page', 1))
    search = request.args.get('search', '').strip()
    user_per_page = 8
    file_limit = int(request.args.get('limit', 8))

    # Exclude current user and paginate others
    user_query = User.query.filter(User.username != current_user.username)
    
    user_pagination = user_query.paginate(page=user_page, per_page=user_per_page, error_out=False)

    # Step 1: Get all friend IDs
    friend_ids = db.session.query(Friendship.user2_id).filter_by(user1_id=current_user.id) \
        .union(
            db.session.query(Friendship.user1_id).filter_by(user2_id=current_user.id)
        ).all()

    # Convert to a set of friend user IDs
    friend_id_set = {fid[0] for fid in friend_ids}

    # Step 2: Filter users who are NOT friends
    contact_info = []
    for user in user_pagination.items:
        if user.id == current_user.id or user.id in friend_id_set:
            continue  # Skip self and friends

        avatar_filename = user.profile_picture
        avatar_url = f"/static/profile/{avatar_filename}" if avatar_filename else ""
        contact_info.append({
            "username": user.username,
            "email": user.email,
            "avatarUrl": avatar_url
        })



    # Fetch current user's files
    contents = Content.query.filter_by(user_id=current_user.id) \
        .order_by(Content.id.desc()) \
        .paginate(page=file_page, per_page=file_limit, error_out=False)

    # filter filename using search query
    if search:
        contents = Content.query.filter(
            Content.user_id == current_user.id,
            Content.orginal_filename.ilike(f"%{search}%")
        ).order_by(Content.id.desc()).paginate(page=file_page, per_page=file_limit, error_out=False)
    

    files_info = []
    for content in contents.items:
        size_bytes = content.file_size
        size = round(size_bytes / 1024, 2) if size_bytes < 1024 * 1024 else round(size_bytes / (1024 * 1024), 2)
        size_str = f"{size} {'KB' if size_bytes < 1024 * 1024 else 'MB'}"
        files_info.append({'file_id':content.id, 'filename': content.orginal_filename, 'date':content.date_created, 'size': size_str})

    return jsonify({
        'message': 'Welcome to the home page!',
        'contacts': contact_info,
        'user_page': {
            'page': user_pagination.page,
            'per_page': user_pagination.per_page,
            'total_pages': user_pagination.pages,
            'total_users': user_pagination.total
        },
        'files': files_info,
        'file_page': {
            'page': contents.page,
            'per_page': contents.per_page,
            'total_pages': contents.pages,
            'total_files': contents.total
        },
        'space_left': current_user.balance_space
    }), 200


@views.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        user_id = get_jwt_identity()
        # user = User.query.get(user_id)
        user = db.session.query(User).with_for_update().get(user_id)#for atomicity
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        # Save file with unique filename
        original_filename = secure_filename(file.filename)
        new_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > user.balance_space:
            return jsonify({'error': 'Not enough storage left'}), 413
        # Save file to disk
        file.save(file_path)

        # Record to DB
        new_content = Content(
            orginal_filename=original_filename,
            modified_filename=new_filename,
            file_size=file_size,
            user_id=user.id
        )
        db.session.add(new_content)
        user.balance_space -= file_size
        db.session.commit()

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': original_filename,
            'size': f"{round(file_size / 1024, 2)} KB" if file_size < 1024*1024 else f"{round(file_size / (1024 * 1024), 2)} MB"
        }), 201

    except RequestEntityTooLarge:
        return jsonify({'error': 'File size exceeds 100 MB limit'}), 413
    except Exception as e:
        return jsonify({'error': 'Server error while uploading'}), 500


@views.route("/user_data", methods=["GET"])
@jwt_required()
def user_data():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'message': 'User data',
        'username': user.username,
        'email': user.email,
        'dob': user.dob,
        'avatarurl': user.profile_picture,
    }), 200


@views.route('/delete/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Fetch the file record
    file_record = Content.query.get(file_id)
    if not file_record:
        return jsonify({"success": False, "message": "File not found"}), 404

    # 🔐 Ensure the file belongs to the current user
    if file_record.user_id != int(user_id):
        return jsonify({"success": False, "message": "Unauthorized access to this file"}), 403

    file_path = os.path.join(UPLOAD_FOLDER, file_record.modified_filename)

    if not os.path.exists(file_path):
        return jsonify({"success": False, "message": "File not found on disk"}), 404

    try:
        # Get file size using os.path.getsize
        file_size = os.path.getsize(file_path)

        # Increase the user's available storage
        user.balance_space += file_size

        # Remove the file from disk and delete the DB record
        os.remove(file_path)
        db.session.delete(file_record)
        db.session.commit()

        return jsonify({"success": True, "message": f"{file_record.modified_filename} deleted successfully"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/download/<int:file_id>", methods=["GET"])
@jwt_required()
def download_file(file_id):
    user_id = get_jwt_identity()

    # Fetch the file record
    file_record = Content.query.get(file_id)
    if not file_record:
        return jsonify({"error": "File not found"}), 404

    # 🔐 Ensure the file belongs to the current user
    if file_record.user_id != int(user_id):
        return jsonify({"error": "Unauthorized access to this file"}), 403

    # Construct the file path
    file_path = os.path.join(UPLOAD_FOLDER, file_record.modified_filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found on disk"}), 404

    return send_file(file_path, as_attachment=True, download_name=file_record.orginal_filename)


@views.route("/share", methods=["POST"])
@jwt_required()
def share_file():
    data = request.get_json()

    # Validate input presence
    file_id = data.get("file_id")
    recipient_email = data.get("recipient_email")
    expiration_hours = data.get("expiration_hours", 24)
    message = data.get("message", "")

    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    if not recipient_email:
        return jsonify({"error": "recipient email  required"}), 400
    
    if not expiration_hours:
        return jsonify({"error": "expiration_hours is required"}), 400

    # Validate email
    is_valid_email(recipient_email)

    # Validate expiration time
    try:
        expiration_hours = int(expiration_hours)
        if expiration_hours <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "expiration_hours must be a positive integer"}), 400

    sharer_id = get_jwt_identity()

    # Validate file ownership
    file = Content.query.filter_by(id=file_id, user_id=sharer_id).first()
    if not file:
        return jsonify({"error": "File not found or access denied"}), 404

    # Create sharing token
    token = str(uuid.uuid4())
    expiration_time = datetime.utcnow() + timedelta(hours=expiration_hours)

    shared = SharedFile(
        file_id=file_id,
        filename=file.orginal_filename,
        sharer_id=sharer_id,
        recipient_email=recipient_email,
        token=token,
        expiration_time=expiration_time,
        message=message,
    )
    db.session.add(shared)
    db.session.commit()

    # Share URL
    share_url = f"http://localhost:5173/shared?token={token}"

    # Email body
    email_body = f"""
    You have received a file from our platform.

    Message: {message}

    Access your file here (valid for {expiration_hours} hours):
    {share_url}
    """

    send_email(recipient_email, "File Share Link", email_body)

    return jsonify({"message": "Share link sent successfully", "url": share_url}), 200


@views.route("/shared/<token>", methods=["GET"])
def access_shared_file(token):
    shared = SharedFile.query.filter_by(token=token).first()

    if not shared:
        return "Invalid link", 404

    if datetime.utcnow() > shared.expiration_time:
        return "This link has expired", 403

    file = Content.query.get(shared.file_id)
    if not file:
        return "File not found", 404
    
    # Send file to user
    path = os.path.join(UPLOAD_FOLDER, file.modified_filename)
    print("before download")
    shared.download = True
    db.session.commit()
    return send_file(path, as_attachment=True, download_name=file.orginal_filename)

@views.route("/sharepage/<token>", methods=["GET"])
def list_shared_files(token):
    if not token:
        return jsonify({"error": "Token is required"}), 400

    shared = SharedFile.query.filter_by(token=token).first()
    if not shared:
        return jsonify({"error": "Invalid or expired token"}), 404

    file = Content.query.get(shared.file_id)
    if not file:
        return jsonify({"error": "File not found"}), 404
    
    user= User.query.get(shared.sharer_id)

    # Prepare response data
    response_data = {
        "file_id": file.id,
        "filename": file.orginal_filename,
        "shared_by": user.username,
        "recipient_email": shared.recipient_email,
        "shared_at": shared.time,
        "expires_at": shared.expiration_time,
        "message": shared.message,
        "downloaded": shared.download
    }
    print(file.id, file.orginal_filename, shared.sharer_id, shared.recipient_email, shared.time, shared.expiration_time, shared.message, shared.download)

    return jsonify(response_data), 200

@views.route("/shared/preview/<token>", methods=["GET"])
def preview_shared_file(token):
    shared = SharedFile.query.filter_by(token=token).first()
    if not shared:
        return "Invalid link", 404
    if datetime.utcnow() > shared.expiration_time:
        return "This link has expired", 403

    file = Content.query.get(shared.file_id)
    if not file:
        return "File not found", 404

    path = os.path.join(UPLOAD_FOLDER, file.modified_filename)
    return send_file(path, as_attachment=False)


@views.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    data = SharedFile.query.filter(
    SharedFile.sharer_id == user.id,
    # SharedFile.time != None
    ).order_by(SharedFile.time.desc())
    print("count of shared files:", data.count())
 
    paginated = data.paginate(page=page, per_page=per_page, error_out=False)
    print("paginated count:", paginated.total)
    history_data = []
    for shared in paginated.items:
            history_data.append({
                "original_filename": shared.filename,
                "shared_with": shared.recipient_email,
                "shared_at": shared.time,
                "expires_at": shared.expiration_time,
                "message": shared.message,
                "downloaded": shared.download,
            })
    return jsonify({
        "history": history_data,
        "page": page,
        "per_page": per_page,
        "total_pages": paginated.pages
    }), 200
