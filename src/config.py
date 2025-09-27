# src/config.py
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MODEL_DIR = ROOT_DIR / "models"

USERS_FILE = DATA_DIR / "users_sample.csv"
REPORTS_FILE = DATA_DIR / "clinical_reports_sample.csv"
FOODS_FILE = DATA_DIR / "foods.csv"
RECOMMENDATIONS_FILE = DATA_DIR / "plans/recommendations.json"
ML_MODEL_PATH = MODEL_DIR / "calorie_macro_predictor_lgbm.pkl"
