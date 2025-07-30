import pytest
import json
from app import app, db, Task
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_task():
    return Task(
        title="Test Task",
        description="Test Description",
        completed=False,
        created_at=datetime.utcnow()
    )

def test_index_page(client):
    """Testa se a página inicial carrega corretamente"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Gerenciador de Tarefas' in response.data

def test_add_task(client):
    """Testa adicionar uma nova tarefa"""
    response = client.post('/add_task', data={
        'title': 'Nova Tarefa',
        'description': 'Descrição da tarefa'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Nova Tarefa' in response.data

def test_add_task_without_title(client):
    """Testa adicionar tarefa sem título"""
    response = client.post('/add_task', data={
        'description': 'Descrição da tarefa'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Título é obrigatório' in response.data

def test_toggle_task(client, sample_task):
    """Testa alternar status da tarefa"""
    with app.app_context():
        db.session.add(sample_task)
        db.session.commit()
        
        # Toggle para completed
        response = client.get(f'/toggle_task/{sample_task.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Verifica se foi marcada como completed
        task = Task.query.get(sample_task.id)
        assert task.completed == True

def test_delete_task(client, sample_task):
    """Testa deletar uma tarefa"""
    with app.app_context():
        db.session.add(sample_task)
        db.session.commit()
        
        response = client.get(f'/delete_task/{sample_task.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Verifica se a tarefa foi deletada
        task = Task.query.get(sample_task.id)
        assert task is None

def test_api_tasks(client, sample_task):
    """Testa a API de tarefas"""
    with app.app_context():
        db.session.add(sample_task)
        db.session.commit()
        
        response = client.get('/api/tasks')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == 'Test Task'
        assert data[0]['description'] == 'Test Description'
        assert data[0]['completed'] == False

def test_health_check(client):
    """Testa o endpoint de health check"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_task_model(sample_task):
    """Testa o modelo Task"""
    assert sample_task.title == "Test Task"
    assert sample_task.description == "Test Description"
    assert sample_task.completed == False
    assert isinstance(sample_task.created_at, datetime)
    
    # Testa o método __repr__
    assert "Test Task" in str(sample_task) 