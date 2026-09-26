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


def test_week_view_hides_duplicate_top_day_strip():
    css = open("static/style.css").read()
    assert 'data-view="week"] .week' in css
    assert 'data-view="month"] .week' in css


def test_week_grid_autoscrolls_to_events():
    js = open("static/app.js").read()
    assert "week-timegrid" in js
    assert "scrollTop" in js


def test_static_assets_are_versioned_for_cache_busting():
    r = client.get("/")
    assert "/static/style.css?v=" in r.text
    assert "/static/app.js?v=" in r.text


def test_layout_caps_overlap_columns_for_readability():
    from app import layout_day_events

    rows = [{"id": f"e{i}", "studio_slug": "lum3x", "start_at": f"2026-01-16T18:{i*5:02d}:00+00:00",
             "end_at": "2026-01-16T20:00:00+00:00", "song": "S", "artist": None,
             "teacher": None, "venue": "V", "area": "A", "difficulty": "All Levels",
             "song_section": None, "price_pence": 1000, "booking_url": "u", "source_url": "u",
             "scraped_at": "2026-01-16T10:00:00+00:00", "studio_raw": "LUM3X"} for i in range(6)]
    laid = layout_day_events(rows)
    shown = laid["events"]
    assert shown
    assert max(p["cols"] for p in shown) <= 3
    assert min(p["width_pct"] for p in shown) >= 50
    assert laid["overflow"] == 3


def test_layout_identical_start_never_fully_occluded():
    from app import layout_day_events

    base = {"studio_slug": "lum3x", "start_at": "2026-01-16T19:00:00+00:00",
            "end_at": "2026-01-16T21:00:00+00:00", "song": "S", "artist": None,
            "teacher": None, "venue": "V", "area": "A", "difficulty": "All Levels",
            "song_section": None, "price_pence": 1000, "booking_url": "u", "source_url": "u",
            "scraped_at": "2026-01-16T10:00:00+00:00", "studio_raw": "LUM3X"}
    rows = [dict(base, id=f"e{i}") for i in range(6)]
    laid = layout_day_events(rows)
    corners = [(p["top_px"], p["left_px"]) for p in laid["events"]]
    assert len(corners) == len(set(corners))
    assert laid["overflow"] == 3


def test_real_stub_day_has_no_hidden_event():
    from app import layout_day_events
    from api.stubs import get_classes

    rows = [r for r in get_classes() if r["start_at"][:10] == "2026-01-16"]
    laid = layout_day_events(rows)
    corners = [(p["top_px"], p["left_px"]) for p in laid["events"]]
    assert len(corners) == len(set(corners))
    assert laid["overflow"] == 3


def test_week_grid_shows_overflow_badge_and_agenda_lists_all():
    r = client.get("/partials/week", params={"day": "2026-01-16"})
    assert "more" in r.text
    # agenda below the grid must still list every class, including overflowed ones
    assert "Lucifer" in r.text
    assert "Boy With Luv" in r.text


def test_week_partial_has_responsive_agenda_and_grid():
    r = client.get("/partials/week", params={"day": "2026-01-16"})
    assert r.status_code == 200
    assert 'class="week-timegrid"' in r.text
    assert 'class="week-agenda"' in r.text
    assert "day-group" in r.text


def test_layout_staggers_overlaps_without_full_occlusion():
    from app import layout_day_events

    rows = [{"id": f"e{i}", "studio_slug": "lum3x", "start_at": f"2026-01-16T18:{i*5:02d}:00+00:00",
             "end_at": "2026-01-16T20:00:00+00:00", "song": "S", "artist": None,
             "teacher": None, "venue": "V", "area": "A", "difficulty": "All Levels",
             "song_section": None, "price_pence": 1000, "booking_url": "u", "source_url": "u",
             "scraped_at": "2026-01-16T10:00:00+00:00", "studio_raw": "LUM3X"} for i in range(6)]
    corners = [(p["top_px"], p["left_px"]) for p in layout_day_events(rows)["events"]]
    assert len(corners) == len(set(corners))


def test_week_agenda_skips_days_without_classes():
    r = client.get("/partials/week", params={"day": "2026-01-16"})
    assert 'data-date="2026-01-12"' not in r.text
    assert "0 classes" not in r.text
    assert "No classes this day" not in r.text
    assert 'data-date="2026-01-16"' in r.text


def test_css_pins_light_color_scheme():
    css = open("static/style.css").read()
    assert "color-scheme: light" in css
    assert "background: #fff" in css


def test_month_counts_every_class_not_just_studios():
    from app import build_month

    jan16 = [d for w in build_month(2026, 1) for d in w if d["date"] == "2026-01-16"][0]
    assert jan16["total"] == 7
    assert len(jan16["classes"]) == 7
    assert len(jan16["dots"]) == 5
    assert jan16["classes"][0]["id"] == "haven-exes"


def test_filters_collapsed_by_default():
    r = client.get("/")
    assert 'id="filtersSection" hidden' in r.text


def test_day_count_pluralized():
    one = client.get("/partials/cards", params={"day": "2026-01-13"})
    assert "1 class" in one.text
    assert "1 classes" not in one.text
    many = client.get("/partials/cards", params={"day": "2026-01-16"})
    assert "7 classes" in many.text


def test_card_time_and_duration_not_run_together():
    r = client.get("/partials/cards", params={"day": "2026-01-13"})
    assert "PM1h" not in r.text
    assert "</time> <span>" in r.text


def test_level_and_song_section_not_run_together():
    r = client.get("/partials/cards", params={"day": "2026-01-14"})
    assert "Last Chorus" in r.text
    # level span and song-section span must be separated in markup so text is not glued
    assert "</span><span>" not in r.text.split('class="level"')[1][:200]


def test_view_links_preserve_active_filters():
    r = client.get("/", params={"query": "BTS", "studio": "lum3x"})
    toggle = r.text.split('id="viewToggle"')[1].split("</div>")[0]
    assert "query=BTS" in toggle
    assert "studio=lum3x" in toggle
    assert toggle.count("query=BTS") >= 3


def test_month_nav_preserves_active_filters():
    r = client.get("/", params={"month": "2026-01", "query": "BTS"})
    nav = r.text.split('class="month-nav"')[1].split("</div>")[0]
    assert "query=BTS" in nav
    assert "month=2025-12" in nav and "month=2026-02" in nav


def test_min_touch_targets_for_month_controls():
    css = open("static/style.css").read()
    chip = css.split(".month-chip {")[1].split("}")[0]
    assert "min-height: 44px" in chip
    more = css.split(".more-link {")[1].split("}")[0]
    assert "min-height: 44px" in more


def test_no_grid_role_without_keyboard_model():
    r = client.get("/partials/week", params={"day": "2026-01-16"})
    assert 'role="grid"' not in r.text


def test_build_hours_can_start_before_six():
    from app import build_hours

    hours = build_hours(5, 23)
    assert hours[0] == {"hour": 5, "label": "5 AM"}


def test_early_class_aligns_to_data_driven_start():
    from app import layout_day_events

    row = {"id": "early", "studio_slug": "lum3x", "start_at": "2026-01-16T05:00:00+00:00",
           "end_at": "2026-01-16T06:00:00+00:00", "song": "S", "artist": None,
           "teacher": None, "venue": "V", "area": "A", "difficulty": "All Levels",
           "song_section": None, "price_pence": 1000, "booking_url": "u", "source_url": "u",
           "scraped_at": "2026-01-16T10:00:00+00:00", "studio_raw": "LUM3X"}
    laid = layout_day_events([row], week_hour_start=5)
    assert laid["events"][0]["top_px"] == 0

