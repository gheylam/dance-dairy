const q = document.getElementById("q");
const results = document.getElementById("results");
const dialog = document.getElementById("detail");
const detailBody = document.getElementById("detailBody");
let t;
let lastOpener = null;

async function loadCards(url) {
  const weekUrl = url.replace("/partials/cards", "/partials/week");
  const weekWrap = document.getElementById("weekWrap");
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(String(r.status));
    results.querySelector(".netfail")?.remove();
    results.innerHTML = await r.text();
  } catch {
    if (!results.querySelector(".netfail")) {
      results.insertAdjacentHTML("afterbegin",
        "<p class=\"netfail\">Couldn't refresh — showing saved list.</p>");
    }
  }
  if (!weekWrap) return;
  try {
    const r = await fetch(weekUrl);
    if (!r.ok) throw new Error(String(r.status));
    weekWrap.querySelector(".netfail")?.remove();
    weekWrap.innerHTML = await r.text();
  } catch {
    if (!weekWrap.querySelector(".netfail")) {
      weekWrap.insertAdjacentHTML("afterbegin",
        "<p class=\"netfail\">Couldn't refresh — showing saved week.</p>");
    }
  }
}

function currentFilterParams() {
  const p = new URLSearchParams();
  document.querySelectorAll('#filters input[type="checkbox"]:checked').forEach((c) => {
    p.append(c.name, c.value);
  });
  document.querySelectorAll(".week button[aria-current]").forEach((b) => {
    if (b.dataset.day) p.append("day", b.dataset.day);
  });
  return p;
}

async function openDetail(id, opener) {
  const r = await fetch("/partials/detail/" + encodeURIComponent(id));
  if (!r.ok) return;
  lastOpener = opener || null;
  detailBody.innerHTML = await r.text();
  dialog.showModal();
  history.pushState({ cid: id }, "", "#class=" + encodeURIComponent(id));
}

dialog?.addEventListener("close", () => {
  if (lastOpener && document.contains(lastOpener)) lastOpener.focus();
  lastOpener = null;
  if (location.hash.startsWith("#class=")) history.replaceState({}, "", location.pathname + location.search);
});

window.addEventListener("popstate", () => {
  if (dialog.open) dialog.close();
});

q?.addEventListener("input", () => {
  clearTimeout(t);
  t = setTimeout(() => {
    const p = currentFilterParams();
    p.delete("query");
    if (q.value) p.set("query", q.value);
    loadCards("/partials/cards?" + p.toString());
  }, 300);
});

results?.addEventListener("click", async (e) => {
  if (e.target.closest("#clearFilters")) {
    q.value = "";
    document.querySelectorAll('#filters input[type="checkbox"]').forEach((c) => { c.checked = false; });
    document.querySelectorAll(".week button").forEach((b) => b.removeAttribute("aria-current"));
    await loadCards("/partials/cards");
    return;
  }
  const opener = e.target.closest("[data-open]");
  const card = e.target.closest(".card");
  if (opener && card) {
    await openDetail(opener.dataset.open, opener);
    return;
  }
  if (!card || e.target.closest("a")) return;
  await openDetail(card.dataset.id, card);
});

async function dayClick(e) {
  const btn = e.target.closest("button[data-day]");
  if (!btn) return;
  document.querySelectorAll(".week button").forEach((b) => b.removeAttribute("aria-current"));
  const weekBtn = document.querySelector('.week button[data-day="' + btn.dataset.day + '"]');
  if (weekBtn) weekBtn.setAttribute("aria-current", "true");
  const p = currentFilterParams();
  p.delete("day");
  if (btn.dataset.day) p.set("day", btn.dataset.day);
  await loadCards("/partials/cards?" + p.toString());
}

document.querySelector(".week")?.addEventListener("click", dayClick);
document.querySelector(".month")?.addEventListener("click", dayClick);
document.getElementById("weekWrap")?.addEventListener("click", dayClick);
document.getElementById("weekWrap")?.addEventListener("click", async (e) => {
  const opener = e.target.closest("[data-open]");
  if (!opener) return;
  await openDetail(opener.dataset.open, opener);
});
document.getElementById("filtersBtn")?.addEventListener("click", (e) => {
  const sec = document.getElementById("filtersSection");
  sec?.toggleAttribute("hidden");
  e.currentTarget.setAttribute("aria-expanded", String(!sec?.hasAttribute("hidden")));
});
document.getElementById("viewToggle")?.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-view]");
  if (!btn) return;
  e.preventDefault();
  const view = btn.dataset.view;
  document.body.dataset.view = view;
  document.querySelectorAll("#viewToggle [data-view]").forEach((b) => {
    b.setAttribute("aria-pressed", String(b === btn));
  });
  document.getElementById("results")?.setAttribute("aria-hidden", String(view !== "list"));
  document.getElementById("weekWrap")?.setAttribute("aria-hidden", String(view !== "week"));
  document.querySelector(".month-wrap")?.setAttribute("aria-hidden", String(view !== "month"));
  const url = new URL(location.href);
  url.searchParams.set("view", view);
  history.replaceState({}, "", url.toString());
});

if (location.hash.startsWith("#class=")) {
  const deepId = location.hash.slice("#class=".length + 1);
  if (/^[A-Za-z0-9-]+$/.test(deepId)) openDetail(deepId, null);
}

function scrollWeekToEvents() {
  const grid = document.querySelector(".week-timegrid");
  if (!grid) return;
  const first = grid.querySelector(".event-block");
  const dayCol = first ? first.closest(".wday-col") : grid.querySelector(".wday-col");
  if (first) grid.scrollTop = Math.max(0, first.offsetTop - 48);
  if (dayCol && grid.scrollWidth > grid.clientWidth) {
    dayCol.scrollIntoView({ block: "nearest", inline: "center" });
  }
}

scrollWeekToEvents();
document.getElementById("viewToggle")?.addEventListener("click", () => setTimeout(scrollWeekToEvents, 0));
