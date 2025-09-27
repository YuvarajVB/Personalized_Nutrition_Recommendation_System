from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from src.recommendation import generate_recommendations_for_user
from pathlib import Path

app = FastAPI(title="Diet Recommender API", version="0.3")

# Models
class UserRequest(BaseModel):
    user_id: int

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Diet Recommender API is running"}

@app.post("/generate_plan")
async def generate_plan(req: UserRequest, report: Optional[UploadFile] = None):
    try:
        # Save uploaded report if provided
        if report:
            report_path = DATA_DIR / "clinical_reports.csv"
            df_new = pd.read_csv(report.file)
            df_new.to_csv(report_path, index=False)

        plan_df, total_cal, meta = generate_recommendations_for_user(req.user_id)

        # Convert plan to JSON serializable
        plan_json = plan_df.to_dict(orient="records")
        return {"user_id": req.user_id, "plan": plan_json, "total_calories": total_cal, "meta": meta}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# For dev: run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
