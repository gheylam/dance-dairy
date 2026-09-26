from fastapi.testclient import TestClient
from app import create_app, fmt

client = TestClient(create_app())


def test_home_ssr_applies_studio_filter():
    r = client.get("/", params={"studio": "lum3x"})
    assert r.status_code == 200
    results = r.text.split('<main id="results">')[1].split("</main>")[0]
    assert "Teeth" in results
    assert "Zen" not in results


def test_home_ssr_empty_day():
    r = client.get("/", params={"day": "2026-01-19"})
    assert "No classes today" in r.text


def test_multi_studio_or_within_group():
    r = client.get("/partials/cards", params=[("studio", "dgcdance"), ("studio", "lum3x")])
    assert "Boy With Luv" in r.text
    assert "Teeth" in r.text


def test_cards_have_keyboard_open_control():
    r = client.get("/")
    results = r.text.split('<main id="results">')[1].split("</main>")[0]
    n_cards = results.count("<article")
    assert n_cards > 0
    assert results.count('data-open=') == n_cards


def test_fmt_converts_to_europe_london():
    assert fmt("2026-01-16T18:30:00+01:00") == "5:30 PM"


def test_month_days_are_buttons():
    r = client.get("/")
    assert r.text.count('data-day="2026-01-16"') >= 2


def test_filter_form_targets_ssr_and_count_renders():
    r = client.get("/", params={"studio": "lum3x"})
    assert 'action="/"' in r.text
    assert "(1)" in r.text


def test_filter_section_toggle_target():
    r = client.get("/")
    assert 'id="filtersSection"' in r.text


def test_refresh_failure_copy_pinned():
    r = client.get("/static/app.js")
    assert "Couldn't refresh" in r.text
