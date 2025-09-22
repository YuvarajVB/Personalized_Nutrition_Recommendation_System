# backend/app/main.py
import sys
from pathlib import Path

# ---------------------------
# Add project root to Python path
# ---------------------------
project_root = Path(__file__).resolve().parents[2]  # go up 2 levels to MINI PROJECT
sys.path.append(str(project_root))

# ---------------------------
# Imports
# ---------------------------
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.recommendation import generate_meal_plan_by_user_id  # now works

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(title="Diet Recommender API", version="0.2")

class UserIdRequest(BaseModel):
    user_id: int
    mode: Optional[str] = "auto"  # "auto" | "greedy" | "opt"

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Diet Recommender API is running"}

@app.post("/generate_plan")
async def generate_plan(req: UserIdRequest):
    try:
        plan_df, total_cal, meta = generate_meal_plan_by_user_id(req.user_id, mode=req.mode)
        # convert plan to JSON serializable
        plan = plan_df.to_dict(orient="records")
        return {"user_id": req.user_id, "plan": plan, "total_calories": total_cal, "meta": meta}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------------
# Run app directly
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
