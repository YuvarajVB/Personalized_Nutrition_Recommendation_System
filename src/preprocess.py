import pandas as pd
from pathlib import Path

# Paths to data files
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FOODS_FILE = DATA_DIR / "foods.csv"
USERS_FILE = DATA_DIR / "users_sample.csv"
REPORTS_FILE = DATA_DIR / "clinical_reports_sample.csv"

def load_datasets():
    foods = pd.read_csv(FOODS_FILE)
    users = pd.read_csv(USERS_FILE)
    reports = pd.read_csv(REPORTS_FILE)
    return foods, users, reports

def check_data(foods, users, reports):
    print("\n--- Foods Dataset ---")
    print(foods.head())
    print("\nMissing values in foods:\n", foods.isnull().sum())

    print("\n--- Users Dataset ---")
    print(users.head())
    print("\nMissing values in users:\n", users.isnull().sum())

    print("\n--- Clinical Reports ---")
    print(reports.head())
    print("\nMissing values in reports:\n", reports.isnull().sum())

if __name__ == "__main__":
    foods, users, reports = load_datasets()
    check_data(foods, users, reports)
