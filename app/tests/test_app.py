import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db, Base
from app.main import app
from app.config import settings
import json

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(session):
    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client

# Test user registration
def test_create_user(client):
    response = client.post(
        "/users/", 
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    new_user = response.json()
    assert new_user["email"] == "test@example.com"
    assert "id" in new_user

# Test authentication
def test_login(client):
    # First create a user
    client.post(
        "/users/", 
        json={"email": "test@example.com", "password": "password123"}
    )
    
    # Then try to login
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

# Test creating a post (requires authentication)
def test_create_post(client, test_user, test_token):
    # Create a new post
    headers = {
        "Authorization": f"Bearer {test_token}"
    }
    response = client.post(
        "/posts/",
        json={"title": "Test Post", "content": "This is a test post", "published": True},
        headers=headers
    )
    assert response.status_code == 201
    created_post = response.json()
    assert created_post["title"] == "Test Post"
    assert created_post["content"] == "This is a test post"
    assert created_post["published"] == True
    assert "id" in created_post

# Test fixtures for authenticated requests
@pytest.fixture
def test_user(client):
    user_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def test_token(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]}
    )
    token = response.json()["access_token"]
    return token