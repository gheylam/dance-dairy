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


def test_month_nav_and_dots():
    r = client.get("/")
    assert 'name="month"' in r.text
    assert client.get("/", params={"month": "2026-13"}).status_code == 200


def test_filter_sheet_groups():
    t = client.get("/").text
    for g in ["Studio", "Pricing", "Difficulty", "Location"]:
        assert g in t


def test_detail_staleness_and_today_keeps_query():
    assert "Last updated" in client.get("/partials/detail/haven-exes").text
    t = client.get("/partials/cards", params={"day": "2026-01-19", "query": "BTS"}).text
    assert "Today" in t and "query=BTS" in t
