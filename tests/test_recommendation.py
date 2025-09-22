# tests/test_recommendation.py
import pytest
from src.recommendation import generate_meal_plan_by_user_id

def test_plan_generation_user1():
    plan_df, total, meta = generate_meal_plan_by_user_id(1, mode="greedy")
    assert total > 0
    assert "user_calorie_target" in meta
