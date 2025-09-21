import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

def test_root_endpoint():
    '''Test the root endpoint returns correct info'''
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert 'version' in data
    assert data['version'] == '2.0.0'

def test_health_endpoint():
    '''Test health check endpoint'''
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'components' in data

def test_analyze_sentiment_positive():
    '''Test sentiment analysis with positive text'''
    test_data = {
        'text': 'I love this amazing API!',
        'user_id': 'test_user'
    }
    response = client.post('/analyze', json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data['sentiment'] == 'positive'  # Human-readable positive label
    assert data['confidence'] > 0.5
    assert 'analysis_id' in data

def test_analyze_sentiment_empty_text():
    '''Test sentiment analysis with empty text'''
    test_data = {'text': ''}
    response = client.post('/analyze', json=test_data)
    assert response.status_code == 400

def test_analyze_sentiment_long_text():
    '''Test sentiment analysis with very long text'''
    long_text = 'This is a test. ' * 100  # Over 1000 characters
    test_data = {'text': long_text}
    response = client.post('/analyze', json=test_data)
    assert response.status_code == 400
