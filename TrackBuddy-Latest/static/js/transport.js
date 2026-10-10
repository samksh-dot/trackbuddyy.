// Transport Comparison Page Controller
const destinationLocations = {
  'jaipur': {
    'station': { name: 'Jaipur Railway Station (Junction)', coords: [26.9189, 75.7885] },
    'hawa-mahal': { name: 'Hawa Mahal (Pink City)', coords: [26.9239, 75.8267] },
    'amber-fort': { name: 'Amber Fort & Palace', coords: [26.9855, 75.8513] },
    'city-palace': { name: 'City Palace Complex', coords: [26.9258, 75.8236] },
    'nahargarh-fort': { name: 'Nahargarh Fort (Sunset Point)', coords: [26.9373, 75.8155] },
    'zostel': { name: 'Zostel Jaipur (Subhash Chowk)', coords: [26.9265, 75.8302] }
  },
  'manali': {
    'mall-road': { name: 'Manali Mall Road / Bus Stand', coords: [32.2396, 77.1887] },
    'solang-valley': { name: 'Solang Valley Adventure Arena', coords: [32.3166, 77.1575] },
    'hadimba-temple': { name: 'Hadimba Devi Temple', coords: [32.2483, 77.1809] },
    'old-manali': { name: 'Old Manali Village & Cafes', coords: [32.2530, 77.1770] },
    'jogini-waterfall': { name: 'Jogini Waterfall Trailhead', coords: [32.2680, 77.1950] }
  },
  'mumbai': {
    'csmt': { name: 'Chhatrapati Shivaji Maharaj Terminus', coords: [18.9400, 72.8354] },
    'gateway': { name: 'Gateway of India & Taj Mahal', coords: [18.9220, 72.8347] },
    'marine-drive': { name: 'Marine Drive Promenade', coords: [18.9432, 72.8230] },
    'colaba': { name: 'Colaba Causeway Market', coords: [18.9217, 72.8315] },
    'bandra': { name: 'Bandra Bandstand & Fort', coords: [19.0435, 72.8193] }
  },
  'goa': {
    'madgaon': { name: 'Madgaon Railway Station', coords: [15.2736, 73.9580] },
    'baga-beach': { name: 'Baga & Calangute Beach', coords: [15.5553, 73.7517] },
    'aguada-fort': { name: 'Fort Aguada & Lighthouse', coords: [15.4925, 73.7736] },
    'fontainhas': { name: 'Fontainhas Latin Quarter', coords: [15.4989, 73.8278] },
    'anjuna': { name: 'Anjuna Beach & Flea Market', coords: [15.5828, 73.7428] }
  },
  'varanasi': {
    'cantt-station': { name: 'Varanasi Junction (Cantt)', coords: [25.3284, 82.9868] },
    'dashashwamedh': { name: 'Dashashwamedh Ghat (Aarti)', coords: [25.3076, 83.0104] },
    'kashi-temple': { name: 'Kashi Vishwanath Temple', coords: [25.3109, 83.0107] },
    'sarnath': { name: 'Sarnath Buddhist Stupa', coords: [25.3811, 83.0222] },
    'assi-ghat': { name: 'Assi Ghat Subah-e-Banaras', coords: [25.2905, 83.0064] }
  }
};

function onTransportHubChange(destId) {
  TrackBuddy.applyDestinationTheme(destId);
  const hubData = destinationLocations[destId] || destinationLocations['jaipur'];
  const originSelect = document.getElementById('originSelect');
  const destSelect = document.getElementById('destSelect');

  if (originSelect && destSelect) {
    originSelect.innerHTML = '';
    destSelect.innerHTML = '';

    const keys = Object.keys(hubData);
    keys.forEach((k, idx) => {
      const opt1 = document.createElement('option');
      opt1.value = k;
      opt1.textContent = hubData[k].name;
      if (idx === 0) opt1.selected = true;
      originSelect.appendChild(opt1);

      const opt2 = document.createElement('option');
      opt2.value = k;
      opt2.textContent = hubData[k].name;
      if (idx === 1 || (idx === keys.length - 1 && keys.length > 1)) opt2.selected = true;
      destSelect.appendChild(opt2);
    });
  }
  fetchComparison();
}

