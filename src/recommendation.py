# src/recommendation.py
import pandas as pd
import random
import joblib
from pathlib import Path
from src.clinical_parser import analyze_report

# Paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FOODS_PATH = DATA_DIR / "foods.csv"
USERS_PATH = DATA_DIR / "users.csv"
REPORTS_PATH = DATA_DIR / "clinical_reports.csv"
ML_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "calorie_macro_predictor_lgbm.pkl"

# Load datasets
foods_df = pd.read_csv(FOODS_PATH)
reports_df = pd.read_csv(REPORTS_PATH)
ml_model = joblib.load(ML_MODEL_PATH)

def generate_recommendations_for_user(user_id: int):
    """
    Generate meal plan for a user by ID.
    
    Returns:
        plan_df (pd.DataFrame): Recommended foods
        total_calories (float): Total calories in plan
        meta (dict): Additional info like predicted calories & clinical status
    """
    # Load user info
    users_df = pd.read_csv(USERS_PATH)
    user = users_df[users_df["user_id"] == user_id].iloc[0]

    # Load clinical report if exists
    report = reports_df[reports_df["user_id"] == user_id]
    if not report.empty:
        report = report.iloc[0]
        clinical_status = analyze_report(report)
    else:
        clinical_status = "normal"

    # Prepare features for ML model
    features = pd.DataFrame([{
        "age": user["age"],
        "gender": 1 if user["gender"].lower() == "m" else 0,
        "height_cm": user["height_cm"],
        "weight_kg": user["weight_kg"],
        "activity_level": 1 if user["activity_level"].lower() == "sedentary" else 2  # encode activity
    }])

    # Predict calorie target
    predicted_calories = ml_model.predict(features)[0]

    # Adjust based on goal
    if user["goal"] == "weight_loss":
        predicted_calories -= 500
    elif user["goal"] == "weight_gain":
        predicted_calories += 500

    # Macro targets
    protein_target = 0.2 * predicted_calories / 4
    carb_target = 0.5 * predicted_calories / 4
    fat_target = 0.3 * predicted_calories / 9

    # Filter foods if diabetic
    available_foods = foods_df.copy()
    if clinical_status == "diabetes":
        available_foods = available_foods[~available_foods["food_name"].str.contains(
            "sweet|sugar|dessert|candy|soft drink|juice|white rice", case=False)]
        available_foods = available_foods[available_foods["fiber"] >= 2]

    # Build meal plan
    meal_plan = []
    total_cal = 0
    while total_cal < predicted_calories * 0.95:
        food = available_foods.sample(1).iloc[0]
        meal_plan.append(food)
        total_cal += food["calories"]
        if len(meal_plan) > 15:  # safety
            break

    plan_df = pd.DataFrame(meal_plan)

    meta = {
        "user_calorie_target": round(predicted_calories),
        "protein_target": round(protein_target),
        "carb_target": round(carb_target),
        "fat_target": round(fat_target),
        "clinical_status": clinical_status
    }

    return plan_df, total_cal, meta
