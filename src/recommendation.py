# src/recommendation.py
import pandas as pd
import random

# ---------------------------
# Helper functions
# ---------------------------
def calculate_bmr(weight, height, age, gender):
    """Calculate BMR using Mifflin-St Jeor formula"""
    if gender.upper() == "M":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def get_activity_multiplier(level):
    """Return activity multiplier for TDEE"""
    return {'low': 1.2, 'medium': 1.55, 'high': 1.725}.get(level.lower(), 1.2)

def analyze_report(report):
    """Simple rule-based clinical analysis"""
    if report.get("blood_sugar_fasting", 0) > 126:
        return "diabetes"
    return "normal"

# ---------------------------
# Load datasets
# ---------------------------
foods = pd.read_csv("data/foods.csv")
users = pd.read_csv("data/users_sample.csv")
reports = pd.read_csv("data/clinical_reports_sample.csv")

# ---------------------------
# Function: Recommend meal
# ---------------------------
def recommend_meal(user, report, foods):
    # 1. Clinical status
    clinical_status = analyze_report(report)

    # 2. Calculate calorie needs
    bmr = calculate_bmr(user["weight_kg"], user["height_cm"], user["age"], user["gender"])
    activity_factor = get_activity_multiplier(user["activity_level"])
    calorie_target = bmr * activity_factor

    if user["goal"] == "weight_loss":
        calorie_target -= 500
    elif user["goal"] == "weight_gain":
        calorie_target += 500

    # 3. Macro targets
    protein_target = (0.2 * calorie_target) / 4
    carb_target = (0.5 * calorie_target) / 4
    fat_target = (0.3 * calorie_target) / 9

    # 4. Apply diabetic filters
    filtered_foods = foods.copy()
    if clinical_status == "diabetes":
        filtered_foods = filtered_foods[~filtered_foods["food_name"].str.contains(
            "sweet|sugar|dessert|candy|soft drink|juice|white rice", case=False
        )]
        filtered_foods = filtered_foods[filtered_foods["fiber"] >= 2]

    # 5. Split calorie targets by meal
    meal_split = {'Breakfast': 0.25, 'Lunch': 0.35, 'Dinner': 0.25, 'Snacks': 0.15}
    daily_meals = {}
    total_calories = 0

    for meal, fraction in meal_split.items():
        meal_cal_target = calorie_target * fraction
        meal_foods = []
        meal_cal = 0

        while meal_cal < meal_cal_target:
            food = filtered_foods.sample(1).iloc[0]

            # Portion adjustment if food exceeds remaining calories
            remaining_cal = meal_cal_target - meal_cal
            if food["calories"] > remaining_cal:
                # Add proportionally
                meal_foods.append({
                    "food_name": food["food_name"],
                    "calories": remaining_cal
                })
                meal_cal += remaining_cal
                break
            else:
                meal_foods.append({
                    "food_name": food["food_name"],
                    "calories": food["calories"]
                })
                meal_cal += food["calories"]

            if len(meal_foods) > 10:  # safety check
                break

        daily_meals[meal] = meal_foods
        total_calories += meal_cal

    return {
        "user": user["name"],
        "clinical_status": clinical_status,
        "calorie_target": round(calorie_target),
        "protein_target": round(protein_target),
        "carb_target": round(carb_target),
        "fat_target": round(fat_target),
        "meal_plan": daily_meals,
        "total_calories": round(total_calories)
    }

# ---------------------------
# Run example
# ---------------------------
if __name__ == "__main__":
    user = users.iloc[0]
    report = reports[reports["user_id"] == user["user_id"]].iloc[0]

    result = recommend_meal(user, report, foods)

    # Print results
    print(f"\nRecommended diet for {result['user']} ({result['clinical_status']} patient):")
    print("Calorie target:", result["calorie_target"])
    print("Protein target:", result["protein_target"], "g")
    print("Carb target:", result["carb_target"], "g")
    print("Fat target:", result["fat_target"], "g")
    print("\n--- Meal Plan ---")
    for meal, items in result["meal_plan"].items():
        print(f"\n{meal}:")
        for item in items:
            print(f"- {item['food_name']} ({round(item['calories'])} kcal)")
    print("\nTotal Calories:", result["total_calories"])
    # ---------------------------
# Function to match run_batch.py
# ---------------------------
def generate_meal_plan_by_user_id(user_id, mode="auto"):
    """
    Wrapper to generate a meal plan for a given user_id.
    Returns: (plan_df, total_calories, meta)
    """
    # Fetch user and report
    user = users[users["user_id"] == user_id].iloc[0]
    report = reports[reports["user_id"] == user_id].iloc[0]

    # Generate meal plan
    result = recommend_meal(user, report, foods)

    # Convert meal plan dict to DataFrame
    plan_rows = []
    for meal, items in result["meal_plan"].items():
        for item in items:
            plan_rows.append({
                "meal": meal,
                "food_name": item["food_name"],
                "calories": round(item["calories"])
            })
    plan_df = pd.DataFrame(plan_rows)

    # Meta information
    meta = {
        "user_calorie_target": result["calorie_target"],
        "clinical_status": result["clinical_status"]
    }

    return plan_df, result["total_calories"], meta

