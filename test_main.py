from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_check_db():
    response = client.get("/check-db")
    print(response.text) 
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_select_demo():
    response = client.get("/select-demo")
    print(response.text) 
    assert response.status_code == 200
    assert "result" in response.json()
