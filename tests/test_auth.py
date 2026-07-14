def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "username": "newuser",
        "password": "securepass"
    })
    assert resp.status_code == 201

# def test_register_duplicate_username(client):
#     client.post("/api/auth/register", json={"username": "dup", "password": "pw"})
#     resp = client.post("/api/auth/register", json={"username": "dup", "password": "pw"})
#     assert resp.status_code == 409  # oder 400, je nach Implementierung

def test_login_success(client):
    client.post("/api/auth/register", json={"username": "u1", "password": "pw123"})
    resp = client.post("/api/auth/login", json={"username": "u1", "password": "pw123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()

def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"username": "u2", "password": "pw123"})
    resp = client.post("/api/auth/login", json={"username": "u2", "password": "wrong"})
    assert resp.status_code == 401