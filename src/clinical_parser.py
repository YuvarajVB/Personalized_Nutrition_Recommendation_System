import pandas as pd

def analyze_report(report_path):
    """
    Analyze a diabetes clinical report CSV for a single user.
    Assumes columns: fasting_blood_sugar, postprandial_sugar, hba1c
    Returns a dict with risk and notes.
    """
    try:
        df = pd.read_csv(report_path)
    except Exception as e:
        return {"error": f"Failed to read report: {e}"}

    # Simple diabetes risk check
    risk = "Low"
    notes = []

    if "fasting_blood_sugar" in df.columns:
        fbs = df["fasting_blood_sugar"].iloc[0]
        if fbs > 126:
            risk = "High"
            notes.append(f"High fasting blood sugar: {fbs}")

    if "postprandial_sugar" in df.columns:
        pps = df["postprandial_sugar"].iloc[0]
        if pps > 200:
            risk = "High"
            notes.append(f"High postprandial sugar: {pps}")

    if "hba1c" in df.columns:
        hba1c = df["hba1c"].iloc[0]
        if hba1c > 6.5:
            risk = "High"
            notes.append(f"High HbA1c: {hba1c}")

    if not notes:
        notes.append("All readings normal")

    return {"risk": risk, "notes": notes}
