"""API tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    """Health check."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_parse_no_file():
    """Parse without file returns 422."""
    r = client.post("/api/parse")
    assert r.status_code == 422
