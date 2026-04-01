import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 認証テスト
def test_register(client):
    response = client.post("/register", json={"username": "newuser", "password": "pass123"})
    assert response.status_code == 200
    assert response.json()["message"] == "登録しました"

def test_register_duplicate(client):
    client.post("/register", json={"username": "dupuser", "password": "pass"})
    response = client.post("/register", json={"username": "dupuser", "password": "pass"})
    assert response.status_code == 400

def test_login(client):
    client.post("/register", json={"username": "loginuser", "password": "mypass"})
    response = client.post("/login", data={"username": "loginuser", "password": "mypass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/register", json={"username": "wrongpass_user", "password": "correct"})
    response = client.post("/login", data={"username": "wrongpass_user", "password": "wrong"})
    assert response.status_code == 401

# 未認証アクセス
def test_get_todos_unauthenticated(client):
    response = client.get("/todos")
    assert response.status_code == 401

def test_create_todo_unauthenticated(client):
    response = client.post("/todos", json={"item": "未認証タスク"})
    assert response.status_code == 401

# 認証済みTODO操作
def test_get_todos(client, auth_headers):
    response = client.get("/todos", headers=auth_headers)
    assert response.status_code == 200

def test_create_todo(client, auth_headers):
    response = client.post("/todos", json={"item": "テストタスク"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["todo"]["item"] == "テストタスク"

def test_toggle_done(client, auth_headers):
    res = client.post("/todos", json={"item": "完了テスト"}, headers=auth_headers)
    todo_id = res.json()["todo"]["id"]
    response = client.patch(f"/todos/{todo_id}/done", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["todo"]["done"] == True

def test_delete_todo(client, auth_headers):
    res = client.post("/todos", json={"item": "削除テスト"}, headers=auth_headers)
    todo_id = res.json()["todo"]["id"]
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200

def test_toggle_done_not_found(client, auth_headers):
    response = client.patch("/todos/99999/done", headers=auth_headers)
    assert response.status_code == 404

def test_delete_not_found(client, auth_headers):
    response = client.delete("/todos/99999", headers=auth_headers)
    assert response.status_code == 404
