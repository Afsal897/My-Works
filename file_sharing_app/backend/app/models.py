from . import db
from datetime import datetime


class User(db.Model):
    """User model representing application users."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100),unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    profile_picture = db.Column(db.String(500))
    balance_space = db.Column(db.Integer, default=1073741824)
    reset_token_used = db.Column(db.Boolean, default=False)

    # One-to-many relationship with Content
    content = db.relationship('Content', backref='user', lazy=True)

class Content(db.Model):
    """Content model representing uploaded or created content."""
    id = db.Column(db.Integer, primary_key=True)
    orginal_filename = db.Column(db.String(500), nullable=False)
    modified_filename = db.Column(db.String(500), nullable=False)
    file_size=db.Column(db.Integer, nullable = False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("content.id"))
    filename = db.Column(db.String(500), nullable=True)
    sharer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient_email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(120), unique=True, nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())
    download= db.Column(db.Boolean, default=False, nullable=False)

    file = db.relationship("Content", backref="shared_links")

#for friend request and friendship management and chat

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])


# models.py

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_file = db.Column(db.Boolean, default=False)
    file_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=True)
    filename = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])
    file = db.relationship("Content", foreign_keys=[file_id])
