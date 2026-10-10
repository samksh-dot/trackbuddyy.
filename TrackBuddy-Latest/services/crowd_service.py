import sqlite3
from config import Config
from services.routing_service import haversine_distance

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_crowd_status(attraction_id=None):
    """
    Returns crowd indicator for attractions.
    Distinguishes transparently between live feeds, historical estimations, and demo simulations.
    """
    conn = get_db()
    cursor = conn.cursor()

    if attraction_id:
        cursor.execute("SELECT * FROM attractions WHERE id = ?", (attraction_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        attr = dict(row)
        return format_crowd_data(attr)

    cursor.execute("SELECT * FROM attractions")
    rows = cursor.fetchall()
    conn.close()
    return [format_crowd_data(dict(r)) for r in rows]

def format_crowd_data(attr):
    crowd_level = attr.get('historical_crowd_level', 'moderate')
    # Label source transparently per PRD requirement
    return {
        'attraction_id': attr['id'],
        'attraction_name': attr['name'],
        'crowd_level': crowd_level, # low, moderate, high, crowded
        'peak_hours': attr.get('crowd_peak_hours', '11:00-15:00'),
        'source': 'Archaeological Survey & Tourism Historical Footfall Model (Demo)',
        'is_live': False,
        'recommendation': get_crowd_recommendation(crowd_level, attr.get('name'))
    }

def get_crowd_recommendation(level, name):
    if level == 'crowded':
        return f"High peak congestion expected at {name}. Consider visiting early morning (before 10:00 AM) or substitute with an uncrowded heritage gem."
    elif level == 'high':
        return f"Moderate queue times expected at {name}. Pre-booking tickets or carrying student ID avoids counter delay."
    elif level == 'moderate':
        return f"Normal visitor density at {name}. Enjoyable visiting conditions."
    else:
        return f"Serene and uncrowded atmosphere at {name}. Optimal for relaxed photography and walking."

def get_crowd_alternative(attraction_id):
    """
    Finds a nearby alternative attraction with lower crowd footprint.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attractions WHERE id = ?", (attraction_id,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        return None
    
    target = dict(target)
    cursor.execute("""
        SELECT * FROM attractions 
        WHERE id != ? AND destination_id = ? AND historical_crowd_level IN ('low', 'moderate')
    """, (attraction_id, target['destination_id']))
    candidates = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not candidates:
        return None

    # Find closest alternative
    for c in candidates:
        c['distance_km'] = haversine_distance(target['latitude'], target['longitude'], c['latitude'], c['longitude'])
    
    candidates.sort(key=lambda x: x['distance_km'])
    best_alt = candidates[0]

    return {
        'original_attraction': target['name'],
        'original_crowd': target['historical_crowd_level'],
        'alternative': best_alt,
        'distance_km': best_alt['distance_km'],
        'reason': f"Swap {target['name']} (currently {target['historical_crowd_level']}) with {best_alt['name']} ({best_alt['historical_crowd_level']} crowd level, {best_alt['distance_km']} km away) to avoid heavy waiting times."
    }
