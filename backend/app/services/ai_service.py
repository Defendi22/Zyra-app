"""
AI Service — xAI Grok (coach, planos de dieta/treino, análise de refeição)
"""

import json
import logging
import hashlib
import base64
from datetime import datetime, timezone
from typing import List, Dict

from openai import AsyncOpenAI

from app.config import settings
from app.cache.redis_client import redis_client

logger = logging.getLogger("zyra.ai")


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )


class AIService:

    # ==================== ANÁLISE DE REFEIÇÃO ====================

    @staticmethod
    async def analyze_meal(image_base64: str, user_id: str) -> Dict:
        """Analisa foto de refeição com Grok Vision."""
        image_hash = hashlib.md5(image_base64.encode()).hexdigest()
        cache_key = f"meal_analysis:{image_hash}"

        try:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit: {image_hash[:8]}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache check failed: {e}")

        try:
            base64.b64decode(image_base64)
        except Exception:
            raise ValueError("Imagem inválida — envie em formato base64")

        try:
            client = _get_client()
            response = await client.chat.completions.create(
                model=settings.XAI_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            },
                            {
                                "type": "text",
                                "text": """Analise esta foto de refeição e retorne um JSON com exatamente este formato:
{
  "foods": [{"name": "nome", "quantity": "quantidade", "kcal": 000}],
  "total_kcal": 000,
  "macros": {"protein_g": 00, "carbs_g": 00, "fat_g": 00},
  "confidence": 0.0
}
Retorne APENAS o JSON, sem texto adicional.""",
                            },
                        ],
                    }
                ],
            )

            text = response.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            result = json.loads(text)

            try:
                await redis_client.set(cache_key, json.dumps(result), ttl=3600)
            except Exception:
                pass

            logger.info(f"Refeição analisada para {user_id}: {result.get('total_kcal')} kcal")
            return result

        except json.JSONDecodeError:
            raise ValueError("Erro ao processar resposta da IA")
        except Exception as e:
            logger.error(f"Erro na análise de refeição: {e}")
            raise

    # ==================== PLANO DE DIETA ====================

    @staticmethod
    async def generate_diet_plan(
        user_id: str,
        goal: str,
        daily_kcal: int,
        restrictions: List[str],
        duration_days: int = 7,
    ) -> Dict:
        """Gera plano de dieta personalizado com Grok."""
        try:
            client = _get_client()
            restrictions_text = ", ".join(restrictions) if restrictions else "nenhuma"

            prompt = f"""Crie um plano de dieta detalhado em português:
- Objetivo: {goal} (loss=perda de peso, gain=ganho de massa, maintenance=manutencao)
- Calorias diárias: {daily_kcal} kcal
- Restrições: {restrictions_text}
- Duração: {duration_days} dias

Retorne um JSON com este formato:
{{
  "summary": "resumo em 2 frases",
  "daily_calories": {daily_kcal},
  "macros_daily": {{"protein_g": 0, "carbs_g": 0, "fat_g": 0}},
  "days": [
    {{
      "day": 1,
      "meals": [
        {{"name": "Cafe da manha", "foods": ["alimento 1"], "kcal": 0}},
        {{"name": "Almoco", "foods": ["alimento 1"], "kcal": 0}},
        {{"name": "Jantar", "foods": ["alimento 1"], "kcal": 0}},
        {{"name": "Lanches", "foods": ["alimento 1"], "kcal": 0}}
      ]
    }}
  ],
  "tips": ["dica 1", "dica 2", "dica 3"]
}}
Retorne APENAS o JSON, sem texto adicional."""

            response = await client.chat.completions.create(
                model=settings.XAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            plan = json.loads(text)
            logger.info(f"Plano de dieta gerado para {user_id}: {goal}, {daily_kcal} kcal")

            return {
                "id": f"diet_{user_id[:8]}_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "goal": goal,
                "calories": daily_kcal,
                "content": plan,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

        except json.JSONDecodeError:
            raise ValueError("Erro ao processar plano de dieta")
        except Exception as e:
            logger.error(f"Erro ao gerar plano de dieta: {e}")
            raise

    # ==================== PLANO DE TREINO ====================

    @staticmethod
    async def generate_workout_plan(
        user_id: str,
        level: str,
        goal: str,
        equipment: List[str],
        duration_days: int = 7,
    ) -> Dict:
        """Gera plano de treino personalizado com Grok."""
        try:
            client = _get_client()
            equipment_text = ", ".join(equipment) if equipment else "sem equipamento"

            prompt = f"""Crie um plano de treino detalhado em português:
- Nível: {level} (beginner=iniciante, intermediate=intermediário, advanced=avançado)
- Objetivo: {goal} (strength=força, endurance=resistência, hypertrophy=hipertrofia, balance=equilíbrio)
- Equipamentos: {equipment_text}
- Duração: {duration_days} dias

Retorne um JSON com este formato:
{{
  "summary": "resumo em 2 frases",
  "days": [
    {{
      "day": 1,
      "focus": "grupo muscular",
      "duration_min": 0,
      "exercises": [
        {{"name": "exercicio", "sets": 0, "reps": "0-0", "rest_sec": 0, "notes": "observacao"}}
      ]
    }}
  ],
  "tips": ["dica 1", "dica 2", "dica 3"]
}}
Retorne APENAS o JSON, sem texto adicional."""

            response = await client.chat.completions.create(
                model=settings.XAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            plan = json.loads(text)
            logger.info(f"Plano de treino gerado para {user_id}: {level}, {goal}")

            return {
                "id": f"workout_{user_id[:8]}_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "level": level,
                "goal": goal,
                "content": plan,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

        except json.JSONDecodeError:
            raise ValueError("Erro ao processar plano de treino")
        except Exception as e:
            logger.error(f"Erro ao gerar plano de treino: {e}")
            raise

    # ==================== COACH ====================

    @staticmethod
    async def coach_chat(user_id: str, message: str) -> Dict:
        """Coach virtual conversacional com histórico no Redis."""
        try:
            client = _get_client()

            history_key = f"coach_history:{user_id}"
            history = []
            try:
                cached_history = await redis_client.get(history_key)
                if cached_history:
                    history = json.loads(cached_history)
            except Exception:
                pass

            messages = [
                {
                    "role": "system",
                    "content": """Você é o ZYRA Coach, personal trainer e nutricionista virtual.
Seja motivador, direto e baseado em ciência. Responda sempre em português.
Máximo 3 parágrafos. Ao final, sugira 2-3 ações práticas numeradas.""",
                }
            ]

            for h in history[-6:]:
                messages.append({"role": h["role"], "content": h["content"]})

            messages.append({"role": "user", "content": message})

            response = await client.chat.completions.create(
                model=settings.XAI_MODEL,
                messages=messages,
            )

            reply = response.choices[0].message.content.strip()

            suggestions = []
            for line in reply.split("\n"):
                line = line.strip()
                if line and line[0].isdigit() and len(line) > 2 and line[1] in ".)":
                    clean = line[2:].strip()
                    if clean:
                        suggestions.append(clean)

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply})
            history = history[-20:]

            try:
                await redis_client.set(history_key, json.dumps(history), ttl=86400)
            except Exception:
                pass

            logger.info(f"Coach respondeu para {user_id}")
            return {"response": reply, "suggestions": suggestions[:3]}

        except Exception as e:
            logger.error(f"Erro no coach: {e}")
            raise


ai_service = AIService()