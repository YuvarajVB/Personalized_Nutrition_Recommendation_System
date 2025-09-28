from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import shutil
import os
from src.recommendation import generate_recommendations_for_user

app = FastAPI(title="Meal Plan API")

# Directory to temporarily save uploaded reports
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic model for request body
class UserInput(BaseModel):
    age: int
    weight_kg: float
    height_cm: float
    activity_level: str  # sedentary/light/moderate/active/very_active
    gender: str  # M/F
    goal: str  # weight_loss/muscle_gain/maintain
    diabetes: bool
    report_file: Optional[str] = None  # optional file path

@app.get("/")
def root():
    return {"message": "Meal Plan API is running"}

@app.post("/generate_meal_plan")
async def generate_meal_plan(user_input: UserInput, report: Optional[UploadFile] = File(None)):
    # Save uploaded report file if provided
    report_path = None
    if report:
        report_path = os.path.join(UPLOAD_DIR, report.filename)
        with open(report_path, "wb") as buffer:
            shutil.copyfileobj(report.file, buffer)

    # Convert request body to dict
    input_data = user_input.dict()
    input_data["report_file"] = report_path

    # Generate meal plan
    plan = generate_recommendations_for_user(input_data)
    return plan
