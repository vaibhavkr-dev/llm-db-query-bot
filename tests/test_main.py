from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sql_query():
    response = client.post("/query", json={"query": "SELECT 1", "db_type": "sql"})
    assert response.status_code == 200
    assert response.json() == {"result": "Executed SQL: SELECT 1"}

def test_mongo_query():
    response = client.post("/query", json={"query": "{ find: 'collection' }", "db_type": "mongo"})
    assert response.status_code == 200
    assert response.json() == {"result": "Executed MongoDB: { find: 'collection' }"}

def test_invalid_db():
    response = client.post("/query", json={"query": "hello", "db_type": "invalid"})
    assert response.status_code == 400
