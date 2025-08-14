const API_BASE = "http://localhost:8000"; // change if hosted

async function loadHotels(sortBy = "rating") {
  const res = await fetch(`${API_BASE}/recommendations?sort_by=${encodeURIComponent(sortBy)}`);
  const data = await res.json();
  const list = document.getElementById("hotel-list");
  if (!list) return;
  list.innerHTML = data.hotels.map(h => `
    <article class="card">
      <h3>${h.name}</h3>
      <p>${h.city}, ${h.state}</p>
      <p><strong>★ ${h.rating}</strong> • ₦${h.price.toLocaleString()}</p>
      <div>${h.amenities.map(a=>`<span class="badge">${a}</span>`).join(' ')}</div>
    </article>
  `).join('');
}

document.addEventListener("DOMContentLoaded", () => {
  const sortSel = document.getElementById("sortBy");
  const btn = document.getElementById("reload");
  if (sortSel && btn) {
    btn.addEventListener("click", () => loadHotels(sortSel.value));
    loadHotels(sortSel.value);
  } else {
    // Fallback: if on home page we won't have sort controls
    if (document.getElementById("hotel-list")) loadHotels("rating");
  }
});