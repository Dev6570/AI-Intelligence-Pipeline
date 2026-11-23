from fastapi.testclient import TestClient
from src.production.api import app
client = TestClient(app)
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
def test_api_documentation():
    response = client.get("/openapi.json")
    assert response.status_code == 200
if __name__ == "__main__":
    test_home()
    test_api_documentation()
    print("All production API tests passed!")