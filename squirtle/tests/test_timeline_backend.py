from app import enrich, apply_filters, build_week, price_bucket, area_to_location, create_app
from fastapi.testclient import TestClient


def test_enrich_adds_duration():
    rows = enrich([{"start_at": "2026-01-16T18:00:00+00:00", "end_at": "2026-01-16T20:00:00+00:00"}])
    assert rows[0]["duration_min"] == 120
    assert rows[0]["duration_label"] == "2h"
    assert rows[0]["start_label"] == "6:00 PM"
    assert rows[0]["end_label"] == "8:00 PM"


def test_price_bucket_edges():
    assert price_bucket(1000) == "0-10"
    assert price_bucket(1500) == "11-15"
    assert price_bucket(1800) == "16-20"
    assert price_bucket(None) is None


def test_area_mapping():
    assert area_to_location("Islington") == "North London"
    assert area_to_location("Kings Cross") == "Central London"
    assert area_to_location("Moon") == "Outside London"


def test_filters_difficulty_price_area():
    from api.stubs import get_classes
    rows = apply_filters(get_classes(), difficulties=["Beginners"])
    assert rows and all(r["difficulty"] == "Beginners" for r in rows)
    rows = apply_filters(get_classes(), prices=["11-15"])
    assert rows and all(price_bucket(r["price_pence"]) == "11-15" for r in rows)
    rows = apply_filters(get_classes(), areas=["North London"])
    assert any(r["id"] == "dgc-on" for r in rows)


def test_bad_day_ignored():
    from api.stubs import get_classes
    assert len(apply_filters(get_classes(), day="not-a-date")) == 10


def test_api_params_parity():
    c = TestClient(create_app())
    r = c.get("/api/classes", params={"query": "BTS", "difficulty": "Beginners"})
    assert r.status_code == 200
    assert all("BTS" in (x.get("song") or "") or "BTS" in (x.get("artist") or "") or "Beginners" == x["difficulty"] for x in r.json())


def test_week_builder():
    w = build_week("2026-01-16")
    assert len(w) == 7 and sum(1 for d in w if d["selected"]) == 1
    assert w[4]["date"] == "2026-01-16"
