from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from datetime import timedelta
import re

from ..models import User, db

# Cria o blueprint de autenticação
auth_bp = Blueprint('auth', __name__)

def validate_password(password: str) -> tuple[bool, str]:
    """Valida a força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    if not re.search(r"[a-z]", password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    if not re.search(r"\d", password):
        return False, "A senha deve conter pelo menos um número"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "A senha deve conter pelo menos um caractere especial"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novos usuários"""
    data = request.get_json()
    
    # Validação dos dados
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({
            'error': 'Dados incompletos. Forneça email, usuário e senha.'
        }), 400
    
    # Validação do email
    try:
        email = validate_email(data['email']).email
    except EmailNotValidError as e:
        return jsonify({'error': 'Email inválido'}), 400
    
    # Validação da senha
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Verifica se o usuário já existe
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Nome de usuário já em uso'}), 400
    
    # Cria o novo usuário
    try:
        user = User(
            username=data['username'],
            email=email,
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Gera tokens de acesso
        tokens = user.generate_auth_token()
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            **tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao registrar usuário: {str(e)}')
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Conta desativada'}), 403
    
    # Gera tokens de acesso
    tokens = user.generate_auth_token()
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        **tokens
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Endpoint para renovar o token de acesso"""
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_token})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obter informações do usuário atual"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat()
    })

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Endpoint para alterar a senha do usuário"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Senha atual incorreta'}), 401
    
    # Validação da nova senha
    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Atualiza a senha
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Senha alterada com sucesso'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao alterar senha: {str(e)}')
        return jsonify({'error': 'Erro ao alterar senha'}), 500
