-- TrackBuddy SQLite Schema
PRAGMA foreign_keys = ON;

-- Trips table
CREATE TABLE IF NOT EXISTS trips (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_location TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    travelers_count INTEGER NOT NULL DEFAULT 1,
    budget_total REAL NOT NULL DEFAULT 0.0,
    budget_per_person REAL NOT NULL DEFAULT 0.0,
    travel_preference TEXT DEFAULT 'balanced', -- cheapest, fastest, balanced, comfortable, crowd-avoiding
    transport_modes TEXT, -- JSON array of strings
    interests TEXT, -- JSON array of strings
    is_student BOOLEAN DEFAULT 0,
    accommodation_pref TEXT DEFAULT 'standard',
    walking_tolerance TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trip Members (for group expense splitting)
CREATE TABLE IF NOT EXISTS trip_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY(trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Destinations table
CREATE TABLE IF NOT EXISTS destinations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    description TEXT,
    image_url TEXT,
    best_time_to_visit TEXT
);

-- Attractions table
CREATE TABLE IF NOT EXISTS attractions (
    id TEXT PRIMARY KEY,
    destination_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL, -- historical, nature, shopping, museum, adventure, entertainment, food
    description TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    opening_time TEXT, -- HH:MM
    closing_time TEXT, -- HH:MM
    entry_fee_general REAL NOT NULL DEFAULT 0.0,
    entry_fee_student REAL NOT NULL DEFAULT 0.0,
    typical_duration_minutes INTEGER NOT NULL DEFAULT 90,
    image_url TEXT,
    is_outdoor BOOLEAN DEFAULT 1,
    historical_crowd_level TEXT DEFAULT 'moderate', -- low, moderate, high, crowded
    crowd_peak_hours TEXT, -- e.g. "11:00-15:00"
    FOREIGN KEY(destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- Itinerary Days
CREATE TABLE IF NOT EXISTS itinerary_days (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    day_number INTEGER NOT NULL,
    date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY(trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Itinerary Stops
CREATE TABLE IF NOT EXISTS itinerary_stops (
    id TEXT PRIMARY KEY,
    itinerary_day_id TEXT NOT NULL,
    attraction_id TEXT,
    custom_name TEXT,
    stop_order INTEGER NOT NULL,
    arrival_time TEXT,
    departure_time TEXT,
    duration_minutes INTEGER,
    recommended_transport TEXT, -- walking, cab, bus, auto, metro
    travel_time_from_prev INTEGER DEFAULT 0, -- in minutes
    travel_distance_from_prev REAL DEFAULT 0.0, -- in km
    cost_estimate REAL DEFAULT 0.0,
    weather_note TEXT,
    crowd_status TEXT, -- low, moderate, high
    crowd_source TEXT, -- "Demo/Historical", "Simulated", "Live"
    FOREIGN KEY(itinerary_day_id) REFERENCES itinerary_days(id) ON DELETE CASCADE,
    FOREIGN KEY(attraction_id) REFERENCES attractions(id) ON DELETE SET NULL
);

-- Hotels table
CREATE TABLE IF NOT EXISTS hotels (
    id TEXT PRIMARY KEY,
    destination_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- hostel, budget_hotel, heritage_haveli, guesthouse, luxury_resort
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    price_per_night REAL NOT NULL,
    rating REAL NOT NULL,
    review_count INTEGER NOT NULL DEFAULT 0,
    review_summary TEXT,
    amenities TEXT, -- JSON array of strings
    image_url TEXT,
    booking_url TEXT,
    occupancy_status TEXT DEFAULT 'Unknown', -- Low occupancy, Moderate occupancy, High occupancy, Nearly full, Unknown
    occupancy_source TEXT DEFAULT 'Provider Demo Indicator',
    student_discount_available BOOLEAN DEFAULT 0,
    FOREIGN KEY(destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- Hotel Reviews (curated / demo with transparent attribution)
CREATE TABLE IF NOT EXISTS hotel_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id TEXT NOT NULL,
    author_name TEXT NOT NULL,
    rating REAL NOT NULL,
    cleanliness_rating REAL,
    location_rating REAL,
    service_rating REAL,
    value_rating REAL,
    review_date TEXT,
    excerpt TEXT NOT NULL,
    source_attribution TEXT NOT NULL, -- "Verified Demo Dataset"
    FOREIGN KEY(hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
);

-- Student Discounts
CREATE TABLE IF NOT EXISTS discounts (
    id TEXT PRIMARY KEY,
    destination_id TEXT,
    provider_name TEXT NOT NULL,
    applicable_category TEXT NOT NULL, -- attraction, transport, accommodation, museum
    title TEXT NOT NULL,
    discount_details TEXT NOT NULL,
    eligibility_requirements TEXT NOT NULL,
    required_id TEXT NOT NULL, -- e.g. "Valid College Student ID Card with current year stamp"
    restrictions TEXT,
    official_source_url TEXT,
    last_verified_date TEXT,
    is_verified BOOLEAN DEFAULT 1,
    FOREIGN KEY(destination_id) REFERENCES destinations(id) ON DELETE SET NULL
);

-- Group Expenses
CREATE TABLE IF NOT EXISTS expenses (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    category TEXT NOT NULL, -- Intercity Transport, Local Transport, Accommodation, Attraction Tickets, Food, Miscellaneous
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    paid_by TEXT NOT NULL, -- member name
    split_type TEXT DEFAULT 'equal', -- equal or custom
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Expense Splits
CREATE TABLE IF NOT EXISTS expense_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id TEXT NOT NULL,
    member_name TEXT NOT NULL,
    amount_owed REAL NOT NULL,
    FOREIGN KEY(expense_id) REFERENCES expenses(id) ON DELETE CASCADE
);

-- Provider Cache table for caching weather or routing responses
CREATE TABLE IF NOT EXISTS provider_cache (
    cache_key TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL
);
