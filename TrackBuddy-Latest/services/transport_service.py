from services.routing_service import haversine_distance

def compare_transport_modes(origin_lat, origin_lon, dest_lat, dest_lon, travelers=4):
    """
    Compares transport options for a specific leg of the journey:
    - Walking (free)
    - Auto-Rickshaw / E-Rickshaw
    - Cab / Taxi (Uber/Ola equivalent pricing for 4-seater hatchback/sedan)
    - Public City Bus (JCTSL / City Bus)
    - Metro (Jaipur Metro Pink Line where route aligns)
    """
    dist_km = haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    options = []

    # 1. Walking
    walk_time = max(2, round((dist_km / 4.5) * 60))
    options.append({
        'mode': 'Walking',
        'icon': 'walk',
        'is_recommended': dist_km <= 1.2,
        'distance_km': dist_km,
        'travel_time_mins': walk_time,
        'total_fare': 0.0,
        'per_person_fare': 0.0,
        'availability': 'Always available',
        'convenience_score': 5 if dist_km <= 1.0 else (3 if dist_km <= 2.0 else 1),
        'source': 'Self-guided pedestrian navigation',
        'note': 'Best for heritage inner Pink City alleys and bazaars.' if dist_km <= 1.5 else 'Consider wheels for longer stretches in warm afternoons.'
    })

    # 2. E-Rickshaw / Auto-Rickshaw (Indian heritage city staple)
    # Typical tariff: base ₹30 for first 1.5 km, then ₹12/km
    auto_base = 35.0
    auto_fare = auto_base + max(0.0, dist_km - 1.5) * 14.0
    auto_fare = round(auto_fare / 10) * 10 # round to nearest 10
    auto_fare = max(40.0, auto_fare)
    auto_time = max(4, round((dist_km / 22.0) * 60) + 3) # traffic factor
    
    # 1 auto seats 3 comfortably, 4 for college students often share or take 1-2 autos
    auto_vehicles_needed = 1 if travelers <= 3 else (1 if travelers == 4 else (travelers + 2) // 3)
    total_auto_fare = auto_fare * auto_vehicles_needed
    
    options.append({
        'mode': 'Auto-Rickshaw',
        'icon': 'auto',
        'is_recommended': 1.0 < dist_km <= 6.0 and travelers <= 4,
        'distance_km': dist_km,
        'travel_time_mins': auto_time,
        'total_fare': total_auto_fare,
        'per_person_fare': round(total_auto_fare / travelers, 1),
        'availability': 'High (Street hail & stand)',
        'convenience_score': 4,
        'source': 'Regional Transport Authority (RTA) Fare Table Estimate',
        'note': f'Traditional 3-wheeler. Negotiate or insist on meter. Seats up to {3 if travelers > 3 else travelers} travelers.'
    })

    # 3. Cab / App Taxi (Uber Go / Ola Mini equivalent)
    # Base ₹60 + ₹16/km + GST
    cab_fare = max(110.0, round(60.0 + (dist_km * 16.5)))
    cab_time = max(5, round((dist_km / 26.0) * 60) + 4)
    # 4-seater cab holds 4 passengers
    cabs_needed = (travelers + 3) // 4
    total_cab_fare = cab_fare * cabs_needed

    options.append({
        'mode': 'Cab / App Taxi',
        'icon': 'car',
        'is_recommended': dist_km > 5.0 or travelers >= 4,
        'distance_km': dist_km,
        'travel_time_mins': cab_time,
        'total_fare': total_cab_fare,
        'per_person_fare': round(total_cab_fare / travelers, 1),
        'availability': 'On-demand (Uber / Ola / Local Taxi Stand)',
        'convenience_score': 5,
        'source': 'Aggregator Standard Fare Model Estimate',
        'note': 'AC 4-seater hatchback/sedan. Very economical when split across 4 friends.'
    })

    # 4. City Bus (JCTSL Low Floor Bus)
    # Typical bus fare in Jaipur: ₹10 to ₹25 per person
    bus_ticket = 10.0 if dist_km <= 3.0 else (15.0 if dist_km <= 8.0 else 25.0)
    bus_time = max(10, round((dist_km / 18.0) * 60) + 12) # bus stops & waiting
    total_bus_fare = bus_ticket * travelers

    options.append({
        'mode': 'City Bus (JCTSL)',
        'icon': 'bus',
        'is_recommended': False, # slower for tourist short hops
        'distance_km': dist_km,
        'travel_time_mins': bus_time,
        'total_fare': total_bus_fare,
        'per_person_fare': bus_ticket,
        'availability': 'Every 15-20 mins (Route dependent)',
        'convenience_score': 2,
        'source': 'Jaipur City Transport Services Limited (JCTSL) Fare Chart',
        'note': 'Cheapest public transit for budget travelers along main arterial roads.'
    })

    # 5. Metro (Jaipur Metro - Mansarovar to Badi Chaupar)
    # If points are within downtown Pink City corridor (lat ~26.91-26.93, lon ~75.76-75.83)
    near_metro = (26.90 <= origin_lat <= 26.94 and 75.75 <= origin_lon <= 75.83) and \
                 (26.90 <= dest_lat <= 26.94 and 75.75 <= dest_lon <= 75.83)
    if near_metro and dist_km >= 2.0:
        metro_ticket = 12.0 if dist_km <= 4.0 else 18.0
        metro_time = max(8, round((dist_km / 35.0) * 60) + 8) # boarding + ride
        options.append({
            'mode': 'Jaipur Metro',
            'icon': 'subway',
            'is_recommended': True,
            'distance_km': dist_km,
            'travel_time_mins': metro_time,
            'total_fare': metro_ticket * travelers,
            'per_person_fare': metro_ticket,
            'availability': 'Runs every 7-10 minutes (06:20 to 22:00)',
            'convenience_score': 4,
            'source': 'Jaipur Metro Rail Corporation (JMRC) Schedule & Fare Card',
            'note': 'Fast, air-conditioned, beats peak bazaar traffic directly to Badi Chaupar / Chhoti Chaupar.'
        })

    # Sort options: default order or best overall
    return options
