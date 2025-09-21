import pandas as pd
from features import daily_calorie_needs
from rules import apply_clinical_rules
from preprocess import load_datasets

def generate_meal_plan(user_row, report_row=None):
    foods, _, _ = load_datasets()

    # Apply clinical filtering if report is provided
    if report_row is not None:
        foods = apply_clinical_rules(report_row, foods)

    # Calculate calorie target
    calorie_target = daily_calorie_needs(
        user_row["weight_kg"],
        user_row["height_cm"],
        user_row["age"],
        user_row["gender"],
        user_row["activity_level"],
        user_row["goal"]
    )

    plan = []
    total_calories = 0

    # Naive strategy: pick foods until reaching target
    for _, food in foods.iterrows():
        if total_calories + food["calories"] <= calorie_target:
            plan.append(food["food_name"])
            total_calories += food["calories"]

    return plan, round(total_calories)

if __name__ == "__main__":
    foods, users, reports = load_datasets()
    user_row = users.iloc[0]
    report_row = reports.iloc[0]
    plan, total = generate_meal_plan(user_row, report_row)
    print("Recommended Meal Plan:", plan)
    print("Total Calories:", total)
