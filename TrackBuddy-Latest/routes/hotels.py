from flask import Blueprint, request, jsonify
from services.hotel_service import search_hotels, get_hotel_details

hotels_bp = Blueprint('hotels', __name__, url_prefix='/api')

@hotels_bp.route('/hotels/search', methods=['GET'])
def search():
    dest_id = request.args.get('destination_id', 'jaipur')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    hotel_type = request.args.get('type')
    near_lat = request.args.get('near_lat', type=float)
    near_lon = request.args.get('near_lon', type=float)
    student_only = request.args.get('student_only', 'false').lower() == 'true'
    sort_by = request.args.get('sort_by', 'best_match')

    hotels = search_hotels(
        destination_id=dest_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        hotel_type=hotel_type,
        near_lat=near_lat,
        near_lon=near_lon,
        student_only=student_only,
        sort_by=sort_by
    )
    return jsonify({'hotels': hotels})

@hotels_bp.route('/hotels/<hotel_id>', methods=['GET'])
def details(hotel_id):
    hotel = get_hotel_details(hotel_id)
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404
    return jsonify(hotel)

@hotels_bp.route('/hotels/<hotel_id>/reviews', methods=['GET'])
def reviews(hotel_id):
    hotel = get_hotel_details(hotel_id)
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404
    return jsonify({
        'hotel_id': hotel_id,
        'hotel_name': hotel['name'],
        'reviews': hotel.get('reviews', [])
    })

@hotels_bp.route('/hotels/<hotel_id>/occupancy', methods=['GET'])
def occupancy(hotel_id):
    hotel = get_hotel_details(hotel_id)
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404
    return jsonify({
        'hotel_id': hotel_id,
        'occupancy_status': hotel.get('occupancy_status', 'Unknown'),
        'occupancy_source': hotel.get('occupancy_source', 'Provider Indicator'),
        'notice': 'Live hotel occupancy data requires direct hospitality PMS integration. Status is based on sample provider availability.'
    })
