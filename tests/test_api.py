# tests/test_api.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from main import app

def test_create_valid_request():
    with TestClient(app) as client:
        response = client.post("/api/requests", json={
            "client_name": "Костя",
            "service": "Мышечный усилитель MyoBoost",
            "date": "2025-12-26",
            "notes": "Тест"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["client_name"] == "Костя"
    assert data["service"] == "Мышечный усилитель MyoBoost"
    assert data["date"] == "2025-12-26"

def test_reject_past_date():
    with TestClient(app) as client:
        response = client.post("/api/requests", json={
            "client_name": "Костя",
            "service": "Мышечный усилитель MyoBoost",
            "date": "2025-12-24",  # прошлое
            "notes": "Тест"
        })
    assert response.status_code == 422
    assert "будущем" in str(response.json())

def test_get_requests_returns_valid_list():
    with TestClient(app) as client:
        response = client.get("/api/requests")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Проверим, что каждый элемент — словарь с нужными полями
    for item in data:
        assert "id" in item
        assert "client_name" in item
        assert "service" in item
        assert "date" in item