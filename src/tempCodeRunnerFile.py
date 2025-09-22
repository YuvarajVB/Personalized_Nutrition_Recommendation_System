# src/run_batch.py
from pathlib import Path
import pandas as pd
from recommendation import generate_meal_plan_by_user_id
from preprocess import load_datasets

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "plans"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def run_all(mode="auto", max_users=None):
    foods, users, reports = load_datasets()
    results = []
    iter_users = users.iterrows()
    for idx, user in iter_users:
        if max_users and user["user_id"] > max_users:
            break
        try:
            plan_df, total_cal, meta = generate_meal_plan_by_user_id(user["user_id"], mode=mode)
            # save plan CSV
            user_file = OUT_DIR / f"user_{user['user_id']}_plan.csv"
            plan_df.to_csv(user_file, index=False)
            results.append({
                "user_id": int(user["user_id"]),
                "name": user["name"],
                "total_calories": total_cal,
                "target_calories": meta["user_calorie_target"],
                "clinical_status": meta["clinical_status"]
            })
            print(f"Saved plan for user {user['user_id']} -> {user_file.name}")
        except Exception as e:
            print(f"Failed for user {user['user_id']}: {e}")

    summary_df = pd.DataFrame(results)
    summary_file = OUT_DIR / "summary_plans.csv"
    summary_df.to_csv(summary_file, index=False)
    print("Summary saved to", summary_file)
    return summary_df

if __name__ == "__main__":
    run_all(mode="auto", max_users=None)
