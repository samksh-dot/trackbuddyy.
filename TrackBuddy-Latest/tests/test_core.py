import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.budget_service import calculate_trip_budget, calculate_group_split_balances

from services.routing_service import haversine_distance, optimize_stop_sequence
from services.itinerary_service import generate_smart_itinerary
from services.transport_service import compare_transport_modes
from services.hotel_service import search_hotels
from services.discount_service import get_student_discounts
from services.ai_service import process_ai_query
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_haversine_distance():
    # Distance between Jaipur Railway Station and Amber Fort (~10 km)
    dist = haversine_distance(26.9189, 75.7885, 26.9855, 75.8513)
    assert 9.0 <= dist <= 12.0

def test_budget_calculations():
    # 4 students, 2 days, hostel ₹650 x 1 night x 4 beds = 2600
    res = calculate_trip_budget(
        travelers_count=4,
        days_count=2,
        hotel_price_per_night=650.0,
        rooms_count=4,
        local_transit_est=480.0,
        attraction_tickets_per_person=100.0, # 400 total
        daily_food_per_person=350.0, # 350 * 2 * 4 = 2800
        misc_per_person=100.0, # 400
        student_discount_total=1000.0
    )
    # Subtotal = 2600 + 480 + 0 + 400 + 2800 + 400 = 6680
    # Total = 6680 - 1000 = 5680
    assert res['total_cost'] == 5680.0
    assert res['per_person_cost'] == 1420.0
    assert res['travelers_count'] == 4

def test_group_expense_splitting():
    members = ['Aarav', 'Neha', 'Kabir', 'Riya']
    expenses = [
        {'paid_by': 'Aarav', 'amount': 1000},
        {'paid_by': 'Neha', 'amount': 200},
        {'paid_by': 'Kabir', 'amount': 0},
        {'paid_by': 'Riya', 'amount': 0}
    ]
    # Total = 1200, Fair share = 300 each
    res = calculate_group_split_balances(expenses, members)
    assert res['total_spent'] == 1200.0
    assert res['per_person_share'] == 300.0
    assert res['member_balances']['Aarav'] == 700.0 # +700
    assert res['member_balances']['Neha'] == -100.0 # -100
    assert res['member_balances']['Kabir'] == -300.0 # -300
    assert res['member_balances']['Riya'] == -300.0 # -300
    assert len(res['settlements']) > 0

def test_itinerary_generation():
    itinerary = generate_smart_itinerary(
        destination_id='jaipur',
        start_date='2026-10-15',
        end_date='2026-10-16',
        travelers_count=4,
        preference='balanced',
        is_student=True
    )
    assert len(itinerary['days']) == 2
    assert len(itinerary['days'][0]['stops']) > 0
    assert itinerary['is_student'] is True

def test_transport_comparison():
    options = compare_transport_modes(26.9189, 75.7885, 26.9855, 75.8513, travelers=4)
    assert len(options) >= 3
    modes = [o['mode'] for o in options]
    assert 'Walking' in modes
    assert 'Auto-Rickshaw' in modes
    assert 'Cab / App Taxi' in modes

def test_student_discounts():
    discs = get_student_discounts('jaipur')
    assert len(discs) > 0
    # Must have Rajasthan monuments concession
    found = any('Rajasthan State Monuments' in d['title'] for d in discs)
    assert found is True

def test_ai_fallback_grounding():
    # Verify AI assistant provides accurate grounded response even when Ollama is offline
    query = "Plan a two-day trip to Jaipur for four college students under 6000"
    res = process_ai_query(query)
    assert "Jaipur" in res['response']
    assert len(res['response']) > 100

def test_api_health_endpoint(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'
    assert data['app'] == 'TrackBuddy'

def test_api_hotels_search(client):
    res = client.get('/api/hotels/search?destination_id=jaipur')
    assert res.status_code == 200
    data = res.get_json()
    assert 'hotels' in data
    assert len(data['hotels']) >= 3
