import json
import pytest
from api.categories import main as categories_main, CATEGORIES
import azure.functions as func


class TestCategoriesEndpoint:
    def test_returns_200_status(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        assert resp.status_code == 200

    def test_returns_json_content_type(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        assert resp.mimetype == "application/json"

    def test_returns_list(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        body = json.loads(resp.get_body())
        assert isinstance(body, list)

    def test_has_six_categories(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        body = json.loads(resp.get_body())
        assert len(body) == 6

    def test_category_structure(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        body = json.loads(resp.get_body())
        for cat in body:
            assert "id" in cat
            assert "name" in cat
            assert "description" in cat

    def test_contains_it_support(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        body = json.loads(resp.get_body())
        names = [cat["name"] for cat in body]
        assert "IT Support" in names

    def test_contains_facilities(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        body = json.loads(resp.get_body())
        names = [cat["name"] for cat in body]
        assert "Facilities" in names

    def test_contains_general_enquiry(self):
        req = func.HttpRequest(method="GET", url="/api/categories", body=None)
        resp = categories_main(req)
        body = json.loads(resp.get_body())
        names = [cat["name"] for cat in body]
        assert "General Enquiry" in names

    def test_constant_matches_endpoint(self):
        assert len(CATEGORIES) == 6
