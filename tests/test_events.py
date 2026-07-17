def test_get_all_events(client):
    resp = client.get("/api/events")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_create_event_requires_auth(client):
    resp = client.post("/api/events", json={
        "title": "Python Meetup",
        "description": "Monthly meetup",
        "date": "2026-01-15T18:00:00",
        "location": "Tech Hub",
        "capacity": 50,
        "is_public": True,
        "requires_admin": False
    })
    assert resp.status_code == 401

def test_create_event_authenticated(client, auth_headers):
    resp = client.post("/api/events", json={
        "title": "Python Meetup",
        "description": "Monthly meetup",
        "date": "2026-01-15T18:00:00",
        "location": "Tech Hub",
        "capacity": 50,
        "is_public": True,
        "requires_admin": False
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Python Meetup"

def test_get_single_event(client, auth_headers):
    create_resp = client.post("/api/events", json={
        "title": "Test Event", "description": "desc", "date": "2026-02-01T10:00:00",
        "location": "X", "capacity": 10, "is_public": True, "requires_admin": False
    }, headers=auth_headers)
    event_id = create_resp.get_json()["id"]

    resp = client.get(f"/api/events/{event_id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == event_id

def test_get_nonexistent_event(client):
    resp = client.get("/api/events/999999999")
    assert resp.status_code == 404