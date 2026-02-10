"""Unit tests for API error handling and logging."""

import json
import logging
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from ajips.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
    assert response.json()["name"] == "AJIPS"


@patch("ajips.app.api.routes.build_job_profile")
def test_analyze_success(mock_build):
    mock_build.return_value = MagicMock()
    response = client.post(
        "/analyze",
        json={"job_posting": {"text": "Test job"}, "resume_text": ""},
    )
    assert response.status_code == 200
    mock_build.assert_called_once()


@patch("ajips.app.api.routes.build_job_profile")
def test_analyze_value_error(mock_build):
    # Simulate SSRF rejection from ingestion
    from ajips.app.services.ingestion import _is_safe_url

    mock_build.side_effect = ValueError("URL not allowed")
    response = client.post(
        "/analyze",
        json={"job_posting": {"url": "http://127.0.0.1/local"}, "resume_text": ""},
    )
    assert response.status_code == 400
    assert "URL not allowed" in response.json()["detail"]


@patch("ajips.app.api.routes.build_job_profile")
def test_analyze_unhandled_error(mock_build):
    mock_build.side_effect = RuntimeError("Unexpected")
    response = client.post(
        "/analyze",
        json={"job_posting": {"text": "Test job"}, "resume_text": ""},
    )
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


def test_cors_headers():
    response = client.options("/analyze")
    # Confirm only allowed methods and our restricted origins
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
