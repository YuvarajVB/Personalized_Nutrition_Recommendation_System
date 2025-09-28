import pandas as pd
import joblib
import os

# Paths
ML_MODEL_PATH = os.path.join("models", "calorie_macro_predictor_lgbm.pkl")
FOODS_PATH = os.path.join("data", "foods.csv")

# Load ML model
ml_model = joblib.load(ML_MODEL_PATH)

# Load food database
foods_df = pd.read_csv(FOODS_PATH)

# Example function to analyze diabetes report (replace with actual logic if available)
def analyze_report(report_file):
    # Placeholder: return dict with any adjustments based on report
    if report_file and os.path.exists(report_file):
        # Example: could parse report to check blood sugar or carbs
        return {"note": "Adjusted for diabetes"}
    return {}

# Function to generate meal plan for a single user (console-friendly)
def generate_recommendations_for_user(user_input):
    """
    user_input: dict with keys:
      age, weight_kg, height_cm, activity_level, gender, goal, diabetes, report_file
    """
    # Prepare features for ML model
    feature_order = ["age", "weight_kg", "height_cm", "activity_level", "gender"]
    features = pd.DataFrame([user_input])[feature_order]

    # Convert categorical columns to numbers if needed
    # Example mapping
    features["activity_level"] = features["activity_level"].map({
        "sedentary": 0,
        "light": 1,
        "moderate": 2,
        "active": 3,
        "very_active": 4
    }).fillna(0)
    features["gender"] = features["gender"].map({"M": 0, "F": 1}).fillna(0)

    # Predict calories
    predicted_calories = ml_model.predict(features)[0]

    # Basic macro distribution (can adjust)
    macros = {
        "protein_g": int(0.3 * predicted_calories / 4),
        "carbs_g": int(0.5 * predicted_calories / 4),
        "fat_g": int(0.2 * predicted_calories / 9),
    }

    # If diabetic, adjust based on report
    diabetes_adjustments = {}
    if user_input.get("diabetes"):
        diabetes_adjustments = analyze_report(user_input.get("report_file"))

    # Generate simple meal plan using foods_df (random example)
    meal_plan = {
        "calories": int(predicted_calories),
        "macros": macros,
        "notes": diabetes_adjustments.get("note", ""),
        "meals": foods_df.sample(3).to_dict(orient="records")  # 3 random foods
    }

    return meal_plan

# For console testing
if __name__ == "__main__":
    # Example input from console
    user_input = {
        "age": int(input("Enter age: ")),
        "weight_kg": float(input("Enter weight (kg): ")),
        "height_cm": float(input("Enter height (cm): ")),
        "activity_level": input("Enter activity level (sedentary/light/moderate/active/very_active): "),
        "gender": input("Enter gender (M/F): "),
        "goal": input("Enter goal (weight_loss/muscle_gain/maintain): "),
        "diabetes": input("Diabetic? (yes/no): ").lower() == "yes",
        "report_file": input("Enter report file path (or leave blank): ")
    }

    plan = generate_recommendations_for_user(user_input)
    print("\nGenerated Meal Plan:")
    print(plan)
