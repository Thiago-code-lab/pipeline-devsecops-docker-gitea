import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, redirect, 
    url_for, jsonify, flash, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from config import config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização das extensões
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name: str = 'default') -> Flask:
    """
    Factory function para criar e configurar a aplicação Flask.
    
    Args:
        config_name: Nome da configuração a ser carregada (development, testing, production)
    """
    app = Flask(__name__)
    
    # Carrega as configurações
    app.config.from_object(config[config_name])
    app.config.from_prefixed_env()
    
    # Inicializa as extensões
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    CORS(app)
    limiter.init_app(app)
    
    # Registra os blueprints
    from .auth import auth_bp
    from .api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Configuração de tratamento de erros
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "ratelimit exceeded",
            "message": str(e.description)
        }), 429
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context() -> Dict[str, Any]:
        return {
            'db': db,
            'User': User,
            'Task': Task
        }
    
    return app

# Models
class User(db.Model):
    """Modelo de usuário para autenticação"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='author', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Gera o hash da senha"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verifica a senha"""
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self) -> Dict[str, str]:
        """Gera tokens de acesso e refresh"""
        return {
            'access_token': create_access_token(identity=self.id),
            'refresh_token': create_refresh_token(identity=self.id)
        }

class Task(db.Model):
    """Modelo de tarefa"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=2)  # 1: Alta, 2: Média, 3: Baixa
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'user_id': self.user_id
        }

# Inicializa a aplicação
app = create_app(os.getenv('FLASK_ENV') or 'default')

# Rotas da aplicação
@app.route('/')
@limiter.limit("100/day")
def index():
    """Rota principal da aplicação"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    tasks = Task.query.filter_by(user_id=current_user.id)\
                     .order_by(Task.created_at.desc())\
                     .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('index.html', tasks=tasks)

# Health check endpoint
@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    try:
        # Verifica a conexão com o banco de dados
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])