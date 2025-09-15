from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from ..models import Task, db

# Cria o blueprint da API
api_bp = Blueprint('api', __name__)

def validate_task_data(data):
    """Valida os dados de uma tarefa"""
    errors = {}
    
    if not data.get('title') or len(data['title'].strip()) < 3:
        errors['title'] = 'O título é obrigatório e deve ter pelo menos 3 caracteres'
    
    if 'description' in data and len(data['description']) > 1000:
        errors['description'] = 'A descrição não pode ter mais de 1000 caracteres'
    
    if 'due_date' in data and data['due_date']:
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            if due_date < datetime.utcnow():
                errors['due_date'] = 'A data de vencimento não pode ser no passado'
        except (ValueError, TypeError):
            errors['due_date'] = 'Formato de data inválido. Use o formato ISO 8601 (ex: 2023-12-31T23:59:59Z)'
    
    if 'priority' in data and data['priority'] not in [1, 2, 3]:
        errors['priority'] = 'A prioridade deve ser 1 (Alta), 2 (Média) ou 3 (Baixa)'
    
    return errors if errors else None

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Obtém todas as tarefas do usuário"""
    try:
        user_id = get_jwt_identity()
        
        # Filtros
        completed = request.args.get('completed', type=lambda v: v.lower() == 'true')
        priority = request.args.get('priority', type=int)
        
        query = Task.query.filter_by(user_id=user_id)
        
        if completed is not None:
            query = query.filter_by(completed=completed)
            
        if priority in [1, 2, 3]:
            query = query.filter_by(priority=priority)
        
        # Ordenação
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_by not in ['created_at', 'due_date', 'priority']:
            sort_by = 'created_at'
        
        sort_field = getattr(Task, sort_by)
        
        if sort_order.lower() == 'asc':
            tasks = query.order_by(sort_field.asc()).all()
        else:
            tasks = query.order_by(sort_field.desc()).all()
        
        return jsonify([task.to_dict() for task in tasks])
    
    except Exception as e:
        current_app.logger.error(f'Erro ao buscar tarefas: {str(e)}')
        return jsonify({'error': 'Erro ao buscar tarefas'}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Obtém uma tarefa específica"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
            
        return jsonify(task.to_dict())
    
    except Exception as e:
        current_app.logger.error(f'Erro ao buscar tarefa {task_id}: {str(e)}')
        return jsonify({'error': 'Erro ao buscar tarefa'}), 500

@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Cria uma nova tarefa"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validação dos dados
        errors = validate_task_data(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Cria a nova tarefa
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            due_date=datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data.get('due_date') else None,
            priority=data.get('priority', 2),  # Prioridade padrão: Média
            user_id=user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa criada com sucesso',
            'task': task.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao criar tarefa: {str(e)}')
        return jsonify({'error': 'Erro ao criar tarefa'}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Atualiza uma tarefa existente"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        data = request.get_json()
        
        # Validação dos dados
        errors = validate_task_data(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Atualiza os campos
        task.title = data.get('title', task.title)
        
        if 'description' in data:
            task.description = data['description']
            
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
            
        if 'priority' in data:
            task.priority = data['priority']
            
        if 'completed' in data:
            task.completed = data['completed']
        
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa atualizada com sucesso',
            'task': task.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao atualizar tarefa {task_id}: {str(e)}')
        return jsonify({'error': 'Erro ao atualizar tarefa'}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Remove uma tarefa"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Tarefa removida com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao remover tarefa {task_id}: {str(e)}')
        return jsonify({'error': 'Erro ao remover tarefa'}), 500

@api_bp.route('/tasks/toggle/<int:task_id>', methods=['POST'])
@jwt_required()
def toggle_task(task_id):
    """Alterna o status de conclusão de uma tarefa"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Status da tarefa atualizado com sucesso',
            'completed': task.completed
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao alternar status da tarefa {task_id}: {str(e)}')
        return jsonify({'error': 'Erro ao atualizar status da tarefa'}), 500
