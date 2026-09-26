import calendar as _cal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from zoneinfo import ZoneInfo
from api.stubs import get_classes

LONDON = ZoneInfo("Europe/London")
BASE = Path(__file__).parent


def fmt(iso: str) -> str:
    return datetime.fromisoformat(iso).astimezone(LONDON).strftime("%I:%M %p").lstrip("0")


def duration_label(mins: int) -> str:
    h, m = divmod(mins, 60)
    if h and m:
        return f"{h}h {m}m"
    return f"{h}h" if h else f"{m}m"


def price_bucket(pence):
    if pence is None:
        return None
    pounds = pence / 100
    if pounds <= 10:
        return "0-10"
    if pounds <= 15:
        return "11-15"
    if pounds <= 20:
        return "16-20"
    if pounds <= 25:
        return "21-25"
    return "26+"


AREA_MAP = {"Islington": "North London", "Kings Cross": "Central London",
            "Holborn": "Central London", "Central London": "Central London",
            "East London": "East London", "South London": "South London"}


def area_to_location(area):
    return AREA_MAP.get(area or "", "Outside London")


def valid_day(day: str) -> bool:
    return isinstance(day, str) and len(day) == 10 and day[4] == "-" and day[7] == "-"


def stale_label(iso: str, now: Optional[str] = None) -> str:
    start = datetime.fromisoformat(iso)
    ref = datetime.fromisoformat(now) if now else datetime.now(start.tzinfo)
    mins = max(0, int((ref - start).total_seconds() // 60))
    if mins < 60:
        return f"Last updated {mins}m ago"
    return f"Last updated {mins // 60}h ago"


def enrich(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["start_label"] = fmt(r["start_at"])
        d["end_label"] = fmt(r["end_at"])
        mins = int((datetime.fromisoformat(r["end_at"]) - datetime.fromisoformat(r["start_at"])).total_seconds() // 60)
        d["duration_min"] = mins
        d["duration_label"] = duration_label(mins)
        out.append(d)
    return out


def apply_filters(rows, query="", studio=None, difficulties=None, prices=None, areas=None, day="",
                  songs=None, artists=None, teachers=None):
    q = (query or "").lower()
    out = rows
    if q:
        out = [r for r in out if q in " ".join(
            str(x or "") for x in (r["song"], r["artist"], r["teacher"], r["studio_raw"], r["venue"], r["area"])).lower()]
    studios = [studio] if isinstance(studio, str) else (studio or [])
    studios = [s for s in studios if s]
    if studios:
        out = [r for r in out if r["studio_slug"] in studios]
    diffs = [difficulties] if isinstance(difficulties, str) else (difficulties or [])
    diffs = [d for d in diffs if d]
    if diffs:
        out = [r for r in out if r.get("difficulty") in diffs]
    prs = [prices] if isinstance(prices, str) else (prices or [])
    prs = [p for p in prs if p]
    if prs:
        out = [r for r in out if price_bucket(r.get("price_pence")) in prs]
    ars = [areas] if isinstance(areas, str) else (areas or [])
    ars = [a for a in ars if a]
    if ars:
        out = [r for r in out if area_to_location(r.get("area")) in ars]
    sgs = [songs] if isinstance(songs, str) else (songs or [])
    sgs = [s for s in sgs if s]
    if sgs:
        out = [r for r in out if r.get("song") in sgs]
    ats = [artists] if isinstance(artists, str) else (artists or [])
    ats = [a for a in ats if a]
    if ats:
        out = [r for r in out if r.get("artist") in ats]
    tch = [teachers] if isinstance(teachers, str) else (teachers or [])
    tch = [t for t in tch if t]
    if tch:
        out = [r for r in out if r.get("teacher") in tch]
    if day and valid_day(day):
        out = [r for r in out if r["start_at"][:10] == day]
    return out


def filter_count(query="", studio=None, difficulties=None, prices=None, areas=None, day="",
                 songs=None, artists=None, teachers=None):
    studios = [studio] if isinstance(studio, str) else (studio or [])
    n = (1 if query else 0) + len([s for s in studios if s]) + (1 if valid_day(day) else 0)
    for v in (difficulties, prices, areas, songs, artists, teachers):
        vals = [v] if isinstance(v, str) else (v or [])
        n += len([x for x in vals if x])
    return n


def as_list(v):
    return [v] if isinstance(v, str) else (v or [])


def build_week(active_day="2026-01-16"):
    try:
        base = datetime.fromisoformat(active_day).date()
    except Exception:
        base = datetime.fromisoformat("2026-01-16").date()
        active_day = "2026-01-16"
    monday = base - timedelta(days=base.weekday())
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    out = []
    for i in range(7):
        d = monday + timedelta(days=i)
        iso = d.isoformat()
        out.append({"date": iso, "dow": names[i], "day": d.day, "selected": iso == active_day})
    return out


def build_week_range(active_day="2026-01-16"):
    return build_week(active_day)


def shift_day(day, delta):
    try:
        return (datetime.fromisoformat(day).date() + timedelta(days=delta)).isoformat()
    except Exception:
        return "2026-01-16"


def distinct(field):
    return sorted({r.get(field) for r in get_classes() if r.get(field)})


def group_by_day(rows):
    by_date = {}
    for r in rows:
        by_date.setdefault(r["start_at"][:10], []).append(r)
    return by_date


def build_month(year, month):
    cal = _cal.Calendar(firstweekday=0)
    enriched = {r["id"]: r for r in enrich(get_classes())}
    by_date = {}
    for r in get_classes():
        by_date.setdefault(r["start_at"][:10], []).append(r)
    for lst in by_date.values():
        lst.sort(key=lambda r: r["start_at"])
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for d in week:
            iso = d.isoformat()
            items = by_date.get(iso, [])
            studios = []
            for x in items:
                if x["studio_slug"] not in studios:
                    studios.append(x["studio_slug"])
            row.append({"day": d.day, "in_month": d.month == month,
                        "date": iso, "dots": studios,
                        "classes": [{"id": x["id"], "song": x.get("song"),
                                     "start_label": enriched[x["id"]]["start_label"],
                                     "studio_slug": x["studio_slug"]} for x in items],
                        "total": len(items)})
        weeks.append(row)
    return weeks


def parse_month(value):
    try:
        y, m = value.split("-")
        y, m = int(y), int(m)
        if 1 <= m <= 12:
            return y, m
    except Exception:
        pass
    return 2026, 1


VALID_VIEWS = ("list", "week", "month")


def valid_view(v: str) -> str:
    return v if v in VALID_VIEWS else "list"


def shift_month(value: str, delta: int) -> str:
    y, m = parse_month(value)
    m += delta
    while m < 1:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return f"{y:04d}-{m:02d}"


WEEK_HOUR_START = 6
WEEK_HOUR_END = 23
PX_PER_HOUR = 48


def build_hours():
    out = []
    for h in range(WEEK_HOUR_START, WEEK_HOUR_END + 1):
        suffix = "AM" if h < 12 else "PM"
        hh = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
        if h == 12:
            hh = 12
        if h == 0:
            hh = 12
        out.append({"hour": h, "label": f"{hh} {suffix}"})
    return out


def _minutes(iso: str) -> int:
    dt = datetime.fromisoformat(iso).astimezone(LONDON)
    return dt.hour * 60 + dt.minute


MAX_EVENT_COLS = 3
STAGGER_PCT = 18


def layout_day_events(rows):
    items = sorted(enrich(rows), key=lambda r: r["start_at"])
    placed = []
    active = []
    for r in items:
        s = _minutes(r["start_at"])
        e = _minutes(r["end_at"])
        active = [a for a in active if a["_end"] > s]
        used = {a["col"] for a in active}
        col = 0
        while col in used:
            col += 1
        entry = dict(r)
        entry["col"] = min(col, MAX_EVENT_COLS - 1)
        entry["_end"] = e
        active.append(entry)
        placed.append(entry)
    for entry in placed:
        s = _minutes(entry["start_at"])
        e = _minutes(entry["end_at"])
        overlap = [o for o in placed
                   if _minutes(o["start_at"]) < e and s < _minutes(o["end_at"])]
        entry["cols"] = min(MAX_EVENT_COLS, max(1, max(o["col"] for o in overlap) + 1))
        top = max(0, (s - WEEK_HOUR_START * 60) * PX_PER_HOUR / 60)
        h = max(24, (e - s) * PX_PER_HOUR / 60)
        entry["top_px"] = int(top)
        entry["height_px"] = int(h)
        entry["left_px"] = entry["col"] * 14
        entry["left_pct"] = entry["col"] * STAGGER_PCT
        entry["width_pct"] = 100 - entry["left_pct"]
    return placed


def sorted_day_groups(rows):
    by_date = group_by_day(enrich(rows))
    out = []
    for d in sorted(by_date):
        try:
            label = datetime.fromisoformat(d).strftime("%a %b %d")
        except Exception:
            label = d
        out.append({"date": d, "label": label,
                    "classes": sorted(by_date[d], key=lambda r: r["start_at"])})
    return out


def create_app():
    app = FastAPI(title="Klassified")
    app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
    tpl = Jinja2Templates(directory=str(BASE / "templates"))

    def asset_v() -> str:
        try:
            files = [(BASE / "static" / n).stat().st_mtime
                     for n in ("style.css", "app.js")]
            return str(int(max(files)))
        except Exception:
            return "1"

    tpl.env.globals["asset_v"] = asset_v

    @app.get("/api/classes")
    def list_classes(query: str = "", studio: list = Query([]), difficulty: list = Query([]),
                     price: list = Query([]), area: list = Query([]), day: str = "",
                     song: list = Query([]), artist: list = Query([]), teacher: list = Query([])):
        return enrich(apply_filters(get_classes(), query, studio, difficulty, price, area, day,
                                    song, artist, teacher))

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request, query: str = "", studio: list = Query([]),
             difficulty: list = Query([]), price: list = Query([]),
             area: list = Query([]), day: str = "", month: str = "2026-01",
             song: list = Query([]), artist: list = Query([]), teacher: list = Query([]),
             view: str = "list"):
        all_rows = get_classes()
        rows = enrich(apply_filters(all_rows, query, studio, difficulty, price, area, day,
                                    song, artist, teacher))
        y, m = parse_month(month)
        active_month = f"{y:04d}-{m:02d}"
        display_day = day if valid_day(day) else "2026-01-16"
        wk = build_week(display_day)
        week_label = f"Week of {wk[0]['date']} to {wk[6]['date']}"
        wrange = build_week_range(display_day)
        first = all_rows[0] if all_rows else {}
        week_by_day = {}
        for d in wrange:
            week_by_day[d["date"]] = layout_day_events(
                [r for r in rows if r["start_at"][:10] == d["date"]])
        return tpl.TemplateResponse(request, "agenda.html", {"request": request, "classes": rows,
                                                             "month": build_month(y, m),
                                                             "week": wk, "week_label": week_label,
                                                             "week_range": wrange,
                                                             "week_by_day": week_by_day,
                                                             "week_hours": build_hours(),
                                                             "classes_by_day": group_by_day(rows),
                                                             "day_groups": sorted_day_groups(rows),
                                                             "prev_day": shift_day(display_day, -7),
                                                             "next_day": shift_day(display_day, 7),
                                                             "prev_month": shift_month(active_month, -1),
                                                             "next_month": shift_month(active_month, 1),
                                                             "stale_label": stale_label(first.get("scraped_at", "2026-01-16T10:00:00+00:00")),
                                                             "query": query, "studios": as_list(studio),
                                                             "difficulties": as_list(difficulty),
                                                             "prices": as_list(price), "areas": as_list(area),
                                                             "songs": as_list(song), "artists": as_list(artist),
                                                             "teachers": as_list(teacher),
                                                             "song_list": distinct("song"),
                                                             "artist_list": distinct("artist"),
                                                             "teacher_list": distinct("teacher"),
                                                             "day": day, "active_month": active_month,
                                                             "view": valid_view(view),
                                                             "fcount": filter_count(query, studio, difficulty, price, area, day,
                                                                                    song, artist, teacher)})

    @app.get("/partials/cards", response_class=HTMLResponse)
    def cards(request: Request, query: str = "", studio: list = Query([]),
              difficulty: list = Query([]), price: list = Query([]),
              area: list = Query([]), day: str = "",
              song: list = Query([]), artist: list = Query([]), teacher: list = Query([])):
        rows = enrich(apply_filters(get_classes(), query, studio, difficulty, price, area, day,
                                    song, artist, teacher))
        return tpl.TemplateResponse(request, "partials/cards.html", {"request": request, "classes": rows,
                                                                     "day_groups": sorted_day_groups(rows),
                                                                     "day": day, "query": query,
                                                                     "studios": as_list(studio),
                                                                     "difficulties": as_list(difficulty),
                                                                     "prices": as_list(price),
                                                                     "areas": as_list(area),
                                                                     "songs": as_list(song),
                                                                     "artists": as_list(artist),
                                                                     "teachers": as_list(teacher)})

    @app.get("/partials/week", response_class=HTMLResponse)
    def week(request: Request, query: str = "", studio: list = Query([]),
             difficulty: list = Query([]), price: list = Query([]),
             area: list = Query([]), day: str = "",
             song: list = Query([]), artist: list = Query([]), teacher: list = Query([])):
        rows = enrich(apply_filters(get_classes(), query, studio, difficulty, price, area, "",
                                    song, artist, teacher))
        display_day = day if valid_day(day) else "2026-01-16"
        wrange = build_week_range(display_day)
        week_by_day = {}
        for d in wrange:
            week_by_day[d["date"]] = layout_day_events(
                [r for r in rows if r["start_at"][:10] == d["date"]])
        return tpl.TemplateResponse(request, "partials/week.html", {"request": request,
                                                                    "week_range": wrange,
                                                                    "week_by_day": week_by_day,
                                                                    "week_hours": build_hours(),
                                                                    "classes_by_day": group_by_day(rows),
                                                                    "prev_day": shift_day(display_day, -7),
                                                                    "next_day": shift_day(display_day, 7)})

    @app.get("/partials/detail/{cid}", response_class=HTMLResponse)
    def detail(request: Request, cid: str):
        rows = [r for r in enrich(get_classes()) if r["id"] == cid]
        if not rows:
            return HTMLResponse("Not found", status_code=404)
        c = rows[0]
        return tpl.TemplateResponse(request, "partials/detail.html", {"request": request, "c": c,
            "stale_label": stale_label(c.get("scraped_at", "2026-01-16T10:00:00+00:00"))})

    return app


app = create_app()
