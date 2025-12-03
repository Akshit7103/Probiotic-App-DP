# app.py

from flask import Flask, render_template, request, jsonify
import requests
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from excel_backend import (
    get_fruit_master,
    auto_suggest_from_excel,
    calculate_blend_manual,
    _calculate_optimal_juice_amount,
)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Logging configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/probiotic_app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Probiotic Designer startup')
else:
    app.logger.setLevel(logging.DEBUG)


@app.route("/")
def index():
    """Render main application page."""
    return render_template("index.html")


@app.route("/health")
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test Excel file access
        fruits = get_fruit_master()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0',
            'fruits_loaded': len(fruits)
        }), 200
    except Exception as e:
        app.logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }), 503


@app.route("/api/metadata", methods=["GET"])
def api_metadata():
    """Provide list of fruits for dropdowns and maybe other config."""
    try:
        fruits = get_fruit_master()
        fruit_names = [f["name"] for f in fruits]
        app.logger.info(f'Metadata requested: {len(fruit_names)} fruits available')
        return jsonify({"fruits": fruit_names})
    except Exception as e:
        app.logger.error(f'Error loading metadata: {str(e)}')
        return jsonify({
            "error": "Failed to load fruit data",
            "message": str(e)
        }), 500


@app.route("/api/weather", methods=["POST"])
def api_weather():
    """Get current temperature for a location."""
    data = request.get_json() or {}
    lat = data.get("lat")
    lon = data.get("lon")

    try:
        if lat and lon:
            # Use wttr.in for weather data (free, no API key needed)
            url = f"https://wttr.in/{lat},{lon}?format=j1"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                weather_data = response.json()
                current = weather_data.get("current_condition", [{}])[0]

                temp_c = float(current.get("temp_C", 28))
                humidity = int(current.get("humidity", 60))
                weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")

                # Get location name
                nearest_area = weather_data.get("nearest_area", [{}])[0]
                city = nearest_area.get("areaName", [{}])[0].get("value", "Unknown")
                country = nearest_area.get("country", [{}])[0].get("value", "")

                return jsonify({
                    "success": True,
                    "temp_c": temp_c,
                    "humidity": humidity,
                    "weather": weather_desc,
                    "location": f"{city}, {country}" if country else city
                })

        # Default fallback
        return jsonify({
            "success": False,
            "temp_c": 28,
            "message": "Could not fetch weather data, using default temperature"
        })

    except requests.Timeout:
        return jsonify({
            "success": False,
            "temp_c": 28,
            "message": "Weather service timed out. Using default 28°C. You can enter your temperature manually."
        }), 200
    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "temp_c": 28,
            "message": "Weather service unavailable. Using default 28°C. Please enter manually."
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "temp_c": 28,
            "message": f"Could not detect weather. Using default 28°C."
        }), 200  # Return 200 with error message instead of failing


@app.route("/api/juice/recommend", methods=["POST"])
def api_juice_recommend():
    """Calculate optimal juice amount based on selected fruits."""
    data = request.get_json() or {}

    # Get fruits from request (support both manual mode fruit list and style-based)
    fruits = []
    if "fruits" in data:
        # Manual mode: list of selected fruits
        fruits = [f for f in data["fruits"] if f and f.strip()]
    else:
        # Could add logic for auto mode based on style
        # For now, return default
        pass

    target_sugar = float(data.get("target_sugar_g_L", 7.0))

    try:
        recommendation = _calculate_optimal_juice_amount(fruits, target_sugar)
        return jsonify({
            "success": True,
            **recommendation
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "recommended_ml_per_L": 80,
            "reasoning": f"Error calculating: {str(e)}. Using default 80 ml/L."
        }), 200


