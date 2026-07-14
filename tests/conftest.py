import pytest
from app import create_app, db  # an deine Struktur anpassen

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key-32-bytes-minimum!",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Registriert einen User, loggt ihn ein und liefert Header mit JWT."""
    client.post("/api/auth/register", json={
        "username": "user123",
        "password": "password123"
    })
    resp = client.post("/api/auth/login", json={
        "username": "user123",
        "password": "password123"
    })
    token = resp.get_json()["access_token"]  # Feldname an deine API anpassen
    return {"Authorization": f"Bearer {token}"}