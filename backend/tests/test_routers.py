from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_get_sky_success():
    # URL params: /sky?latitude=50.45&...)
    params = {"observed_at": "2023-10-27T20:00:00", "longitude": 30.52, "latitude": 50.45}

    response = client.get("/sky", params=params)

    assert response.status_code == 200

    data = response.json()
    assert "stars" in data
    assert isinstance(data["stars"], list)
