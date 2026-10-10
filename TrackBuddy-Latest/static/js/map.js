// Interactive Leaflet Map Script
let leafMap = null;
let routePolyline = null;
let stopMarkers = [];

function initLeafletMap(centerLat = 26.9124, centerLon = 75.7873, zoom = 12) {
  if (leafMap) return;

  const mapElement = document.getElementById('map');
  if (!mapElement) return;

  leafMap = L.map('map').setView([centerLat, centerLon], zoom);

  // Warm vintage / standard OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors | TrackBuddy'
  }).addTo(leafMap);
}

function updateMapStops(stops) {
  if (!leafMap || !stops || stops.length === 0) return;

  // Clear existing markers & polylines
  stopMarkers.forEach(m => leafMap.removeLayer(m));
  stopMarkers = [];
  if (routePolyline) {
    leafMap.removeLayer(routePolyline);
    routePolyline = null;
  }

  const latlngs = [];

  stops.forEach((stop, idx) => {
    const lat = stop.latitude;
    const lon = stop.longitude;
    latlngs.push([lat, lon]);

    // Create custom numbered vintage terracotta marker
    const iconHtml = `
      <div style="background-color: #C85A32; color: #fff; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; border: 2px solid #F9F6F0; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        ${idx + 1}
      </div>
    `;

    const customIcon = L.divIcon({
      html: iconHtml,
      className: 'vintage-marker',
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    const popupContent = `
      <div style="font-family: var(--font-sans); min-width: 180px;">
        <h4 style="margin: 0 0 4px 0; color: #2C2623;">${stop.name}</h4>
        <div style="font-size: 12px; color: #5C524B; margin-bottom: 6px;">
          Order: #${idx + 1} • Arrival: ${stop.arrival_time || 'N/A'}
        </div>
        <div style="font-size: 12px; margin-bottom: 4px;">
          Crowd: <strong>${stop.crowd_level || 'Moderate'}</strong>
        </div>
        <div style="font-size: 11px; color: #8C8077;">${stop.description ? stop.description.substring(0, 90) + '...' : ''}</div>
      </div>
    `;

    const marker = L.marker([lat, lon], { icon: customIcon }).addTo(leafMap).bindPopup(popupContent);
    stopMarkers.push(marker);
  });

  // Fetch or draw polyline connecting the stops
  if (latlngs.length > 1) {
    routePolyline = L.polyline(latlngs, {
      color: '#C85A32',
      weight: 4,
      dashArray: '6, 8',
      opacity: 0.85
    }).addTo(leafMap);

    leafMap.fitBounds(L.latLngBounds(latlngs), { padding: [40, 40] });
  } else if (latlngs.length === 1) {
    leafMap.setView(latlngs[0], 13);
  }
}
