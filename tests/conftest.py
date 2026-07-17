import uuid
import requests
import pytest

BASE_URL = "http://localhost:5000"


class HttpTestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, method, path, **kwargs):
        resp = requests.request(method, self.base_url + path, **kwargs)
        resp.get_json = resp.json
        return resp

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)


@pytest.fixture
def client():
    try:
        requests.get(BASE_URL + "/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Server unter {BASE_URL} nicht erreichbar. Läuft Docker (docker compose up)?")
    return HttpTestClient(BASE_URL)


@pytest.fixture
def auth_headers(client):
    """Registriert einen eindeutigen User, loggt ihn ein und liefert Header mit JWT."""
    username = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    resp = client.post("/api/auth/login", json={
        "username": username,
        "password": "password123"
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
