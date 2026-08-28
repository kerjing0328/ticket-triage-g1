import json
import pytest
import azure.functions as func


class TestHealthEndpoint:
    def test_returns_200_status(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        assert resp.status_code == 200

    def test_returns_json_content_type(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        assert resp.mimetype == "application/json"

    def test_returns_valid_json(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert isinstance(body, dict)

    def test_contains_status_field(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert "status" in body

    def test_contains_storage_field(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert "storage" in body

    def test_contains_classifier_field(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert "classifier" in body

    def test_storage_value_is_valid(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["storage"] in ["cosmos", "in-memory"]

    def test_classifier_value_is_valid(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["classifier"] in ["azure-ai-language", "keyword-rules"]

    def test_health_status_healthy(self):
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["status"] == "healthy"

    def test_health_storage_without_cosmos(self, monkeypatch):
        monkeypatch.delenv("COSMOS_CONNECTION_STRING", raising=False)
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["storage"] == "in-memory"

    def test_health_classifier_without_ai(self, monkeypatch):
        monkeypatch.delenv("AI_LANGUAGE_ENDPOINT", raising=False)
        monkeypatch.delenv("AI_LANGUAGE_KEY", raising=False)
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["classifier"] == "keyword-rules"

    def test_health_with_all_configured(self, monkeypatch):
        monkeypatch.setenv("COSMOS_CONNECTION_STRING", "AccountEndpoint=https://localhost:8081/;AccountKey=fake==")
        monkeypatch.setenv("AI_LANGUAGE_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
        monkeypatch.setenv("AI_LANGUAGE_KEY", "fakekey")
        from api.health import main as health_main
        req = func.HttpRequest(method="GET", url="/api/health", body=None)
        resp = health_main(req)
        body = json.loads(resp.get_body())
        assert body["storage"] == "cosmos"
        assert body["classifier"] == "azure-ai-language"


class TestCategoriesEndpoint:
    def test_returns_200_status(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        assert resp.status_code == 200

    def test_returns_json_content_type(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        assert resp.mimetype == "application/json"

    def test_returns_list(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        body = json.loads(resp.get_body())
        assert isinstance(body, list)

    def test_has_six_categories(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        body = json.loads(resp.get_body())
        assert len(body) == 6

    def test_category_structure(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        body = json.loads(resp.get_body())
        for cat in body:
            assert "id" in cat
            assert "name" in cat
            assert "description" in cat

    def test_contains_it_support(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        body = json.loads(resp.get_body())
        names = [cat["name"] for cat in body]
        assert "IT Support" in names

    def test_contains_facilities(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        body = json.loads(resp.get_body())
        names = [cat["name"] for cat in body]
        assert "Facilities" in names

    def test_contains_general_enquiry(self):
        from api.categories import main as cat_main
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = cat_main(req)
        body = json.loads(resp.get_body())
        names = [cat["name"] for cat in body]
        assert "General Enquiry" in names

    def test_all_categories_have_ids(self):
        from api.categories import CATEGORIES
        for cat in CATEGORIES:
            assert isinstance(cat["id"], str)
            assert len(cat["id"]) > 0
