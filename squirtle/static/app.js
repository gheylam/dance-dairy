const q = document.getElementById("q");
const results = document.getElementById("results");
const dialog = document.getElementById("detail");
const detailBody = document.getElementById("detailBody");
let t;
let lastOpener = null;

async function loadCards(url) {
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
}

async function openDetail(id, opener) {
  const r = await fetch("/partials/detail/" + id);
  if (!r.ok) return;
  lastOpener = opener || null;
  detailBody.innerHTML = await r.text();
  dialog.showModal();
}

dialog?.addEventListener("close", () => {
  if (lastOpener && document.contains(lastOpener)) lastOpener.focus();
  lastOpener = null;
});

q?.addEventListener("input", () => {
  clearTimeout(t);
  t = setTimeout(() => loadCards("/partials/cards?query=" + encodeURIComponent(q.value)), 300);
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
  const url = btn.dataset.day ? "/partials/cards?day=" + btn.dataset.day : "/partials/cards";
  await loadCards(url);
}

document.querySelector(".week")?.addEventListener("click", dayClick);
document.querySelector(".month")?.addEventListener("click", dayClick);
document.getElementById("filtersBtn")?.addEventListener("click", () => {
  document.getElementById("filtersSection")?.toggleAttribute("hidden");
});
