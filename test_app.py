
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

def test_update_note():
    client = app.test_client()

    response = client.post("/notes", json={"text": "old note"})
    note_id = response.get_json()["id"]

    response = client.put(
        f"/notes/{note_id}",
        json={"text": "updated note"}
    )

    assert response.status_code == 200
    assert response.get_json()["text"] == "updated note"

def test_delete_note():
    client = app.test_client()

    response = client.post("/notes", json={"text": "delete me"})
    note_id = response.get_json()["id"]

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 200

    response = client.get("/notes")
    assert not any(n["id"] == note_id for n in response.get_json())