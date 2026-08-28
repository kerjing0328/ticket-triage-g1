import json
import pytest
from api.health import main as health_main
import azure.functions as func


class TestHealthEndpoint:
    def test_returns_200_status(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        assert resp.status_code == 200

    def test_returns_json_content_type(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        assert resp.mimetype == "application/json"

    def test_returns_valid_json(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert isinstance(body, dict)

    def test_contains_status_field(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert "status" in body

    def test_contains_storage_field(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert "storage" in body

    def test_contains_classifier_field(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert "classifier" in body

    def test_storage_value_is_valid(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["storage"] in ["cosmos", "in-memory"]

    def test_classifier_value_is_valid(self):
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["classifier"] in ["azure-ai-language", "keyword-rules"]
