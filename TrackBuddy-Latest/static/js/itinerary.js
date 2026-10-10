// Itinerary & Timeline Interaction Controller
let currentTrip = null;
let currentDayIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
  initLeafletMap();

  currentTrip = TrackBuddy.getActiveTrip();
  if (!currentTrip || !currentTrip.days || currentTrip.days.length === 0) {
    // If no active trip, check active destination
    const activeDest = TrackBuddy.getActiveDestination() || 'jaipur';
    loadDefaultDestinationItinerary(activeDest);
    return;
  }

  if (currentTrip.destination && currentTrip.destination.id) {
    TrackBuddy.applyDestinationTheme(currentTrip.destination.id);
  }

  renderItineraryView();
  setupEventListeners();
});

async function loadDefaultDestinationItinerary(destId = 'jaipur') {
  TrackBuddy.applyDestinationTheme(destId);
  TrackBuddy.showToast(`Loading ${destId.toUpperCase()} expedition...`);
  try {
    const res = await fetch('/api/itinerary/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        destination_id: destId,
        start_date: '2026-10-15',
        end_date: '2026-10-16',
        travelers_count: 4,
        preference: 'balanced',
        is_student: true,
        budget_total: 6000
      })
    });
    currentTrip = await res.json();
    currentTrip.title = `${currentTrip.destination ? currentTrip.destination.name : destId} 2-Day Expedition`;
    currentTrip.budget_total = 6000;
    currentTrip.travelers_count = 4;
    TrackBuddy.setActiveTrip(currentTrip);
    renderItineraryView();
    setupEventListeners();
  } catch(err) {
    TrackBuddy.showToast("Error loading trip: " + err.message);
  }
}


function renderItineraryView() {
  if (!currentTrip) return;

  // Header and Stats
  document.getElementById('tripTitle').textContent = currentTrip.title || "Jaipur Itinerary";
  const studentBadge = document.getElementById('studentBadge');
  if (studentBadge) {
    studentBadge.style.display = currentTrip.is_student ? 'inline-flex' : 'none';
  }

  const travelers = currentTrip.travelers_count || 4;
  document.getElementById('statTravelers').textContent = travelers;
  document.getElementById('statDays').textContent = (currentTrip.days.length) + " Days";

  // Weather overview
  if (currentTrip.weather_summary) {
    document.getElementById('statWeather').textContent = 
      `${Math.round(currentTrip.weather_summary.temperature)}°C ${currentTrip.weather_summary.condition}`;
  }

  // Render Day Selector Tabs
  const tabsContainer = document.getElementById('dayTabsContainer');
  tabsContainer.innerHTML = '';
  currentTrip.days.forEach((day, idx) => {
    const tabBtn = document.createElement('button');
    tabBtn.className = `btn btn-sm ${idx === currentDayIndex ? 'btn-primary' : 'btn-secondary'}`;
    tabBtn.textContent = `Day ${day.day_number} (${day.date || 'Oct ' + (15 + idx)})`;
    tabBtn.addEventListener('click', () => {
      currentDayIndex = idx;
      renderItineraryView();
    });
    tabsContainer.appendChild(tabBtn);
  });

  // Active Day Content
  const activeDay = currentTrip.days[currentDayIndex];
  if (!activeDay) return;

  // Update weather advisory
  const alertBox = document.getElementById('weatherAlertBox');
  const alertText = document.getElementById('weatherAlertText');
  if (activeDay.weather) {
    alertBox.style.display = 'flex';
    alertText.textContent = `Forecast: ${activeDay.weather.condition} (${activeDay.weather.temp_min}°C to ${activeDay.weather.temp_max}°C). ${activeDay.weather.recommendation}`;
  } else {
    alertBox.style.display = 'none';
  }

  // Render Stops Timeline
  const timeline = document.getElementById('timelineContainer');
  timeline.innerHTML = '';

  let dayDistance = 0;
  let hasCrowdAlert = false;
  let crowdedStopName = "";

  activeDay.stops.forEach((stop, idx) => {
    dayDistance += stop.travel_distance_km || 0;

    // Check crowd alert
    if (stop.crowd_level === 'crowded' || stop.crowd_level === 'high') {
      hasCrowdAlert = true;
      crowdedStopName = stop.name;
    }

    // Transit leg from previous stop
    if (idx > 0) {
      const transitLeg = document.createElement('div');
      transitLeg.className = 'timeline-transit-leg';
      transitLeg.innerHTML = `
        <span>🚗 Leg: <strong>${stop.recommended_transport || 'Auto'}</strong> (~${stop.travel_time_mins || 10} mins, ${stop.travel_distance_km || 1.5} km)</span>
        <span>• Est. Leg Fare: ₹${stop.transit_cost_est || 40}</span>
      `;
      timeline.appendChild(transitLeg);
    }

    // Attraction card
    const item = document.createElement('div');
    item.className = 'timeline-item';

    const crowdBadgeClass = stop.crowd_level === 'crowded' ? 'badge-alert' : 
                            (stop.crowd_level === 'high' ? 'badge-caution' : 'badge-verified');

    item.innerHTML = `
      <div class="timeline-dot"></div>
      <div class="timeline-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <div>
            <span style="font-size: 0.82rem; font-weight: 600; color: var(--terracotta-primary);">
              #${stop.stop_order} • ${stop.arrival_time} - ${stop.departure_time} (${stop.duration_minutes} mins)
            </span>
            <h3 style="margin: 2px 0 6px 0;">${stop.name}</h3>
          </div>
          <span class="badge ${crowdBadgeClass}">
            ${stop.crowd_level ? stop.crowd_level.toUpperCase() : 'MODERATE'} CROWD
          </span>
        </div>
        
        <p style="font-size: 0.9rem; margin-bottom: 12px;">${stop.description || ''}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--ink-secondary); border-top: 1px dashed var(--border-vintage); padding-top: 10px;">
          <div>
            <span>🎟️ Entry Fee: <strong>₹${stop.ticket_fee_per_person}</strong>/person</span>
            ${stop.student_discount_applied ? '<span class="badge badge-verified" style="margin-left: 6px; font-size: 0.72rem;">Student Concession Applied</span>' : ''}
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-secondary btn-sm" onclick="swapStopPosition(${currentDayIndex}, ${idx}, -1)" ${idx === 0 ? 'disabled' : ''}>▲</button>
            <button class="btn btn-secondary btn-sm" onclick="swapStopPosition(${currentDayIndex}, ${idx}, 1)" ${idx === activeDay.stops.length - 1 ? 'disabled' : ''}>▼</button>
          </div>
        </div>
      </div>
    `;

    timeline.appendChild(item);
  });

  // Route distance display
  document.getElementById('routeDistanceDisplay').textContent = 
    `Day ${activeDay.day_number} Route: ~${dayDistance.toFixed(1)} km across ${activeDay.stops.length} stops`;

  // Crowd notice box
  const crowdBox = document.getElementById('crowdActionBox');
  if (hasCrowdAlert) {
    crowdBox.style.display = 'block';
    document.getElementById('crowdNoticeText').textContent = 
      `${crowdedStopName} experiences peak tourist density during midday. We recommend visiting in early morning (08:30 AM) or replacing with an uncrowded cultural gem like Albert Hall / Galta Ji.`;
  } else {
    crowdBox.style.display = 'none';
  }

  // Update map polyline and markers
  updateMapStops(activeDay.stops);
}

