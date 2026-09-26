def test_js_history_and_toggle():
    js = open("static/app.js").read()
    assert "#class=" in js
    assert "popstate" in js
    assert "data-view" in js
    assert "URLSearchParams" in js
