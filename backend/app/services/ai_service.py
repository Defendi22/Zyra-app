"""
AI Service — Google Gemini (análise de refeição, planos, coach)
"""

import json
import logging
import hashlib
import base64
from datetime import datetime, timezone
from typing import List, Optional, Dict

import google.generativeai as genai

from app.config import settings
from app.cache.redis_client import redis_client

logger = logging.getLogger("zyra.ai")


def _init_gemini():
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(settings.GEMINI_MODEL)


class AIService:

    # ==================== ANÁLISE DE REFEIÇÃO ====================

    @staticmethod
    async def analyze_meal(image_base64: str, user_id: str) -> Dict:
        """
        Analisa foto de refeição com Gemini Vision.
        Retorna alimentos identificados, calorias e macros.
        Usa cache Redis para evitar chamadas repetidas da mesma imagem.
        """
        # Hash da imagem para cache
        image_hash = hashlib.md5(image_base64.encode()).hexdigest()
        cache_key = f"meal_analysis:{image_hash}"

        # Verifica cache
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit para análise de refeição: {image_hash[:8]}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache check failed: {e}")

        # Valida base64
        try:
            image_data = base64.b64decode(image_base64)
        except Exception:
            raise ValueError("Imagem inválida — envie em formato base64")

        # Chama Gemini Vision
        try:
            model = _init_gemini()

            prompt = """Analise esta foto de refeição e retorne um JSON com exatamente este formato:
{
  "foods": [
    {"name": "nome do alimento", "quantity": "quantidade estimada", "kcal": 000}
  ],
  "total_kcal": 000,
  "macros": {
    "protein_g": 00,
    "carbs_g": 00,
    "fat_g": 00
  },
  "confidence": 0.0
}
Seja preciso nas estimativas calóricas. Retorne APENAS o JSON, sem texto adicional."""

            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data,
            }

            response = model.generate_content([prompt, image_part])
            text = response.text.strip()

            # Remove markdown se presente
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            result = json.loads(text)

            # Salva no cache por 1 hora
            try:
                await redis_client.set(cache_key, json.dumps(result), ttl=3600)
            except Exception as e:
                logger.warning(f"Redis cache save failed: {e}")

            logger.info(f"Refeição analisada para user {user_id}: {result.get('total_kcal')} kcal")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Gemini retornou JSON inválido: {e}")
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
        """Gera plano de dieta personalizado com Gemini"""
        try:
            model = _init_gemini()

            restrictions_text = ", ".join(restrictions) if restrictions else "nenhuma"

            prompt = f"""Crie um plano de dieta detalhado em português com estas especificações:
- Objetivo: {goal} (loss=perda de peso, gain=ganho de massa, maintenance=manutenção)
- Calorias diárias: {daily_kcal} kcal
- Restrições alimentares: {restrictions_text}
- Duração: {duration_days} dias

Retorne um JSON com este formato:
{{
  "summary": "resumo do plano em 2 frases",
  "daily_calories": {daily_kcal},
  "macros_daily": {{"protein_g": 0, "carbs_g": 0, "fat_g": 0}},
  "days": [
    {{
      "day": 1,
      "meals": [
        {{"name": "Café da manhã", "foods": ["alimento 1", "alimento 2"], "kcal": 0}},
        {{"name": "Almoço", "foods": ["alimento 1", "alimento 2"], "kcal": 0}},
        {{"name": "Jantar", "foods": ["alimento 1", "alimento 2"], "kcal": 0}},
        {{"name": "Lanches", "foods": ["alimento 1"], "kcal": 0}}
      ]
    }}
  ],
  "tips": ["dica 1", "dica 2", "dica 3"]
}}
Retorne APENAS o JSON, sem texto adicional."""

            response = model.generate_content(prompt)
            text = response.text.strip()

            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            plan = json.loads(text)

            result = {
                "id": f"diet_{user_id[:8]}_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "goal": goal,
                "calories": daily_kcal,
                "content": plan,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"Plano de dieta gerado para user {user_id}: {goal}, {daily_kcal} kcal")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Gemini retornou JSON inválido: {e}")
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
        """Gera plano de treino personalizado com Gemini"""
        try:
            model = _init_gemini()

            equipment_text = ", ".join(equipment) if equipment else "sem equipamento (peso corporal)"

            prompt = f"""Crie um plano de treino detalhado em português com estas especificações:
- Nível: {level} (beginner=iniciante, intermediate=intermediário, advanced=avançado)
- Objetivo: {goal} (strength=força, endurance=resistência, hypertrophy=hipertrofia, balance=equilíbrio)
- Equipamentos disponíveis: {equipment_text}
- Duração: {duration_days} dias

Retorne um JSON com este formato:
{{
  "summary": "resumo do plano em 2 frases",
  "days": [
    {{
      "day": 1,
      "focus": "grupo muscular ou tipo de treino",
      "duration_min": 0,
      "exercises": [
        {{"name": "exercício", "sets": 0, "reps": "0-0", "rest_sec": 0, "notes": "observação"}}
      ]
    }}
  ],
  "tips": ["dica 1", "dica 2", "dica 3"]
}}
Retorne APENAS o JSON, sem texto adicional."""

            response = model.generate_content(prompt)
            text = response.text.strip()

            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            plan = json.loads(text)

            result = {
                "id": f"workout_{user_id[:8]}_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "level": level,
                "goal": goal,
                "content": plan,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"Plano de treino gerado para user {user_id}: {level}, {goal}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Gemini retornou JSON inválido: {e}")
            raise ValueError("Erro ao processar plano de treino")
        except Exception as e:
            logger.error(f"Erro ao gerar plano de treino: {e}")
            raise

    # ==================== COACH ====================

    @staticmethod
    async def coach_chat(user_id: str, message: str) -> Dict:
        """
        Coach virtual conversacional.
        Mantém histórico da conversa no Redis (últimas 10 mensagens).
        """
        try:
            model = _init_gemini()

            # Busca histórico do Redis
            history_key = f"coach_history:{user_id}"
            history = []
            try:
                cached_history = await redis_client.get(history_key)
                if cached_history:
                    history = json.loads(cached_history)
            except Exception as e:
                logger.warning(f"Erro ao buscar histórico do coach: {e}")

            # Monta conversa
            system_prompt = """Você é o ZYRA Coach, um personal trainer e nutricionista virtual especializado.
Você é motivador, direto e baseado em ciência. Responda sempre em português.
Dê conselhos práticos sobre treino, nutrição e saúde. Seja conciso (máximo 3 parágrafos).
Ao final, sugira 2-3 ações práticas que o usuário pode tomar."""

            # Formata histórico para o Gemini
            chat_history = []
            for h in history[-10:]:  # últimas 10 mensagens
                chat_history.append({"role": h["role"], "parts": [h["content"]]})

            chat = model.start_chat(history=chat_history)
            full_message = f"{system_prompt}\n\nUsuário: {message}"
            response = chat.send_message(full_message)
            reply = response.text

            # Extrai sugestões (últimas linhas com bullets)
            suggestions = []
            lines = reply.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(("•", "-", "*", "1.", "2.", "3.")):
                    clean = line.lstrip("•-*123. ").strip()
                    if clean:
                        suggestions.append(clean)

            # Salva histórico
            history.append({"role": "user", "content": message})
            history.append({"role": "model", "content": reply})
            history = history[-20:]  # mantém últimas 20 mensagens

            try:
                await redis_client.set(history_key, json.dumps(history), ttl=86400)  # 24h
            except Exception as e:
                logger.warning(f"Erro ao salvar histórico do coach: {e}")

            logger.info(f"Coach respondeu para user {user_id}")
            return {
                "response": reply,
                "suggestions": suggestions[:3],
            }

        except Exception as e:
            logger.error(f"Erro no coach: {e}")
            raise


ai_service = AIService()