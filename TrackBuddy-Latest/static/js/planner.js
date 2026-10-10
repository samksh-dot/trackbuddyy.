const defaultStartingHubs = {
  'jaipur': 'Jaipur Junction Railway Station',
  'manali': 'Mall Road Manali / Volvo Bus Stand',
  'mumbai': 'Chhatrapati Shivaji Maharaj Terminus (CSMT)',
  'goa': 'Madgaon Railway Station / Dabolim Airport',
  'varanasi': 'Varanasi Junction (Cantt) Station'
};

function onPlannerDestinationChange(destId) {
  TrackBuddy.applyDestinationTheme(destId);
  const startInput = document.getElementById('startLocationInput');
  if (startInput && defaultStartingHubs[destId]) {
    startInput.value = defaultStartingHubs[destId];
  }
}

// Trip Planner Script
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('tripPlannerForm');
  const presetBtn = document.getElementById('fillJaipurBtn');
  const destSelect = document.getElementById('destinationSelect');

  // Check URL params (e.g. ?destination=manali)
  const urlParams = new URLSearchParams(window.location.search);
  const requestedDest = urlParams.get('destination');
  if (requestedDest && destSelect) {
    destSelect.value = requestedDest;
    onPlannerDestinationChange(requestedDest);
  }

  if (presetBtn) {
    presetBtn.addEventListener('click', () => {
      document.getElementById('travelersInput').value = 4;
      document.getElementById('budgetInput').value = 6000;
      document.getElementById('preferenceSelect').value = 'balanced';
      document.getElementById('studentCheckbox').checked = true;
      TrackBuddy.showToast("Loaded Jaipur 4-student ₹6,000 preset!");
    });
  }


  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const submitBtn = document.getElementById('generateItineraryBtn');
      submitBtn.disabled = true;
      submitBtn.textContent = "Synthesizing Routes & Weather...";

      const destination = document.getElementById('destinationSelect').value;
      const startLocation = document.getElementById('startLocationInput').value;
      const startDate = document.getElementById('startDateInput').value;
      const endDate = document.getElementById('endDateInput').value;
      const travelers = parseInt(document.getElementById('travelersInput').value) || 1;
      const budget = parseFloat(document.getElementById('budgetInput').value) || 0;
      const preference = document.getElementById('preferenceSelect').value;
      const isStudent = document.getElementById('studentCheckbox').checked;

      const checkedInterests = [];
      document.querySelectorAll('input[name="interests"]:checked').forEach(cb => {
        checkedInterests.push(cb.value);
      });

      try {
        const response = await fetch('/api/itinerary/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            destination_id: destination,
            start_date: startDate,
            end_date: endDate,
            travelers_count: travelers,
            preference: preference,
            interests: checkedInterests,
            is_student: isStudent,
            budget_total: budget
          })
        });

        if (!response.ok) {
          throw new Error("Server responded with status " + response.status);
        }

        const data = await response.json();
        data.title = `Expedition to ${data.destination ? data.destination.name : 'Jaipur'}`;
        data.budget_total = budget;
        data.start_location = startLocation;
        data.start_date = startDate;
        data.end_date = endDate;
        data.travelers_count = travelers;

        TrackBuddy.setActiveTrip(data);
        TrackBuddy.showToast("Itinerary optimized successfully! Opening Map & Timeline...", 1500);

        setTimeout(() => {
          window.location.href = '/itinerary';
        }, 800);
      } catch (err) {
        TrackBuddy.showToast("Failed to generate itinerary: " + err.message);
        submitBtn.disabled = false;
        submitBtn.textContent = "Generate Optimized Itinerary →";
      }
    });
  }
});
