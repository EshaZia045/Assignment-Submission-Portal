import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app

VALID = {"name": "Ali Khan", "reg_no": "2022-CS-101",
         "title": "Assignment 1", "url": "https://github.com/ali/a1"}

@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "subs.json"))
    app.config["TESTING"] = True
    return app.test_client()

def test_valid_submission_is_saved_and_listed(client):
    r = client.post("/", data=VALID)
    assert r.status_code == 200
    page = client.get("/").get_data(as_text=True)
    assert "Assignment 1" in page and "2022-CS-101" in page

def test_missing_registration_number_is_rejected(client):
    data = {**VALID, "reg_no": ""}
    r = client.post("/", data=data)
    assert r.status_code == 200
    assert "Registration number is required" in r.get_data(as_text=True)

def test_invalid_url_is_rejected_and_not_saved(client):
    data = {**VALID, "url": "not-a-url"}
    r = client.post("/", data=data)
    assert r.status_code == 400
    page = client.get("/").get_data(as_text=True)
    assert "Assignment 1" not in page
