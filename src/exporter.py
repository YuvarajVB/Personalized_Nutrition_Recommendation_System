# src/exporter.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
import pandas as pd

def save_plan_csv(plan_df, out_path):
    plan_df.to_csv(out_path, index=False)

def save_plan_pdf(plan_df, user_name, out_path):
    # Very simple PDF layout
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    x = 40
    y = height - 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, f"Meal Plan for {user_name}")
    y -= 30
    c.setFont("Helvetica", 10)
    for idx, row in plan_df.iterrows():
        text = f"{row.get('food_name')} — servings: {row.get('servings')}, cal: {row.get('calories')}"
        c.drawString(x, y, text)
        y -= 16
        if y < 80:
            c.showPage()
            y = height - 60
    c.save()
