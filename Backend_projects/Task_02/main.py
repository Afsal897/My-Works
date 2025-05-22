'''Entry point for the Flask web application.

This script initializes the Flask app using the application factory pattern
and runs the app in debug mode for development.
'''

from web import create_app  # Import the app factory function

# Create the Flask application instance using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the app in debug mode (recommended only during development)
    app.run(debug=True)
