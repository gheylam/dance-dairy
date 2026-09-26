def test_js_history_and_toggle():
    from pathlib import Path
    js = (Path(__file__).parent.parent / "static" / "app.js").read_text()
    assert "#class=" in js
    assert "popstate" in js
    assert "data-view" in js
    assert "URLSearchParams" in js
    assert "aria-hidden" in js
