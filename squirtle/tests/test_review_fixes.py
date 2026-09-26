from fastapi.testclient import TestClient
from app import create_app, filter_count, stale_label

client = TestClient(create_app())


def test_today_link_preserves_all_filters():
    t = client.get("/partials/cards", params={"day": "2026-01-19", "query": "BTS",
        "difficulty": "Beginners", "price": "11-15", "area": "North London"}).text
    assert "Today" in t
    for bit in ["query=BTS", "difficulty=Beginners", "price=11-15", "area=North"]:
        assert bit in t, bit


def test_filter_count_ignores_invalid_day():
    assert filter_count(query="", day="not-a-date") == 0


def test_detail_shows_range_and_duration():
    t = client.get("/partials/detail/haven-exes").text
    assert "6:00 PM - 8:00 PM" in t and "2h" in t
    assert " · " not in t


def test_stale_label_helper():
    assert stale_label("2026-01-16T10:00:00+00:00", "2026-01-16T12:00:00+00:00") == "Last updated 2h ago"
    assert stale_label("2026-01-16T10:00:00+00:00", "2026-01-16T10:30:00+00:00") == "Last updated 30m ago"


def test_month_aria_label_dynamic():
    assert "January 2026 calendar" not in client.get("/", params={"month": "2026-02"}).text


def test_js_history_and_a11y():
    js = open("static/app.js").read()
    assert "replaceState" in js
    assert "closeDetail" not in js
    assert "encodeURIComponent" in js
    assert "aria-pressed" in js and "aria-expanded" in js
    assert 'p.set("day"' in js or "p.set('day'" in js


def test_home_empty_stubs_no_500(monkeypatch):
    import app as appmod
    monkeypatch.setattr(appmod, "get_classes", lambda: [])
    c = TestClient(appmod.create_app())
    r = c.get("/")
    assert r.status_code == 200
    assert "No classes found" in r.text
