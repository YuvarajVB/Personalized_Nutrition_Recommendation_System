from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import shutil
import os

from src.recommendation import generate_recommendations_for_user

app = FastAPI(title="Meal Plan API")

# Allow CORS (frontend can access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Force absolute path for upload folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "uploads")

# Force-create the upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)
print("✅ Upload directory path:", UPLOAD_DIR)

# Serve static HTML
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def home():
    return {"message": "Meal Plan API is running properly."}


@app.post("/generate_meal_plan")
async def generate_meal_plan(
    age: int = Form(...),
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
    activity_level: str = Form(...),
    gender: str = Form(...),
    goal: str = Form(...),
    diabetes: str = Form(...),
    report: Optional[UploadFile] = File(None),
):
    try:
        report_path = None

        # ✅ Ensure upload folder exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # ✅ Save uploaded file (if provided)
        if report:
            filename = report.filename or "uploaded_report.txt"
            report_path = os.path.join(UPLOAD_DIR, filename)

            # Debug print (will show in terminal)
            print(f"Saving file to: {report_path}")

            with open(report_path, "wb") as buffer:
                shutil.copyfileobj(report.file, buffer)

        # ✅ Prepare data for recommendation
        input_data = {
            "age": age,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "activity_level": activity_level,
            "gender": gender,
            "goal": goal,
            "diabetes": diabetes.lower() == "true",
            "report_file": report_path,
        }

        plan = generate_recommendations_for_user(input_data)
        return plan

    except Exception as e:
        print("❌ Error occurred:", e)
        return {"error": str(e)}
