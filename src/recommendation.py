# src/recommendation.py
from pathlib import Path
import pandas as pd
import math

from preprocess import load_datasets
from features import daily_calorie_needs, calculate_bmi
from clinical_parser import parse_diabetes_report
from rules import apply_clinical_rules

# Optional optimizer
try:
    import pulp
    HAS_PULP = True
except Exception:
    HAS_PULP = False

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def macro_targets_from_calories(cal_target, style="balanced"):
    """
    Return macro targets (grams) for protein, carbs, fat based on calorie target.
    style: "balanced" -> P/C/F = 20/50/30
    """
    if style == "balanced":
        p_pct, c_pct, f_pct = 0.20, 0.50, 0.30
    else:
        p_pct, c_pct, f_pct = 0.20, 0.50, 0.30
    prot_g = (cal_target * p_pct) / 4.0
    carb_g = (cal_target * c_pct) / 4.0
    fat_g = (cal_target * f_pct) / 9.0
    return {"protein_g": prot_g, "carbs_g": carb_g, "fat_g": fat_g}


def _prepare_foods_df(foods_df):
    # Ensure necessary numeric columns and no weird types
    for col in ["calories", "protein", "g_carbs", "fat", "fiber"]:
        if col in foods_df.columns:
            foods_df[col] = pd.to_numeric(foods_df[col], errors="coerce").fillna(0.0)
        else:
            foods_df[col] = 0.0
    # Normalize text tags
    if "suitable_for" in foods_df.columns:
        foods_df["suitable_for"] = foods_df["suitable_for"].astype(str).fillna("").str.lower()
    else:
        foods_df["suitable_for"] = "all"
    return foods_df


def greedy_meal_planner(foods_df, calorie_target, tolerance=0.05, prefer_veg=False):
    """
    Very simple greedy filler: repeatedly pick a food that increases
    total calories but not exceed target*(1 + tolerance) as best-fit.
    Returns list of (food_name, servings=1).
    """
    foods = foods_df.copy().reset_index(drop=True)
    # shuffle so selection isn't always top items
    foods = foods.sample(frac=1, random_state=42).sort_values("calories", ascending=False)
    plan = []
    total = 0.0
    max_allowed = calorie_target * (1 + tolerance)

    # Try to add items one-by-one
    for _, row in foods.iterrows():
        if total >= calorie_target * (1 - tolerance):
            break
        if total + row["calories"] <= max_allowed:
            plan.append({"food_id": row.get("food_id", None),
                         "food_name": row["food_name"],
                         "servings": 1,
                         "calories": row["calories"],
                         "protein": row["protein"],
                         "carbs": row["g_carbs"],
                         "fat": row["fat"],
                         "fiber": row["fiber"]})
            total += row["calories"]

    # If still under target, try adding smallest calorie item repeatedly
    if total < calorie_target * (1 - tolerance):
        smallest = foods.sort_values("calories").iloc[0]
        while total < calorie_target * (1 - tolerance):
            plan.append({"food_id": smallest.get("food_id", None),
                         "food_name": smallest["food_name"],
                         "servings": 1,
                         "calories": smallest["calories"],
                         "protein": smallest["protein"],
                         "carbs": smallest["g_carbs"],
                         "fat": smallest["fat"],
                         "fiber": smallest["fiber"]})
            total += smallest["calories"]
            if len(plan) > 50:
                break

    return pd.DataFrame(plan), round(total)


