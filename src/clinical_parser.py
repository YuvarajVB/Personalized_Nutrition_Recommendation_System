import pandas as pd

def parse_diabetes_report(report_row):
    """Takes one user's clinical report row and returns a status."""
    fasting = report_row['fasting_blood_sugar']
    postprandial = report_row['postprandial_sugar']
    hba1c = report_row['hba1c']

    status = "normal"
    if fasting >= 126 or postprandial >= 200 or hba1c >= 6.5:
        status = "diabetes"
    elif fasting >= 100 and fasting < 126:
        status = "prediabetes"

    return status

if __name__ == "__main__":
    reports = pd.read_csv("data/clinical_reports_sample.csv")
    for _, row in reports.iterrows():
        print(f"User {row['user_id']} → {parse_diabetes_report(row)}")
