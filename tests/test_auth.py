import uuid


def test_register_success(client):
    username = f"user_{uuid.uuid4().hex[:8]}"
    resp = client.post("/api/auth/register", json={
        "username": username,
        "password": "securepass"
    })
    assert resp.status_code == 201

def test_register_duplicate_username(client):
    username = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"username": username, "password": "pw"})
    resp = client.post("/api/auth/register", json={"username": username, "password": "pw"})
    assert resp.status_code == 400

def test_login_success(client):
    username = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"username": username, "password": "pw123"})
    resp = client.post("/api/auth/login", json={"username": username, "password": "pw123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()

def test_login_wrong_password(client):
    username = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"username": username, "password": "pw123"})
    resp = client.post("/api/auth/login", json={"username": username, "password": "wrong"})
    assert resp.status_code == 401
