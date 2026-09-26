from api.stubs import get_classes


def test_stub_contract():
    rows = get_classes()
    assert len(rows) == 10
    required = {"id", "studio_slug", "studio_raw", "teacher", "song", "artist",
                "difficulty", "song_section", "start_at", "end_at", "venue",
                "area", "price_pence", "price_raw", "booking_url", "source_url"}
    for r in rows:
        assert required <= set(r.keys()), f"missing keys in {r.get('id')}"
    slugs = {r["studio_slug"] for r in rows}
    assert {"dgcdance", "lum3x"} <= slugs
