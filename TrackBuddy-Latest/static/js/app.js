// TrackBuddy Global JavaScript Helper
const TrackBuddy = {
  // Show toast notification
  showToast: function(message, duration = 3500) {
    const toast = document.getElementById('toastNotification');
    if (!toast) return;
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
      toast.style.display = 'none';
    }, duration);
  },

  // Save current active trip into localStorage for easy instant access
  setActiveTrip: function(tripData) {
    localStorage.setItem('trackbuddy_active_trip', JSON.stringify(tripData));
  },

  getActiveTrip: function() {
    const raw = localStorage.getItem('trackbuddy_active_trip');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch(e) {
      return null;
    }
  },

  formatRupee: function(val) {
    return '₹' + parseFloat(val || 0).toLocaleString('en-IN', { maximumFractionDigits: 1 });
  },

  // Apply visual destination theme dynamically across the app
  applyDestinationTheme: function(destId) {
    document.body.classList.remove('theme-jaipur', 'theme-manali', 'theme-mumbai', 'theme-goa', 'theme-varanasi');
    if (destId && destId !== 'jaipur') {
      document.body.classList.add(`theme-${destId}`);
    }
    localStorage.setItem('trackbuddy_active_destination', destId || 'jaipur');
  },

  getActiveDestination: function() {
    return localStorage.getItem('trackbuddy_active_destination') || 'jaipur';
  }
};


// Highlight current nav link
document.addEventListener('DOMContentLoaded', () => {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // Automatically apply currently chosen destination theme
  const activeTrip = TrackBuddy.getActiveTrip();
  const destId = (activeTrip && activeTrip.destination && activeTrip.destination.id) 
    ? activeTrip.destination.id 
    : TrackBuddy.getActiveDestination();
  TrackBuddy.applyDestinationTheme(destId);
});

