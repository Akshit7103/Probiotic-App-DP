# app.py

from flask import Flask, render_template, request, jsonify
import requests
from excel_backend import (
    get_fruit_master,
    auto_suggest_from_excel,
    calculate_blend_manual,
    _calculate_optimal_juice_amount,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/metadata", methods=["GET"])
def api_metadata():
    """Provide list of fruits for dropdowns and maybe other config."""
    fruits = get_fruit_master()
    fruit_names = [f["name"] for f in fruits]
    return jsonify({"fruits": fruit_names})


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
    data = request.get_json() or {}
    try:
        target_sweet = int(data.get("sweetness", 7))
        target_tart = int(data.get("tartness", 5))
        style = data.get("style", "").strip()
        batch_l = float(data.get("batch_l", 3))
        juice_ml_per_L = float(data.get("juice_ml_per_L", 80))
        temp_C = float(data.get("temp_C", 28))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    base = auto_suggest_from_excel(target_sweet, target_tart, style, total_juice_ml_per_L=juice_ml_per_L, batch_l=batch_l, temp_C=temp_C)

    for f in base["fruits"]:
        f["juice_ml_batch"] = round(f["juice_ml_per_L"] * batch_l, 2)

    base["batch_l"] = batch_l
    base["juice_ml_per_L"] = juice_ml_per_L
    return jsonify(base)


@app.route("/api/suggest/manual", methods=["POST"])
def api_suggest_manual():
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
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    result = calculate_blend_manual(fruits, pcts, juice_ml_per_L, batch_l, temp_C=temp_C)
    return jsonify(result)


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
