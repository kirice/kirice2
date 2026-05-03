"""
Модели данных для Fitness RPG
Использует Pydantic для валидации и сериализации
"""

from datetime import datetime
from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ExerciseType(str, Enum):
    """Типы упражнений"""
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    MOBILITY = "mobility"
    FLEXIBILITY = "flexibility"
    CARDIO = "cardio"


class ZoneName(str, Enum):
    """Названия зон тела"""
    LEGS = "legs"
    BACK = "back"
    CHEST = "chest"
    ARMS = "arms"
    CORE = "core"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    MOBILITY = "mobility"
    NECK = "neck"
    GRIP = "grip"
    SHOULDERS = "shoulders"
    OBLIQUES = "obliques"


class IntensityLevel(str, Enum):
    """Уровни интенсивности"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ============================================================================
# Модели конфигурации
# ============================================================================

class ProgressionConfig(BaseModel):
    """Конфигурация прогрессии уровней"""
    base_xp: int = 100
    exponent: float = 1.6
    smoothing_constant: float = 0.5


class DecayConfig(BaseModel):
    """Конфигурация системы декремента"""
    grace_period_days: int = 1
    soft_decay_day: int = 2
    soft_decay_rate: float = 0.05
    base_decay_rate: float = 0.04
    level_scaling_factor: float = 0.015
    min_buffer_percent: float = 0.10
    min_buffer_absolute: int = 50
    skip_days_tolerance: int = 2
    vacation_mode_decay_multiplier: float = 0.0
    illness_mode_decay_multiplier: float = 0.5


class OverallLevelConfig(BaseModel):
    """Конфигурация расчёта общего уровня"""
    variance_penalty_coefficient: float = 0.25


class AppConfig(BaseModel):
    """Основная конфигурация приложения"""
    progression: ProgressionConfig
    decay: DecayConfig
    overall_level: OverallLevelConfig
    
    class Config:
        from_attributes = True


# ============================================================================
# Модели упражнений
# ============================================================================

class BeginnerParams(BaseModel):
    """Параметры для новичков"""
    sets: int = 3
    reps: int = 10
    rest_seconds: int = 60
    duration_seconds: Optional[int] = None
    duration_minutes: Optional[int] = None
    distance_meters: Optional[int] = None


class Exercise(BaseModel):
    """Модель упражнения"""
    name: str
    type: ExerciseType
    base_xp_per_rep: float = Field(gt=0)
    zones: Dict[str, float]
    beginner_params: BeginnerParams
    notes: Optional[str] = None
    is_active: bool = True
    
    @field_validator('zones')
    @classmethod
    def validate_zone_coeffs(cls, v):
        """Проверка коэффициентов зон (должны быть в диапазоне 0-1)"""
        for zone, coeff in v.items():
            if not (0 < coeff <= 1.0):
                raise ValueError(f"Коэффициент зоны {zone} должен быть в диапазоне (0, 1.0]")
        return v


class ExercisesDatabase(BaseModel):
    """База данных упражнений"""
    exercises: List[Exercise]


# ============================================================================
# Модели пользователя и прогресса
# ============================================================================

class User(BaseModel):
    """Модель пользователя"""
    id: Optional[int] = None
    username: str
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    vacation_mode: bool = False
    illness_mode: bool = False


class ZoneProgress(BaseModel):
    """Прогресс по зоне тела"""
    id: Optional[int] = None
    user_id: int
    zone_id: int
    zone_name: str
    current_xp: float = 0.0
    total_xp_earned: float = 0.0
    level: int = 0
    last_trained_date: Optional[datetime] = None


class ZoneWithLevel(BaseModel):
    """Зона с рассчитанным уровнем"""
    zone_name: str
    display_name: str
    level: int
    current_xp: float
    xp_to_next_level: float
    xp_threshold_current: float
    xp_threshold_next: float
    progress_percent: float
    last_trained_date: Optional[datetime] = None
    days_since_trained: Optional[int] = None


class OverallStats(BaseModel):
    """Общая статистика пользователя"""
    overall_level: int
    overall_xp: float
    overall_xp_threshold: float
    harmonic_mean: float
    variance_penalty: float
    zones_count: int
    max_zone_level: int
    min_zone_level: int


# ============================================================================
# Модели тренировок
# ============================================================================

class WorkoutLog(BaseModel):
    """Запись о тренировке"""
    id: Optional[int] = None
    user_id: int
    exercise_id: int
    exercise_name: str
    workout_date: datetime = Field(default_factory=datetime.now)
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    intensity_factor: float = 1.0
    xp_earned: float
    notes: Optional[str] = None


class ZoneXPEntry(BaseModel):
    """XP заработанный в конкретной зоне"""
    zone_name: str
    xp_earned: float


class WorkoutResult(BaseModel):
    """Результат тренировки с детализацией по зонам"""
    workout_log: WorkoutLog
    zone_xp: List[ZoneXPEntry]
    levels_gained: List[Dict[str, int]]  # zone_id -> new_level


class LevelHistoryEntry(BaseModel):
    """Запись истории изменения уровня"""
    id: Optional[int] = None
    user_id: int
    zone_id: int
    old_level: Optional[int]
    new_level: int
    old_xp: float
    new_xp: float
    change_type: Literal["gain", "decay", "manual"]
    changed_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# DTO для API
# ============================================================================

class AddWorkoutRequest(BaseModel):
    """Запрос на добавление тренировки"""
    user_id: int
    exercise_name: str
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    intensity_level: IntensityLevel = IntensityLevel.BEGINNER
    notes: Optional[str] = None


class GetBodyMapResponse(BaseModel):
    """Ответ для карты тела"""
    zones: List[ZoneWithLevel]
    overall_stats: OverallStats


class ApplyDecayRequest(BaseModel):
    """Запрос на применение декремента"""
    user_id: int
    force_apply: bool = False  # Применить даже если прошло мало времени


class DecayResult(BaseModel):
    """Результат применения декремента"""
    zones_decayed: List[Dict[str, str]] = Field(default_factory=list)
    total_xp_lost: float = 0.0
    days_processed: int = 0
