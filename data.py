# data.py

FRUITS = [
    # name, sugar_g_per_100ml, sweetness(1-10), tartness(1-10), style tags
    {"name": "Apple",       "sugar": 10.0, "sweet": 7, "tart": 3, "styles": ["neutral", "apple", "balanced"]},
    {"name": "Orange",      "sugar": 8.5,  "sweet": 6, "tart": 5, "styles": ["citrus", "bright"]},
    {"name": "Pineapple",   "sugar": 10.0, "sweet": 7, "tart": 6, "styles": ["tropical", "bright"]},
    {"name": "Grape",       "sugar": 15.0, "sweet": 8, "tart": 3, "styles": ["sweet", "grape"]},
    {"name": "Watermelon",  "sugar": 6.0,  "sweet": 5, "tart": 2, "styles": ["refreshing", "neutral"]},
    {"name": "Pomegranate", "sugar": 13.0, "sweet": 7, "tart": 7, "styles": ["red", "tannic"]},
    {"name": "Mango",       "sugar": 14.0, "sweet": 9, "tart": 3, "styles": ["tropical", "mango"]},
    {"name": "Lemon",       "sugar": 2.5,  "sweet": 2, "tart": 9, "styles": ["citrus", "acid"]},
    {"name": "Lime",        "sugar": 2.0,  "sweet": 2, "tart": 9, "styles": ["citrus", "acid"]},
    {"name": "Blueberry",   "sugar": 10.0, "sweet": 6, "tart": 4, "styles": ["berry", "premium"]},
    {"name": "Strawberry",  "sugar": 5.0,  "sweet": 5, "tart": 4, "styles": ["berry", "aromatic"]},
    {"name": "Raspberry",   "sugar": 4.0,  "sweet": 4, "tart": 6, "styles": ["berry", "tart"]},
    {"name": "Cherry",      "sugar": 13.0, "sweet": 7, "tart": 5, "styles": ["berry", "red"]},
    {"name": "Passionfruit","sugar": 11.0, "sweet": 6, "tart": 8, "styles": ["tropical", "aromatic"]},
    {"name": "Lychee",      "sugar": 15.0, "sweet": 9, "tart": 3, "styles": ["floral", "sweet"]},
    {"name": "Guava",       "sugar": 7.0,  "sweet": 6, "tart": 5, "styles": ["tropical"]},
    {"name": "Cranberry",   "sugar": 4.0,  "sweet": 2, "tart": 9, "styles": ["berry", "tart"]},
]

STYLE_ALIASES = {
    "tropical": ["tropical", "mango", "pineapple", "aromatic"],
    "berry":    ["berry", "red", "grape"],
    "citrus":   ["citrus", "acid", "bright"],
    "neutral":  ["neutral", "refreshing", "balanced"],
}


def suggest_blend(target_sweet, target_tart, style, total_juice_ml_per_L=80.0):
    """
    Returns:
      {
        "fruits": [
            {"name": ..., "pct": 0.4, "juice_ml_per_L": ..., "juice_ml_batch": ...},
            ...
        ],
        "sugar_g_per_L": float,
        "co2_vols": float,
        "abv_percent": float,
        "safety_flag": str
      }
    """
    # Score each fruit by closeness to target sweetness & tartness
    scored = []
    style = (style or "").lower().strip()
    style_tags = STYLE_ALIASES.get(style, [])

    for f in FRUITS:
        base_distance = abs(f["sweet"] - target_sweet) + abs(f["tart"] - target_tart)
        # style bonus: if style matches, reduce distance slightly
        style_bonus = 0
        if style_tags:
            if any(tag in f["styles"] for tag in style_tags):
                style_bonus = -1  # better
        score = base_distance + style_bonus
        scored.append((score, f))

    scored.sort(key=lambda x: x[0])
    top_fruits = [f for _, f in scored[:4]]

    # Default percentages
    pct_pattern = [0.4, 0.3, 0.2, 0.1]

    # Calculate sugar etc.
    fruits_out = []
    sugar_total_g_L = 0.0

    for i, fruit in enumerate(top_fruits):
        pct = pct_pattern[i] if i < len(pct_pattern) else 0.0
        juice_ml_per_L = total_juice_ml_per_L * pct
        sugar_g_L = fruit["sugar"] * juice_ml_per_L / 100.0
        sugar_total_g_L += sugar_g_L

        fruits_out.append({
            "name": fruit["name"],
            "pct": pct,
            "juice_ml_per_L": round(juice_ml_per_L, 2),
        })

    co2_vols = sugar_total_g_L * 0.24
    abv_percent = sugar_total_g_L * 0.065
    safety_flag = "OK (≤ 8 g/L)" if sugar_total_g_L <= 8 else "Too high – reduce juice/sugar"

    return {
        "fruits": fruits_out,
        "sugar_g_per_L": round(sugar_total_g_L, 2),
        "co2_vols": round(co2_vols, 2),
        "abv_percent": round(abv_percent, 3),
        "safety_flag": safety_flag,
    }
