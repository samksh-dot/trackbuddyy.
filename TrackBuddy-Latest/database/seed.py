import sqlite3
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open(os.path.join(Config.BASE_DIR, 'database', 'schema.sql'), 'r', encoding='utf-8') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database schema initialized successfully.")

def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Seed Destinations (Jaipur, Manali, Mumbai, Goa, Varanasi)
    destinations_data = [
        (
            'jaipur', 'Jaipur', 'Rajasthan', 'India',
            26.9124, 75.7873,
            'The historic Pink City, famous for majestic hilltop forts, ornate royal palaces, vibrant Johari & Bapu bazaars, and rich Rajasthani heritage.',
            'https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80',
            'October to March'
        ),
        (
            'manali', 'Manali (Himachal)', 'Himachal Pradesh', 'India',
            32.2432, 77.1892,
            'Himalayan paradise surrounded by alpine cedar forests, gushing Beas river, Solang Valley adventures, Rohtang snowy heights, and Old Manali bohemian cafes.',
            'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80',
            'March to June (Summer) & Nov to Feb (Snow)'
        ),
        (
            'mumbai', 'Mumbai', 'Maharashtra', 'India',
            18.9220, 72.8347,
            'The vibrant City of Dreams on the Arabian Sea coast, famous for Marine Drive Queens Necklace, colonial Gateway of India, Bandra seaside, and coastal street food.',
            'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80',
            'November to February'
        ),
        (
            'goa', 'Goa', 'Goa', 'India',
            15.4989, 73.8278,
            'Sun-kissed coastal haven celebrated for golden sand beaches, Portuguese colonial architecture, beach shacks, water sports, and tranquil coconut groves.',
            'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80',
            'November to March'
        ),
        (
            'varanasi', 'Varanasi', 'Uttar Pradesh', 'India',
            25.3176, 82.9739,
            'The spiritual capital of India on the sacred banks of the Ganges, renowned for ancient ghats, evening Ganga Aarti, silk weavers, and winding temple alleys.',
            'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80',
            'October to March'
        )
    ]

    for dest in destinations_data:
        cursor.execute("SELECT COUNT(*) FROM destinations WHERE id = ?", (dest[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO destinations (id, name, state, country, latitude, longitude, description, image_url, best_time_to_visit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, dest)

    # 2. Seed Attractions
    attractions_data = [
        # --- JAIPUR ---
        (
            'hawa-mahal', 'jaipur', 'Hawa Mahal (Palace of Winds)', 'historical',
            'Iconic 5-story pink sandstone palace with 953 intricately carved jharokhas (windows), built in 1799 by Maharaja Sawai Pratap Singh.',
            26.9239, 75.8267, '09:00', '17:00', 50.0, 25.0, 60,
            'https://images.unsplash.com/photo-1609137144822-263f92fae3f1?auto=format&fit=crop&w=800&q=80',
            1, 'high', '10:30-14:30'
        ),
        (
            'city-palace', 'jaipur', 'City Palace', 'historical',
            'A splendid blend of Mughal and Rajput architecture featuring courtyards, gardens, Chandra Mahal, and the Maharaja Sawai Man Singh II Museum.',
            26.9258, 75.8236, '09:30', '17:00', 300.0, 150.0, 120,
            'https://images.unsplash.com/photo-1598890777032-bde835ba27c2?auto=format&fit=crop&w=800&q=80',
            0, 'high', '11:00-15:00'
        ),
        (
            'jantar-mantar', 'jaipur', 'Jantar Mantar', 'historical',
            'UNESCO World Heritage astronomical observatory built by Rajput king Sawai Jai Singh II, featuring the world stone sundial.',
            26.9248, 75.8246, '09:00', '17:00', 50.0, 15.0, 60,
            'https://images.unsplash.com/photo-1627916607164-7b20241db935?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '11:00-14:00'
        ),
        (
            'amber-fort', 'jaipur', 'Amber Fort & Palace', 'historical',
            'Magnificent hilltop fort palace overlooking Maota Lake, famous for the Sheesh Mahal (Mirror Palace) and ornate Rajput architecture.',
            26.9855, 75.8513, '08:00', '17:30', 100.0, 20.0, 150,
            'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '10:00-15:30'
        ),
        (
            'nahargarh-fort', 'jaipur', 'Nahargarh Fort', 'adventure',
            'Majestic fort standing on the edge of the Aravalli Hills, offering breathtaking panoramic sunset views over the entire Jaipur city.',
            26.9373, 75.8155, '10:00', '22:00', 50.0, 25.0, 90,
            'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=800&q=80',
            1, 'high', '16:30-18:30'
        ),
        (
            'jal-mahal', 'jaipur', 'Jal Mahal (Water Palace)', 'nature',
            'Serene palace situated right in the middle of Man Sagar Lake. Admire the stunning exterior view and lake promenade.',
            26.9535, 75.8462, '06:00', '21:00', 0.0, 0.0, 45,
            'https://images.unsplash.com/photo-1608958435020-e8a7109ba809?auto=format&fit=crop&w=800&q=80',
            1, 'low', '17:00-19:00'
        ),
        (
            'albert-hall', 'jaipur', 'Albert Hall Museum', 'museum',
            'The oldest museum of Rajasthan in Ram Niwas Garden, functioning as the state museum with fine art, carpets, sculptures, and Egyptian mummy.',
            26.9116, 75.8194, '09:00', '17:00', 40.0, 20.0, 75,
            'https://images.unsplash.com/photo-1598890777032-bde835ba27c2?auto=format&fit=crop&w=800&q=80',
            0, 'moderate', '12:00-15:00'
        ),
        (
            'bapu-bazar', 'jaipur', 'Bapu & Johari Bazaars', 'shopping',
            'Bustling traditional markets renowned for Rajasthani textiles, Jaipuri juttis, gemstones, bandhani dupattas, and authentic local street food.',
            26.9205, 75.8242, '10:30', '21:00', 0.0, 0.0, 90,
            'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '17:00-20:30'
        ),

        # --- HIMACHAL (MANALI) ---
        (
            'solang-valley', 'manali', 'Solang Valley Adventure Hub', 'adventure',
            'Spectacular valley renowned for paragliding, zorbing, quad biking, cable car ropeway, and snow slopes against Himalayan peaks.',
            32.3166, 77.1575, '09:00', '18:00', 0.0, 0.0, 150,
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '11:00-15:00'
        ),
        (
            'hadimba-temple', 'manali', 'Hadimba Devi Temple & Cedar Forest', 'historical',
            'Unique 16th-century four-tier wooden pagoda temple dedicated to Hidimba Devi, nestled amidst dense giant Deodar pine forests.',
            32.2483, 77.1809, '08:00', '18:00', 0.0, 0.0, 60,
            'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80',
            1, 'high', '11:00-14:30'
        ),
        (
            'jogini-waterfall', 'manali', 'Jogini Waterfalls Trek', 'nature',
            'Picturesque cascading waterfall reachable through an easy pine forest trail from Vashisht village with views of the snow-clad Rohtang range.',
            32.2680, 77.1950, '06:00', '18:00', 0.0, 0.0, 120,
            'https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=800&q=80',
            1, 'low', '10:00-13:00'
        ),
        (
            'old-manali-village', 'manali', 'Old Manali Village & Cafes', 'entertainment',
            'Charming vintage wooden houses, live music acoustic cafes, bakeries, handicrafts, and riverside apple orchards.',
            32.2530, 77.1770, '09:00', '22:00', 0.0, 0.0, 90,
            'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '16:00-20:00'
        ),
        (
            'vashisht-baths', 'manali', 'Vashisht Natural Hot Springs', 'nature',
            'Ancient stone temple complex famous for therapeutic natural sulfur hot water springs and scenic mountain viewpoints.',
            32.2600, 77.1910, '07:00', '20:00', 0.0, 0.0, 60,
            'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '08:00-11:00'
        ),

        # --- MUMBAI ---
        (
            'gateway-of-india', 'mumbai', 'Gateway of India & Taj Mahal Palace', 'historical',
            'Iconic 26-meter basalt arch built in 1924 overlooking the Arabian Sea, standing alongside the legendary Victorian Taj Mahal Palace hotel.',
            18.9220, 72.8347, '06:00', '23:00', 0.0, 0.0, 60,
            'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '16:30-20:00'
        ),
        (
            'marine-drive', 'mumbai', 'Marine Drive (Queens Necklace)', 'nature',
            'Sweeping 3.6-kilometer C-shaped seaside boulevard hugging the Arabian Sea, famous for scenic coastal breeze, sunset walks, and skyline lights.',
            18.9432, 72.8230, '05:00', '23:59', 0.0, 0.0, 75,
            'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '17:30-21:00'
        ),
        (
            'cst-station', 'mumbai', 'Chhatrapati Shivaji Maharaj Terminus (CSMT)', 'historical',
            'UNESCO World Heritage Victorian Gothic railway headquarters featuring carved gargoyles, stained glass windows, and grand stone dome.',
            18.9400, 72.8354, '08:00', '20:00', 0.0, 0.0, 45,
            'https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=800&q=80',
            0, 'high', '09:00-11:30'
        ),
        (
            'colaba-causeway', 'mumbai', 'Colaba Causeway Cultural Market', 'shopping',
            'Bustling street shopping artery famous for vintage jewelry, brass antiques, stylish apparel, and historic cafes like Leopold Cafe.',
            18.9217, 72.8315, '10:00', '21:30', 0.0, 0.0, 90,
            'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '16:00-19:30'
        ),
        (
            'bandra-bandstand', 'mumbai', 'Bandra Bandstand & Fort', 'entertainment',
            'Rocky seafront promenade in Bandra near Castella de Aguada Portuguese fort, Bollywood celebrity mansions, and Bandra-Worli Sea Link vista.',
            19.0435, 72.8193, '06:00', '22:00', 0.0, 0.0, 60,
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '17:00-19:30'
        ),

        # --- GOA ---
        (
            'baga-beach', 'goa', 'Baga & Calangute Beach', 'nature',
            'Vibrant golden sand shoreline offering water sports (parasailing, jet-ski), buzzing coastal shacks, seafood curries, and nightlife.',
            15.5553, 73.7517, '06:00', '23:59', 0.0, 0.0, 120,
            'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '15:00-20:00'
        ),
        (
            'aguada-fort', 'goa', 'Fort Aguada & Lighthouse', 'historical',
            'Well-preserved 17th-century Portuguese fortress and stone lighthouse overlooking the vast expanse of the Mandovi River meeting the sea.',
            15.4925, 73.7736, '09:30', '17:30', 25.0, 10.0, 75,
            'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
            1, 'high', '11:00-15:00'
        ),
        (
            'fontainhas', 'goa', 'Fontainhas Latin Quarter (Panaji)', 'historical',
            'Heritage Portuguese residential district known for narrow winding cobblestone lanes, pastel-colored colonial villas, and art galleries.',
            15.4989, 73.8278, '07:00', '21:00', 0.0, 0.0, 90,
            'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80',
            1, 'low', '09:00-12:00'
        ),
        (
            'anjuna-flea-market', 'goa', 'Anjuna Beach & Flea Market', 'shopping',
            'Legendary bohemian cliff-side beach known for red laterite rocks, vibrant hippie flea markets, handicrafts, and sunset gatherings.',
            15.5828, 73.7428, '08:00', '22:00', 0.0, 0.0, 90,
            'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '16:00-19:30'
        ),

        # --- VARANASI ---
        (
            'dashashwamedh-ghat', 'varanasi', 'Dashashwamedh Ghat & Evening Ganga Aarti', 'historical',
            'The main and oldest sacred ghat on the holy river Ganges, famous for the magnificent choreographed twilight Maha Aarti with brass lamps.',
            25.3076, 83.0104, '05:00', '23:00', 0.0, 0.0, 90,
            'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=800&q=80',
            1, 'crowded', '17:30-20:00'
        ),
        (
            'kashi-vishwanath', 'varanasi', 'Kashi Vishwanath Temple Corridor', 'historical',
            'One of the twelve revered Jyotirlinga temples dedicated to Lord Shiva, featuring gold-plated spires and modern grand pilgrim corridor.',
            25.3109, 83.0107, '04:00', '23:00', 0.0, 0.0, 75,
            'https://images.unsplash.com/photo-1598890777032-bde835ba27c2?auto=format&fit=crop&w=800&q=80',
            0, 'crowded', '06:00-12:00'
        ),
        (
            'sarnath', 'varanasi', 'Sarnath Buddhist Monument & Deer Park', 'museum',
            'Ancient sacred site where Gautama Buddha first taught the Dharma; features Dhamek Stupa, Ashoka Pillar capital, and archaeological museum.',
            25.3811, 83.0222, '09:00', '17:00', 25.0, 10.0, 120,
            'https://images.unsplash.com/photo-1627916607164-7b20241db935?auto=format&fit=crop&w=800&q=80',
            1, 'moderate', '10:00-14:00'
        ),
        (
            'assi-ghat', 'varanasi', 'Assi Ghat Morning Sunrise & Boat Tour', 'nature',
            'Tranquil southernmost ghat popular with students and yoga practitioners for sunrise Subah-e-Banaras concerts and morning wooden boat rides.',
            25.2905, 83.0064, '05:00', '22:00', 0.0, 0.0, 75,
            'https://images.unsplash.com/photo-1608958435020-e8a7109ba809?auto=format&fit=crop&w=800&q=80',
            1, 'low', '05:30-08:30'
        )
    ]

    for attr in attractions_data:
        cursor.execute("SELECT COUNT(*) FROM attractions WHERE id = ?", (attr[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO attractions (
                    id, destination_id, name, category, description,
                    latitude, longitude, opening_time, closing_time,
                    entry_fee_general, entry_fee_student, typical_duration_minutes,
                    image_url, is_outdoor, historical_crowd_level, crowd_peak_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, attr)

    # 3. Seed Hotels across all destinations with direct official website links
    hotels_data = [
        # --- JAIPUR ---
        (
            'zostel-jaipur', 'jaipur', 'Zostel Jaipur (Heritage Hostel)', 'hostel',
            'Near Hawa Mahal, First Chowk, Subhash Chowk, Pink City, Jaipur',
            26.9265, 75.8302, 650.0, 4.7, 1420,
            'Vibrant backpacking hostel walking distance from Hawa Mahal with rooftop cafe, dorms, private rooms, and student backpacker community.',
            json.dumps(['Free High-Speed Wi-Fi', 'Air Conditioning', 'Rooftop Cafe', 'Luggage Storage', '24/7 Reception', 'Female Dorms']),
            'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80',
            'https://www.zostel.com/zostel/jaipur/',
            'Moderate occupancy', 'Provider Demo Indicator (Est. 65% booked for upcoming weekend)',
            1
        ),
        (
            'moustache-jaipur', 'jaipur', 'Moustache Jaipur Hostel', 'hostel',
            'Mirza Ismail Rd, near Ganpati Plaza, Gopalbari, Jaipur',
            26.9189, 75.7954, 550.0, 4.5, 980,
            'Traditional Rajasthani decor meets modern backpacker hostel near Jaipur Railway Station. Rooftop pool and social lounge.',
            json.dumps(['Free Wi-Fi', 'Rooftop Pool', 'Cafe', 'Common Room', 'Lockers', 'Board Games']),
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80',
            'https://moustachehostel.com/destinations/jaipur/',
            'Low occupancy', 'Provider Demo Indicator (Est. 40% booked)',
            1
        ),
        (
            'hotel-pearl-palace', 'jaipur', 'Hotel Pearl Palace & Peacock Rooftop', 'budget_hotel',
            '51, Hathroi Fort, Hari Kishan Somani Marg, Ajmer Rd, Jaipur',
            26.9135, 75.7932, 1400.0, 4.6, 2150,
            'Award-winning heritage budget stay renowned for artistic antique decor, clean rooms, and the famous Peacock Rooftop Restaurant.',
            json.dumps(['Free Wi-Fi', 'Restaurant', 'Room Service', 'Airport Shuttle', 'Travel Desk', 'Air Conditioning']),
            'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80',
            'https://hotelpearlpalace.com/',
            'Nearly full', 'Provider Demo Indicator (Only 2 rooms remaining)',
            0
        ),
        (
            'rawla-rawatsar', 'jaipur', 'Rawla Rawatsar Heritage Haveli', 'heritage_haveli',
            'Rawatsar House, D-211, Bihari Marg, Bani Park, Jaipur',
            26.9272, 75.7901, 2400.0, 4.8, 620,
            'Authentic royal family-run boutique haveli in serene Bani Park with lush green lawns and traditional Rajput hospitality.',
            json.dumps(['Free Wi-Fi', 'Garden', 'Heritage Dining', 'Free Parking', 'Tea/Coffee Maker', 'Daily Breakfast']),
            'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80',
            'https://rawatsar.com/',
            'Moderate occupancy', 'Provider Demo Indicator (Est. 55% booked)',
            0
        ),

        # --- HIMACHAL (MANALI) ---
        (
            'zostel-manali', 'manali', 'Zostel Manali (Old Manali)', 'hostel',
            'Manu Temple Road, Old Manali, Himachal Pradesh',
            32.2540, 77.1755, 750.0, 4.8, 1680,
            'Scenic river-view backpacker hostel amidst apple orchards and cedar woods with garden cafe, outdoor bonfire pit, and mountain treks.',
            json.dumps(['Free High-Speed Wi-Fi', 'Mountain View Garden', 'Bonfire Nights', 'Cafe', 'Board Games', 'Shared Kitchen']),
            'https://images.unsplash.com/photo-1586611292717-f828b167408c?auto=format&fit=crop&w=800&q=80',
            'https://www.zostel.com/zostel/manali/',
            'Moderate occupancy', 'Provider Demo Indicator (Est. 60% booked)',
            1
        ),
        (
            'the-lost-tribe-manali', 'manali', 'The Lost Tribe Mountain Hostels', 'hostel',
            'Jagatsukh Village Road, Manali, Himachal Pradesh',
            32.2045, 77.2012, 590.0, 4.6, 610,
            'Rustic cedar wood alpine chalet offering student dorms, organic mountain food, river soundscapes, and stargazing.',
            json.dumps(['Free Wi-Fi', 'Organic Cafe', 'Stargazing Balcony', 'Luggage Storage', 'Heating', 'Trekking Desk']),
            'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80',
            'https://www.thelosttribehostels.com/',
            'Low occupancy', 'Provider Demo Indicator (Plentiful dorm beds available)',
            1
        ),
        (
            'johnson-lodge-manali', 'manali', 'The Johnson Lodge & Spa', 'budget_hotel',
            'Circuit House Road, Siyal, Manali, Himachal Pradesh',
            32.2470, 77.1850, 2600.0, 4.7, 940,
            'Heritage alpine lodge established in 1904 with lush lawn gardens, authentic Italian pizzeria, pine log fireplaces, and warm hospitality.',
            json.dumps(['Free Wi-Fi', 'Italian Restaurant', 'Fireplace Lounge', 'Garden', 'Room Service', 'Spa']),
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80',
            'https://www.thejohnsonlodge.com/',
            'Nearly full', 'Provider Demo Indicator (High weekend demand)',
            0
        ),

        # --- MUMBAI ---
        (
            'zostel-mumbai', 'mumbai', 'Zostel Mumbai (Andheri East)', 'hostel',
            'Karve Road, Off Military Road, Marol, Andheri East, Mumbai',
            19.1176, 72.8845, 899.0, 4.6, 1250,
            'Bustling urban hostel with Bollywood-themed street art, air-conditioned bunk pods, rooftop lounge, and quick metro transit connection.',
            json.dumps(['Free High-Speed Wi-Fi', 'Air Conditioning', 'Rooftop Cafe', 'Metro Shuttle Info', '24/7 Security', 'Lockers']),
            'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80',
            'https://www.zostel.com/zostel/mumbai/',
            'Moderate occupancy', 'Provider Demo Indicator (70% reserved)',
            1
        ),
        (
            'abode-bombay', 'mumbai', 'Abode Bombay Heritage Boutique Stay', 'budget_hotel',
            'First Floor, Lansdowne House, M.B. Marg, Apollo Bunder, Colaba, Mumbai',
            18.9228, 72.8322, 3800.0, 4.8, 890,
            'Mumbais first luxury boutique heritage hotel in Colaba, 2 minutes walk from Gateway of India with vintage art deco interiors.',
            json.dumps(['Free High-Speed Wi-Fi', 'Artisan Breakfast', 'Spa', 'Air Conditioning', 'Vintage Library', 'Airport Transfer']),
            'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80',
            'https://abodeboutiquehotels.com/',
            'Nearly full', 'Provider Demo Indicator (Limited rooms)',
            0
        ),
        (
            'hotel-suba-palace', 'mumbai', 'Hotel Suba Palace Colaba', 'budget_hotel',
            'Apollo Bunder, Near Gateway of India, Colaba, Mumbai',
            18.9235, 72.8330, 2900.0, 4.5, 1420,
            'Clean modern hotel right behind the Taj Mahal Palace, ideal base for exploring South Bombay, Marine Drive, and Fort art district.',
            json.dumps(['Free Wi-Fi', 'Buffet Breakfast', 'Air Conditioning', '24/7 Front Desk', 'Elevator', 'Tea/Coffee']),
            'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80',
            'https://www.subahotels.com/',
            'Moderate occupancy', 'Provider Demo Indicator (65% reserved)',
            0
        ),

        # --- GOA ---
        (
            'woke-hostel-arpora', 'goa', 'Woke Hostel Arpora (Heritage Villa)', 'hostel',
            'House No. 154, Diwan Bhati, Arpora, Goa',
            15.5670, 73.7650, 650.0, 4.7, 820,
            '100-year-old whitewashed Portuguese villa with a sparkling garden swimming pool, hammocks, co-working tables, and beach shuttles.',
            json.dumps(['Swimming Pool', 'Free Wi-Fi', 'Hammocks', 'Poolside Bar', 'Air Conditioning', 'Scooter Rental Desk']),
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80',
            'https://www.wokehostels.com/',
            'Low occupancy', 'Provider Demo Indicator (45% reserved)',
            1
        ),
        (
            'zostel-goa-anjuna', 'goa', 'Zostel Goa (Anjuna Beachside)', 'hostel',
            'Anjuna Flea Market Road, Dmello Vaddo, Anjuna, Goa',
            15.5780, 73.7430, 799.0, 4.8, 1950,
            'Tropical paradise hostel walking distance from Anjuna Beach, featuring palm-tree courtyards, seaside bistro, and live music nights.',
            json.dumps(['Free Wi-Fi', 'Air Conditioning', 'Beach Bistro', 'Swimming Pool', 'Lockers', 'Yoga Deck']),
            'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80',
            'https://www.zostel.com/zostel/goa-anjuna/',
            'Moderate occupancy', 'Provider Demo Indicator (68% reserved)',
            1
        ),

        # --- VARANASI ---
        (
            'zostel-varanasi', 'varanasi', 'Zostel Varanasi (Near Dashashwamedh)', 'hostel',
            'D-44/1, Ramapura Luxa Road, Varanasi, Uttar Pradesh',
            25.3090, 83.0035, 599.0, 4.7, 1340,
            'Colorfully painted backpacker hostel located in the heart of old city, 10 minutes walk to the holy ghats with rooftop common room.',
            json.dumps(['Free Wi-Fi', 'Rooftop Lounge', 'Air Conditioning', 'Walking Tour Desk', 'Board Games', 'Lockers']),
            'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80',
            'https://www.zostel.com/zostel/varanasi/',
            'Low occupancy', 'Provider Demo Indicator (50% reserved)',
            1
        ),
        (
            'brijrama-palace', 'varanasi', 'BrijRama Palace Heritage on Ganges', 'heritage_haveli',
            'Darbhanga Ghat, Dashashwamedh, Varanasi, Uttar Pradesh',
            25.3055, 83.0112, 6500.0, 4.9, 580,
            'One of the oldest historical palace havelis on Darbhanga Ghat, built in 1812. Traditional live classical Indian music and boat access.',
            json.dumps(['Ganges River View', 'Fine Dining', 'Historic Boat Transfers', 'Live Sitar Recital', 'Spa', 'Free Wi-Fi']),
            'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=800&q=80',
            'https://www.brijrama.com/',
            'Nearly full', 'Provider Demo Indicator (Only 1 suite remaining)',
            0
        )
    ]

    for h in hotels_data:
        cursor.execute("SELECT COUNT(*) FROM hotels WHERE id = ?", (h[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO hotels (
                    id, destination_id, name, type, address,
                    latitude, longitude, price_per_night, rating, review_count,
                    review_summary, amenities, image_url, booking_url,
                    occupancy_status, occupancy_source, student_discount_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, h)
        else:
            # Update booking URL to ensure direct official links are present
            cursor.execute("UPDATE hotels SET booking_url = ?, destination_id = ? WHERE id = ?", (h[13], h[1], h[0]))

    # 4. Seed Reviews
    reviews_data = [
        ('zostel-jaipur', 'Aakash Verma', 5.0, 4.8, 5.0, 4.9, 5.0, '2026-02-14', 'Stayed with 3 college friends for 2 nights. Very clean dorms, fast wifi, and it takes just 7 minutes to walk to Hawa Mahal! Super budget-friendly for students.', 'Verified Demo Dataset (Student Traveler)'),
        ('zostel-jaipur', 'Pooja Sharma', 4.5, 4.5, 4.8, 4.5, 4.6, '2026-01-20', 'Great vibe and rooftop cafe. Met fellow solo travelers. Staff assisted with auto fare guidelines to Amber Fort.', 'Verified Demo Dataset (Solo Explorer)'),
        ('zostel-manali', 'Rishabh Dogra', 5.0, 4.9, 4.8, 5.0, 4.8, '2026-03-02', 'Waking up to snow peaks and river sounds in Old Manali is priceless. The garden cafe serves stellar shakshuka and chai.', 'Verified Demo Dataset (Backpacker)'),
        ('zostel-mumbai', 'Tanvi Mehta', 4.5, 4.7, 4.2, 4.5, 4.6, '2026-02-18', 'Great hostel pods with air conditioning in Mumbai heat. Very convenient for budget travel with Metro station nearby.', 'Verified Demo Dataset (Solo Explorer)'),
        ('woke-hostel-arpora', 'Samir Kulkarni', 4.8, 4.6, 4.7, 4.9, 4.9, '2026-02-25', 'Portuguese villa with pool is magical. Rented scooters right from reception to visit Anjuna and Vagator.', 'Verified Demo Dataset (Group of Friends)'),
        ('zostel-varanasi', 'Arjun Sen', 4.7, 4.5, 4.9, 4.8, 4.7, '2026-01-29', 'Just a short walk to Dashashwamedh Ghat for Ganga Aarti. The rooftop view of the ghats at dawn is unforgettable.', 'Verified Demo Dataset (Heritage Explorer)')
    ]

    for rev in reviews_data:
        cursor.execute("SELECT COUNT(*) FROM hotel_reviews WHERE hotel_id = ? AND author_name = ?", (rev[0], rev[1]))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO hotel_reviews (
                    hotel_id, author_name, rating, cleanliness_rating, location_rating,
                    service_rating, value_rating, review_date, excerpt, source_attribution
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rev)

    # 5. Seed Student Discounts across regions
    discounts_data = [
        (
            'rajasthan-archaeology-concession', 'jaipur',
            'Department of Archaeology & Museums, Govt. of Rajasthan',
            'attraction',
            'Rajasthan State Monuments Student Concession (Amber, Hawa Mahal, Nahargarh, Albert Hall, Jantar Mantar)',
            'Up to 75% to 80% discount on standard entry tickets (e.g. Amber Fort ₹20 instead of ₹100, Hawa Mahal ₹25 instead of ₹50, Jantar Mantar ₹15 instead of ₹50). Combined student composite ticket available for ₹100 covering 8 key monuments for 2 days.',
            'Regular bona fide student currently enrolled in recognized Indian school/college/university.',
            'Original physical Student Identity Card issued by recognized college/university with photo and current academic year validity.',
            'Not applicable for foreign university student cards unless accompanied by ISIC.',
            'https://artandculture.rajasthan.gov.in',
            '2026-01-15',
            1
        ),
        (
            'himachal-state-museum-pass', 'manali',
            'Himachal Tourism & Forest Department',
            'attraction',
            'Himalayan Wildlife & Heritage Student Pass',
            'Free entry to Manali Nature Park and 50% discount on Solang Valley cultural museum tickets.',
            'Valid College or School students.',
            'Institutional ID card.',
            'Available on spot ticket window.',
            'https://himachaltourism.gov.in',
            '2026-02-12',
            1
        ),
        (
            'mumbai-cst-heritage-student', 'mumbai',
            'Central Railway Heritage Gallery',
            'attraction',
            'CSMT Railway Heritage Museum Student Pass',
            'Concession rate ₹50 (instead of ₹150) for students to tour the grand Victorian Gothic CSMT architectural halls.',
            'Students aged 16-25.',
            'College Student ID card.',
            'Booked at CSMT Heritage counter weekdays 14:00-17:00.',
            'https://cr.indianrailways.gov.in',
            '2026-01-20',
            1
        ),
        (
            'goa-museum-archaeology', 'goa',
            'Archaeological Survey of India (ASI Goa Circle)',
            'attraction',
            'ASI Fort Aguada & Old Goa Churches Student Concession',
            'Discounted entry at ₹10 (instead of ₹25) for all ASI protected historical forts and monuments across North and South Goa.',
            'Students of recognized institutions.',
            'Valid Student ID.',
            'Available online via ASI monument portal or physical ticket booths.',
            'https://asi.nic.in',
            '2026-02-01',
            1
        ),
        (
            'varanasi-sarnath-concession', 'varanasi',
            'Archaeological Survey of India (ASI Sarnath)',
            'attraction',
            'Sarnath Excavated Remains & Museum Student Pass',
            'Entry ₹10 (vs ₹25) for Sarnath Buddhist archaeological park and museum.',
            'Students with valid institution credentials.',
            'Physical College ID card.',
            'Applicable daily from sunrise to sunset.',
            'https://asi.nic.in',
            '2026-02-15',
            1
        )
    ]

    for disc in discounts_data:
        cursor.execute("SELECT COUNT(*) FROM discounts WHERE id = ?", (disc[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO discounts (
                    id, destination_id, provider_name, applicable_category, title,
                    discount_details, eligibility_requirements, required_id,
                    restrictions, official_source_url, last_verified_date, is_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, disc)

    conn.commit()
    conn.close()
    print("Database seeded with Multi-Destination Hubs: Jaipur, Manali (Himachal), Mumbai, Goa, and Varanasi!")

if __name__ == '__main__':
    init_db()
    seed_db()
