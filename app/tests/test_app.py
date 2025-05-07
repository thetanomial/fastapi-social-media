"""
Simple test file for FastAPI Social Media app
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create a test client
client = TestClient(app)

# Basic test for the root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200