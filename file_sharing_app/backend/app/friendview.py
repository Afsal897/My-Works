from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, FriendRequest, Friendship
from . import db


friend = Blueprint('friend', __name__)


@friend.route("/connect/<email>", methods=["GET"])
@jwt_required()
def connect(email):
    """Connect with a user by email."""
    current_user_id = int(get_jwt_identity())
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.id == current_user_id:
        return jsonify({"message": "You cannot connect with yourself"}), 400
    
    friend = Friendship.query.filter(
        db.or_(
            db.and_(Friendship.user1_id == current_user_id, Friendship.user2_id == user.id),
            db.and_(Friendship.user1_id == user.id, Friendship.user2_id == current_user_id)
        )
    ).first()

    if friend:
        return jsonify({"message": "Already friends"}), 400


    existing_request = FriendRequest.query.filter_by(
        from_user_id=current_user_id,
        to_user_id=user.id,
        status='pending'
    ).first()

    if existing_request:
        return jsonify({"message": "Friend request already sent"}), 400

    new_request = FriendRequest(from_user_id=current_user_id, to_user_id=user.id)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Friend request sent successfully"}), 200


@friend.route("/requests", methods=["GET"])
@jwt_required()
def get_friend_requests():
    """Get all friend requests for the current user.whnere friendrequest.status=pending"""
    current_user_id = int(get_jwt_identity())
    
    requests = FriendRequest.query.filter_by(to_user_id=current_user_id, status='pending').all()
    requests_data = [{
        "id": req.id,
        "from_user_id": req.from_user_id,
        "created_at": req.created_at.isoformat(),
        "from_user": {
            "id": req.from_user.id,
            "email": req.from_user.email,
            "first_name": req.from_user.first_name,
            "last_name": req.from_user.last_name
        }
    } for req in requests]

    return jsonify(requests_data), 200
    

@friend.route("/requests/<int:request_id>/accept", methods=["POST"])
@jwt_required()
def accept_request(request_id):
    """Accept a friend request."""
    current_user_id = int(get_jwt_identity())
    req = FriendRequest.query.get(request_id)

    if not req or req.to_user_id != current_user_id or req.status != 'pending':
        return jsonify({"message": "Invalid request"}), 400

    req.status = 'accepted'

    # Create a friendship record
    friendship = Friendship(user1_id=req.from_user_id, user2_id=current_user_id)
    db.session.add(friendship)

    # Optional: add both users as friends in a separate table if needed
    db.session.commit()
    return jsonify({"message": "Friend request accepted"}), 200


@friend.route("/requests/<int:request_id>/reject", methods=["POST"])
@jwt_required()
def reject_request(request_id):
    """Reject a friend request."""
    current_user_id = int(get_jwt_identity())
    req = FriendRequest.query.get(request_id)

    if not req or req.to_user_id != current_user_id or req.status != 'pending':
        return jsonify({"message": "Invalid request"}), 400

    req.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Friend request rejected"}), 200
