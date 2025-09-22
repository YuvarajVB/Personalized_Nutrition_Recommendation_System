# src/clinical_parser.py
import pandas as pd
def analyze_report(report):
    """
    Analyze a clinical report and return patient's status.
    Supports diabetes (sugar patients) or normal.
    """
    # Normalize the report_type (handle sugar as diabetes)
    report_type = str(report["report_type"]).strip().lower()
    if report_type == "sugar":
        report_type = "diabetes"

    if report_type == "diabetes":
        fasting = report["fasting_blood_sugar"]
        pp = report["postprandial_sugar"]
        hba1c = report["hba1c"]

        if fasting >= 126 or pp >= 200 or hba1c >= 6.5:
            return "diabetes"
        else:
            return "normal"
    else:
        return "normal"


if __name__ == "__main__":
    # Example run
    reports = pd.read_csv("data/clinical_reports_sample.csv")
    for _, row in reports.iterrows():
        status = analyze_report(row)
        print(f"User {row['user_id']} → {status}")
