"""
База данных упражнений (40+ упражнений).
Каждое упражнение содержит:
- name: название
- zones: Dict[zone_name, coefficient] - коэффициенты влияния на зоны
- type: тип нагрузки (strength, endurance, mobility, flexibility, cardio)
- intensity_multiplier: множитель интенсивности (для расчёта XP)
- recommendations: рекомендации для новичка/среднего/продвинутого
"""

from typing import Dict, List, Any

ExerciseDB = List[Dict[str, Any]]

EXERCISES: ExerciseDB = [
    # ========================================================================
    # LEGS (НОГИ) - 8 упражнений
    # ========================================================================
    {
        "id": "squats_001",
        "name": "Приседания (Squats)",
        "zones": {"Legs": 1.0, "Core": 0.4, "Back": 0.2},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "bodyweight"},
            "intermediate": {"sets": 4, "reps": 15, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 20, "weight": "heavy"},
        },
    },
    {
        "id": "lunges_001",
        "name": "Выпады (Lunges)",
        "zones": {"Legs": 0.9, "Core": 0.3, "Mobility": 0.2},
        "type": "strength",
        "intensity_multiplier": 0.9,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "weight": "bodyweight"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "dumbbells"},
            "advanced": {"sets": 5, "reps": 20, "weight": "barbell"},
        },
    },
    {
        "id": "deadlift_001",
        "name": "Становая тяга (Deadlift)",
        "zones": {"Legs": 0.8, "Back": 0.9, "Core": 0.5, "Arms": 0.3},
        "type": "strength",
        "intensity_multiplier": 1.2,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 5, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 8, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 10, "weight": "heavy"},
        },
    },
    {
        "id": "calf_raises_001",
        "name": "Подъёмы на носки (Calf Raises)",
        "zones": {"Legs": 0.7, "Mobility": 0.1},
        "type": "strength",
        "intensity_multiplier": 0.6,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 15, "weight": "bodyweight"},
            "intermediate": {"sets": 4, "reps": 25, "weight": "dumbbells"},
            "advanced": {"sets": 5, "reps": 40, "weight": "barbell"},
        },
    },
    {
        "id": "leg_press_001",
        "name": "Жим ногами (Leg Press)",
        "zones": {"Legs": 1.0, "Core": 0.2},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 15, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 20, "weight": "heavy"},
        },
    },
    {
        "id": "goblet_squat_001",
        "name": "Кубковые приседания (Goblet Squat)",
        "zones": {"Legs": 0.9, "Core": 0.5, "Arms": 0.2},
        "type": "strength",
        "intensity_multiplier": 0.9,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light_kettlebell"},
            "intermediate": {"sets": 4, "reps": 15, "weight": "moderate_kettlebell"},
            "advanced": {"sets": 5, "reps": 25, "weight": "heavy_kettlebell"},
        },
    },
    {
        "id": "bulgarian_split_001",
        "name": "Болгарские сплит-приседания",
        "zones": {"Legs": 0.95, "Core": 0.4, "Mobility": 0.3},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 6, "weight": "bodyweight"},
            "intermediate": {"sets": 4, "reps": 10, "weight": "dumbbells"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy_dumbbells"},
        },
    },
    {
        "id": "wall_sit_001",
        "name": "Стенка (Wall Sit)",
        "zones": {"Legs": 0.8, "Core": 0.3},
        "type": "endurance",
        "intensity_multiplier": 0.7,
        "isometric": True,
        "recommendations": {
            "beginner": {"sets": 3, "duration_seconds": 30},
            "intermediate": {"sets": 4, "duration_seconds": 60},
            "advanced": {"sets": 5, "duration_seconds": 120},
        },
    },
    # ========================================================================
    # BACK (СПИНА) - 6 упражнений
    # ========================================================================
    {
        "id": "pullups_001",
        "name": "Подтягивания (Pull-ups)",
        "zones": {"Back": 1.0, "Arms": 0.7, "Core": 0.3},
        "type": "strength",
        "intensity_multiplier": 1.2,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 3, "assistance": "band"},
            "intermediate": {"sets": 4, "reps": 8, "assistance": "none"},
            "advanced": {"sets": 5, "reps": 15, "weight": "weighted"},
        },
    },
    {
        "id": "bent_row_001",
        "name": "Тяга в наклоне (Bent-over Row)",
        "zones": {"Back": 0.95, "Arms": 0.5, "Core": 0.4, "Legs": 0.2},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy"},
        },
    },
    {
        "id": "lat_pulldown_001",
        "name": "Тяга верхнего блока (Lat Pulldown)",
        "zones": {"Back": 0.9, "Arms": 0.6, "Core": 0.2},
        "type": "strength",
        "intensity_multiplier": 0.9,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy"},
        },
    },
    {
        "id": "superman_001",
        "name": "Супермен (Superman Hold)",
        "zones": {"Back": 0.8, "Core": 0.5, "Glutes": 0.3},
        "type": "endurance",
        "intensity_multiplier": 0.6,
        "isometric": True,
        "recommendations": {
            "beginner": {"sets": 3, "duration_seconds": 20},
            "intermediate": {"sets": 4, "duration_seconds": 40},
            "advanced": {"sets": 5, "duration_seconds": 60},
        },
    },
    {
        "id": "reverse_fly_001",
        "name": "Обратные разведения (Reverse Fly)",
        "zones": {"Back": 0.7, "Arms": 0.3, "Mobility": 0.2},
        "type": "strength",
        "intensity_multiplier": 0.7,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 12, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 15, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 20, "weight": "moderate"},
        },
    },
    {
        "id": "good_morning_001",
        "name": "Доброе утро (Good Morning)",
        "zones": {"Back": 0.85, "Legs": 0.4, "Core": 0.5},
        "type": "strength",
        "intensity_multiplier": 0.9,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "weight": "bodyweight"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "barbell_light"},
            "advanced": {"sets": 5, "reps": 15, "weight": "barbell_moderate"},
        },
    },
    # ========================================================================
    # CHEST (ГРУДЬ) - 5 упражнений
    # ========================================================================
    {
        "id": "pushups_001",
        "name": "Отжимания (Push-ups)",
        "zones": {"Chest": 1.0, "Arms": 0.6, "Core": 0.4},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "variation": "knee"},
            "intermediate": {"sets": 4, "reps": 15, "variation": "standard"},
            "advanced": {"sets": 5, "reps": 25, "variation": "decline"},
        },
    },
    {
        "id": "bench_press_001",
        "name": "Жим лёжа (Bench Press)",
        "zones": {"Chest": 1.0, "Arms": 0.5, "Back": 0.2},
        "type": "strength",
        "intensity_multiplier": 1.1,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 10, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 12, "weight": "heavy"},
        },
    },
    {
        "id": "incline_press_001",
        "name": "Жим на наклонной скамье (Incline Press)",
        "zones": {"Chest": 0.9, "Arms": 0.5, "Shoulders": 0.4},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy"},
        },
    },
    {
        "id": "dips_001",
        "name": "Отжимания на брусьях (Dips)",
        "zones": {"Chest": 0.85, "Arms": 0.7, "Core": 0.3},
        "type": "strength",
        "intensity_multiplier": 1.1,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 5, "assistance": "band"},
            "intermediate": {"sets": 4, "reps": 10, "assistance": "none"},
            "advanced": {"sets": 5, "reps": 15, "weight": "weighted"},
        },
    },
    {
        "id": "chest_fly_001",
        "name": "Разведения гантелей (Chest Fly)",
        "zones": {"Chest": 0.9, "Arms": 0.3, "Mobility": 0.2},
        "type": "strength",
        "intensity_multiplier": 0.8,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 15, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 20, "weight": "moderate"},
        },
    },
    # ========================================================================
    # ARMS (РУКИ) - 6 упражнений
    # ========================================================================
    {
        "id": "bicep_curl_001",
        "name": "Сгибания на бицепс (Bicep Curl)",
        "zones": {"Arms": 1.0, "Core": 0.1},
        "type": "strength",
        "intensity_multiplier": 0.7,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy"},
        },
    },
    {
        "id": "tricep_ext_001",
        "name": "Разгибания на трицепс (Tricep Extension)",
        "zones": {"Arms": 0.95, "Core": 0.1},
        "type": "strength",
        "intensity_multiplier": 0.7,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 15, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 20, "weight": "heavy"},
        },
    },
    {
        "id": "hammer_curl_001",
        "name": "Молотки (Hammer Curl)",
        "zones": {"Arms": 0.9, "Forearms": 0.4},
        "type": "strength",
        "intensity_multiplier": 0.7,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy"},
        },
    },
    {
        "id": "close_grip_push_001",
        "name": "Узкие отжимания (Close-grip Push-up)",
        "zones": {"Arms": 0.85, "Chest": 0.5, "Core": 0.3},
        "type": "strength",
        "intensity_multiplier": 0.9,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 6, "variation": "knee"},
            "intermediate": {"sets": 4, "reps": 12, "variation": "standard"},
            "advanced": {"sets": 5, "reps": 20, "variation": "feet_elevated"},
        },
    },
    {
        "id": "chinups_001",
        "name": "Подтягивания обратным хватом (Chin-ups)",
        "zones": {"Arms": 0.8, "Back": 0.7, "Core": 0.2},
        "type": "strength",
        "intensity_multiplier": 1.1,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 3, "assistance": "band"},
            "intermediate": {"sets": 4, "reps": 8, "assistance": "none"},
            "advanced": {"sets": 5, "reps": 12, "weight": "weighted"},
        },
    },
    {
        "id": "plank_to_push_001",
        "name": "Планка с переходом (Plank to Push-up)",
        "zones": {"Arms": 0.7, "Core": 0.8, "Chest": 0.4},
        "type": "endurance",
        "intensity_multiplier": 0.8,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8},
            "intermediate": {"sets": 4, "reps": 15},
            "advanced": {"sets": 5, "reps": 25},
        },
    },
    # ========================================================================
    # CORE (ПРЕСС/КОР) - 6 упражнений
    # ========================================================================
    {
        "id": "plank_001",
        "name": "Планка (Plank)",
        "zones": {"Core": 1.0, "Back": 0.3, "Arms": 0.2},
        "type": "endurance",
        "intensity_multiplier": 0.8,
        "isometric": True,
        "recommendations": {
            "beginner": {"sets": 3, "duration_seconds": 30},
            "intermediate": {"sets": 4, "duration_seconds": 60},
            "advanced": {"sets": 5, "duration_seconds": 120},
        },
    },
    {
        "id": "crunches_001",
        "name": "Скручивания (Crunches)",
        "zones": {"Core": 0.9, "Flexibility": 0.1},
        "type": "strength",
        "intensity_multiplier": 0.6,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 15},
            "intermediate": {"sets": 4, "reps": 25},
            "advanced": {"sets": 5, "reps": 40},
        },
    },
    {
        "id": "leg_raises_001",
        "name": "Подъёмы ног (Leg Raises)",
        "zones": {"Core": 0.95, "Hip_flexors": 0.4},
        "type": "strength",
        "intensity_multiplier": 0.7,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10, "variation": "bent_knee"},
            "intermediate": {"sets": 4, "reps": 15, "variation": "straight_leg"},
            "advanced": {"sets": 5, "reps": 25, "variation": "hanging"},
        },
    },
    {
        "id": "russian_twist_001",
        "name": "Русский твист (Russian Twist)",
        "zones": {"Core": 0.9, "Obliques": 0.6, "Mobility": 0.2},
        "type": "strength",
        "intensity_multiplier": 0.7,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 20, "weight": "bodyweight"},
            "intermediate": {"sets": 4, "reps": 30, "weight": "medicine_ball"},
            "advanced": {"sets": 5, "reps": 50, "weight": "weighted"},
        },
    },
    {
        "id": "mountain_climber_001",
        "name": "Альпинист (Mountain Climbers)",
        "zones": {"Core": 0.8, "Cardio": 0.5, "Legs": 0.3},
        "type": "cardio",
        "intensity_multiplier": 0.9,
        "recommendations": {
            "beginner": {"sets": 3, "duration_seconds": 30},
            "intermediate": {"sets": 4, "duration_seconds": 45},
            "advanced": {"sets": 5, "duration_seconds": 60},
        },
    },
    {
        "id": "dead_bug_001",
        "name": "Мёртвый жук (Dead Bug)",
        "zones": {"Core": 0.85, "Mobility": 0.3, "Back": 0.2},
        "type": "mobility",
        "intensity_multiplier": 0.6,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 10},
            "intermediate": {"sets": 4, "reps": 15},
            "advanced": {"sets": 5, "reps": 25},
        },
    },
    # ========================================================================
    # CARDIO (КАРДИО) - 5 упражнений
    # ========================================================================
    {
        "id": "running_001",
        "name": "Бег (Running)",
        "zones": {"Cardio": 1.0, "Legs": 0.4, "Core": 0.2},
        "type": "cardio",
        "intensity_multiplier": 1.0,
        "distance_based": True,
        "recommendations": {
            "beginner": {"distance_km": 2, "pace": "easy"},
            "intermediate": {"distance_km": 5, "pace": "moderate"},
            "advanced": {"distance_km": 10, "pace": "fast"},
        },
    },
    {
        "id": "cycling_001",
        "name": "Велосипед (Cycling)",
        "zones": {"Cardio": 0.95, "Legs": 0.5, "Core": 0.2},
        "type": "cardio",
        "intensity_multiplier": 0.9,
        "distance_based": True,
        "recommendations": {
            "beginner": {"distance_km": 5, "pace": "easy"},
            "intermediate": {"distance_km": 15, "pace": "moderate"},
            "advanced": {"distance_km": 30, "pace": "fast"},
        },
    },
    {
        "id": "jump_rope_001",
        "name": "Скакалка (Jump Rope)",
        "zones": {"Cardio": 0.9, "Legs": 0.4, "Coordination": 0.3},
        "type": "cardio",
        "intensity_multiplier": 1.0,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 300, "rest_between": 30},
            "intermediate": {"duration_seconds": 600, "rest_between": 20},
            "advanced": {"duration_seconds": 900, "rest_between": 10},
        },
    },
    {
        "id": "burpees_001",
        "name": "Бёрпи (Burpees)",
        "zones": {"Cardio": 0.95, "Full_body": 0.7, "Core": 0.4},
        "type": "cardio",
        "intensity_multiplier": 1.2,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 5},
            "intermediate": {"sets": 4, "reps": 15},
            "advanced": {"sets": 5, "reps": 30},
        },
    },
    {
        "id": "hiit_001",
        "name": "HIIT тренировка",
        "zones": {"Cardio": 1.0, "Full_body": 0.8, "Core": 0.4},
        "type": "cardio",
        "intensity_multiplier": 1.3,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 900, "work_rest_ratio": "1:2"},
            "intermediate": {"duration_seconds": 1200, "work_rest_ratio": "1:1"},
            "advanced": {"duration_seconds": 1800, "work_rest_ratio": "2:1"},
        },
    },
    # ========================================================================
    # FLEXIBILITY & MOBILITY (ГИБКОСТЬ И МОБИЛЬНОСТЬ) - 6 упражнений
    # ========================================================================
    {
        "id": "yoga_flow_001",
        "name": "Йога поток (Yoga Flow)",
        "zones": {"Flexibility": 0.9, "Mobility": 0.8, "Core": 0.4, "Cardio": 0.2},
        "type": "flexibility",
        "intensity_multiplier": 0.8,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 900},
            "intermediate": {"duration_seconds": 1800},
            "advanced": {"duration_seconds": 3600},
        },
    },
    {
        "id": "dynamic_stretch_001",
        "name": "Динамическая растяжка",
        "zones": {"Flexibility": 0.8, "Mobility": 0.9, "Cardio": 0.2},
        "type": "mobility",
        "intensity_multiplier": 0.6,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 600},
            "intermediate": {"duration_seconds": 900},
            "advanced": {"duration_seconds": 1200},
        },
    },
    {
        "id": "foam_rolling_001",
        "name": "Фом-роллинг (Foam Rolling)",
        "zones": {"Flexibility": 0.7, "Mobility": 0.8, "Recovery": 0.5},
        "type": "mobility",
        "intensity_multiplier": 0.5,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 600},
            "intermediate": {"duration_seconds": 900},
            "advanced": {"duration_seconds": 1200},
        },
    },
    {
        "id": "hip_mobility_001",
        "name": "Мобильность бёдер (Hip Mobility)",
        "zones": {"Mobility": 1.0, "Flexibility": 0.6, "Legs": 0.2},
        "type": "mobility",
        "intensity_multiplier": 0.6,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 600},
            "intermediate": {"duration_seconds": 900},
            "advanced": {"duration_seconds": 1200},
        },
    },
    {
        "id": "shoulder_mobility_001",
        "name": "Мобильность плеч (Shoulder Mobility)",
        "zones": {"Mobility": 0.9, "Flexibility": 0.7, "Arms": 0.2},
        "type": "mobility",
        "intensity_multiplier": 0.5,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 480},
            "intermediate": {"duration_seconds": 720},
            "advanced": {"duration_seconds": 900},
        },
    },
    {
        "id": "static_stretch_001",
        "name": "Статическая растяжка (Static Stretching)",
        "zones": {"Flexibility": 1.0, "Mobility": 0.5, "Recovery": 0.4},
        "type": "flexibility",
        "intensity_multiplier": 0.5,
        "time_based": True,
        "recommendations": {
            "beginner": {"duration_seconds": 600},
            "intermediate": {"duration_seconds": 900},
            "advanced": {"duration_seconds": 1200},
        },
    },
    # ========================================================================
    # COMPOUND / FULL BODY (КОМПЛЕКСНЫЕ) - 4 упражнения
    # ========================================================================
    {
        "id": "thrusters_001",
        "name": "Трастеры (Thrusters)",
        "zones": {"Legs": 0.7, "Chest": 0.5, "Arms": 0.6, "Core": 0.5, "Cardio": 0.4},
        "type": "strength",
        "intensity_multiplier": 1.2,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 8, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 12, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 20, "weight": "heavy"},
        },
    },
    {
        "id": "clean_press_001",
        "name": "Взятие на грудь + жим (Clean & Press)",
        "zones": {"Legs": 0.6, "Back": 0.6, "Arms": 0.7, "Core": 0.5, "Shoulders": 0.6},
        "type": "strength",
        "intensity_multiplier": 1.3,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 5, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 8, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 12, "weight": "heavy"},
        },
    },
    {
        "id": "renegade_row_001",
        "name": "Тяга ренегата (Renegade Row)",
        "zones": {"Back": 0.7, "Core": 0.8, "Arms": 0.6, "Chest": 0.3},
        "type": "strength",
        "intensity_multiplier": 1.0,
        "recommendations": {
            "beginner": {"sets": 3, "reps": 6, "weight": "light"},
            "intermediate": {"sets": 4, "reps": 10, "weight": "moderate"},
            "advanced": {"sets": 5, "reps": 15, "weight": "heavy"},
        },
    },
    {
        "id": "bear_crawl_001",
        "name": "Медвежья проходка (Bear Crawl)",
        "zones": {"Core": 0.7, "Arms": 0.6, "Legs": 0.5, "Cardio": 0.4, "Mobility": 0.3},
        "type": "cardio",
        "intensity_multiplier": 0.9,
        "distance_based": True,
        "recommendations": {
            "beginner": {"distance_meters": 20},
            "intermediate": {"distance_meters": 40},
            "advanced": {"distance_meters": 60},
        },
    },
]

# Общее количество упражнений: 46
# Можно легко расширить, добавив новые записи в список


def get_exercise_by_id(exercise_id: str) -> dict | None:
    """Получить упражнение по ID."""
    for exercise in EXERCISES:
        if exercise["id"] == exercise_id:
            return exercise
    return None


def search_exercises(query: str) -> list:
    """Поиск упражнений по названию."""
    query_lower = query.lower()
    return [
        ex for ex in EXERCISES 
        if query_lower in ex["name"].lower() or query_lower in ex.get("id", "").lower()
    ]


def get_exercises_by_zone(zone: str) -> list:
    """Получить все упражнения, влияющие на указанную зону."""
    return [ex for ex in EXERCISES if zone in ex["zones"]]


def get_all_zone_names() -> set:
    """Получить все уникальные зоны из базы упражнений."""
    zones = set()
    for ex in EXERCISES:
        zones.update(ex["zones"].keys())
    return zones
