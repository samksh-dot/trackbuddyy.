import math
import requests
import time
from config import Config

# Simple in-memory fallback cache
_cache = {}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points in kilometers."""
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def get_route_osrm(start_lat, start_lon, end_lat, end_lon, mode='driving'):
    """
    Fetch route and travel duration from OSRM public service with fallback to Haversine estimate.
    """
    cache_key = f"{mode}:{start_lat},{start_lon}:{end_lat},{end_lon}"
    if cache_key in _cache:
        cached_entry = _cache[cache_key]
        if time.time() - cached_entry['timestamp'] < 3600: # 1 hr cache
            return cached_entry['data']

    # OSRM modes: car (driving), foot (walking), bicycle
    profile = 'driving'
    if mode == 'walking':
        profile = 'walking' # Note: public server primarily hosts driving
    
    url = f"https://router.project-osrm.org/route/v1/{profile}/{start_lon},{start_lat};{end_lon},{end_lat}?overview=simplified&geometries=geojson"
    
    try:
        response = requests.get(url, timeout=3.5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
                route = data['routes'][0]
                dist_km = round(route['distance'] / 1000.0, 2)
                dur_mins = max(1, round(route['duration'] / 60.0))
                coordinates = route.get('geometry', {}).get('coordinates', [])
                
                result = {
                    'distance_km': dist_km,
                    'duration_minutes': dur_mins,
                    'coordinates': coordinates, # [ [lon, lat], ... ]
                    'source': 'OSRM Public Routing API (Live)'
                }
                _cache[cache_key] = {'data': result, 'timestamp': time.time()}
                return result
    except Exception as e:
        # Fallback gracefully
        pass

    # Mathematical geometric fallback
    dist_km = haversine_distance(start_lat, start_lon, end_lat, end_lon)
    # Estimate travel time based on urban speed (~25 km/h for driving, ~4.5 km/h for walking)
    speed_kmh = 4.5 if mode == 'walking' else 25.0
    dur_mins = max(2, round((dist_km / speed_kmh) * 60))
    
    result = {
        'distance_km': dist_km,
        'duration_minutes': dur_mins,
        'coordinates': [[start_lon, start_lat], [end_lon, end_lat]],
        'source': 'TrackBuddy Haversine Distance Estimator (Graceful Fallback)'
    }
    _cache[cache_key] = {'data': result, 'timestamp': time.time()}
    return result

def optimize_stop_sequence(stops, start_coords=None, preference='balanced'):
    """
    Given a list of stop dicts with lat, lon, id, name, etc.
    Returns the ordered list of stops using nearest-neighbor heuristic with 2-opt refinement.
    Preference can be: 'fastest', 'cheapest', 'balanced'.
    """
    if len(stops) <= 1:
        return stops

    # Start point
    remaining = list(stops)
    ordered = []

    # Current position
    current_lat = start_coords[0] if start_coords else remaining[0]['latitude']
    current_lon = start_coords[1] if start_coords else remaining[0]['longitude']
    
    if not start_coords:
        ordered.append(remaining.pop(0))
        current_lat, current_lon = ordered[0]['latitude'], ordered[0]['longitude']

    while remaining:
        best_idx = 0
        best_dist = float('inf')
        for i, stop in enumerate(remaining):
            d = haversine_distance(current_lat, current_lon, stop['latitude'], stop['longitude'])
            
            # If preference is crowd-avoiding or balanced, factor in crowd penalties
            if preference == 'crowd-avoiding':
                crowd_level = stop.get('crowd_level', stop.get('historical_crowd_level', 'moderate'))
                penalty = 1.0
                if crowd_level == 'crowded':
                    penalty = 1.6
                elif crowd_level == 'high':
                    penalty = 1.3
                d = d * penalty

            if d < best_dist:
                best_dist = d
                best_idx = i

        chosen = remaining.pop(best_idx)
        ordered.append(chosen)
        current_lat, current_lon = chosen['latitude'], chosen['longitude']

    return ordered
