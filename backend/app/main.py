from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
import os
from src.recommendation import generate_recommendations_for_user

app = FastAPI(title="Meal Plan API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Directory to temporarily save uploaded reports
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_index():
    return FileResponse("frontend/ind.html")

@app.post("/generate_meal_plan")
async def generate_meal_plan(
    age: int = Form(...),
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
    activity_level: str = Form(...),
    gender: str = Form(...),
    goal: str = Form(...),
    diabetes: bool = Form(...),
    report: Optional[UploadFile] = File(None)
):
    # Save uploaded report file if provided
    report_path = None
    if report:
        report_path = os.path.join(UPLOAD_DIR, report.filename)
        with open(report_path, "wb") as buffer:
            shutil.copyfileobj(report.file, buffer)

    # Prepare input data for recommendation
    input_data = {
        "age": age,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "activity_level": activity_level,
        "gender": gender,
        "goal": goal,
        "diabetes": diabetes,
        "report_file": report_path,
    }

    try:
        # Generate meal plan
        plan = generate_recommendations_for_user(input_data)
        return JSONResponse(content=plan)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
