"""
RPG Fitness Tracker - FastAPI Backend
Серверная часть с REST API для фронтенда
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from progression import (
    calculate_level_from_xp,
    calculate_xp_for_level,
    calculate_overall_level,
    apply_decrement,
    calculate_xp_from_exercise as calculate_workout_xp
)
from exercises_db import EXERCISES, get_exercise_by_id as get_exercise, search_exercises

def get_all_exercises():
    """Вернуть все упражнения"""
    return EXERCISES

from database import Database

app = FastAPI(title="RPG Fitness Tracker", version="1.0")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД
db = Database()

def get_user_progress(user_id: str = "default"):
    """Получить прогресс пользователя"""
    if not db.load_user(user_id):
        db.create_user(user_id)
        db.load_user(user_id)
    return db

# === Pydantic модели ===

class WorkoutLog(BaseModel):
    exercise_id: str
    sets: int = 1
    reps: int = 1
    duration_seconds: Optional[float] = None
    distance_meters: Optional[float] = None
    intensity_multiplier: float = 1.0
    notes: Optional[str] = None

class ZoneUpdate(BaseModel):
    zone_name: str
    xp_to_add: float
    skip_decrement_days: int = 0

class UserProgress(BaseModel):
    overall_level: int
    overall_xp: float
    next_level_xp: float
    zones: Dict[str, dict]
    last_workout: Optional[str]
    streak_days: int

# === Эндпоинты ===

@app.get("/")
def root():
    return {"message": "RPG Fitness API", "status": "running"}

@app.get("/api/progress", response_model=UserProgress)
def get_progress(user_id: str = "default"):
    """Получить весь прогресс пользователя"""
    user_db = get_user_progress(user_id)
    zones = user_db.get_zones()
    
    # Применяем декремент перед возвратом данных
    today = datetime.now().date()
    for zone_name, zone_obj in zones.items():
        if zone_obj.last_trained:
            last_date = datetime.fromisoformat(zone_obj.last_trained).date()
            days_skipped = (today - last_date).days
            if days_skipped > 1:
                new_xp = apply_decrement(
                    zone_obj.current_xp,
                    calculate_level_from_xp(zone_obj.current_xp),
                    days_skipped
                )
                zone_obj.current_xp = new_xp
    
    user_db.save()
    
    # Считаем общий уровень и XP
    zone_levels_dict = {}
    total_level_xp = 0.0
    for name, z in zones.items():
        level_tuple = calculate_level_from_xp(z.current_xp)
        zone_levels_dict[name] = level_tuple[0]  # level
        total_level_xp += level_tuple[0]
    
    overall = calculate_overall_level(zones)  # Передаём объекты ZoneProgress
    overall_xp = total_level_xp / len(zones) if zones else 0
    
    return UserProgress(
        overall_level=overall,
        overall_xp=overall_xp,
        next_level_xp=calculate_xp_for_level(overall + 1),
        zones={
            name: {
                "level": calculate_level_from_xp(z.current_xp),
                "current_xp": z.current_xp,
                "next_level_xp": calculate_xp_for_level(calculate_level_from_xp(z.current_xp) + 1),
                "last_trained": z.last_trained,
                "total_workouts": z.total_workouts
            }
            for name, z in zones.items()
        },
        last_workout=user_db.user_data.get("last_workout"),
        streak_days=user_db.user_data.get("streak_days", 0)
    )

@app.post("/api/workout")
def log_workout(workout: WorkoutLog, user_id: str = "default"):
    """Записать тренировку и начислить XP"""
    exercise = get_exercise(workout.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    user_db = get_user_progress(user_id)
    
    # Считаем XP для каждой зоны
    xp_gains = calculate_workout_xp(
        exercise,
        workout.sets,
        workout.reps,
        workout.duration_seconds,
        workout.distance_meters,
        workout.intensity_multiplier
    )
    
    # Начисляем XP через Database API
    today = datetime.now().isoformat()
    for zone_name, xp in xp_gains.items():
        zones = user_db.get_zones()
        if zone_name in zones:
            zone = zones[zone_name]
            zone.current_xp += xp
            zone.last_trained = today
            zone.total_workouts += 1
            user_db.set_zone(zone)
    
    user_db.user_data["last_workout"] = today
    
    # Обновляем стрик
    if user_db.user_data.get("last_workout"):
        last = datetime.fromisoformat(user_db.user_data["last_workout"]).date()
        today_date = datetime.now().date()
        diff = (today_date - last).days
        if diff == 1:
            user_db.user_data["streak_days"] = user_db.user_data.get("streak_days", 0) + 1
        elif diff > 1:
            user_db.user_data["streak_days"] = 1
    else:
        user_db.user_data["streak_days"] = 1
    
    user_db.save()
    
    return {
        "message": "Workout logged!",
        "xp_gains": xp_gains,
        "new_levels": {
            zone: calculate_level_from_xp(user_db.get_zones()[zone].current_xp)
            for zone in xp_gains.keys()
        }
    }

@app.get("/api/exercises")
def list_exercises(category: Optional[str] = None):
    """Получить список упражнений"""
    exercises = get_all_exercises()
    if category:
        exercises = [e for e in exercises if e.get("category") == category]
    return exercises

@app.get("/api/exercises/{exercise_id}")
def get_exercise_detail(exercise_id: str):
    """Получить детали упражнения"""
    exercise = get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@app.get("/api/zones")
def list_zones():
    """Получить список зон тела"""
    from config import ZONES
    return [{"name": z, "description": ZONES[z]} for z in ZONES]

@app.post("/api/decrement/simulate")
def simulate_decrement(days: int = 7):
    """Симулировать декремент через N дней (для демонстрации)"""
    data = db.load_data()
    results = {}
    
    for zone_name, zone_data in data["zones"].items():
        current_xp = zone_data["current_xp"]
        level = calculate_level_from_xp(current_xp)
        new_xp = apply_decrement(current_xp, level, days)
        results[zone_name] = {
            "current_xp": current_xp,
            "level": level,
            "xp_after_decay": new_xp,
            "loss_percent": round((1 - new_xp / max(current_xp, 0.01)) * 100, 2)
        }
    
    return {"days": days, "decay_simulation": results}

@app.get("/api/stats")
def get_stats():
    """Получить расширенную статистику"""
    data = db.load_data()
    history = data.get("workout_history", [])[-20:]  # Последние 20 тренировок
    
    zone_levels = {
        name: calculate_level_from_xp(z["current_xp"])
        for name, z in data["zones"].items()
    }
    
    return {
        "total_workouts": len(history),
        "current_streak": data.get("streak_days", 0),
        "zone_levels": zone_levels,
        "overall_level": calculate_overall_level(zone_levels),
        "recent_history": history
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
