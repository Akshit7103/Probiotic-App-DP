# excel_backend.py

from openpyxl import load_workbook
from functools import lru_cache
import os

EXCEL_FILE = "WWY_ProbioticDrink_Model_v1_DASHBOARD.xlsx"


@lru_cache(maxsize=1)
def _load_wb():
    if not os.path.exists(EXCEL_FILE):
        raise FileNotFoundError(f"Excel file not found: {EXCEL_FILE}")
    return load_workbook(EXCEL_FILE, data_only=True)


def get_fruit_master():
    """Return list of fruits with sugar, sweetness, tartness from FruitMaster sheet."""
    wb = _load_wb()
    ws = wb["FruitMaster"]
    fruits = []

    # Assuming headers in row 1: Fruit | Sugar_g_per_100ml | Sweetness_Score_1to10 | Tartness_Score_1to10 | Notes
    for row in ws.iter_rows(min_row=2, values_only=True):
        name, sugar, sweet, tart, notes = row
        if not name:
            continue
        fruits.append({
            "name": str(name),
            "sugar": float(sugar or 0),
            "sweet": int(sweet or 0),
            "tart": int(tart or 0),
            "notes": notes or "",
        })
    return fruits


def get_cost_table():
    """Read Costing sheet into a dict keyed by ingredient (lowercase)."""
    wb = _load_wb()
    if "Costing" not in wb.sheetnames:
        return {}
    ws = wb["Costing"]
    costs = {}
    # Assuming: Ingredient | Cost_per_L_or_kg | Usage_Unit | Cost_for_Batch
    for row in ws.iter_rows(min_row=2, values_only=True):
        ingredient, cost_per_unit, unit, _ = row
        if not ingredient:
            continue
        key = str(ingredient).strip().lower()
        costs[key] = {
            "ingredient": ingredient,
            "cost_per_unit": float(cost_per_unit or 0),
            "unit": unit or "",
        }
    return costs


def get_co2_safety_table():
    """Read CO2Safety sheet into a list of rows."""
    wb = _load_wb()
    if "CO2Safety" not in wb.sheetnames:
        return []
    ws = wb["CO2Safety"]
    rows = []
    # Sugar_g_per_L | Temp_C | Max_Time_Hours | Risk
    for row in ws.iter_rows(min_row=2, values_only=True):
        sugar, temp, hours, risk = row
        if sugar is None or temp is None:
            continue
        rows.append({
            "sugar_g_L": float(sugar),
            "temp_C": float(temp),
            "max_hours": float(hours or 0),
            "risk": str(risk or ""),
        })
    return rows


def _style_aliases():
    return {
        "tropical": ["tropical", "mango", "pineapple", "aromatic"],
        "berry": ["berry", "red", "grape"],
        "citrus": ["citrus", "acid", "bright"],
        "neutral": ["neutral", "refreshing", "balanced"],
    }


