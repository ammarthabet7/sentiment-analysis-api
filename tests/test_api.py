import pytest
import requests
import time
import subprocess
import signal
import os

def test_basic_imports():
    '''Test that we can import our modules'''
    try:
        from main import app
        from database import get_database_config
        from model import get_sentiment_analyzer
        assert app is not None
        assert True
    except Exception as e:
        pytest.fail(f"Import failed: {e}")

def test_database_config():
    '''Test database configuration logic'''
    from database import get_database_config
    # Ensure no DATABASE_URL for testing
    os.environ.pop('DATABASE_URL', None)
    url, engine = get_database_config()
    assert 'sqlite' in url.lower()

def test_model_loading():
    '''Test that sentiment analyzer can be created'''
    from model import get_sentiment_analyzer
    analyzer = get_sentiment_analyzer()
    assert analyzer is not None
    
    # Test basic functionality
    result = analyzer.analyze_sentiment("This is a test")
    assert 'sentiment' in result
    assert 'confidence' in result
