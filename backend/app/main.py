from fastapi import FastAPI
from pydantic import BaseModel
from src.recommendation import generate_recommendations_for_user  # updated import

app = FastAPI()

class UserInput(BaseModel):
    age: int
    weight_kg: float
    height_cm: float
    activity_level: str
    gender: str
    goal: str
    diabetes: bool
    report_file: str = None  # optional

@app.post("/recommend")
def recommend(user: UserInput):
    """
    Receives user input and returns personalized meal plan.
    """
    result = generate_recommendations_for_user(user.dict())
    return result

@app.get("/")
def home():
    return {"message": "Meal Plan API is running"}
