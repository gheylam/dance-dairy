const q = document.getElementById("q");
const results = document.getElementById("results");
let t;
q?.addEventListener("input", () => {
  clearTimeout(t);
  t = setTimeout(async () => {
    const r = await fetch("/partials/cards?query=" + encodeURIComponent(q.value));
    results.innerHTML = await r.text();
  }, 300);
});
results?.addEventListener("click", async (e) => {
  if (e.target.closest("#clearFilters")) {
    q.value = "";
    document.querySelectorAll(".week button").forEach((b) => b.removeAttribute("aria-current"));
    const r = await fetch("/partials/cards");
    results.innerHTML = await r.text();
    return;
  }
  const card = e.target.closest(".card");
  if (!card || e.target.closest("a")) return;
  const r = await fetch("/partials/detail/" + card.dataset.id);
  if (!r.ok) return;
  document.getElementById("detailBody").innerHTML = await r.text();
  document.getElementById("detail").showModal();
});
document.querySelector(".week")?.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-day]");
  if (!btn) return;
  document.querySelectorAll(".week button").forEach((b) => b.removeAttribute("aria-current"));
  btn.setAttribute("aria-current", "true");
  const url = btn.dataset.day ? "/partials/cards?day=" + btn.dataset.day : "/partials/cards";
  const r = await fetch(url);
  results.innerHTML = await r.text();
});
