import uuid
import json
import sqlite3
from flask import Blueprint, request, jsonify
from config import Config
from services.itinerary_service import generate_smart_itinerary
from services.routing_service import optimize_stop_sequence
from services.budget_service import calculate_trip_budget

trips_bp = Blueprint('trips', __name__, url_prefix='/api')

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@trips_bp.route('/destinations/search', methods=['GET'])
def search_destinations():
    query = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor()
    if query:
        cursor.execute("SELECT * FROM destinations WHERE name LIKE ? OR state LIKE ?", (f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("SELECT * FROM destinations")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'destinations': rows})

@trips_bp.route('/attractions', methods=['GET'])
def get_attractions():
    destination_id = request.args.get('destination_id', 'jaipur')
    category = request.args.get('category')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM attractions WHERE destination_id = ?"
    params = [destination_id]
    if category:
        query += " AND category = ?"
        params.append(category)
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'attractions': rows})

@trips_bp.route('/itinerary/generate', methods=['POST'])
def generate_itinerary_endpoint():
    data = request.get_json() or {}
    dest_id = data.get('destination_id', 'jaipur')
    start_date = data.get('start_date', '2026-10-15')
    end_date = data.get('end_date', '2026-10-16')
    travelers = int(data.get('travelers_count', 4))
    preference = data.get('preference', 'balanced')
    interests = data.get('interests', [])
    is_student = bool(data.get('is_student', True))
    
    start_coords = None
    if 'start_lat' in data and 'start_lon' in data:
        try:
            start_coords = (float(data['start_lat']), float(data['start_lon']))
        except:
            pass

    itinerary = generate_smart_itinerary(
        destination_id=dest_id,
        start_date=start_date,
        end_date=end_date,
        travelers_count=travelers,
        preference=preference,
        interests=interests,
        is_student=is_student,
        start_coords=start_coords
    )

    return jsonify(itinerary)

@trips_bp.route('/itinerary/optimize', methods=['POST'])
def optimize_stops_endpoint():
    data = request.get_json() or {}
    stops = data.get('stops', [])
    start_coords = data.get('start_coords')
    preference = data.get('preference', 'balanced')

    optimized = optimize_stop_sequence(stops, start_coords, preference)
    return jsonify({'optimized_stops': optimized})

@trips_bp.route('/trips', methods=['POST'])
def save_trip():
    data = request.get_json() or {}
    trip_id = str(uuid.uuid4())[:8]
    title = data.get('title', f"Trip to {data.get('destination', 'Jaipur')}")
    dest = data.get('destination', 'jaipur')
    start_loc = data.get('start_location', 'Jaipur Railway Station')
    start_date = data.get('start_date', '2026-10-15')
    end_date = data.get('end_date', '2026-10-16')
    travelers = int(data.get('travelers_count', 4))
    budget_total = float(data.get('budget_total', 6000.0))
    budget_per_person = round(budget_total / travelers, 2)
    pref = data.get('travel_preference', 'balanced')
    transport_modes = json.dumps(data.get('transport_modes', ['walking', 'auto', 'cab']))
    interests = json.dumps(data.get('interests', ['historical', 'shopping']))
    is_student = 1 if data.get('is_student') else 0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trips (
            id, title, destination, start_location, start_date, end_date,
            travelers_count, budget_total, budget_per_person, travel_preference,
            transport_modes, interests, is_student
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trip_id, title, dest, start_loc, start_date, end_date,
        travelers, budget_total, budget_per_person, pref,
        transport_modes, interests, is_student
    ))

    # Add default members
    members = data.get('members', ['Aarav', 'Neha', 'Kabir', 'Riya'][:travelers])
    for m in members:
        cursor.execute("INSERT INTO trip_members (trip_id, name) VALUES (?, ?)", (trip_id, m))

    # If itinerary days are supplied, store them
    days_data = data.get('days', [])
    for d in days_data:
        day_id = f"{trip_id}-d{d.get('day_number', 1)}"
        cursor.execute("""
            INSERT INTO itinerary_days (id, trip_id, day_number, date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (day_id, trip_id, d.get('day_number', 1), d.get('date', start_date), d.get('notes', '')))

        for stop in d.get('stops', []):
            stop_id = str(uuid.uuid4())[:8]
            cursor.execute("""
                INSERT INTO itinerary_stops (
                    id, itinerary_day_id, attraction_id, custom_name, stop_order,
                    arrival_time, departure_time, duration_minutes, recommended_transport,
                    travel_time_from_prev, travel_distance_from_prev, cost_estimate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stop_id, day_id, stop.get('attraction_id'), stop.get('name'),
                stop.get('stop_order', 1), stop.get('arrival_time'), stop.get('departure_time'),
                stop.get('duration_minutes', 90), stop.get('recommended_transport'),
                stop.get('travel_time_mins', 0), stop.get('travel_distance_km', 0.0),
                stop.get('ticket_fee_per_person', 0.0)
            ))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Trip saved successfully', 'trip_id': trip_id}), 201

@trips_bp.route('/trips/<trip_id>', methods=['GET'])
def get_trip(trip_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
    t_row = cursor.fetchone()
    if not t_row:
        conn.close()
        return jsonify({'error': 'Trip not found'}), 404

    trip = dict(t_row)
    cursor.execute("SELECT name FROM trip_members WHERE trip_id = ?", (trip_id,))
    trip['members'] = [r['name'] for r in cursor.fetchall()]

    # Fetch days & stops
    cursor.execute("SELECT * FROM itinerary_days WHERE trip_id = ? ORDER BY day_number ASC", (trip_id,))
    days_rows = cursor.fetchall()
    days = []
    for dr in days_rows:
        day_dict = dict(dr)
        cursor.execute("""
            SELECT s.*, a.image_url, a.description, a.latitude, a.longitude
            FROM itinerary_stops s
            LEFT JOIN attractions a ON s.attraction_id = a.id
            WHERE s.itinerary_day_id = ?
            ORDER BY s.stop_order ASC
        """, (day_dict['id'],))
        day_dict['stops'] = [dict(sr) for sr in cursor.fetchall()]
        days.append(day_dict)

    trip['days'] = days
    conn.close()
    return jsonify(trip)

@trips_bp.route('/trips', methods=['GET'])
def list_trips():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips ORDER BY created_at DESC")
    trips = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'trips': trips})
