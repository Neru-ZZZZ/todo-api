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

def test_get_todos(client):
    response = client.get("/todos")
    assert response.status_code == 200

def test_create_todo(client):
    response = client.post("/todos", json={"item": "テストタスク"})
    assert response.status_code == 200
    assert response.json()["todo"]["item"] == "テストタスク"

def test_toggle_done(client):
    res = client.post("/todos", json={"item": "完了テスト"})
    todo_id = res.json()["todo"]["id"]
    response = client.patch(f"/todos/{todo_id}/done")
    assert response.status_code == 200
    assert response.json()["todo"]["done"] == True

def test_delete_todo(client):
    res = client.post("/todos", json={"item": "削除テスト"})
    todo_id = res.json()["todo"]["id"]
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200

def test_toggle_done_not_found(client):
    response = client.patch("/todos/99999/done")
    assert response.status_code == 404

def test_delete_not_found(client):
    response = client.delete("/todos/99999")
    assert response.status_code == 404