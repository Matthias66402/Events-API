import uuid


def _register_and_login(client):
    """Registers a fresh user and returns (auth_headers, user_id)."""
    username = f"user_{uuid.uuid4().hex[:8]}"
    reg = client.post("/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    user_id = reg.get_json()["user"]["id"]
    resp = client.post("/api/auth/login", json={
        "username": username,
        "password": "password123"
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def _create_event(client, headers, **overrides):
    payload = {
        "title": f"Event {uuid.uuid4().hex[:8]}",
        "description": "desc",
        "date": "2026-03-01T10:00:00",
        "location": "Loc",
        "capacity": None,
        "is_public": True,
        "requires_admin": False,
    }
    payload.update(overrides)
    resp = client.post("/api/events", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.get_json()


def test_rsvp_nonexistent_event_returns_404(client):
    resp = client.post("/api/rsvps/event/999999999", json={})
    assert resp.status_code == 404


def test_rsvp_public_event_without_auth_succeeds(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=True)

    resp = client.post(f"/api/rsvps/event/{event['id']}", json={})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["event_id"] == event["id"]
    assert body["user_id"] is None
    assert body["attending"] is True  # defaults to True when not specified


def test_rsvp_public_event_with_auth_succeeds(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=True)
    rsvp_headers, user_id = _register_and_login(client)

    resp = client.post(f"/api/rsvps/event/{event['id']}", json={"attending": True}, headers=rsvp_headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["user_id"] == user_id
    assert body["attending"] is True


def test_rsvp_private_event_without_auth_returns_401(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=False)

    resp = client.post(f"/api/rsvps/event/{event['id']}", json={})
    assert resp.status_code == 401


def test_rsvp_private_event_with_auth_succeeds(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=False)
    rsvp_headers, _ = _register_and_login(client)

    resp = client.post(f"/api/rsvps/event/{event['id']}", json={}, headers=rsvp_headers)
    assert resp.status_code == 201


def test_rsvp_admin_event_without_auth_returns_401(client, auth_headers):
    event = _create_event(client, auth_headers, requires_admin=True)

    resp = client.post(f"/api/rsvps/event/{event['id']}", json={})
    assert resp.status_code == 401


def test_rsvp_admin_event_non_admin_returns_403(client, auth_headers):
    event = _create_event(client, auth_headers, requires_admin=True)
    # A freshly registered user is only an admin if they happen to be the very
    # first user ever created in the database, which is not the case once the
    # suite (or the app) has run before.
    rsvp_headers, _ = _register_and_login(client)

    resp = client.post(f"/api/rsvps/event/{event['id']}", json={}, headers=rsvp_headers)
    assert resp.status_code == 403


def test_rsvp_rejected_when_event_at_full_capacity(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=True, capacity=1)

    first = client.post(f"/api/rsvps/event/{event['id']}", json={})
    assert first.status_code == 201

    second = client.post(f"/api/rsvps/event/{event['id']}", json={})
    assert second.status_code == 400
    assert "capacity" in second.get_json()["error"].lower()


def test_rsvp_again_updates_existing_rsvp_instead_of_creating_new(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=True)
    rsvp_headers, user_id = _register_and_login(client)

    first = client.post(f"/api/rsvps/event/{event['id']}", json={"attending": True}, headers=rsvp_headers)
    assert first.status_code == 201
    first_id = first.get_json()["id"]

    second = client.post(f"/api/rsvps/event/{event['id']}", json={"attending": False}, headers=rsvp_headers)
    assert second.status_code == 200
    body = second.get_json()
    assert body["id"] == first_id
    assert body["attending"] is False

    stats = client.get(f"/api/rsvps/event/{event['id']}").get_json()["stats"]
    assert stats["total"] == 1
    assert stats["attending"] == 0
    assert stats["not_attending"] == 1


def test_get_rsvps_returns_event_list_and_stats(client, auth_headers):
    event = _create_event(client, auth_headers, is_public=True)

    attending_headers, _ = _register_and_login(client)
    not_attending_headers, _ = _register_and_login(client)
    client.post(f"/api/rsvps/event/{event['id']}", json={"attending": True}, headers=attending_headers)
    client.post(f"/api/rsvps/event/{event['id']}", json={"attending": False}, headers=not_attending_headers)

    resp = client.get(f"/api/rsvps/event/{event['id']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["event"]["id"] == event["id"]
    assert len(body["rsvps"]) == 2
    assert body["stats"] == {"attending": 1, "not_attending": 1, "total": 2}


def test_get_rsvps_nonexistent_event_returns_404(client):
    resp = client.get("/api/rsvps/event/999999999")
    assert resp.status_code == 404