def optimize_meal_plan(foods_df, calorie_target, macro_targets, max_items=10, tol=0.05):
    """
    Uses PuLP to solve a linear program that chooses continuous servings x_i.
    Minimizes absolute macro deviations (linearized) and number of servings.
    If pulp not available or problem infeasible, raises Exception.
    """
    if not HAS_PULP:
        raise RuntimeError("PuLP not installed (HAS_PULP is False). Install pulp to use optimizer.")

    prob = pulp.LpProblem("meal_plan", pulp.LpMinimize)

    n = len(foods_df)
    # Variables: servings (continuous)
    x_vars = {}
    for i in range(n):
        x_vars[i] = pulp.LpVariable(f"x_{i}", lowBound=0, upBound=5, cat="Continuous")

    # Slack variables for macro deviations
    pos_p = pulp.LpVariable("pos_prot", lowBound=0)
    neg_p = pulp.LpVariable("neg_prot", lowBound=0)
    pos_c = pulp.LpVariable("pos_carb", lowBound=0)
    neg_c = pulp.LpVariable("neg_carb", lowBound=0)
    pos_f = pulp.LpVariable("pos_fat", lowBound=0)
    neg_f = pulp.LpVariable("neg_fat", lowBound=0)

    # Calorie constraints (tolerance)
    cal_expr = pulp.lpSum([foods_df.iloc[i]["calories"] * x_vars[i] for i in range(n)])
    prob += cal_expr >= calorie_target * (1 - tol)
    prob += cal_expr <= calorie_target * (1 + tol)

    # Protein/carbs/fat constraints via deviation variables
    prot_expr = pulp.lpSum([foods_df.iloc[i]["protein"] * x_vars[i] for i in range(n)])
    carb_expr = pulp.lpSum([foods_df.iloc[i]["g_carbs"] * x_vars[i] for i in range(n)])
    fat_expr = pulp.lpSum([foods_df.iloc[i]["fat"] * x_vars[i] for i in range(n)])

    prob += prot_expr - macro_targets["protein_g"] == pos_p - neg_p
    prob += carb_expr - macro_targets["carbs_g"] == pos_c - neg_c
    prob += fat_expr - macro_targets["fat_g"] == pos_f - neg_f

    # Limit number of distinct items roughly (sum of servings <= max_items)
    prob += pulp.lpSum([x_vars[i] for i in range(n)]) <= max_items

    # Objective: minimize weighted sum of macro deviations + small penalty on total servings
    prob += (1.0 * (pos_p + neg_p) + 0.5 * (pos_c + neg_c) + 2.0 * (pos_f + neg_f)
             + 0.01 * pulp.lpSum([x_vars[i] for i in range(n)]))

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=False)
    result = prob.solve(solver)
    status = pulp.LpStatus[result]
    if status != "Optimal":
        raise RuntimeError(f"Optimizer did not find optimal solution: {status}")

    # Build plan from x_vars
    rows = []
    total_cal = 0.0
    for i in range(n):
        val = x_vars[i].value()
        if val is None:
            continue
        # treat small rounding noise as zero
        if val and val > 1e-6:
            row = foods_df.iloc[i]
            servings = round(val, 2)
            rows.append({
                "food_id": int(row.get("food_id", -1)),
                "food_name": row["food_name"],
                "servings": servings,
                "calories": float(row["calories"]) * servings,
                "protein": float(row["protein"]) * servings,
                "carbs": float(row["g_carbs"]) * servings,
                "fat": float(row["fat"]) * servings,
                "fiber": float(row["fiber"]) * servings
            })
            total_cal += float(row["calories"]) * servings

    return pd.DataFrame(rows), round(total_cal)


def generate_meal_plan(user_row, report_row=None, mode="auto"):
    """
    user_row: pandas Series with fields (age, gender, height_cm, weight_kg, activity_level, goal)
    report_row: pandas Series from clinical_reports_sample.csv (or None)
    mode: "auto" (uses optimizer if available), "greedy", or "opt"
    Returns: (plan_df, total_calories, meta_dict)
    """
    foods, users, reports = load_datasets()
    foods = _prepare_foods_df(foods)

    # Apply clinical filtering
    clinical_status = None
    if report_row is not None:
        clinical_status = parse_diabetes_report(report_row)
    else:
        # try to find report by user_id
        try:
            uid = int(user_row.get("user_id"))
            all_reports = reports[reports["user_id"] == uid]
            if not all_reports.empty:
                clinical_status = parse_diabetes_report(all_reports.iloc[0])
        except Exception:
            clinical_status = None

    if clinical_status:
        foods = apply_clinical_rules({"report_type": clinical_status}, foods)

    # calculate calorie target
    cal_target = daily_calorie_needs(user_row["weight_kg"],
                                     user_row["height_cm"],
                                     user_row["age"],
                                     user_row["gender"],
                                     user_row["activity_level"],
                                     user_row["goal"])

    macro_targets = macro_targets_from_calories(cal_target)

    # Decide mode
    if mode == "auto":
        if HAS_PULP:
            try:
                plan_df, total = optimize_meal_plan(foods, cal_target, macro_targets)
            except Exception:
                plan_df, total = greedy_meal_planner(foods, cal_target)
        else:
            plan_df, total = greedy_meal_planner(foods, cal_target)
    elif mode == "opt":
        plan_df, total = optimize_meal_plan(foods, cal_target, macro_targets)
    else:
        plan_df, total = greedy_meal_planner(foods, cal_target)

    meta = {
        "user_calorie_target": round(cal_target),
        "clinical_status": clinical_status,
        "macro_targets": macro_targets
    }

    return plan_df, total, meta


def generate_meal_plan_by_user_id(user_id, mode="auto"):
    foods, users, reports = load_datasets()
    user_row = users[users["user_id"] == int(user_id)]
    if user_row.empty:
        raise ValueError("User id not found")
    user_row = user_row.iloc[0]
    report_row = reports[reports["user_id"] == int(user_id)]
    report_row = report_row.iloc[0] if not report_row.empty else None
    return generate_meal_plan(user_row, report_row, mode=mode)


if __name__ == "__main__":
    # quick local test (first user)
    foods, users, reports = load_datasets()
    user = users.iloc[0]
    report = reports[reports["user_id"] == user["user_id"]]
    report = report.iloc[0] if not report.empty else None
    plan, total, meta = generate_meal_plan(user, report, mode="auto")
    print("Meta:", meta)
    print(plan.head())
    print("Total calories:", total)
