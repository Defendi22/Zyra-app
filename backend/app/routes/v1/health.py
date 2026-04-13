"""
Roteador de Saúde — Métricas (IMC, TMB), Treinos, Streak, Check-ins
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.middleware.auth import require_auth
from app.services.health_service import health_service

router = APIRouter()


# ==================== SCHEMAS ====================

class HealthMetricsRequest(BaseModel):
    date: datetime
    weight_kg: float = Field(..., gt=0, le=500, description="Peso em kg")
    height_cm: float = Field(..., gt=0, le=300, description="Altura em cm")
    body_fat_pct: Optional[float] = Field(None, ge=0, le=100)
    age: int = Field(25, ge=1, le=120, description="Idade em anos")
    gender: str = Field("male", description="'male' ou 'female'")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-04-10T10:00:00",
                "weight_kg": 80.5,
                "height_cm": 178.0,
                "body_fat_pct": 18.0,
                "age": 25,
                "gender": "male",
            }
        }


class HealthMetricsResponse(BaseModel):
    id: str
    user_id: str
    date: str
    weight_kg: float
    height_cm: float
    body_fat_pct: Optional[float]
    imc: float
    tmb: float
    imc_classification: str
    created_at: str


class CreateWorkoutRequest(BaseModel):
    date: datetime
    duration_min: int = Field(..., gt=0, description="Duração em minutos")
    notes: Optional[str] = Field(None, max_length=500)
    gym_name: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-04-10T08:00:00",
                "duration_min": 60,
                "notes": "Treino de peito e tríceps",
                "gym_name": "Smart Fit",
                "latitude": -23.5505,
                "longitude": -46.6333,
            }
        }


class WorkoutResponse(BaseModel):
    id: str
    user_id: str
    date: str
    duration_min: int
    notes: Optional[str]
    gym_name: Optional[str]
    created_at: str


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_checkin: Optional[str]


# ==================== ENDPOINTS ====================

@router.post("/metrics", response_model=HealthMetricsResponse, status_code=201)
async def create_health_metrics(
    body: HealthMetricsRequest,
    user_id: str = Depends(require_auth),
):
    """
    Registrar métricas de saúde.
    Calcula automaticamente IMC e TMB.
    """
    try:
        result = await health_service.create_metrics(
            user_id=user_id,
            date=body.date,
            weight_kg=body.weight_kg,
            height_cm=body.height_cm,
            body_fat_pct=body.body_fat_pct,
            age=body.age,
            gender=body.gender,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar métricas: {str(e)}",
        )


@router.get("/metrics", response_model=List[HealthMetricsResponse])
async def get_health_metrics(
    limit: int = Query(30, ge=1, le=100),
    user_id: str = Depends(require_auth),
):
    """Histórico de métricas de saúde (últimos 30 por padrão)"""
    try:
        return await health_service.get_metrics(user_id=user_id, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar métricas: {str(e)}",
        )


@router.post("/workouts", response_model=WorkoutResponse, status_code=201)
async def create_workout(
    body: CreateWorkoutRequest,
    user_id: str = Depends(require_auth),
):
    """Registrar novo treino"""
    try:
        result = await health_service.create_workout(
            user_id=user_id,
            date=body.date,
            duration_min=body.duration_min,
            notes=body.notes,
            gym_name=body.gym_name,
            latitude=body.latitude,
            longitude=body.longitude,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar treino: {str(e)}",
        )


@router.get("/workouts", response_model=List[WorkoutResponse])
async def get_workouts(
    limit: int = Query(30, ge=1, le=100),
    user_id: str = Depends(require_auth),
):
    """Histórico de treinos"""
    try:
        return await health_service.get_workouts(user_id=user_id, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar treinos: {str(e)}",
        )


@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    user_id: str = Depends(require_auth),
):
    """Streak atual e maior streak de treinos consecutivos"""
    try:
        return await health_service.get_streak(user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular streak: {str(e)}",
        )


@router.post("/checkin", response_model=WorkoutResponse, status_code=201)
async def checkin(
    gym_name: str = Query(..., description="Nome da academia"),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    user_id: str = Depends(require_auth),
):
    """Check-in rápido na academia — conta para o streak do dia"""
    try:
        result = await health_service.checkin(
            user_id=user_id,
            gym_name=gym_name,
            latitude=latitude,
            longitude=longitude,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no check-in: {str(e)}",
        )