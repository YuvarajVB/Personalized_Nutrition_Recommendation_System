# src/train_model_lgbm.py
import pandas as pd
import numpy as np
import joblib
from lightgbm import LGBMRegressor

users_df = pd.read_csv("data/users.csv")

# Encode goal
users_df["goal_binary"] = users_df["goal"].apply(lambda x: 1 if x=="weight_gain" else 0)

features = ["age", "height_cm", "weight_kg", "activity_level_encoded", "goal_binary"]

# Encode activity_level as int
users_df["activity_level_encoded"] = users_df["activity_level"].map({
    "sedentary": 0,
    "lightly_active": 1,
    "moderately_active": 2,
    "very_active": 3,
    "extra_active": 4
})

X = users_df[["age","height_cm","weight_kg","activity_level_encoded","goal_binary"]]
y = 22 * users_df["weight_kg"]  # Example calorie target

model = LGBMRegressor()
model.fit(X, y)

joblib.dump(model, "models/calorie_macro_predictor_lgbm.pkl")
print("✅ Model trained and saved!")
