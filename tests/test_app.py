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
    """Test if the home page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Gerenciador de Tarefas' in response.data

def test_add_task(client):
    """Test adding a new task"""
    response = client.post('/add_task', data={
        'title': 'New Task',
        'description': 'Task description'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'New Task' in response.data

def test_add_task_without_title(client):
    """Test adding task without title"""
    response = client.post('/add_task', data={
        'description': 'Task description'
    }, follow_redirects=True)
    
    assert response.status_code == 200

def test_toggle_task(client, sample_task):
    """Test toggling task status"""
    with app.app_context():
        db.session.add(sample_task)
        db.session.commit()
        
        # Toggle to completed
        response = client.get(f'/toggle_task/{sample_task.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Check if it was marked as completed
        task = Task.query.get(sample_task.id)
        assert task.completed == True

def test_delete_task(client, sample_task):
    """Test deleting a task"""
    with app.app_context():
        db.session.add(sample_task)
        db.session.commit()
        
        response = client.get(f'/delete_task/{sample_task.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Check if the task was deleted
        task = Task.query.get(sample_task.id)
        assert task is None

def test_api_tasks(client, sample_task):
    """Test the tasks API"""
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
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_task_model(sample_task):
    """Test the Task model"""
    assert sample_task.title == "Test Task"
    assert sample_task.description == "Test Description"
    assert sample_task.completed == False
    assert isinstance(sample_task.created_at, datetime)
    
    # Test the __repr__ method
    assert "Test Task" in str(sample_task) 