"""
Конфигурация системы RPG Fitness Tracker.
Все настраиваемые параметры вынесены сюда для лёгкой калибровки.
"""

from typing import Dict, List

# =============================================================================
# 1. ЗОНЫ ТЕЛА
# =============================================================================
BODY_ZONES: List[str] = [
    "Legs",         # Ноги
    "Back",         # Спина
    "Chest",        # Грудь
    "Arms",         # Руки
    "Core",         # Пресс/Кор
    "Cardio",       # Кардио
    "Flexibility",  # Гибкость
    "Mobility",     # Мобильность
]

# =============================================================================
# 2. ФОРМУЛА ПРОГРЕССИИ УРОВНЯ ЗОНЫ
# =============================================================================
# Формула: XP_to_level = base_xp * (level ^ exponent)
# Это полиномиальный рост. Для уровня L требуется сумма XP от 1 до L.
LEVEL_BASE_XP: float = 100.0      # Базовое количество XP для уровня 1
LEVEL_EXPONENT: float = 1.8       # Экспонента роста (1.5 = мягкий, 2.0 = квадратичный)

# Пример расчёта порога для уровня N:
# threshold(N) = BASE_XP * (N ^ EXPONENT)
# Накопленный XP для уровня N = sum(threshold(i) for i in 1..N)

# =============================================================================
# 3. КОНВЕРСИЯ УПРАЖНЕНИЙ В XP
# =============================================================================
# Базовая формула: XP = (reps * sets * intensity_multiplier) * zone_coefficient
# Для изометрических упражнений: XP = (seconds / 10) * zone_coefficient
# Для кардио: XP = (distance_km * 100) * zone_coefficient или (minutes * 5) * zone_coefficient

XP_PER_REP_BASE: float = 1.0      # Базовое XP за одно повторение
XP_PER_SECOND_HOLD: float = 0.5   # XP за секунду удержания (планка и т.п.)
XP_PER_MINUTE_CARDIO: float = 10.0 # XP за минуту кардио
XP_PER_KM_RUN: float = 50.0       # XP за км бега/езды

# =============================================================================
# 4. ОБЩИЙ УРОВЕНЬ (PENALTY FORMULA)
# =============================================================================
# Используем модифицированное гармоническое среднее с весами
# Формула: Overall = n / sum(1 / max(level_i, min_floor))
# min_floor защищает от деления на ноль и слишком сильного влияния одной зоны
OVERALL_MIN_FLOOR: float = 1.0    # Минимальный уровень зоны для расчёта общего

# Альтернатива: геометрическое среднее с коррекцией
# Overall = (prod(level_i)) ^ (1/n)
# Мы используем гармоническое, так как оно сильнее штрафует за слабые звенья

# =============================================================================
# 5. ДЕКРЕМЕНТ (ДЕТРЕНИНГ)
# =============================================================================
# Период полураспада XP в днях для разных уровней
# Чем выше уровень, тем быстрее потеря (принцип обратимости)
HALFLIFE_DAYS: float = 7.0        # Период полураспада для среднего уровня
HALFLIFE_SCALE: float = 0.1       # Насколько увеличивается halflife с уровнем

# Формула ежедневной потери:
# loss_rate = ln(2) / (HALFLIFE_DAYS + current_level * HALFLIFE_SCALE)
# new_xp = old_xp * exp(-loss_rate * days_skipped)

# Защитный буфер: минимальный % XP, который не сгорает
DECREMENT_BUFFER_PERCENT: float = 0.10  # 10% XP сохраняется всегда

# Грейс-период: сколько дней можно пропустить без потерь
GRACE_PERIOD_DAYS: int = 1        # 1 день пропуска без последствий

# =============================================================================
# 6. БАЛАНС И НАСТРОЙКИ
# =============================================================================
MAX_LEVEL_CAP: int = 200          # Максимальный уровень зоны (для масштабирования)
NEWBIE_BOOST: float = 1.5         # Множитель XP для новичков (первые 5 уровней)

# Настройки для разных типов пользователей
DIFFICULTY_PRESETS = {
    "easy": {
        "LEVEL_BASE_XP": 80.0,
        "LEVEL_EXPONENT": 1.6,
        "HALFLIFE_DAYS": 10.0,
        "NEWBIE_BOOST": 2.0,
    },
    "normal": {
        "LEVEL_BASE_XP": 100.0,
        "LEVEL_EXPONENT": 1.8,
        "HALFLIFE_DAYS": 7.0,
        "NEWBIE_BOOST": 1.5,
    },
    "hard": {
        "LEVEL_BASE_XP": 150.0,
        "LEVEL_EXPONENT": 2.0,
        "HALFLIFE_DAYS": 5.0,
        "NEWBIE_BOOST": 1.2,
    },
}

# =============================================================================
# 7. СХЕМА ДАННЫХ (JSON/SQLite)
# =============================================================================
# Структура пользовательского файла (user_data.json):
"""
{
    "user_id": "unique_id",
    "created_at": "2025-01-01T00:00:00",
    "difficulty": "normal",
    "zones": {
        "Legs": {
            "current_xp": 1250.5,
            "level": 5,
            "last_trained": "2025-01-15T10:30:00"
        },
        ...
    },
    "workout_log": [
        {
            "timestamp": "2025-01-15T10:30:00",
            "exercise_id": "squats_001",
            "sets": 3,
            "reps": 15,
            "duration_seconds": null,
            "distance_km": null,
            "xp_gained": {...}  // XP по каждой зоне
        }
    ]
}
"""

# Таблица SQLite (альтернатива JSON):
"""
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    difficulty TEXT
);

CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    zone_name TEXT,
    current_xp REAL,
    level INTEGER,
    last_trained TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE workout_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    exercise_id TEXT,
    timestamp TIMESTAMP,
    sets INTEGER,
    reps INTEGER,
    duration_seconds REAL,
    distance_km REAL,
    xp_data TEXT  -- JSON с XP по зонам
);
"""
