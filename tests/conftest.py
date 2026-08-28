import pytest
import json
import azure.functions as func


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("COSMOS_CONNECTION_STRING", "AccountEndpoint=https://localhost:8081/;AccountKey=fakekey==")
    monkeypatch.setenv("AI_LANGUAGE_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
    monkeypatch.setenv("AI_LANGUAGE_KEY", "fakekey123")


@pytest.fixture
def sample_ticket():
    """Sample ticket data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@university.ac.uk",
        "title": "Cannot access campus Wi-Fi",
        "description": "I cannot connect to the campus Wi-Fi from my laptop. It was working yesterday.",
        "priority": "Medium"
    }


@pytest.fixture
def create_request():
    """Factory for creating mock HTTP requests."""
    def _create(method="GET", body=None, params=None):
        req = func.HttpRequest(method=method, url="/api/test", body=json.dumps(body).encode() if body else None)
        if params:
            for key, value in params.items():
                req.params[key] = value
        return req
    return _create
