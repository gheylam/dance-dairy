from fastapi.testclient import TestClient
from app import create_app

client = TestClient(create_app())


def test_header_has_search_toggle_filters():
    r = client.get("/")
    assert r.status_code == 200
    assert 'id="q"' in r.text and "Filters" in r.text and "viewToggle" in r.text


def test_timeline_gutter_and_duration():
    r = client.get("/partials/cards", params={"day": "2026-01-16"})
    assert 'class="tl"' in r.text or "gutter" in r.text
    assert "2h" in r.text
