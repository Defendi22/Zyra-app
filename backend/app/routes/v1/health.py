"""
Roteador de Saúde — Métricas (IMC, TMB), Treinos, Streak, Check-ins
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.middleware.auth import require_auth

router = APIRouter()

# ==================== SCHEMAS ====================

class HealthMetricsRequest(BaseModel):
    """Registrar métricas de saúde"""
    date: datetime
    weight_kg: float
    body_fat_pct: Optional[float] = None
    height_cm: Optional[float] = None


class HealthMetricsResponse(BaseModel):
    """Resposta com métricas calculadas"""
    id: str
    user_id: str
    date: datetime
    weight_kg: float
    body_fat_pct: Optional[float]
    imc: float  # Índice de Massa Corporal
    tmb: float  # Taxa Metabólica Basal


class CreateWorkoutRequest(BaseModel):
    """Registrar treino"""
    date: datetime
    duration_min: int
    notes: Optional[str] = None
    gym_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class WorkoutResponse(BaseModel):
    """Resposta de treino"""
    id: str
    user_id: str
    date: datetime
    duration_min: int
    notes: Optional[str]
    created_at: datetime


class StreakResponse(BaseModel):
    """Response de streak"""
    current_streak: int
    longest_streak: int
    last_checkin: Optional[datetime]


# ==================== ENDPOINTS ====================

@router.post("/metrics", response_model=HealthMetricsResponse)
async def create_health_metrics(
    request: Request,
    body: HealthMetricsRequest,
    user_id: str = Depends(require_auth),
):
    """Registrar métricas de saúde (peso, body fat, altura)"""
    # TODO: Implementar cálculo de IMC + TMB
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/metrics", response_model=List[HealthMetricsResponse])
async def get_health_metrics(
    request: Request,
    limit: int = 30,
    user_id: str = Depends(require_auth),
):
    """Histórico de métricas de saúde"""
    # TODO: Implementar histórico
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/workouts", response_model=WorkoutResponse)
async def create_workout(
    request: Request,
    body: CreateWorkoutRequest,
    user_id: str = Depends(require_auth),
):
    """Registrar novo treino + check-in na academia"""
    # TODO: Implementar criação de treino
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/workouts", response_model=List[WorkoutResponse])
async def get_workouts(
    request: Request,
    limit: int = 30,
    user_id: str = Depends(require_auth),
):
    """Histórico de treinos"""
    # TODO: Implementar histórico de treinos
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    request: Request,
    user_id: str = Depends(require_auth),
):
    """Obter streak (dias consecutivos na academia)"""
    # TODO: Implementar cálculo de streak
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/checkin")
async def checkin(
    request: Request,
    gym_name: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    user_id: str = Depends(require_auth),
):
    """Check-in rápido de academia (para streak)"""
    # TODO: Implementar check-in
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )
