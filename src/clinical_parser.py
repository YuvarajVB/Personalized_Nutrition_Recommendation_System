# src/clinical_parser.py
import pandas as pd

def analyze_report(report: pd.Series) -> str:
    """
    Analyze a user's clinical report and return their clinical status.
    Currently checks for diabetes based on standard thresholds.
    
    Args:
        report (pd.Series): A row from clinical_reports CSV containing
                            fasting_blood_sugar, postprandial_sugar, hba1c.
    
    Returns:
        str: 'diabetes' or 'normal'
    """
    # Thresholds for diabetes
    FBS_THRESHOLD = 126          # mg/dL
    PPBS_THRESHOLD = 200         # mg/dL
    HBA1C_THRESHOLD = 6.5        # %

    fasting = report.get("fasting_blood_sugar", 0)
    postprandial = report.get("postprandial_sugar", 0)
    hba1c = report.get("hba1c", 0)

    # If any value crosses threshold, classify as diabetes
    if fasting >= FBS_THRESHOLD or postprandial >= PPBS_THRESHOLD or hba1c >= HBA1C_THRESHOLD:
        return "diabetes"
    
    return "normal"
