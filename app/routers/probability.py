# app/routers/probability.py
from fastapi import APIRouter
from app.services.probability_service import ProbabilityService
from app.core.exceptions import handle_app_exception
import logging

router = APIRouter(tags=["Análisis Probabilístico"])

@router.get("/probability/joint")
async def joint_probability_analysis():
    
    try:
        return await ProbabilityService.joint_probability_analysis()
    except Exception as e:
        handle_app_exception(e)

@router.get("/probability/binomial")
async def binomial_analysis():
    try:
        return await ProbabilityService.binomial_analysis()
    except Exception as e:
        handle_app_exception(e)