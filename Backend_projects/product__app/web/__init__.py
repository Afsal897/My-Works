"""
Flask Application Factory

This file defines the create_app() function used to initialize and configure the Flask application.

It sets up:
- Environment-based configuration using dotenv (.env)
- SQLAlchemy for ORM and Flask-Migrate for database migrations
- JWT-based authentication using cookies
- Application Blueprints for route modularity

Configurations like SECRET_KEY, JWT_SECRET_KEY, and DB path are loaded from environment variables.
"""

import os
from datetime import timedelta

from flask import Flask
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

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')}"
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token_cookie'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        minutes=int(os.getenv('JWT_EXPIRES_MINUTES', 15))
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Should be True in production

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register Blueprints
    from .view import views
    from .auth import authn

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(authn, url_prefix='/')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
