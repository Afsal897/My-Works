'''Application factory module.

This module sets up the Flask app instance, initializes extensions such as 
JWTManager, and registers blueprints for authentication 
and operations.
'''

from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

def create_app():
    '''Application factory function.

    Creates and configures the Flask application instance, initializes
    extensions like SQLAlchemy and JWT, and registers app blueprints.

    Returns:
        Flask: Configured Flask application instance.
    '''
    app = Flask(__name__)

    # Configuration settings
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

    # Initialize extensions
    jwt = JWTManager(app)

    # Import and register blueprints
    from .auth import authn
    from .operations import op

    app.register_blueprint(authn, url_prefix='/')
    app.register_blueprint(op, url_prefix='/')  

    return app
