import pandas as pd
import lightgbm as lgb
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

def train_model():
    users_df = pd.read_csv(DATA_DIR / "users.csv")

    # Encode gender (M=1, F=0)
    users_df["gender"] = users_df["gender"].str.lower().map({"male": 1, "m": 1, "female": 0, "f": 0})

    # Encode activity_level
    activity_map = {
        "low": 1,
        "moderate": 2,
        "high": 3
    }
    users_df["activity_level"] = users_df["activity_level"].str.lower().map(activity_map)

    # Encode goal
    goal_map = {
        "weight_loss": 0,
        "maintain": 1,
        "muscle_gain": 2
    }
    users_df["goal"] = users_df["goal"].str.lower().map(goal_map)

    feature_columns = ["age", "weight_kg", "height_cm", "activity_level", "gender"]

    # Validate required columns
    for col in feature_columns:
        if col not in users_df.columns:
            raise KeyError(f"❌ Column '{col}' not found in users.csv")

    X = users_df[feature_columns]
    y = users_df["goal"]

    # Train model
    model = lgb.LGBMRegressor()
    model.fit(X, y)

    # Save model
    model_path = MODEL_DIR / "calorie_macro_predictor_lgbm.pkl"
    joblib.dump(model, model_path)

    print(f"✅ Model trained successfully with {len(X)} samples, saved at {model_path}")


if __name__ == "__main__":
    train_model()
