import os
os.environ["DATABASE_URL"] = "sqlite:///./test_expenses.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_auth_and_expense_crud():
    email = "pytest-user@example.com"
    client.post("/api/auth/register", json={"name":"Pytest User","email":email,"password":"strongpass123"})
    response = client.post("/api/auth/login", json={"email":email,"password":"strongpass123"})
    assert response.status_code == 200
    headers = {"Authorization":f"Bearer {response.json()['access_token']}"}
    created = client.post("/api/expenses", headers=headers, json={"title":"Test lunch","amount":250,"category":"Food","transaction_type":"expense","spent_on":"2026-11-05","description":"test"})
    assert created.status_code == 201
    expense_id = created.json()["id"]
    assert client.get("/api/expenses", headers=headers).json()[0]["title"] == "Test lunch"
    assert client.delete(f"/api/expenses/{expense_id}", headers=headers).status_code == 204
