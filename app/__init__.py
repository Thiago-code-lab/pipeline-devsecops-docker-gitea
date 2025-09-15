import os
import logging
import click
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from .config import config
from .models import User, Task, db as db_model

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name=None):
    """Create and configure the Flask application.
    
    Args:
        config_name: The configuration to use. If None, uses FLASK_ENV or 'default'.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Set up logging
    from .utils import setup_logging
    setup_logging(app)
    
    # Initialize extensions
    db_model.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db_model)
    
    # Rate limiting configuration
    limiter.init_app(app)
    
    # JWT configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Registra os blueprints
    from .auth import auth_bp
    from .api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Adiciona o comando init-db para inicializar o banco de dados
    @app.cli.command('init-db')
    def init_db():
        """Inicializa o banco de dados"""
        with app.app_context():
            db.create_all()
            print('Banco de dados inicializado com sucesso!')
    
    # Adiciona o comando create-admin para criar um usuário administrador
    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin(username, email, password):
        """Cria um usuário administrador"""
        with app.app_context():
            if User.query.filter_by(email=email).first():
                print('Já existe um usuário com este email')
                return
                
            admin = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            print('Administrador criado com sucesso!')
    
    # Rota principal
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Task Manager API',
            'version': '1.0.0',
            'status': 'running',
            'documentation': '/api/v1/docs'
        })
    
    # Tratamento de erros
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Recurso não encontrado',
            'message': 'O recurso solicitado não existe.'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Erro interno: {str(error)}')
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado. Tente novamente mais tarde.'
        }), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Limite de requisições excedido',
            'message': str(e.description)
        }), 429
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db_model,
            'User': User,
            'Task': Task,
            'create_admin': create_admin
        }
    
    return app
