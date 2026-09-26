from fastapi.testclient import TestClient
from app import create_app

client = TestClient(create_app())


def test_home_has_cards_and_booking_links():
    r = client.get("/")
    assert r.status_code == 200
    assert "Tate McRae" in r.text
    assert 'target="_blank"' in r.text
    assert "Last updated" in r.text


def test_cards_partial_filters_by_query():
    r = client.get("/partials/cards", params={"query": "BTS"})
    assert r.status_code == 200
    assert "Boy With Luv" in r.text
    assert "Zen" not in r.text


def test_cards_partial_empty_state():
    r = client.get("/partials/cards", params={"query": "zzz-no-match"})
    assert "No classes found" in r.text
    assert "Clear filters" in r.text


def test_day_filter_and_empty_day():
    r = client.get("/partials/cards", params={"day": "2026-01-16"})
    assert "Tate McRae" in r.text
    r2 = client.get("/partials/cards", params={"day": "2026-01-19"})
    assert "No classes today" in r2.text
