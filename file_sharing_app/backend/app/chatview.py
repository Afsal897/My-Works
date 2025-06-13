from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Content, User, Friendship, Message
from . import db
from datetime import datetime
from .utils import UPLOAD_FOLDER
import os


chat = Blueprint('chat', __name__)


@chat.route("/friends", methods=["GET"])
@jwt_required()
def get_friends():
    current_user_id = int(get_jwt_identity())

    # Get pagination and search params
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search", "").strip().lower()

    # Get all friendships
    friendships = Friendship.query.filter(
        (Friendship.user1_id == current_user_id) | 
        (Friendship.user2_id == current_user_id)
    ).all()

    friend_users = []
    for f in friendships:
        if f.user1_id == current_user_id:
            friend = f.user2
        else:
            friend = f.user1

        # Get latest message timestamp between user and friend
        latest_msg = (
            Message.query.filter(
                ((Message.sender_id == current_user_id) & (Message.receiver_id == friend.id)) |
                ((Message.sender_id == friend.id) & (Message.receiver_id == current_user_id))
            )
            .order_by(Message.timestamp.desc())
            .first()
        )

        last_msg_time = latest_msg.timestamp if latest_msg else None

        friend_users.append((friend, last_msg_time))

    # Apply search filter
    if search:
        friend_users = [
            (f, t) for f, t in friend_users if
            search in f.first_name.lower() or
            search in f.last_name.lower() or
            search in f.email.lower() or
            search in f.username.lower()
        ]

    # Sort friends by last message time (None values go to bottom)
    friend_users.sort(key=lambda ft: ft[1] or datetime.min, reverse=True)

    total_friends = len(friend_users)
    total_pages = (total_friends + per_page - 1) // per_page

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated_friends = friend_users[start:end]

    friends_data = [{
        "id": friend.id,
        "email": friend.email,
        "first_name": friend.first_name,
        "last_name": friend.last_name,
        "avatar": getattr(friend, "profile_picture", None),
        "last_msg_time": last_msg_time.isoformat() if last_msg_time else None
    } for friend, last_msg_time in paginated_friends]

    return jsonify({
        "friends": friends_data,
        "total": total_friends,
        "total_pages": total_pages,
        "page": page
    }), 200


@chat.route("/chat/<email>", methods=["GET"])
@jwt_required()
def get_chat_messages(email):
    current_user_id = int(get_jwt_identity())

    friend = User.query.filter_by(email=email).first()
    if not friend:
        return jsonify({"error": "Friend not found"}), 404
    
    friend_id = friend.id

    # Pagination params
    limit = int(request.args.get("limit", 30))
    offset = int(request.args.get("offset", 0))

    total_messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == current_user_id))
    ).count()

    messages = (
        Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == friend_id)) |
            ((Message.sender_id == friend_id) & (Message.receiver_id == current_user_id))
        )
        .order_by(Message.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    unread_messages = [
        msg for msg in messages if (msg.receiver_id == current_user_id and not msg.is_read)
    ]
    for msg in unread_messages:
        msg.is_read = True
    if unread_messages:
        db.session.commit()

    result = [{
        "id": msg.id,
        "sender": msg.sender.email,
        "receiver": msg.receiver.email,
        "content": msg.content,
        "is_file": msg.is_file,
        "filename": msg.filename if msg.is_file else None,
        "file_id": msg.file_id if msg.is_file else None,
        "timestamp": msg.timestamp.isoformat(),
        "is_read": msg.is_read
    } for msg in messages]


    return jsonify({
        "messages": result,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_messages,
            "has_more": offset + limit < total_messages
        }
        }), 200


@chat.route("/filenames", methods=["GET"])
@jwt_required()
def get_filenames():
    user_id = get_jwt_identity()
    contents = Content.query.filter_by(user_id=int(user_id)).all()

    files_info = []
    for content in contents:
        files_info.append({'file_id':content.id, 'filename': content.orginal_filename})

    return jsonify({"files" : files_info}),200


@chat.route("/download/<int:file_id>", methods=["GET"])
@jwt_required()
def download_file(file_id):

    # Fetch the file record
    file_record = Content.query.get(file_id)
    if not file_record:
        return jsonify({"error": "File not found"}), 404

    # Construct the file path
    file_path = os.path.join(UPLOAD_FOLDER, file_record.modified_filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found on disk"}), 404

    return send_file(file_path, as_attachment=True, download_name=file_record.orginal_filename)