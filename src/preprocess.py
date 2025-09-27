import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_datasets():
    foods = pd.read_csv(DATA_DIR / "foods.csv")
    users = pd.read_csv(DATA_DIR / "users.csv")
    reports = pd.read_csv(DATA_DIR / "clinical_reports_sample.csv")
    return foods, users, reports
