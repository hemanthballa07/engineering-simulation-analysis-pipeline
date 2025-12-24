import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "simulation-platform"}

@patch("api.app.list_runs_summary")
def test_list_runs(mock_list):
    mock_list.return_value = [{"run_id": "r1", "status": "SUCCESS"}]
    response = client.get("/runs")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["runs"][0]["run_id"] == "r1"

@patch("api.app.get_run_metrics")
def test_get_metrics_success(mock_get):
    mock_get.return_value = ({"max_temp": 1.0}, None)
    response = client.get("/runs/r1/metrics")
    assert response.status_code == 200
    assert response.json()["max_temp"] == 1.0

@patch("api.app.get_run_metrics")
def test_get_metrics_not_found(mock_get):
    mock_get.return_value = (None, "Run directory not found")
    response = client.get("/runs/missing/metrics")
    assert response.status_code == 404

@patch("api.app.get_run_metrics")
def test_get_metrics_invalid(mock_get):
    mock_get.return_value = (None, "Validation Failed: Physics error")
    response = client.get("/runs/bad/metrics")
    assert response.status_code == 422