// Allow user to reorder stops manually
window.swapStopPosition = function(dayIdx, stopIdx, direction) {
  const day = currentTrip.days[dayIdx];
  const targetIdx = stopIdx + direction;
  if (targetIdx < 0 || targetIdx >= day.stops.length) return;

  const temp = day.stops[stopIdx];
  day.stops[stopIdx] = day.stops[targetIdx];
  day.stops[targetIdx] = temp;

  // Re-index stop order
  day.stops.forEach((s, i) => { s.stop_order = i + 1; });

  TrackBuddy.setActiveTrip(currentTrip);
  renderItineraryView();
  TrackBuddy.showToast("Stops reordered! Recalculating route...");
};

function setupEventListeners() {
  // Re-optimize stops button
  const reoptBtn = document.getElementById('reoptimizeBtn');
  if (reoptBtn) {
    reoptBtn.addEventListener('click', async () => {
      const activeDay = currentTrip.days[currentDayIndex];
      TrackBuddy.showToast("Re-optimizing stop sequence via nearest-neighbor heuristic...");
      try {
        const res = await fetch('/api/itinerary/optimize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stops: activeDay.stops,
            preference: currentTrip.preference || 'balanced'
          })
        });
        const data = await res.json();
        activeDay.stops = data.optimized_stops;
        activeDay.stops.forEach((s, i) => { s.stop_order = i + 1; });
        TrackBuddy.setActiveTrip(currentTrip);
        renderItineraryView();
        TrackBuddy.showToast("Stops successfully re-optimized!");
      } catch(e) {
        TrackBuddy.showToast("Optimization failed: " + e.message);
      }
    });
  }

  // Crowd alternative button
  const crowdBtn = document.getElementById('applyCrowdAlternativeBtn');
  if (crowdBtn) {
    crowdBtn.addEventListener('click', () => {
      TrackBuddy.showToast("Shifting crowded stop to morning slot (08:30 AM) and adjusting bazaar schedule...");
      const day = currentTrip.days[currentDayIndex];
      // Move crowded stop to first slot
      if (day.stops.length > 1) {
        const crowdedIdx = day.stops.findIndex(s => s.crowd_level === 'crowded' || s.crowd_level === 'high');
        if (crowdedIdx > 0) {
          const item = day.stops.splice(crowdedIdx, 1)[0];
          day.stops.unshift(item);
          day.stops.forEach((s, i) => { s.stop_order = i + 1; });
        }
      }
      TrackBuddy.setActiveTrip(currentTrip);
      renderItineraryView();
      TrackBuddy.showToast("Itinerary updated to beat the crowd!");
    });
  }

  // Save Trip Button
  const saveBtn = document.getElementById('saveTripBtn');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      saveBtn.disabled = true;
      saveBtn.textContent = "Saving...";
      try {
        const res = await fetch('/api/trips', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(currentTrip)
        });
        const data = await res.json();
        TrackBuddy.showToast("Expedition saved successfully! ID: " + data.trip_id);
        saveBtn.textContent = "Saved ✓";
      } catch(e) {
        TrackBuddy.showToast("Save failed: " + e.message);
        saveBtn.disabled = false;
        saveBtn.textContent = "Save Expedition";
      }
    });
  }
}
