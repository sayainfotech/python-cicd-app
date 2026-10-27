from app import app


def test_homepage():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Python CI/CD" in response.data


def test_api():
    client = app.test_client()
    response = client.get("/api")

    assert response.status_code == 200
    assert response.json["status"] == "running"


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "UP"}


def test_version():
    client = app.test_client()
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json["version"] == "1.0.0"
