from flask import Blueprint, request, jsonify
from services.transport_service import compare_transport_modes
from services.routing_service import get_route_osrm

transport_bp = Blueprint('transport', __name__, url_prefix='/api')

@transport_bp.route('/transport/compare', methods=['POST'])
def compare_transport():
    data = request.get_json() or {}
    try:
        origin_lat = float(data.get('origin_lat', 26.9124))
        origin_lon = float(data.get('origin_lon', 75.7873))
        dest_lat = float(data.get('dest_lat', 26.9855))
        dest_lon = float(data.get('dest_lon', 75.8513))
        travelers = int(data.get('travelers', 4))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid geographic coordinates'}), 400

    options = compare_transport_modes(origin_lat, origin_lon, dest_lat, dest_lon, travelers)
    return jsonify({
        'origin': [origin_lat, origin_lon],
        'destination': [dest_lat, dest_lon],
        'travelers': travelers,
        'options': options
    })

@transport_bp.route('/routes', methods=['GET'])
def get_route_data():
    try:
        start_lat = float(request.args.get('start_lat', 26.9124))
        start_lon = float(request.args.get('start_lon', 75.7873))
        end_lat = float(request.args.get('end_lat', 26.9855))
        end_lon = float(request.args.get('end_lon', 75.8513))
        mode = request.args.get('mode', 'driving')
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid coordinates provided'}), 400

    route_info = get_route_osrm(start_lat, start_lon, end_lat, end_lon, mode)
    return jsonify(route_info)
