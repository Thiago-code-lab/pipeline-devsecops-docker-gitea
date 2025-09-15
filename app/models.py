from datetime import datetime
from typing import Dict, Any
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

# Inicialização do SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """Modelo de usuário para autenticação"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='author', lazy='dynamic', 
                          cascade='all, delete-orphan')
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'tasks_count': self.tasks.count()
        }

class Task(db.Model):
    """Modelo de tarefa"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                         onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=2)  # 1: Alta, 2: Média, 3: Baixa
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                       nullable=False, index=True)
    
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
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Atualiza os atributos a partir de um dicionário"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'user_id']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

# Relacionamentos adicionais
User.tasks = db.relationship('Task', back_populates='author', lazy='dynamic')
Task.author = db.relationship('User', back_populates='tasks')
