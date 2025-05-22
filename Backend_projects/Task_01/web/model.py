from . import db


class User(db.Model):
    """User model representing application users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # One-to-many relationship with Content
    content = db.relationship('Content', backref='user', lazy=True)


class Content(db.Model):
    """Content model representing uploaded or created content."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000), nullable=True)
    filename = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
