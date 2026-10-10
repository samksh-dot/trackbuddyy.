import json
import sqlite3
from config import Config
from services.routing_service import haversine_distance

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def search_hotels(destination_id='jaipur', min_price=None, max_price=None, min_rating=None, hotel_type=None, near_lat=None, near_lon=None, student_only=False, sort_by='best_match'):
    """
    Search and filter hotels near destination or specific attractions.
    """
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM hotels WHERE destination_id = ?"
    params = [destination_id]

    if min_price is not None:
        query += " AND price_per_night >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price_per_night <= ?"
        params.append(max_price)
    if min_rating is not None:
        query += " AND rating >= ?"
        params.append(min_rating)
    if hotel_type:
        query += " AND type = ?"
        params.append(hotel_type)
    if student_only:
        query += " AND student_discount_available = 1"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    hotels = []
    for r in rows:
        h = dict(r)
        if isinstance(h.get('amenities'), str):
            try:
                h['amenities'] = json.loads(h['amenities'])
            except:
                h['amenities'] = []
        
        # Calculate distance from reference location if provided
        if near_lat is not None and near_lon is not None:
            h['distance_from_point_km'] = haversine_distance(near_lat, near_lon, h['latitude'], h['longitude'])
        else:
            h['distance_from_point_km'] = None

        hotels.append(h)

    conn.close()

    # Sorting
    if sort_by == 'cheapest':
        hotels.sort(key=lambda x: x['price_per_night'])
    elif sort_by == 'highest_rated':
        hotels.sort(key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'closest' and near_lat is not None:
        hotels.sort(key=lambda x: x.get('distance_from_point_km') or 999)
    else: # best_match: balance of rating and price
        hotels.sort(key=lambda x: (x['rating'] / max(1, x['price_per_night'] / 500)), reverse=True)

    return hotels

def get_hotel_details(hotel_id):
    """
    Get hotel by ID including its transparently attributed reviews.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hotels WHERE id = ?", (hotel_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    hotel = dict(row)
    if isinstance(hotel.get('amenities'), str):
        try:
            hotel['amenities'] = json.loads(hotel['amenities'])
        except:
            hotel['amenities'] = []

    cursor.execute("SELECT * FROM hotel_reviews WHERE hotel_id = ? ORDER BY review_date DESC", (hotel_id,))
    reviews = [dict(r) for r in cursor.fetchall()]

    conn.close()

    hotel['reviews'] = reviews
    return hotel