@app.route("/api/suggest/auto", methods=["POST"])
def api_suggest_auto():
    """Generate automatic blend based on preferences."""
    data = request.get_json() or {}
    try:
        target_sweet = int(data.get("sweetness", 7))
        target_tart = int(data.get("tartness", 5))
        style = data.get("style", "").strip()
        batch_l = float(data.get("batch_l", 3))
        juice_ml_per_L = float(data.get("juice_ml_per_L", 80))
        temp_C = float(data.get("temp_C", 28))

        # Validate ranges
        if not (1 <= target_sweet <= 10):
            return jsonify({"error": "Sweetness must be between 1 and 10"}), 400
        if not (1 <= target_tart <= 10):
            return jsonify({"error": "Tartness must be between 1 and 10"}), 400
        if not (0.5 <= batch_l <= 50):
            return jsonify({"error": "Batch size must be between 0.5 and 50 liters"}), 400
        if not (10 <= juice_ml_per_L <= 200):
            return jsonify({"error": "Juice amount must be between 10 and 200 ml/L"}), 400
        if not (5 <= temp_C <= 45):
            return jsonify({"error": "Temperature must be between 5 and 45°C"}), 400

    except (TypeError, ValueError) as e:
        app.logger.warning(f'Invalid input in auto suggest: {str(e)}')
        return jsonify({"error": "Invalid input format"}), 400

    try:
        base = auto_suggest_from_excel(target_sweet, target_tart, style, total_juice_ml_per_L=juice_ml_per_L, batch_l=batch_l, temp_C=temp_C)

        for f in base["fruits"]:
            f["juice_ml_batch"] = round(f["juice_ml_per_L"] * batch_l, 2)

        base["batch_l"] = batch_l
        base["juice_ml_per_L"] = juice_ml_per_L

        app.logger.info(f'Auto blend generated: sweetness={target_sweet}, tartness={target_tart}, style={style}')
        return jsonify(base)
    except Exception as e:
        app.logger.error(f'Error generating auto blend: {str(e)}')
        return jsonify({"error": "Failed to generate blend", "message": str(e)}), 500


@app.route("/api/suggest/manual", methods=["POST"])
def api_suggest_manual():
    """Calculate manual blend based on selected fruits."""
    data = request.get_json() or {}
    try:
        fruits = [
            data.get("fruit1", ""),
            data.get("fruit2", ""),
            data.get("fruit3", ""),
            data.get("fruit4", ""),
        ]
        pcts = [
            float(data.get("pct1", 0)) / 100.0,
            float(data.get("pct2", 0)) / 100.0,
            float(data.get("pct3", 0)) / 100.0,
            float(data.get("pct4", 0)) / 100.0,
        ]
        batch_l = float(data.get("batch_l", 3))
        juice_ml_per_L = float(data.get("juice_ml_per_L", 80))
        temp_C = float(data.get("temp_C", 28))

        # Validate ranges
        if not (0.5 <= batch_l <= 50):
            return jsonify({"error": "Batch size must be between 0.5 and 50 liters"}), 400
        if not (10 <= juice_ml_per_L <= 200):
            return jsonify({"error": "Juice amount must be between 10 and 200 ml/L"}), 400
        if not (5 <= temp_C <= 45):
            return jsonify({"error": "Temperature must be between 5 and 45°C"}), 400

    except (TypeError, ValueError) as e:
        app.logger.warning(f'Invalid input in manual suggest: {str(e)}')
        return jsonify({"error": "Invalid input format"}), 400

    try:
        result = calculate_blend_manual(fruits, pcts, juice_ml_per_L, batch_l, temp_C=temp_C)
        app.logger.info(f'Manual blend calculated: fruits={[f for f in fruits if f]}, batch={batch_l}L')
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'Error calculating manual blend: {str(e)}')
        return jsonify({"error": "Failed to calculate blend", "message": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(f'Server Error: {error}')
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong. Please try again later.',
        'status': 500
    }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({
        'error': 'Request too large',
        'message': 'Request size exceeds maximum allowed',
        'status': 413
    }), 413


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    # Change default port from 5000 to 8000; still overrideable via PORT env var
    port = int(os.environ.get("PORT", 8000))

    if debug_mode:
        app.logger.info(f'Starting in DEBUG mode on port {port}')
    else:
        app.logger.info(f'Starting in PRODUCTION mode on port {port}')

    app.run(debug=debug_mode, host="0.0.0.0", port=port)
