from fastapi.testclient import TestClient

from toy_app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_notes_forbidden_without_guest():
    r = client.get("/api/notes/")
    assert r.status_code == 403


def test_guest_idor_recovers_planted_secret():
    start = client.post("/api/guest/start")
    assert start.status_code == 200
    assert "sessionid" in start.cookies
    r = client.get("/api/notes/")
    assert r.status_code == 200
    body = r.text
    assert "PLANTED_SECRET_ALPHA" in body
