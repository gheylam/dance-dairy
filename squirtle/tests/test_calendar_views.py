from fastapi.testclient import TestClient
from app import create_app

client = TestClient(create_app())


def test_view_param_sets_body_view_week():
    r = client.get("/", params={"view": "week"})
    assert r.status_code == 200
    assert '<body data-view="week"' in r.text


def test_view_param_sets_body_view_month():
    r = client.get("/", params={"view": "month"})
    assert r.status_code == 200
    assert '<body data-view="month"' in r.text


def test_week_timegrid_has_hours_and_positioned_events():
    r = client.get("/partials/week", params={"day": "2026-01-16"})
    assert r.status_code == 200
    # hour gutter rows (e.g. 6 AM / 18:00 style labels)
    assert "week-hours" in r.text or "hour-row" in r.text
    # positioned event blocks carry start info for time placement
    assert "data-start" in r.text or "event-block" in r.text


def test_month_nav_has_prev_next():
    r = client.get("/", params={"month": "2026-01"})
    assert r.status_code == 200
    assert 'month=2025-12' in r.text
    assert 'month=2026-02' in r.text


def test_month_cells_show_chips_and_more():
    r = client.get("/", params={"month": "2026-01"})
    assert "month-chip" in r.text or "more-link" in r.text


def test_agenda_groups_by_day_headers():
    r = client.get("/partials/cards")
    assert r.status_code == 200
    assert "day-group" in r.text or "day-header" in r.text
