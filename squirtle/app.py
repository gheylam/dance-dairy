import calendar as _cal
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.stubs import get_classes


def fmt(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime("%I:%M %p").lstrip("0")


def enrich(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["start_label"] = fmt(r["start_at"]) + " - " + fmt(r["end_at"])
        out.append(d)
    return out


def apply_filters(rows, query="", studio="", day=""):
    q = (query or "").lower()
    out = rows
    if q:
        out = [r for r in out if q in " ".join(
            str(x or "") for x in (r["song"], r["artist"], r["teacher"], r["studio_raw"], r["venue"], r["area"])).lower()]
    if studio:
        out = [r for r in out if r["studio_slug"] == studio]
    if day:
        out = [r for r in out if r["start_at"][:10] == day]
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


def create_app():
    app = FastAPI(title="Klassified")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    tpl = Jinja2Templates(directory="templates")

    @app.get("/api/classes")
    def list_classes():
        return get_classes()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return tpl.TemplateResponse(request, "agenda.html", {"request": request, "classes": enrich(get_classes()),
                                                             "month": build_month(2026, 1)})

    @app.get("/partials/cards", response_class=HTMLResponse)
    def cards(request: Request, query: str = "", studio: str = "", day: str = ""):
        rows = enrich(apply_filters(get_classes(), query, studio, day))
        return tpl.TemplateResponse(request, "partials/cards.html", {"request": request, "classes": rows, "day": day})

    @app.get("/partials/detail/{cid}", response_class=HTMLResponse)
    def detail(request: Request, cid: str):
        rows = [r for r in enrich(get_classes()) if r["id"] == cid]
        if not rows:
            return HTMLResponse("Not found", status_code=404)
        return tpl.TemplateResponse(request, "partials/detail.html", {"request": request, "c": rows[0]})

    return app


app = create_app()
