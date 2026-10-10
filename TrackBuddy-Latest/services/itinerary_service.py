import sqlite3
import datetime
from config import Config
from services.routing_service import optimize_stop_sequence, get_route_osrm, haversine_distance
from services.weather_service import get_weather
from services.crowd_service import get_crowd_status

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_smart_itinerary(destination_id='jaipur', start_date='2026-10-15', end_date='2026-10-16', travelers_count=4, preference='balanced', interests=None, is_student=True, start_coords=None):
    """
    Generates a structured multi-day itinerary:
    1. Selects attractions tailored to interests & schedule
    2. Clusters and optimizes route per day using routing heuristics
    3. Allocates realistic arrival/visit/departure times (with lunch breaks)
    4. Connects legs with transit mode recommendations & ticket fares
    5. Checks weather & historical crowd indicators
    """
    conn = get_db()
    cursor = conn.cursor()

    # Destination coordinates
    cursor.execute("SELECT * FROM destinations WHERE id = ?", (destination_id,))
    dest_row = cursor.fetchone()
    dest = dict(dest_row) if dest_row else {'name': 'Jaipur', 'latitude': 26.9124, 'longitude': 75.7873}

    # Calculate number of days
    try:
        d1 = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        d2 = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        days_count = max(1, (d2 - d1).days + 1)
    except:
        days_count = 2

    # Fetch available attractions
    query = "SELECT * FROM attractions WHERE destination_id = ?"
    cursor.execute(query, (destination_id,))
    all_attractions = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not all_attractions:
        return {'days': [], 'summary': 'No attractions found for this destination.'}

    # Filter/rank by interests if specified
    if interests and len(interests) > 0:
        interests_lower = [i.lower() for i in interests]
        all_attractions.sort(key=lambda a: (a['category'].lower() in interests_lower), reverse=True)

    # Weather forecast
    weather_data = get_weather(dest['latitude'], dest['longitude'], start_date)

    # Capacity per day: typically 3-4 attractions per day for a comfortable, realistic pace
    attractions_per_day = 3 if preference in ('comfortable', 'crowd-avoiding') else 4
    total_stops_needed = min(len(all_attractions), days_count * attractions_per_day)
    chosen_attractions = all_attractions[:total_stops_needed]

    # Partition attractions across days geographically (K-means / north-south split)
    # Jaipur: North side (Amber, Jal Mahal, Nahargarh) vs Central Pink City (City Palace, Hawa Mahal, Jantar Mantar, Bapu Bazar)
    chosen_attractions.sort(key=lambda a: a['latitude'], reverse=True) # North to South
    
    chunk_size = (len(chosen_attractions) + days_count - 1) // days_count
    itinerary_days = []

    total_ticket_expenses_per_person = 0.0
    current_date = d1

    for day_idx in range(days_count):
        day_stops_pool = chosen_attractions[day_idx * chunk_size : (day_idx + 1) * chunk_size]
        if not day_stops_pool and chosen_attractions:
            # fallback reuse or stretch
            day_stops_pool = chosen_attractions[-2:]

        # Optimize sequence for this day
        start_point = start_coords if (day_idx == 0 and start_coords) else (dest['latitude'], dest['longitude'])
        optimized_stops = optimize_stop_sequence(day_stops_pool, start_point, preference=preference)

        # Build detailed timeline starting at 09:30 AM
        current_minute = 9 * 60 + 30 # 09:30 AM
        day_schedule = []
        prev_coords = start_point

        for stop_order, stop in enumerate(optimized_stops):
            # Travel from previous stop
            dist_km = haversine_distance(prev_coords[0], prev_coords[1], stop['latitude'], stop['longitude'])
            
            # Transport recommendation
            if dist_km <= 1.2:
                rec_transport = 'Walking'
                transit_mins = max(4, round((dist_km / 4.5) * 60))
                transit_cost = 0.0
            elif dist_km <= 5.0 and travelers_count <= 4:
                rec_transport = 'Auto-Rickshaw'
                transit_mins = max(6, round((dist_km / 22.0) * 60) + 4)
                transit_cost = 40.0 + max(0.0, dist_km - 1.5) * 14.0
            else:
                rec_transport = 'Cab / Taxi'
                transit_mins = max(8, round((dist_km / 28.0) * 60) + 6)
                transit_cost = max(110.0, 60.0 + (dist_km * 16.5))

            current_minute += transit_mins
            arr_h, arr_m = divmod(current_minute, 60)
            arrival_time_str = f"{arr_h:02d}:{arr_m:02d}"

            # Visit duration
            visit_mins = stop.get('typical_duration_minutes', 90)
            
            # Add lunch break if passing around 13:30 (1:30 PM)
            if current_minute <= 13 * 60 + 30 < (current_minute + visit_mins):
                current_minute += 45 # 45 min Rajasthani lunch / snack break

            current_minute += visit_mins
            dep_h, dep_m = divmod(current_minute, 60)
            departure_time_str = f"{dep_h:02d}:{dep_m:02d}"

            # Ticket price (apply student concession if eligible)
            ticket_price = stop['entry_fee_student'] if is_student else stop['entry_fee_general']
            total_ticket_expenses_per_person += ticket_price

            # Crowd intelligence
            crowd_info = get_crowd_status(stop['id'])
            crowd_level = crowd_info['crowd_level'] if crowd_info else stop.get('historical_crowd_level', 'moderate')

            day_schedule.append({
                'stop_order': stop_order + 1,
                'attraction_id': stop['id'],
                'name': stop['name'],
                'category': stop['category'],
                'description': stop['description'],
                'latitude': stop['latitude'],
                'longitude': stop['longitude'],
                'image_url': stop['image_url'],
                'arrival_time': arrival_time_str,
                'departure_time': departure_time_str,
                'duration_minutes': visit_mins,
                'recommended_transport': rec_transport,
                'travel_distance_km': dist_km,
                'travel_time_mins': transit_mins,
                'transit_cost_est': round(transit_cost, 1),
                'ticket_fee_per_person': ticket_price,
                'student_discount_applied': is_student and (stop['entry_fee_general'] > stop['entry_fee_student']),
                'crowd_level': crowd_level,
                'crowd_source': 'Historical Footfall Model & Demo Analytics',
                'crowd_recommendation': crowd_info.get('recommendation') if crowd_info else 'Standard visit window.',
                'opening_time': stop.get('opening_time', '09:00'),
                'closing_time': stop.get('closing_time', '18:00')
            })

            prev_coords = (stop['latitude'], stop['longitude'])

        day_date_str = (d1 + datetime.timedelta(days=day_idx)).strftime('%Y-%m-%d')
        
        # Day weather
        day_weather = None
        if weather_data and 'forecast_days' in weather_data and len(weather_data['forecast_days']) > day_idx:
            day_weather = weather_data['forecast_days'][day_idx]

        itinerary_days.append({
            'day_number': day_idx + 1,
            'date': day_date_str,
            'weather': day_weather,
            'stops': day_schedule,
            'total_distance_km': round(sum(s['travel_distance_km'] for s in day_schedule), 2),
            'total_transit_time_mins': sum(s['travel_time_mins'] for s in day_schedule)
        })

    return {
        'destination': dest,
        'days_count': days_count,
        'travelers_count': travelers_count,
        'is_student': is_student,
        'preference': preference,
        'days': itinerary_days,
        'weather_summary': weather_data.get('current') if weather_data else None,
        'weather_source': weather_data.get('source') if weather_data else 'Unavailable',
        'est_ticket_cost_per_person': round(total_ticket_expenses_per_person, 2)
    }