document.addEventListener('DOMContentLoaded', () => {
  const hubSelect = document.getElementById('transportHubSelect');
  const activeDest = TrackBuddy.getActiveDestination() || 'jaipur';
  if (hubSelect && activeDest) {
    hubSelect.value = activeDest;
    onTransportHubChange(activeDest);
  } else {
    onTransportHubChange('jaipur');
  }

  const compareBtn = document.getElementById('compareBtn');
  if (compareBtn) {
    compareBtn.addEventListener('click', fetchComparison);
  }
});


async function fetchComparison() {
  const hubKey = document.getElementById('transportHubSelect') ? document.getElementById('transportHubSelect').value : 'jaipur';
  const hubData = destinationLocations[hubKey] || destinationLocations['jaipur'];

  const originKey = document.getElementById('originSelect').value;
  const destKey = document.getElementById('destSelect').value;
  const travelers = parseInt(document.getElementById('passengerCountInput').value) || 4;

  const originObj = hubData[originKey] || Object.values(hubData)[0];
  const destObj = hubData[destKey] || Object.values(hubData)[1] || originObj;

  const origin = originObj.coords;
  const dest = destObj.coords;

  const tbody = document.getElementById('transportTableBody');
  tbody.innerHTML = `<tr><td colspan="7" style="padding: 24px; text-align: center; color: var(--ink-muted);">Calculating transit fares & distances for ${hubKey.toUpperCase()}...</td></tr>`;


  try {
    const res = await fetch('/api/transport/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        origin_lat: origin[0],
        origin_lon: origin[1],
        dest_lat: dest[0],
        dest_lon: dest[1],
        travelers: travelers
      })
    });

    const data = await res.json();
    renderTransportTable(data.options, travelers);
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="7" style="padding: 24px; text-align: center; color: var(--status-alert);">Failed to load transport data: ${e.message}</td></tr>`;
  }
}

function renderTransportTable(options, travelers) {
  const tbody = document.getElementById('transportTableBody');
  tbody.innerHTML = '';

  if (!options || options.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="padding: 24px; text-align: center;">No transit options available.</td></tr>`;
    return;
  }

  options.forEach(opt => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--border-vintage)';

    const recBadge = opt.is_recommended ? 
      '<span class="badge badge-verified" style="margin-left: 8px;">Recommended</span>' : '';

    tr.innerHTML = `
      <td style="padding: 16px 20px;">
        <div style="font-weight: 600; font-size: 0.98rem; display: flex; align-items: center;">
          ${opt.mode} ${recBadge}
        </div>
        <div style="font-size: 0.82rem; color: var(--ink-muted); margin-top: 4px;">${opt.note}</div>
      </td>
      <td style="padding: 16px; font-weight: 700; color: var(--terracotta-primary); font-size: 1.05rem;">
        ${opt.total_fare === 0 ? 'Free' : '₹' + opt.total_fare.toFixed(0)}
      </td>
      <td style="padding: 16px; font-weight: 600; color: var(--ink-primary);">
        ${opt.per_person_fare === 0 ? 'Free' : '₹' + opt.per_person_fare.toFixed(1)}
      </td>
      <td style="padding: 16px;">
        ⏱️ ${opt.travel_time_mins} mins
      </td>
      <td style="padding: 16px;">
        ${opt.distance_km} km
      </td>
      <td style="padding: 16px; font-size: 0.88rem;">
        ${opt.availability}
      </td>
      <td style="padding: 16px 20px; font-size: 0.82rem; color: var(--ink-muted);">
        ${opt.source}
      </td>
    `;

    tbody.appendChild(tr);
  });
}
