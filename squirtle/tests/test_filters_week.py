from fastapi.testclient import TestClient

from app import create_app

client = TestClient(create_app())


def test_cards_filter_by_song_exact():
    r = client.get("/partials/cards", params={"song": "Zen"})
    assert r.status_code == 200
    assert "Zen" in r.text
    assert "Tate McRae" not in r.text


def test_cards_filter_by_artist_exact():
    r = client.get("/partials/cards", params={"artist": "BTS"})
    assert r.status_code == 200
    assert "Boy With Luv" in r.text
    assert "Zen" not in r.text


def test_cards_filter_by_teacher_exact():
    r = client.get("/partials/cards", params={"teacher": "Caroline"})
    assert r.status_code == 200
    assert "ON" in r.text
    assert "Zen" not in r.text


def test_filter_count_includes_new_facets():
    from app import filter_count

    assert filter_count("", [], [], [], [], "", ["Zen"], ["BTS"], ["Caroline"]) == 3


def test_week_range_derived_from_day():
    from app import build_week_range

    week = build_week_range("2026-01-16")
    assert [d["date"] for d in week] == [
        "2026-01-12",
        "2026-01-13",
        "2026-01-14",
        "2026-01-15",
        "2026-01-16",
        "2026-01-17",
        "2026-01-18",
    ]
    assert [d["selected"] for d in week] == [False, False, False, False, True, False, False]


def test_week_partial_groups_chips():
    r = client.get("/partials/week", params={"day": "2026-01-16"})
    assert r.status_code == 200
    assert "2026-01-16" in r.text
    assert "Zen" in r.text
    assert "data-open" in r.text


def test_home_toggle_has_three_views():
    r = client.get("/")
    assert r.status_code == 200
    assert 'data-view="list"' in r.text
    assert 'data-view="week"' in r.text
    assert 'data-view="month"' in r.text


def test_home_renders_new_filter_groups():
    r = client.get("/")
    assert r.status_code == 200
    assert "Song" in r.text
    assert "Artist" in r.text
    assert "Teacher" in r.text
