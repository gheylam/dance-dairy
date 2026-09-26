from fastapi.testclient import TestClient
from app import create_app, build_month

client = TestClient(create_app())


def test_month_grid_jan_2026():
    weeks = build_month(2026, 1)
    assert len(weeks) in (5, 6)
    assert all(len(w) == 7 for w in weeks)
    jan16 = [d for w in weeks for d in w if d["date"] == "2026-01-16"][0]
    assert jan16["in_month"] is True
    assert len(jan16["dots"]) >= 3


def test_detail_modal():
    r = client.get("/partials/detail/haven-exes")
    assert r.status_code == 200
    assert "Tate McRae" in r.text
    assert "source" in r.text.lower()


def test_detail_404():
    r = client.get("/partials/detail/nope")
    assert r.status_code == 404
