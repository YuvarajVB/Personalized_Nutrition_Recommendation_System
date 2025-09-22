# src/recommendation.py
import pandas as pd
import random
from utils import calculate_bmr, get_activity_multiplier
from clinical_parser import analyze_report

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
    # 1. Get clinical status (normal or diabetes)
    clinical_status = analyze_report(report)

    # 2. Calculate calorie needs
    bmr = calculate_bmr(user["weight_kg"], user["height_cm"], user["age"], user["gender"])
    activity_factor = get_activity_multiplier(user["activity_level"])
    calorie_target = bmr * activity_factor

    # Adjust based on goal
    if user["goal"] == "weight_loss":
        calorie_target -= 500
    elif user["goal"] == "weight_gain":
        calorie_target += 500

    # 3. Macro distribution
    protein_target = (0.2 * calorie_target) / 4   # 20% protein
    carb_target = (0.5 * calorie_target) / 4      # 50% carbs
    fat_target = (0.3 * calorie_target) / 9       # 30% fat

    # 4. Apply filters for diabetes (sugar patients)
    if clinical_status == "diabetes":
        foods = foods[~foods["food_name"].str.contains(
            "sweet|sugar|dessert|candy|soft drink|juice|white rice", case=False
        )]
        foods = foods[foods["fiber"] >= 2]  # prefer high-fiber foods

    # 5. Randomly build a meal plan until near calorie target
    meal_plan = []
    total_cal = 0

    while total_cal < calorie_target * 0.95:  # stop when 95% of calories filled
        food = foods.sample(1).iloc[0]
        meal_plan.append(food)
        total_cal += food["calories"]

        # Safety check to avoid infinite loop
        if len(meal_plan) > 15:
            break

    return {
        "user": user["name"],
        "clinical_status": clinical_status,
        "calorie_target": round(calorie_target),
        "protein_target": round(protein_target),
        "carb_target": round(carb_target),
        "fat_target": round(fat_target),
        "meal_plan": meal_plan,
        "total_calories": total_cal
    }


# ---------------------------
# Run example
# ---------------------------
if __name__ == "__main__":
    # Pick first user and their report
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
    for item in result["meal_plan"]:
        print(f"- {item['food_name']} ({item['calories']} kcal)")
    print("Total Calories:", round(result["total_calories"]))
