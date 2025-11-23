# app.py

from flask import Flask, render_template, request, jsonify
from excel_backend import (
    get_fruit_master,
    auto_suggest_from_excel,
    calculate_blend_manual,
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


@app.route("/api/suggest/auto", methods=["POST"])
def api_suggest_auto():
    data = request.get_json() or {}
    try:
        target_sweet = int(data.get("sweetness", 7))
        target_tart = int(data.get("tartness", 5))
        style = data.get("style", "").strip()
        batch_l = float(data.get("batch_l", 3))
        juice_ml_per_L = float(data.get("juice_ml_per_L", 80))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    base = auto_suggest_from_excel(target_sweet, target_tart, style, total_juice_ml_per_L=juice_ml_per_L)

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
