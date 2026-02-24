import pytest
import json
from src.serving.enhanced_inference import app

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'model_loaded' in data

def test_add_review_success(client):
    """Test adding a review"""
    response = client.post('/add_review',
        json={'movie': 'Test Movie', 'review': 'Great film!'},
        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['review_added'] == True
    assert data['sentiment'] in ['positive', 'negative']

def test_add_review_missing_data(client):
    """Test adding review with missing data"""
    response = client.post('/add_review',
        json={'movie': 'Test Movie'},
        content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_get_movie_not_found(client):
    """Test getting non-existent movie"""
    response = client.get('/movie/nonexistent')
    assert response.status_code == 404

def test_predict_endpoint(client):
    """Test simple prediction"""
    response = client.post('/predict',
        json={'text': 'This is amazing!'},
        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sentiment' in data
    assert 'confidence' in data
    assert data['sentiment'] in ['positive', 'negative']

def test_list_movies_empty(client):
    """Test listing movies when empty"""
    response = client.get('/movies')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'movies' in data
    assert isinstance(data['movies'], list)
