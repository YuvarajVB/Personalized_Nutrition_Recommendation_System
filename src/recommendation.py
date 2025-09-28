import pandas as pd
import joblib
from src.clinical_parser import analyze_report  # Import from src
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "calorie_macro_predictor_lgbm.pkl")

# Load the ML model once
ml_model = joblib.load(MODEL_PATH)

# Example: simple feature encoding
activity_map = {"sedentary": 1, "light": 2, "moderate": 3, "active": 4}
gender_map = {"M": 1, "F": 0}

def generate_recommendations_for_user(user_info):
    """
    Generate a meal plan for a single user.
    user_info: dict with keys - age, weight_kg, height_cm, activity_level, gender, goal, diabetes, report_file(optional)
    Returns: dict with calories, macros, and report notes if any
    """
    # Prepare features for ML model
    try:
        features = pd.DataFrame([{
            "age": user_info["age"],
            "weight_kg": user_info["weight_kg"],
            "height_cm": user_info["height_cm"],
            "activity_level": activity_map.get(user_info["activity_level"], 1),
            "gender": gender_map.get(user_info["gender"], 0)
        }])

        predicted_calories = ml_model.predict(features)[0]

        # Simple macro split
        proteins = 0.3 * predicted_calories / 4
        carbs = 0.5 * predicted_calories / 4
        fats = 0.2 * predicted_calories / 9

        plan = {
            "calories": round(predicted_calories, 2),
            "protein_g": round(proteins, 2),
            "carbs_g": round(carbs, 2),
            "fats_g": round(fats, 2)
        }

        # If diabetic, analyze report
        report_notes = None
        if user_info.get("diabetes") and user_info.get("report_file"):
            report_path = user_info["report_file"]
            if os.path.exists(report_path):
                report_notes = analyze_report(report_path)
            else:
                report_notes = {"error": "Report file not found"}

        return {"meal_plan": plan, "report_notes": report_notes}

    except Exception as e:
        return {"error": str(e)}
