"""
Roteador de IA — Gemini Integration (Meal Analysis, Workout Plans, Coach)
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
import base64

from app.middleware.auth import require_auth

router = APIRouter()

# ==================== SCHEMAS ====================

class MealAnalysisRequest(BaseModel):
    """Análise de foto de refeição"""
    image_base64: str  # Imagem em base64


class FoodItem(BaseModel):
    """Item de comida identificado"""
    name: str
    quantity: str  # Ex: "200g", "1 prato"
    kcal: float


class MealAnalysisResponse(BaseModel):
    """Resposta de análise de refeição"""
    foods: List[FoodItem]
    total_kcal: float
    macros: dict  # {protein_g, carbs_g, fat_g}
    confidence: float  # 0-1


class GenerateDietRequest(BaseModel):
    """Gerar plano de dieta personalizado"""
    goal: str  # 'loss' | 'gain' | 'maintenance'
    daily_kcal: int
    restrictions: List[str] = []  # Ex: ["vegetarian", "gluten-free"]
    duration_days: int = 7


class GenerateDietResponse(BaseModel):
    """Resposta com plano de dieta"""
    id: str
    user_id: str
    content: str  # Plano em formato texto/json
    calories: int
    created_at: str


class GenerateWorkoutRequest(BaseModel):
    """Gerar plano de treino personalizado"""
    level: str  # 'beginner' | 'intermediate' | 'advanced'
    goal: str  # 'strength' | 'endurance' | 'hypertrophy' | 'balance'
    equipment: List[str] = []  # Ex: ["dumbbells", "barbell"]
    duration_days: int = 7


class CoachMessageRequest(BaseModel):
    """Mensagem para o coach de IA"""
    message: str


class CoachMessageResponse(BaseModel):
    """Resposta do coach"""
    response: str
    suggestions: List[str] = []


# ==================== ENDPOINTS ====================

@router.post("/analyze-meal", response_model=MealAnalysisResponse)
async def analyze_meal(
    request: Request,
    body: MealAnalysisRequest,
    user_id: str = Depends(require_auth),
):
    """
    Analisar foto de refeição com Gemini Vision
    - Input: imagem em base64
    - Output: alimentos identificados, calorias totais, macros
    - Cache: hash da imagem no Redis por 1h
    """
    # TODO: Implementar integração com Gemini Vision
    # 1. Validar base64
    # 2. Fazer hash da imagem
    # 3. Verificar cache no Redis
    # 4. Se cache miss: chamar Gemini API
    # 5. Salvar resultado no Redis
    # 6. Retornar análise
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/generate-diet", response_model=GenerateDietResponse)
async def generate_diet_plan(
    request: Request,
    body: GenerateDietRequest,
    user_id: str = Depends(require_auth),
):
    """
    Gerar plano de dieta personalizado com Gemini
    """
    # TODO: Implementar geração de dieta
    # 1. Pegar contexto do usuário (peso, altura, objetivo)
    # 2. Chamar Gemini com prompt estruturado
    # 3. Salvar plano no Supabase (diet_plans)
    # 4. Retornar plano
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/generate-workout")
async def generate_workout_plan(
    request: Request,
    body: GenerateWorkoutRequest,
    user_id: str = Depends(require_auth),
):
    """
    Gerar plano de treino personalizado com Gemini
    """
    # TODO: Implementar geração de treino
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )


@router.post("/coach", response_model=CoachMessageResponse)
async def coach_chat(
    request: Request,
    body: CoachMessageRequest,
    user_id: str = Depends(require_auth),
):
    """
    Coach virtual conversacional com contexto do usuário
    """
    # TODO: Implementar chat com Gemini
    # 1. Pegar histórico de mensagens do Redis
    # 2. Pegar contexto do usuário (métricas, treinos, refeições)
    # 3. Montar prompt com contexto
    # 4. Chamar Gemini API
    # 5. Salvar conversa no Redis
    # 6. Retornar resposta
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento",
    )
