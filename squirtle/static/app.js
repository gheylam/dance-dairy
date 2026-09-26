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
  const card = e.target.closest(".card");
  if (!card || e.target.closest("a")) return;
  const r = await fetch("/partials/detail/" + card.dataset.id);
  if (!r.ok) return;
  document.getElementById("detailBody").innerHTML = await r.text();
  document.getElementById("detail").showModal();
});
