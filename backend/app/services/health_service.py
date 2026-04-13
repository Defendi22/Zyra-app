"""
Health Service — IMC, TMB, Treinos, Streak
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
from uuid import uuid4

from app.db.supabase_client import supabase_client

logger = logging.getLogger("zyra.health")


def calcular_imc(weight_kg: float, height_cm: float) -> float:
    """IMC = peso / (altura em metros)²"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def classificar_imc(imc: float) -> str:
    """Classificação da OMS"""
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidade grau I"
    elif imc < 40:
        return "Obesidade grau II"
    else:
        return "Obesidade grau III"


def calcular_tmb(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    TMB pela fórmula de Harris-Benedict revisada (Mifflin-St Jeor):
    Homem:  10 × peso + 6.25 × altura - 5 × idade + 5
    Mulher: 10 × peso + 6.25 × altura - 5 × idade - 161
    """
    tmb = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender.lower() in ("male", "masculino", "m"):
        tmb += 5
    else:
        tmb -= 161
    return round(tmb, 2)


class HealthService:

    # ==================== MÉTRICAS ====================

    @staticmethod
    async def create_metrics(
        user_id: str,
        date: datetime,
        weight_kg: float,
        height_cm: float,
        body_fat_pct: Optional[float] = None,
        age: int = 25,
        gender: str = "male",
    ) -> Dict:
        """Salva métricas e calcula IMC + TMB"""
        imc = calcular_imc(weight_kg, height_cm)
        tmb = calcular_tmb(weight_kg, height_cm, age, gender)

        data = {
            "user_id": user_id,
            "date": date.isoformat(),
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "body_fat_pct": body_fat_pct,
            "imc": imc,
            "tmb": tmb,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = supabase_client.service_client.table("health_metrics").insert(data).execute()
            record = result.data[0] if result.data else data
            logger.info(f"Métricas salvas para user {user_id}: IMC={imc}, TMB={tmb}")
        except Exception as e:
            logger.warning(f"Supabase unavailable, returning calculated data: {e}")
            record = {"id": str(uuid4()), **data}

        return {
            **record,
            "imc": imc,
            "tmb": tmb,
            "imc_classification": classificar_imc(imc),
        }

    @staticmethod
    async def get_metrics(user_id: str, limit: int = 30) -> List[Dict]:
        """Histórico de métricas do usuário"""
        try:
            result = (
                supabase_client.service_client
                .table("health_metrics")
                .select("*")
                .eq("user_id", user_id)
                .order("date", desc=True)
                .limit(limit)
                .execute()
            )
            records = result.data or []
            # Adiciona classificação em cada registro
            for r in records:
                r["imc_classification"] = classificar_imc(r["imc"])
            return records
        except Exception as e:
            logger.warning(f"Erro ao buscar métricas: {e}")
            return []

    # ==================== TREINOS ====================

    @staticmethod
    async def create_workout(
        user_id: str,
        date: datetime,
        duration_min: int,
        notes: Optional[str] = None,
        gym_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict:
        """Registra um treino"""
        data = {
            "user_id": user_id,
            "date": date.isoformat(),
            "duration_min": duration_min,
            "notes": notes,
            "gym_name": gym_name,
            "latitude": latitude,
            "longitude": longitude,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = supabase_client.service_client.table("workouts").insert(data).execute()
            record = result.data[0] if result.data else {"id": str(uuid4()), **data}
            logger.info(f"Treino salvo para user {user_id}: {duration_min}min")
            return record
        except Exception as e:
            logger.warning(f"Erro ao salvar treino: {e}")
            return {"id": str(uuid4()), **data}

    @staticmethod
    async def get_workouts(user_id: str, limit: int = 30) -> List[Dict]:
        """Histórico de treinos do usuário"""
        try:
            result = (
                supabase_client.service_client
                .table("workouts")
                .select("*")
                .eq("user_id", user_id)
                .order("date", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.warning(f"Erro ao buscar treinos: {e}")
            return []

    # ==================== STREAK ====================

    @staticmethod
    async def get_streak(user_id: str) -> Dict:
        """
        Calcula streak (dias consecutivos com treino).
        Considera um treino por dia — não importa quantos.
        """
        try:
            result = (
                supabase_client.service_client
                .table("workouts")
                .select("date")
                .eq("user_id", user_id)
                .order("date", desc=True)
                .execute()
            )
            workouts = result.data or []
        except Exception as e:
            logger.warning(f"Erro ao buscar treinos para streak: {e}")
            return {"current_streak": 0, "longest_streak": 0, "last_checkin": None}

        if not workouts:
            return {"current_streak": 0, "longest_streak": 0, "last_checkin": None}

        # Extrai datas únicas (sem hora)
        dates = sorted(set(
            datetime.fromisoformat(w["date"].replace("Z", "+00:00")).date()
            for w in workouts
        ), reverse=True)

        today = datetime.now(timezone.utc).date()
        last_checkin = dates[0]

        # Streak atual
        current_streak = 0
        check_date = today
        for d in dates:
            if d == check_date or d == check_date - timedelta(days=1):
                current_streak += 1
                check_date = d
            else:
                break

        # Streak mais longo
        longest_streak = 1
        temp_streak = 1
        for i in range(1, len(dates)):
            if (dates[i - 1] - dates[i]).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_checkin": last_checkin.isoformat(),
        }

    # ==================== CHECK-IN ====================

    @staticmethod
    async def checkin(
        user_id: str,
        gym_name: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict:
        """Check-in rápido — cria treino de duração mínima para contar no streak"""
        return await HealthService.create_workout(
            user_id=user_id,
            date=datetime.now(timezone.utc),
            duration_min=1,
            notes="Check-in",
            gym_name=gym_name,
            latitude=latitude,
            longitude=longitude,
        )


health_service = HealthService()