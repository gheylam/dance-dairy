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


def apply_filters(rows, query="", studio=None, difficulties=None, prices=None, areas=None, day=""):
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
    if day and valid_day(day):
        out = [r for r in out if r["start_at"][:10] == day]
    return out


def filter_count(query="", studio=None, difficulties=None, prices=None, areas=None, day=""):
    studios = [studio] if isinstance(studio, str) else (studio or [])
    n = (1 if query else 0) + len([s for s in studios if s]) + (1 if valid_day(day) else 0)
    for v in (difficulties, prices, areas):
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


def build_month(year, month):
    cal = _cal.Calendar(firstweekday=0)
    by_date = {}
    for r in get_classes():
        d = r["start_at"][:10]
        by_date.setdefault(d, [])
        if r["studio_slug"] not in by_date[d]:
            by_date[d].append(r["studio_slug"])
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        weeks.append([{"day": d.day, "in_month": d.month == month,
                       "date": d.isoformat(), "dots": by_date.get(d.isoformat(), [])}
                      for d in week])
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


def create_app():
    app = FastAPI(title="Klassified")
    app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
    tpl = Jinja2Templates(directory=str(BASE / "templates"))

    @app.get("/api/classes")
    def list_classes(query: str = "", studio: list = Query([]), difficulty: list = Query([]),
                     price: list = Query([]), area: list = Query([]), day: str = ""):
        return enrich(apply_filters(get_classes(), query, studio, difficulty, price, area, day))

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request, query: str = "", studio: list = Query([]),
             difficulty: list = Query([]), price: list = Query([]),
             area: list = Query([]), day: str = "", month: str = "2026-01"):
        all_rows = get_classes()
        rows = enrich(apply_filters(all_rows, query, studio, difficulty, price, area, day))
        y, m = parse_month(month)
        display_day = day if valid_day(day) else "2026-01-16"
        wk = build_week(display_day)
        week_label = f"Week of {wk[0]['date']} to {wk[6]['date']}"
        first = all_rows[0] if all_rows else {}
        return tpl.TemplateResponse(request, "agenda.html", {"request": request, "classes": rows,
                                                             "month": build_month(y, m),
                                                             "week": wk, "week_label": week_label,
                                                             "stale_label": stale_label(first.get("scraped_at", "2026-01-16T10:00:00+00:00")),
                                                             "query": query, "studios": as_list(studio),
                                                             "difficulties": as_list(difficulty),
                                                             "prices": as_list(price), "areas": as_list(area),
                                                             "day": day, "active_month": f"{y:04d}-{m:02d}",
                                                             "fcount": filter_count(query, studio, difficulty, price, area, day)})

    @app.get("/partials/cards", response_class=HTMLResponse)
    def cards(request: Request, query: str = "", studio: list = Query([]),
              difficulty: list = Query([]), price: list = Query([]),
              area: list = Query([]), day: str = ""):
        rows = enrich(apply_filters(get_classes(), query, studio, difficulty, price, area, day))
        return tpl.TemplateResponse(request, "partials/cards.html", {"request": request, "classes": rows,
                                                                     "day": day, "query": query,
                                                                     "studios": as_list(studio),
                                                                     "difficulties": as_list(difficulty),
                                                                     "prices": as_list(price),
                                                                     "areas": as_list(area)})

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
