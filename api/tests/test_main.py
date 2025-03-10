from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_api_working():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_example_search():
    response = client.get("search/?q=42+rue+papernest+75011+Paris")
    assert response.status_code == 200
    assert response.json() == {
        "orange": {"2G": True, "3G": True, "4G": False}, 
        "SFR": {"2G": True, "3G": True, "4G": True}
    }
