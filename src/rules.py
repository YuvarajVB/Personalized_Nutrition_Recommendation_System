def apply_clinical_rules(report_row, foods_df):
    """
    Filters food options based on clinical conditions.
    Example: diabetes patients -> avoid high sugar foods.
    """
    if report_row["report_type"] == "diabetes":
        allowed = foods_df[foods_df["suitable_for"].str.contains("diabetic|all", case=False)]
        return allowed
    else:
        return foods_df
