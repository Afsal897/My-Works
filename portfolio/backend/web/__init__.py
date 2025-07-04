import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Extensions

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


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

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register Blueprints
    from .views import views

    app.register_blueprint(views, url_prefix='/')


    # Create database tables
    with app.app_context():
        db.create_all()

    return app