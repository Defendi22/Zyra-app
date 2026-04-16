"""
Roteador de IA — xAI Grok (Meal Analysis, Workout Plans, Diet Plans, Coach)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List

from app.middleware.auth import require_auth
from app.services.ai_service import ai_service
from app.config import settings

router = APIRouter()


# ==================== SCHEMAS ====================

class MealAnalysisRequest(BaseModel):
    image_base64: str = Field(..., description="Imagem da refeição em base64")

    class Config:
        json_schema_extra = {"example": {"image_base64": "/9j/4AAQSkZJRgAB..."}}


class FoodItem(BaseModel):
    name: str
    quantity: str
    kcal: float


class MealAnalysisResponse(BaseModel):
    foods: List[FoodItem]
    total_kcal: float
    macros: dict
    confidence: float


class GenerateDietRequest(BaseModel):
    goal: str = Field(..., description="'loss' | 'gain' | 'maintenance'")
    daily_kcal: int = Field(..., ge=1000, le=10000)
    restrictions: List[str] = Field(default=[])
    duration_days: int = Field(default=7, ge=1, le=30)

    class Config:
        json_schema_extra = {
            "example": {"goal": "gain", "daily_kcal": 3000, "restrictions": [], "duration_days": 7}
        }


class GenerateWorkoutRequest(BaseModel):
    level: str = Field(..., description="'beginner' | 'intermediate' | 'advanced'")
    goal: str = Field(..., description="'strength' | 'endurance' | 'hypertrophy' | 'balance'")
    equipment: List[str] = Field(default=[])
    duration_days: int = Field(default=7, ge=1, le=30)

    class Config:
        json_schema_extra = {
            "example": {"level": "intermediate", "goal": "hypertrophy", "equipment": ["dumbbells"], "duration_days": 7}
        }


class CoachMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

    class Config:
        json_schema_extra = {"example": {"message": "Quero ganhar massa muscular. Por onde começo?"}}


class CoachMessageResponse(BaseModel):
    response: str
    suggestions: List[str] = []


def _check_ai_key():
    if not settings.XAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="XAI_API_KEY não configurada",
        )


# ==================== ENDPOINTS ====================

@router.post("/analyze-meal", response_model=MealAnalysisResponse)
async def analyze_meal(
    body: MealAnalysisRequest,
    user_id: str = Depends(require_auth),
):
    """Analisa foto de refeição com Grok Vision. Envie a imagem em base64."""
    _check_ai_key()
    try:
        return await ai_service.analyze_meal(body.image_base64, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@router.post("/generate-diet")
async def generate_diet_plan(
    body: GenerateDietRequest,
    user_id: str = Depends(require_auth),
):
    """Gera plano de dieta personalizado com Grok."""
    _check_ai_key()
    if body.goal not in ("loss", "gain", "maintenance"):
        raise HTTPException(status_code=400, detail="goal deve ser: loss, gain ou maintenance")
    try:
        return await ai_service.generate_diet_plan(
            user_id=user_id,
            goal=body.goal,
            daily_kcal=body.daily_kcal,
            restrictions=body.restrictions,
            duration_days=body.duration_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dieta: {str(e)}")


@router.post("/generate-workout")
async def generate_workout_plan(
    body: GenerateWorkoutRequest,
    user_id: str = Depends(require_auth),
):
    """Gera plano de treino personalizado com Grok."""
    _check_ai_key()
    if body.level not in ("beginner", "intermediate", "advanced"):
        raise HTTPException(status_code=400, detail="level deve ser: beginner, intermediate ou advanced")
    if body.goal not in ("strength", "endurance", "hypertrophy", "balance"):
        raise HTTPException(status_code=400, detail="goal deve ser: strength, endurance, hypertrophy ou balance")
    try:
        return await ai_service.generate_workout_plan(
            user_id=user_id,
            level=body.level,
            goal=body.goal,
            equipment=body.equipment,
            duration_days=body.duration_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar treino: {str(e)}")


@router.post("/coach", response_model=CoachMessageResponse)
async def coach_chat(
    body: CoachMessageRequest,
    user_id: str = Depends(require_auth),
):
    """Coach virtual conversacional. Mantém histórico da conversa por 24h."""
    _check_ai_key()
    try:
        return await ai_service.coach_chat(user_id=user_id, message=body.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no coach: {str(e)}")