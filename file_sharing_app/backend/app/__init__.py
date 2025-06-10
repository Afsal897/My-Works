import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from flask_socketio import SocketIO


# Load environment variables from .env file
load_dotenv()

# Extensions

socketio = SocketIO(cors_allowed_origins="*") 
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
serializer = None

def get_serializer():
    global serializer
    return serializer

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')}"
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        minutes=int(os.getenv('JWT_EXPIRES_MINUTES', 15))
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'afsal.salim@innovaturelabs.com'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'afsal.salim@innovaturelabs.com'
    global serializer
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail = Mail(app)
    socketio.init_app(app)

    # Register Blueprints
    from .view import views
    from .auth import authn
    from .profile_view import profile_view
    from .friendview import friend
    from .chatview import chat

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(authn, url_prefix='/')
    app.register_blueprint(profile_view, url_prefix='/profile')
    app.register_blueprint(friend, url_prefix='/friend')
    app.register_blueprint(chat, url_prefix='/chat')

    # Create database tables
    with app.app_context():
        db.create_all()

    from . import socket 

    return app
