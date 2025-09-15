""
WSGI config for Task Manager API.

This module contains the WSGI application used by the production server.
"""
import os
from app import create_app

# Cria a aplicação usando a configuração apropriada
app = create_app(os.getenv('FLASK_ENV') or 'production')

if __name__ == "__main__":
    # Isso é usado apenas durante o desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
