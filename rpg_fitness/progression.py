"""
Модуль расчёта прогрессии: XP, уровни зон, общий уровень, декремент.
Содержит все математические формулы системы.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from config import (
    LEVEL_BASE_XP,
    LEVEL_EXPONENT,
    OVERALL_MIN_FLOOR,
    HALFLIFE_DAYS,
    HALFLIFE_SCALE,
    DECREMENT_BUFFER_PERCENT,
    GRACE_PERIOD_DAYS,
    NEWBIE_BOOST,
    MAX_LEVEL_CAP,
    BODY_ZONES,
    XP_PER_REP_BASE,
    XP_PER_SECOND_HOLD,
    XP_PER_MINUTE_CARDIO,
    XP_PER_KM_RUN,
)


@dataclass
class ZoneProgress:
    """Прогресс одной зоны тела."""
    name: str
    current_xp: float = 0.0
    level: int = 1
    last_trained: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "current_xp": round(self.current_xp, 2),
            "level": self.level,
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ZoneProgress":
        last_trained = None
        if data.get("last_trained"):
            last_trained = datetime.fromisoformat(data["last_trained"])
        return cls(
            name=data["name"],
            current_xp=data.get("current_xp", 0.0),
            level=data.get("level", 1),
            last_trained=last_trained,
        )


def calculate_xp_for_level(level: int, base_xp: float = LEVEL_BASE_XP, 
                           exponent: float = LEVEL_EXPONENT) -> float:
    """
    Рассчитать количество XP, необходимое для достижения следующего уровня.
    
    Формула: XP_threshold(L) = BASE_XP * (L ^ EXPONENT)
    
    Это полиномиальный рост. Пример для BASE_XP=100, EXPONENT=1.8:
    - Уровень 1→2: 100 * (1^1.8) = 100 XP
    - Уровень 2→3: 100 * (2^1.8) ≈ 348 XP
    - Уровень 3→4: 100 * (3^1.8) ≈ 722 XP
    - Уровень 4→5: 100 * (4^1.8) ≈ 1212 XP
    - Уровень 5→6: 100 * (5^1.8) ≈ 1811 XP
    - Уровень 6→7: 100 * (6^1.8) ≈ 2519 XP
    - Уровень 7→8: 100 * (7^1.8) ≈ 3334 XP
    - Уровень 8→9: 100 * (8^1.8) ≈ 4254 XP
    - Уровень 9→10: 100 * (9^1.8) ≈ 5277 XP
    - Уровень 10→11: 100 * (10^1.8) ≈ 6310 XP
    
    Накопленный XP для уровня 10 = сумма всех порогов от 1 до 10 ≈ 25,887 XP
    """
    if level < 1:
        level = 1
    return base_xp * (level ** exponent)


def calculate_total_xp_for_level(target_level: int, base_xp: float = LEVEL_BASE_XP,
                                  exponent: float = LEVEL_EXPONENT) -> float:
    """
    Рассчитать общее количество XP, необходимое для достижения target_level с нуля.
    
    Формула: Total_XP(L) = sum(XP_threshold(i) for i in 1..L-1)
    """
    if target_level <= 1:
        return 0.0
    total = 0.0
    for i in range(1, target_level):
        total += calculate_xp_for_level(i, base_xp, exponent)
    return total


def calculate_level_from_xp(total_xp: float, base_xp: float = LEVEL_BASE_XP,
                            exponent: float = LEVEL_EXPONENT) -> Tuple[int, float, float]:
    """
    Рассчитать текущий уровень и прогресс на основе накопленного XP.
    
    Возвращает: (level, current_level_xp, xp_needed_for_next)
    """
    if total_xp <= 0:
        return (1, 0.0, calculate_xp_for_level(1, base_xp, exponent))
    
    accumulated = 0.0
    level = 1
    
    while True:
        xp_needed = calculate_xp_for_level(level, base_xp, exponent)
        if accumulated + xp_needed > total_xp:
            # Мы нашли текущий уровень
            current_level_xp = total_xp - accumulated
            xp_for_next = xp_needed
            break
        accumulated += xp_needed
        level += 1
        
        # Защита от бесконечного цикла
        if level > MAX_LEVEL_CAP:
            level = MAX_LEVEL_CAP
            current_level_xp = total_xp - accumulated
            xp_for_next = float('inf')
            break
    
    return (level, current_level_xp, xp_for_next)


def calculate_overall_level(zones: Dict[str, ZoneProgress]) -> int:
    """
    Рассчитать общий уровень игрока с учётом дисбаланса.
    
    ИСПОЛЬЗУЕМАЯ ФОРМУЛА: Модифицированное гармоническое среднее
    
    Формула: Overall = n / sum(1 / max(level_i, min_floor))
    
    Почему гармоническое среднее?
    - Арифметическое: (100+1+50+50+50+50+50+50)/8 = 56.25 — слишком много, не штрафует
    - Геометрическое: (100*1*50^6)^(1/8) ≈ 36.8 — лучше, но всё ещё мягко
    - Гармоническое: 8 / (1/100 + 1/1 + 1/50*6) = 8 / (0.01 + 1 + 0.12) = 8 / 1.13 ≈ 7.08
    
    Гармоническое среднее сильно штрафует за слабые звенья, что соответствует
    принципу "цепь крепка настолько, насколько крепко её самое слабое звено".
    
    Пример расчёта для Legs=100, Back=1, остальные 6 зон=50:
    - sum_reciprocals = 1/100 + 1/1 + 6*(1/50) = 0.01 + 1 + 0.12 = 1.13
    - overall = 8 / 1.13 ≈ 7.08 → округляем до 7
    
    Это даёт диапазон ~5-12 как требовалось, а не 56 (арифметическое).
    
    Защита от нулей: используем max(level_i, MIN_FLOOR), где MIN_FLOOR=1.0
    Это гарантирует, что деление на ноль невозможно и зона с уровнем 0
    будет считаться как 1 для расчёта общего уровня.
    """
    if not zones:
        return 1
    
    levels = []
    for zone in zones.values():
        # Используем max для защиты от нулей и отрицательных значений
        effective_level = max(zone.level, OVERALL_MIN_FLOOR)
        levels.append(effective_level)
    
    n = len(levels)
    sum_reciprocals = sum(1.0 / lvl for lvl in levels)
    
    if sum_reciprocals == 0:
        # Краевой случай: все уровни бесконечность
        return MAX_LEVEL_CAP
    
    overall = n / sum_reciprocals
    return max(1, int(round(overall)))


def calculate_xp_from_exercise(
    exercise: dict,
    sets: int,
    reps: int,
    duration_seconds: Optional[float] = None,
    distance_km: Optional[float] = None,
    user_level_avg: float = 1.0,
) -> Dict[str, float]:
    """
    Рассчитать XP, начисляемое за выполнение упражнения по каждой зоне.
    
    Базовые формулы:
    - Силовые (reps-based): XP = sets * reps * XP_PER_REP_BASE * intensity_mult * zone_coeff
    - Изометрические: XP = sets * (duration / 10) * XP_PER_SECOND_HOLD * intensity_mult * zone_coeff
    - Кардио (время): XP = (duration / 60) * XP_PER_MINUTE_CARDIO * intensity_mult * zone_coeff
    - Кардио (дистанция): XP = distance_km * XP_PER_KM_RUN * intensity_mult * zone_coeff
    
    Бонус новичка: если средний уровень пользователя < 5, XP умножается на NEWBIE_BOOST
    """
    if sets <= 0:
        return {}
    
    zones_xp = {}
    zone_coeffs = exercise.get("zones", {})
    intensity_mult = exercise.get("intensity_multiplier", 1.0)
    is_isometric = exercise.get("isometric", False)
    is_distance_based = exercise.get("distance_based", False)
    is_time_based = exercise.get("time_based", False)
    exercise_type = exercise.get("type", "strength")
    
    # Бонус новичка
    newbie_bonus = NEWBIE_BOOST if user_level_avg < 5 else 1.0
    
    # Расчёт базового XP в зависимости от типа упражнения
    if is_distance_based and distance_km is not None:
        base_xp = distance_km * XP_PER_KM_RUN * intensity_mult
    elif is_time_based and duration_seconds is not None:
        base_xp = (duration_seconds / 60) * XP_PER_MINUTE_CARDIO * intensity_mult
    elif is_isometric and duration_seconds is not None:
        base_xp = sets * (duration_seconds / 10) * XP_PER_SECOND_HOLD * intensity_mult
    elif exercise_type == "cardio" and duration_seconds is not None:
        base_xp = (duration_seconds / 60) * XP_PER_MINUTE_CARDIO * intensity_mult
    else:
        # Стандартная силовая формула
        base_xp = sets * reps * XP_PER_REP_BASE * intensity_mult
    
    # Распределение XP по зонам с коэффициентами
    for zone_name, coeff in zone_coeffs.items():
        zone_xp = base_xp * coeff * newbie_bonus
        zones_xp[zone_name] = round(zone_xp, 2)
    
    return zones_xp


def apply_decrement(
    zone: ZoneProgress,
    current_time: datetime,
    halflife_days: float = HALFLIFE_DAYS,
    halflife_scale: float = HALFLIFE_SCALE,
    buffer_percent: float = DECREMENT_BUFFER_PERCENT,
    grace_period: int = GRACE_PERIOD_DAYS,
) -> ZoneProgress:
    """
    Применить декремент (детренинг) к зоне на основе времени простоя.
    
    Формула потери XP:
    - Период полураспада зависит от уровня: HL = halflife_days + level * halflife_scale
    - Коэффициент потерь: loss_rate = ln(2) / HL
    - Оставшийся XP: new_xp = old_xp * exp(-loss_rate * days_skipped)
    
    Правила:
    - 0-1 день пропуска: без потерь (grace_period)
    - 2 дня: начало мягкого снижения
    - 3+ дня: прогрессивный декремент по экспоненте
    
    Защитный буфер: минимальные buffer_percent (10%) XP никогда не сгорают.
    Это мотивирует возвращаться, даже после долгого простоя.
    
    Пример расчёта:
    - Зона уровня 10, XP = 5000, пропуск 7 дней
    - HL = 7 + 10 * 0.1 = 8 дней
    - loss_rate = ln(2) / 8 ≈ 0.0866
    - remaining = 5000 * exp(-0.0866 * 7) ≈ 5000 * 0.545 ≈ 2725
    - С защитным буфером: max(2725, 5000 * 0.10) = 2725 (буфер не активен)
    
    Пример с буфером:
    - Пропуск 30 дней, remaining = 5000 * exp(-0.0866 * 30) ≈ 5000 * 0.074 ≈ 370
    - С буфером: max(370, 5000 * 0.10) = 500
    """
    if zone.last_trained is None:
        return zone  # Нет данных о последней тренировке
    
    days_skipped = (current_time - zone.last_trained).days
    
    if days_skipped <= grace_period:
        return zone  # В пределах грейс-периода, потерь нет
    
    # Расчёт периода полураспада с учётом уровня
    effective_halflife = halflife_days + zone.level * halflife_scale
    
    # Коэффициент потерь
    loss_rate = math.log(2) / effective_halflife
    
    # Экспоненциальное затухание
    decay_factor = math.exp(-loss_rate * days_skipped)
    
    # Новый XP
    new_xp = zone.current_xp * decay_factor
    
    # Применение защитного буфера
    min_xp = zone.current_xp * buffer_percent
    new_xp = max(new_xp, min_xp)
    
    # Пересчёт уровня на основе нового XP
    new_level, _, _ = calculate_level_from_xp(new_xp)
    
    return ZoneProgress(
        name=zone.name,
        current_xp=new_xp,
        level=new_level,
        last_trained=zone.last_trained,  # Не меняем last_trained
    )


def apply_decrement_all_zones(
    zones: Dict[str, ZoneProgress],
    current_time: Optional[datetime] = None,
) -> Dict[str, ZoneProgress]:
    """Применить декремент ко всем зонам."""
    if current_time is None:
        current_time = datetime.now()
    
    updated_zones = {}
    for zone_name, zone in zones.items():
        updated_zones[zone_name] = apply_decrement(zone, current_time)
    
    return updated_zones


def get_zone_progress_percentage(zone: ZoneProgress) -> float:
    """Получить процент прогресса до следующего уровня (0.0 - 1.0)."""
    _, current_xp, xp_needed = calculate_level_from_xp(zone.current_xp)
    if xp_needed == 0 or xp_needed == float('inf'):
        return 1.0
    return min(1.0, current_xp / xp_needed)


def print_level_table(base_xp: float = LEVEL_BASE_XP, exponent: float = LEVEL_EXPONENT, 
                      max_level: int = 10) -> None:
    """Вывести таблицу XP для первых N уровней."""
    print(f"\n{'='*60}")
    print(f"ТАБЛИЦА ПРОГРЕССИИ УРОВНЕЙ (BASE={base_xp}, EXP={exponent})")
    print(f"{'='*60}")
    print(f"{'Уровень':<10} {'XP для след.':<15} {'Накоплено XP':<15}")
    print(f"{'-'*60}")
    
    accumulated = 0.0
    for level in range(1, max_level + 1):
        xp_for_next = calculate_xp_for_level(level, base_xp, exponent)
        print(f"{level:<10} {xp_for_next:<15.1f} {accumulated:<15.1f}")
        accumulated += xp_for_next
    
    print(f"{'-'*60}")
    print(f"Для уровня {max_level + 1} требуется накопить: {accumulated:.1f} XP")
    print(f"{'='*60}\n")


# Тестовая функция для демонстрации работы формул
def demo_formulas() -> None:
    """Демонстрация работы всех формул."""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ МАТЕМАТИЧЕСКИХ МОДЕЛЕЙ RPG FITNESS")
    print("="*70)
    
    # 1. Таблица прогрессии
    print_level_table()
    
    # 2. Пример расчёта общего уровня с дисбалансом
    print("\nПРИМЕР РАСЧЁТА ОБЩЕГО УРОВНЯ С ДИСБАЛАНСОМ:")
    print("-"*50)
    
    test_zones = {
        "Legs": ZoneProgress(name="Legs", current_xp=calculate_total_xp_for_level(100), level=100),
        "Back": ZoneProgress(name="Back", current_xp=0, level=1),
        "Chest": ZoneProgress(name="Chest", current_xp=calculate_total_xp_for_level(50), level=50),
        "Arms": ZoneProgress(name="Arms", current_xp=calculate_total_xp_for_level(50), level=50),
        "Core": ZoneProgress(name="Core", current_xp=calculate_total_xp_for_level(50), level=50),
        "Cardio": ZoneProgress(name="Cardio", current_xp=calculate_total_xp_for_level(50), level=50),
        "Flexibility": ZoneProgress(name="Flexibility", current_xp=calculate_total_xp_for_level(50), level=50),
        "Mobility": ZoneProgress(name="Mobility", current_xp=calculate_total_xp_for_level(50), level=50),
    }
    
    overall = calculate_overall_level(test_zones)
    arithmetic_mean = sum(z.level for z in test_zones.values()) / len(test_zones)
    
    print(f"Уровни зон: Legs=100, Back=1, остальные=50")
    print(f"Арифметическое среднее: {arithmetic_mean:.2f} (НЕ используется)")
    print(f"Гармоническое среднее (наш метод): {overall}")
    print(f"Разница: {arithmetic_mean - overall:.2f} уровней штрафа за дисбаланс")
    
    # 3. Пример декремента
    print("\nПРИМЕР ДЕКРЕМЕНТА (ДЕТРЕНИНГА):")
    print("-"*50)
    
    test_zone = ZoneProgress(
        name="Legs",
        current_xp=5000,
        level=10,
        last_trained=datetime.now() - timedelta(days=14)
    )
    
    print(f"До декремента: XP={test_zone.current_xp:.1f}, Level={test_zone.level}")
    decremented = apply_decrement(test_zone, datetime.now())
    print(f"После 14 дней пропуска: XP={decremented.current_xp:.1f}, Level={decremented.level}")
    print(f"Потеряно XP: {test_zone.current_xp - decremented.current_xp:.1f}")
    print(f"Потеряно уровней: {test_zone.level - decremented.level}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    demo_formulas()
