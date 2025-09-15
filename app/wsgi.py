"""
WSGI config for Task Manager API.

This module contains the WSGI application used by the production server.
"""
import os
from . import create_app

# Create the application using the appropriate configuration
app = create_app(os.getenv('FLASK_ENV') or 'production')

if __name__ == "__main__":
    # This is only used during development
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
