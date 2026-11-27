from app import app


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_add_and_get_note():
    client = app.test_client()
    response = client.post("/notes", json={"text": "learn devops"})
    assert response.status_code == 201

    response = client.get("/notes")
    assert any(n["text"] == "learn devops" for n in response.get_json())