def auto_suggest_from_excel(target_sweet, target_tart, style, total_juice_ml_per_L=80.0):
    """Use FruitMaster to suggest 4 fruits that best match target sweet/tart."""
    fruits = get_fruit_master()
    style = (style or "").lower().strip()
    style_tags = _style_aliases().get(style, [])

    scored = []
    for f in fruits:
        base_distance = abs(f["sweet"] - target_sweet) + abs(f["tart"] - target_tart)
        style_bonus = 0
        if style_tags and any(tag in (f["notes"] or "").lower() for tag in style_tags):
            style_bonus = -1
        score = base_distance + style_bonus
        scored.append((score, f))

    scored.sort(key=lambda x: x[0])
    top_fruits = [f for _, f in scored[:4]]

    pct_pattern = [0.4, 0.3, 0.2, 0.1]
    fruits_out = []
    sugar_total_g_L = 0.0

    for i, f in enumerate(top_fruits):
        pct = pct_pattern[i] if i < len(pct_pattern) else 0.0
        juice_ml_per_L = total_juice_ml_per_L * pct
        sugar_g_L = f["sugar"] * juice_ml_per_L / 100.0
        sugar_total_g_L += sugar_g_L

        fruits_out.append({
            "name": f["name"],
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


def _lookup_fruit_sugar(name):
    name = (name or "").strip().lower()
    for f in get_fruit_master():
        if f["name"].strip().lower() == name:
            return f["sugar"]
    return 0.0


def _estimate_cost_for_blend(fruits, batch_l):
    """Estimate cost for a given blend using Costing sheet."""
    costs = get_cost_table()
    total_cost = 0.0

    for f in fruits:
        fruit_name = f["name"]
        juice_ml_batch = f["juice_ml_batch"]
        key_candidates = [
            fruit_name.strip().lower(),
            (fruit_name + " juice").strip().lower(),
        ]
        cost_info = None
        for key in key_candidates:
            if key in costs:
                cost_info = costs[key]
                break

        if cost_info:
            if "per L" in cost_info["unit"]:
                liters = juice_ml_batch / 1000.0
                total_cost += liters * cost_info["cost_per_unit"]
            elif "per kg" in cost_info["unit"]:
                # rough approximation: assume juice density ~1 kg/L
                liters = juice_ml_batch / 1000.0
                total_cost += liters * cost_info["cost_per_unit"]
            # else: ignore or extend logic as needed
    return round(total_cost, 2)


def _lookup_safety_row(sugar_g_L, temp_C):
    """Find the closest safety row given sugar and temp."""
    rows = get_co2_safety_table()
    if not rows:
        return None
    # Simple: choose row where sugar_g_L <= sheet sugar and closest temp
    candidates = [r for r in rows if sugar_g_L <= r["sugar_g_L"] + 0.1]
    if not candidates:
        candidates = rows
    candidates.sort(key=lambda r: (abs(r["temp_C"] - temp_C), r["sugar_g_L"]))
    return candidates[0]


def calculate_blend_manual(fruit_names, pcts, juice_ml_per_L, batch_l, temp_C=28.0):
    """
    Manual mode:
      fruit_names: list of 4 names (can be empty)
      pcts: list of 4 floats (fractions, should sum ~1)
    """
    fruits_out = []
    sugar_total_g_L = 0.0

    for name, pct in zip(fruit_names, pcts):
        if not name or pct <= 0:
            continue
        sugar_per_100 = _lookup_fruit_sugar(name)
        juice_ml_L = juice_ml_per_L * pct
        juice_ml_batch = juice_ml_L * batch_l
        sugar_g_L = sugar_per_100 * juice_ml_L / 100.0
        sugar_total_g_L += sugar_g_L

        fruits_out.append({
            "name": name,
            "pct": pct,
            "juice_ml_per_L": round(juice_ml_L, 2),
            "juice_ml_batch": round(juice_ml_batch, 2),
            "sugar_g_L": round(sugar_g_L, 2),
        })

    co2_vols = sugar_total_g_L * 0.24
    abv_percent = sugar_total_g_L * 0.065
    safety_flag = "OK (≤ 8 g/L)" if sugar_total_g_L <= 8 else "Too high – reduce juice/sugar"

    safety_row = _lookup_safety_row(sugar_total_g_L, temp_C)
    est_cost = _estimate_cost_for_blend(fruits_out, batch_l)

    result = {
        "fruits": fruits_out,
        "sugar_g_per_L": round(sugar_total_g_L, 2),
        "co2_vols": round(co2_vols, 2),
        "abv_percent": round(abv_percent, 3),
        "safety_flag": safety_flag,
        "batch_l": batch_l,
        "juice_ml_per_L": juice_ml_per_L,
        "cost_estimate": est_cost,
    }

    if safety_row:
        result["safety_detail"] = {
            "temp_C": safety_row["temp_C"],
            "max_hours": safety_row["max_hours"],
            "risk": safety_row["risk"],
        }

    return result
