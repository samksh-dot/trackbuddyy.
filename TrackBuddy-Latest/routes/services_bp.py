import uuid
import sqlite3
from flask import Blueprint, request, jsonify
from config import Config
from services.budget_service import calculate_trip_budget, calculate_group_split_balances
from services.discount_service import get_student_discounts
from services.weather_service import get_weather
from services.crowd_service import get_crowd_status, get_crowd_alternative
from services.ai_service import process_ai_query

services_bp = Blueprint('services', __name__, url_prefix='/api')

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 1. Budget Endpoints
@services_bp.route('/budget/calculate', methods=['POST'])
def calculate_budget():
    data = request.get_json() or {}
    travelers = data.get('travelers_count', 4)
    days = data.get('days_count', 2)
    intercity = data.get('intercity_transit', 0.0)
    hotel_price = data.get('hotel_price_per_night', 650.0)
    rooms = data.get('rooms_count', 1)
    local_transit = data.get('local_transit_est', 400.0)
    tickets = data.get('attraction_tickets_per_person', 150.0)
    food = data.get('daily_food_per_person', 350.0)
    misc = data.get('misc_per_person', 100.0)
    discount = data.get('student_discount_total', 0.0)

    result = calculate_trip_budget(
        travelers_count=travelers,
        days_count=days,
        intercity_transit=intercity,
        hotel_price_per_night=hotel_price,
        rooms_count=rooms,
        local_transit_est=local_transit,
        attraction_tickets_per_person=tickets,
        daily_food_per_person=food,
        misc_per_person=misc,
        student_discount_total=discount
    )
    return jsonify(result)

# 2. Expenses Endpoints
@services_bp.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json() or {}
    trip_id = data.get('trip_id')
    category = data.get('category', 'Food')
    desc = data.get('description', '')
    amount = float(data.get('amount', 0.0))
    paid_by = data.get('paid_by', 'Aarav')

    if not trip_id:
        return jsonify({'error': 'trip_id is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    exp_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO expenses (id, trip_id, category, description, amount, paid_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (exp_id, trip_id, category, desc, amount, paid_by))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Expense recorded', 'expense_id': exp_id}), 201

@services_bp.route('/expenses/summary', methods=['GET'])
def get_expenses_summary():
    trip_id = request.args.get('trip_id')
    if not trip_id:
        return jsonify({'error': 'trip_id is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE trip_id = ? ORDER BY created_at DESC", (trip_id,))
    expenses = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT name FROM trip_members WHERE trip_id = ?", (trip_id,))
    members = [r['name'] for r in cursor.fetchall()]
    conn.close()

    if not members and expenses:
        members = list(set(e['paid_by'] for e in expenses))

    summary = calculate_group_split_balances(expenses, members)
    summary['expenses'] = expenses
    return jsonify(summary)

# 3. Discounts
@services_bp.route('/discounts', methods=['GET'])
def discounts():
    dest = request.args.get('destination_id', 'jaipur')
    cat = request.args.get('category')
    disc_list = get_student_discounts(dest, cat)
    return jsonify({'discounts': disc_list})

# 4. Weather
@services_bp.route('/weather', methods=['GET'])
def weather_endpoint():
    try:
        lat = float(request.args.get('lat', 26.9124))
        lon = float(request.args.get('lon', 75.7873))
    except (ValueError, TypeError):
        lat, lon = 26.9124, 75.7873
    date_str = request.args.get('date')
    w_data = get_weather(lat, lon, date_str)
    return jsonify(w_data)

# 5. Crowd
@services_bp.route('/crowd', methods=['GET'])
def crowd_endpoint():
    attr_id = request.args.get('attraction_id')
    if attr_id:
        c = get_crowd_status(attr_id)
        alt = get_crowd_alternative(attr_id)
        return jsonify({'crowd': c, 'alternative_suggestion': alt})
    all_c = get_crowd_status()
    return jsonify({'attractions_crowd': all_c})

# 6. AI Assistant
@services_bp.route('/assistant/chat', methods=['POST'])
def assistant_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    trip_context = data.get('trip_context')
    reply = process_ai_query(message, trip_context)
    return jsonify(reply)
