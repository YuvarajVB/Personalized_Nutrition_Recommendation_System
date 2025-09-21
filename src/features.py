def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def calculate_bmr(weight, height_cm, age, gender):
    if gender.lower() == "m":
        return 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height_cm - 5 * age - 161

def activity_multiplier(level):
    mapping = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }
    return mapping.get(level.lower(), 1.2)

def daily_calorie_needs(weight, height_cm, age, gender, activity_level, goal):
    bmr = calculate_bmr(weight, height_cm, age, gender)
    maintenance = bmr * activity_multiplier(activity_level)
    
    if goal == "weight_loss":
        return maintenance - 500
    elif goal == "weight_gain":
        return maintenance + 500
    else:
        return maintenance

if __name__ == "__main__":
    # Demo user
    bmi = calculate_bmi(70, 175)
    cal = daily_calorie_needs(70, 175, 25, "M", "moderate", "maintain")
    print("BMI:", bmi)
    print("Daily Calories:", round(cal))
