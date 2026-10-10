import requests
import time
from config import Config

_weather_cache = {}

def get_weather(lat, lon, date_str=None):
    """
    Fetch weather forecast from Open-Meteo free API (no API key required).
    Falls back cleanly to demo meteorological guidance if offline.
    """
    cache_key = f"{round(lat, 2)},{round(lon, 2)}"
    now = time.time()
    if cache_key in _weather_cache:
        cached = _weather_cache[cache_key]
        if now - cached['timestamp'] < 1800: # 30 min cache
            return cached['data']

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&"
        f"hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weathercode,windspeed_10m&"
        f"daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&"
        f"timezone=Asia%2FKolkata"
    )

    try:
        resp = requests.get(url, timeout=3.5)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get('current_weather', {})
            daily = data.get('daily', {})

            weather_code = curr.get('weathercode', 0)
            condition, recommendation, is_favorable = parse_wmo_code(weather_code)

            days = []
            if 'time' in daily:
                for i, day_time in enumerate(daily['time'][:7]):
                    day_code = daily['weathercode'][i] if 'weathercode' in daily else 0
                    day_cond, day_rec, _ = parse_wmo_code(day_code)
                    days.append({
                        'date': day_time,
                        'temp_max': daily['temperature_2m_max'][i] if 'temperature_2m_max' in daily else 28,
                        'temp_min': daily['temperature_2m_min'][i] if 'temperature_2m_min' in daily else 18,
                        'rain_prob': daily['precipitation_probability_max'][i] if 'precipitation_probability_max' in daily else 10,
                        'precipitation_mm': daily['precipitation_sum'][i] if 'precipitation_sum' in daily else 0.0,
                        'condition': day_cond,
                        'recommendation': day_rec
                    })

            result = {
                'current': {
                    'temperature': curr.get('temperature', 26.5),
                    'windspeed': curr.get('windspeed', 12.0),
                    'condition': condition,
                    'recommendation': recommendation,
                    'is_favorable_outdoor': is_favorable,
                    'weather_code': weather_code
                },
                'forecast_days': days,
                'source': 'Open-Meteo Meteorological Service (Live)',
                'is_live': True
            }
            _weather_cache[cache_key] = {'data': result, 'timestamp': now}
            return result
    except Exception as e:
        pass

    # Graceful Offline Demo Data (clearly labeled)
    result = {
        'current': {
            'temperature': 27.0,
            'windspeed': 10.5,
            'condition': 'Pleasant & Sunny',
            'recommendation': 'Favorable weather for outdoor heritage walking and sightseeing.',
            'is_favorable_outdoor': True,
            'weather_code': 0
        },
        'forecast_days': [
            {'date': 'Day 1', 'temp_max': 29.5, 'temp_min': 17.0, 'rain_prob': 5, 'precipitation_mm': 0.0, 'condition': 'Sunny / Clear Sky', 'recommendation': 'Ideal for Amber Fort and Nahargarh sunset.'},
            {'date': 'Day 2', 'temp_max': 28.0, 'temp_min': 16.5, 'rain_prob': 15, 'precipitation_mm': 0.0, 'condition': 'Partly Cloudy', 'recommendation': 'Comfortable conditions for City Palace and shopping bazaars.'},
            {'date': 'Day 3', 'temp_max': 27.5, 'temp_min': 16.0, 'rain_prob': 20, 'precipitation_mm': 0.0, 'condition': 'Mild Breeze', 'recommendation': 'Great for photography at Patrika Gate.'}
        ],
        'source': 'Demonstration Weather Model (Offline Fallback)',
        'is_live': False
    }
    return result

def parse_wmo_code(code):
    """Map WMO Weather interpretation code to readable description & recommendation."""
    if code == 0:
        return 'Clear Sky / Sunny', 'Ideal weather for outdoor fort exploration and open bazaars.', True
    elif code in (1, 2, 3):
        return 'Partly Cloudy', 'Comfortable ambient temperature. Perfect for walking tours.', True
    elif code in (45, 48):
        return 'Foggy / Hazy', 'Visibility may be lower in early morning; plan hilltop forts after 10 AM.', True
    elif code in (51, 53, 55, 61, 63):
        return 'Slight / Moderate Rain', 'Carry umbrellas; consider scheduling indoor museums like Albert Hall or City Palace.', False
    elif code in (65, 80, 81, 82, 95):
        return 'Heavy Rain / Thunderstorm', 'Disruption warning: prioritize indoor heritage complexes or delay open-terrace forts.', False
    else:
        return 'Fair Weather', 'Standard travel conditions.', True
