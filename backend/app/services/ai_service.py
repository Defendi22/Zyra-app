"""
AI Service — Modo Mock Ativado (para desenvolvimento)
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict

from app.config import settings
from app.cache.redis_client import redis_client

logger = logging.getLogger("zyra.ai")


class AIService:

    # ==================== MODO MOCK ====================
    USE_MOCK = True   # ← Mantenha como True enquanto não tiver créditos

    @staticmethod
    async def analyze_meal(image_base64: str, user_id: str) -> Dict:
        """Análise de refeição simulada"""
        logger.info(f"🍽️  MODO MOCK - Análise de refeição (user: {user_id})")
        return {
            "foods": [
                {"name": "Arroz branco", "quantity": "200g", "kcal": 260},
                {"name": "Peito de frango grelhado", "quantity": "150g", "kcal": 248},
                {"name": "Feijão carioca", "quantity": "120g", "kcal": 150},
                {"name": "Salada de alface e tomate", "quantity": "100g", "kcal": 35}
            ],
            "total_kcal": 693,
            "macros": {"protein_g": 48, "carbs_g": 72, "fat_g": 18},
            "confidence": 0.92,
            "notes": "Refeição bem balanceada. Boa fonte de proteína."
        }

    @staticmethod
    async def generate_diet_plan(
        user_id: str, goal: str, daily_kcal: int, restrictions: List[str] = None, duration_days: int = 7
    ) -> Dict:
        """Plano de dieta simulado"""
        logger.info(f"📋 MODO MOCK - Diet Plan gerado ({goal} - {daily_kcal}kcal)")
        return {
            "id": f"diet_mock_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "goal": goal,
            "calories": daily_kcal,
            "summary": f"Plano de {duration_days} dias para {goal} com {daily_kcal} calorias diárias.",
            "macros_daily": {"protein_g": 140, "carbs_g": 180, "fat_g": 70},
            "days": [{"day": i, "meals": [
                {"name": "Café da manhã", "kcal": 500},
                {"name": "Almoço", "kcal": 700},
                {"name": "Jantar", "kcal": 600}
            ]} for i in range(1, 4)],
            "tips": ["Beba no mínimo 3 litros de água", "Durma bem", "Seja consistente"]
        }

    @staticmethod
    async def generate_workout_plan(
        user_id: str, level: str, goal: str, equipment: List[str] = None, duration_days: int = 7
    ) -> Dict:
        """Plano de treino simulado"""
        logger.info(f"🏋️ MODO MOCK - Workout Plan gerado ({goal} - {level})")
        return {
            "id": f"workout_mock_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "level": level,
            "goal": goal,
            "summary": f"Plano de treino de {duration_days} dias focado em {goal}",
            "days": [
                {"day": 1, "focus": "Peito e Tríceps", "exercises": [
                    {"name": "Supino Reto", "sets": 4, "reps": "8-12"}
                ]}
            ],
            "tips": ["Aquecimento de 5-10 min", "Foquem na técnica", "Aumente a carga gradualmente"]
        }

    @staticmethod
    async def coach_chat(user_id: str, message: str) -> Dict:
        """Coach conversacional simulado"""
        logger.info(f"🗣️  MODO MOCK - Coach respondeu")
        return {
            "response": "Ótima pergunta! Para ter resultados rápidos, o mais importante é consistência. Qual é seu principal objetivo agora: perder gordura, ganhar massa ou melhorar desempenho?",
            "suggestions": [
                "Me conte seu peso e altura atuais",
                "Quantos dias por semana você consegue treinar?",
                "Qual sua refeição principal do dia?"
            ]
        }


# Instância global
ai_service = AIService()