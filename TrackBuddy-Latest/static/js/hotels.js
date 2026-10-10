// Hotels Catalog Script
document.addEventListener('DOMContentLoaded', () => {
  const destFilter = document.getElementById('hotelDestinationFilter');
  const typeFilter = document.getElementById('hotelTypeFilter');
  const priceFilter = document.getElementById('priceFilter');
  const sortSelect = document.getElementById('sortBySelect');
  const studentCheck = document.getElementById('studentDiscountFilter');

  // Sync with active destination if available
  const activeDest = TrackBuddy.getActiveDestination();
  if (destFilter && activeDest) {
    destFilter.value = activeDest;
  }

  if (destFilter) {
    destFilter.addEventListener('change', () => {
      TrackBuddy.applyDestinationTheme(destFilter.value);
      fetchHotels();
    });
  }
  if (typeFilter) typeFilter.addEventListener('change', fetchHotels);
  if (priceFilter) priceFilter.addEventListener('change', fetchHotels);
  if (sortSelect) sortSelect.addEventListener('change', fetchHotels);
  if (studentCheck) studentCheck.addEventListener('change', fetchHotels);

  fetchHotels();
});

async function fetchHotels() {
  const grid = document.getElementById('hotelsGrid');
  grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--ink-muted);">Loading accommodations...</div>';

  const dest = document.getElementById('hotelDestinationFilter') ? document.getElementById('hotelDestinationFilter').value : 'jaipur';
  const type = document.getElementById('hotelTypeFilter').value;
  const maxPrice = document.getElementById('priceFilter').value;
  const sort = document.getElementById('sortBySelect').value;
  const studentOnly = document.getElementById('studentDiscountFilter').checked;

  let url = `/api/hotels/search?destination_id=${dest}&sort_by=${sort}`;
  if (type) url += `&type=${type}`;
  if (maxPrice) url += `&max_price=${maxPrice}`;
  if (studentOnly) url += `&student_only=true`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderHotels(data.hotels);
  } catch(e) {
    grid.innerHTML = `<div style="grid-column: 1/-1; color: var(--status-alert); text-align: center;">Failed to load hotels: ${e.message}</div>`;
  }
}

function renderHotels(hotels) {
  const grid = document.getElementById('hotelsGrid');
  grid.innerHTML = '';

  if (!hotels || hotels.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--ink-muted);">No stays match your active filters. Try broadening your criteria.</div>';
    return;
  }

  hotels.forEach(h => {
    const card = document.createElement('div');
    card.className = 'card card-illustrated';
    card.style.padding = '0';
    card.style.overflow = 'hidden';

    const occClass = h.occupancy_status === 'Nearly full' ? 'badge-alert' : 
                     (h.occupancy_status === 'Moderate occupancy' ? 'badge-caution' : 'badge-verified');

    const amenitiesHtml = (h.amenities || []).slice(0, 3).map(a => `
      <span style="font-size: 0.78rem; background: var(--bg-card-subtle); padding: 2px 8px; border-radius: 4px; color: var(--ink-secondary);">${a}</span>
    `).join(' ');

    const directWebsiteBtn = h.booking_url ? `
      <a href="${h.booking_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" title="Visit Official Hotel Website" style="display: inline-flex; align-items: center; gap: 4px;">
        <span>Official Site</span>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
      </a>
    ` : '';

    card.innerHTML = `
      <div style="height: 190px; position: relative; overflow: hidden;">
        <img src="${h.image_url}" alt="${h.name}" style="width: 100%; height: 100%; object-fit: cover;">
        <span class="badge ${occClass}" style="position: absolute; top: 12px; right: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
          ${h.occupancy_status}
        </span>
      </div>
      <div style="padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
          <h3 style="font-size: 1.2rem; margin: 0;">${h.name}</h3>
          <span style="font-weight: 700; color: var(--sage-dark); font-size: 0.95rem;">★ ${h.rating.toFixed(1)}</span>
        </div>
        <div style="font-size: 0.82rem; color: var(--ink-muted); margin-bottom: 10px;">
          📍 ${h.address}
        </div>
        <p style="font-size: 0.88rem; margin-bottom: 14px; line-height: 1.5;">${h.review_summary}</p>
        
        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px;">
          ${amenitiesHtml}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-vintage); padding-top: 14px; flex-wrap: wrap; gap: 8px;">
          <div>
            <span style="font-size: 1.25rem; font-weight: 700; color: var(--terracotta-primary); font-family: var(--font-serif);">
              ₹${h.price_per_night}
            </span>
            <span style="font-size: 0.82rem; color: var(--ink-muted);"> / night</span>
          </div>
          <div style="display: flex; gap: 6px;">
            <a href="/hotels/${h.id}" class="btn btn-secondary btn-sm">Reviews</a>
            ${directWebsiteBtn}
          </div>
        </div>
      </div>
    `;

    grid.appendChild(card);
  });

}
