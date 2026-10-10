import os
from flask import Flask, render_template, jsonify
from config import Config
from database.seed import init_db, seed_db

from routes.trips import trips_bp
from routes.transport import transport_bp
from routes.hotels import hotels_bp
from routes.services_bp import services_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize DB if not present
    if not os.path.exists(Config.DATABASE):
        with app.app_context():
            init_db()
            seed_db()

    # Register API Blueprints
    app.register_blueprint(trips_bp)
    app.register_blueprint(transport_bp)
    app.register_blueprint(hotels_bp)
    app.register_blueprint(services_bp)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'app': 'TrackBuddy',
            'version': '1.0.0-hackathon',
            'weather_provider': Config.WEATHER_PROVIDER,
            'routing_provider': Config.ROUTING_PROVIDER,
            'demo_mode': Config.DEMO_MODE
        })

    # Frontend View Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/planner')
    def planner():
        return render_template('planner.html')

    @app.route('/itinerary')
    def itinerary():
        return render_template('itinerary.html')

    @app.route('/hotels')
    def hotels_view():
        return render_template('hotels.html')

    @app.route('/hotels/<hotel_id>')
    def hotel_detail_view(hotel_id):
        return render_template('hotel_detail.html', hotel_id=hotel_id)

    @app.route('/transport')
    def transport_view():
        return render_template('transport.html')

    @app.route('/discounts')
    def discounts_view():
        return render_template('discounts.html')

    @app.route('/weather')
    def weather_view():
        return render_template('weather.html')

    @app.route('/expenses')
    def expenses_view():
        return render_template('expenses.html')

    @app.route('/saved-trips')
    def saved_trips_view():
        return render_template('saved_trips.html')

    @app.route('/assistant')
    def assistant_view():
        return render_template('assistant.html')

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
