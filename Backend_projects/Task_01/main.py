"""
Application Entry Point

This module initializes and runs the web application.
"""

from web import create_app

app = create_app()

def main():
    """Runs the web application in debug mode."""
    app.run(debug=True)

if __name__ == '__main__':
    main()
